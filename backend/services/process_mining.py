from typing import Any, Dict

import pandas as pd
import pm4py

from sqlalchemy.orm import Session

from backend.services.celonis_process import (
    build_celonis_dataframe,
)


def get_pm4py_event_log(
    db: Session,
) -> pd.DataFrame:
    dataframe = build_celonis_dataframe(db)

    if dataframe.empty:
        return pd.DataFrame(
            columns=[
                "case:concept:name",
                "concept:name",
                "time:timestamp",
            ]
        )

    dataframe = dataframe.copy()

    dataframe = dataframe.rename(
        columns={
            "case_id": "case:concept:name",
            "activity": "concept:name",
            "timestamp": "time:timestamp",
            "resource_id": "org:resource",
        }
    )

    dataframe["case:concept:name"] = (
        dataframe["case:concept:name"].astype(str)
    )

    dataframe["concept:name"] = (
        dataframe["concept:name"].astype(str)
    )

    dataframe["time:timestamp"] = pd.to_datetime(
        dataframe["time:timestamp"],
        errors="coerce",
    )

    dataframe = dataframe.dropna(
        subset=[
            "case:concept:name",
            "concept:name",
            "time:timestamp",
        ]
    )

    dataframe = dataframe.sort_values(
        by=[
            "case:concept:name",
            "time:timestamp",
        ]
    ).reset_index(drop=True)

    return dataframe


def generate_pm4py_summary(
    db: Session,
) -> Dict[str, Any]:
    dataframe = get_pm4py_event_log(db)

    if dataframe.empty:
        return {
            "status": "NO_PROCESS_DATA",
            "total_events": 0,
            "total_cases": 0,
            "total_activities": 0,
            "start_activities": [],
            "end_activities": [],
        }

    start_activities = (
        dataframe.groupby("case:concept:name")["concept:name"]
        .first()
        .value_counts()
        .to_dict()
    )

    end_activities = (
        dataframe.groupby("case:concept:name")["concept:name"]
        .last()
        .value_counts()
        .to_dict()
    )

    return {
        "status": "PROCESS_DATA_AVAILABLE",
        "total_events": int(len(dataframe)),
        "total_cases": int(
            dataframe["case:concept:name"].nunique()
        ),
        "total_activities": int(
            dataframe["concept:name"].nunique()
        ),
        "activities": sorted(
            dataframe["concept:name"].unique().tolist()
        ),
        "start_activities": [
            {
                "activity": activity,
                "count": int(count),
            }
            for activity, count in start_activities.items()
        ],
        "end_activities": [
            {
                "activity": activity,
                "count": int(count),
            }
            for activity, count in end_activities.items()
        ],
    }


def generate_process_variants(
    db: Session,
) -> Dict[str, Any]:
    dataframe = get_pm4py_event_log(db)

    if dataframe.empty:
        return {
            "status": "NO_PROCESS_DATA",
            "total_variants": 0,
            "variants": [],
        }

    variants = pm4py.get_variants_as_tuples(dataframe)

    variant_records = []

    for variant, cases in variants.items():
        case_count = int(cases)

        variant_records.append(
            {
                "variant": [
                    str(activity)
                    for activity in variant
                ],
                "case_count": case_count,
                "frequency": case_count,
            }
        )

    variant_records.sort(
        key=lambda item: item["case_count"],
        reverse=True,
    )

    return {
        "status": "PROCESS_DATA_AVAILABLE",
        "total_variants": len(variant_records),
        "variants": variant_records,
    }


def generate_directly_follows_graph(
    db: Session,
) -> Dict[str, Any]:
    dataframe = get_pm4py_event_log(db)

    if dataframe.empty:
        return {
            "status": "NO_PROCESS_DATA",
            "nodes": [],
            "edges": [],
        }

    dfg_result = pm4py.discover_dfg(dataframe)

    if isinstance(dfg_result, tuple):
        dfg = dfg_result[0]
    else:
        dfg = dfg_result

    nodes = sorted(
        dataframe["concept:name"].unique().tolist()
    )

    edges = []

    for (source, target), frequency in dfg.items():
        edges.append(
            {
                "source": str(source),
                "target": str(target),
                "frequency": int(frequency),
            }
        )

    edges.sort(
        key=lambda item: item["frequency"],
        reverse=True,
    )

    return {
        "status": "PROCESS_DATA_AVAILABLE",
        "nodes": [
            {
                "id": str(node),
                "label": str(node),
            }
            for node in nodes
        ],
        "edges": edges,
        "total_nodes": len(nodes),
        "total_edges": len(edges),
    }


def discover_process_model(
    db: Session,
) -> Dict[str, Any]:
    dataframe = get_pm4py_event_log(db)

    if dataframe.empty:
        return {
            "status": "NO_PROCESS_DATA",
            "model_type": None,
        }

    net, initial_marking, final_marking = (
        pm4py.discover_petri_net_inductive(
            dataframe
        )
    )

    transitions = []

    for transition in net.transitions:
        transitions.append(
            {
                "id": str(transition.name),
                "label": (
                    str(transition.label)
                    if transition.label
                    else None
                ),
            }
        )

    places = [
        {
            "id": str(place.name),
        }
        for place in net.places
    ]

    arcs = []

    for arc in net.arcs:
        arcs.append(
            {
                "source": str(arc.source.name),
                "target": str(arc.target.name),
            }
        )

    return {
        "status": "PROCESS_MODEL_DISCOVERED",
        "model_type": "PETRI_NET",
        "statistics": {
            "places": len(net.places),
            "transitions": len(net.transitions),
            "arcs": len(net.arcs),
        },
        "transitions": transitions,
        "places": places,
        "arcs": arcs,
        "initial_marking": [
            {
                "place": str(place.name),
                "tokens": int(tokens),
            }
            for place, tokens in initial_marking.items()
        ],
        "final_marking": [
            {
                "place": str(place.name),
                "tokens": int(tokens),
            }
            for place, tokens in final_marking.items()
        ],
    }


def discover_process_tree(
    db: Session,
) -> Dict[str, Any]:
    dataframe = get_pm4py_event_log(db)

    if dataframe.empty:
        return {
            "status": "NO_PROCESS_DATA",
            "model_type": None,
            "process_tree": None,
        }

    process_tree = pm4py.discover_process_tree_inductive(
        dataframe
    )

    return {
        "status": "PROCESS_TREE_DISCOVERED",
        "model_type": "PROCESS_TREE",
        "process_tree": str(process_tree),
    }


def generate_process_mining_dashboard(
    db: Session,
) -> Dict[str, Any]:
    summary = generate_pm4py_summary(db)
    variants = generate_process_variants(db)
    dfg = generate_directly_follows_graph(db)

    return {
        "summary": summary,
        "variants": variants,
        "directly_follows_graph": dfg,
    }


def generate_process_mining_analysis(
    db: Session,
) -> Dict[str, Any]:
    summary = generate_pm4py_summary(db)
    variants = generate_process_variants(db)
    dfg = generate_directly_follows_graph(db)

    return {
        "status": "PROCESS_MINING_ANALYSIS_COMPLETE",
        "summary": summary,
        "variants": variants,
        "directly_follows_graph": dfg,
    }