from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import SessionLocal

from backend.services.celonis_process import (
    build_celonis_event_log,
    generate_celonis_process_summary,
    generate_celonis_export_payload,
)

from backend.services.process_mining import (
    generate_pm4py_summary,
    generate_process_variants,
    generate_directly_follows_graph,
    discover_process_model,
    discover_process_tree,
    generate_process_mining_dashboard,
)


router = APIRouter(
    prefix="/process-mining",
    tags=["Process Mining"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get("/summary")
def process_mining_summary(
    db: Session = Depends(get_db),
):
    return generate_pm4py_summary(db)


@router.get("/celonis/summary")
def celonis_process_summary(
    db: Session = Depends(get_db),
):
    return generate_celonis_process_summary(
        db
    )


@router.get("/celonis/event-log")
def celonis_event_log(
    db: Session = Depends(get_db),
):
    return {
        "platform": "Celonis",
        "source": "NEXUS",
        "process": "PROCURE_TO_PAY",
        "event_log": build_celonis_event_log(
            db
        ),
    }


@router.get("/celonis/export")
def celonis_export(
    db: Session = Depends(get_db),
):
    return generate_celonis_export_payload(
        db
    )


@router.get("/variants")
def process_variants(
    db: Session = Depends(get_db),
):
    return generate_process_variants(
        db
    )


@router.get("/dfg")
def directly_follows_graph(
    db: Session = Depends(get_db),
):
    return generate_directly_follows_graph(
        db
    )


@router.get("/discover")
def discover_petri_net(
    db: Session = Depends(get_db),
):
    return discover_process_model(db)


@router.get("/process-tree")
def process_tree(
    db: Session = Depends(get_db),
):
    return discover_process_tree(db)


@router.get("/dashboard")
def process_mining_dashboard(
    db: Session = Depends(get_db),
):
    return generate_process_mining_dashboard(
        db
    )