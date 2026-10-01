from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.database import SessionLocal

from backend.models import (
    Supplier,
    Product,
    PurchaseRequisition,
    PurchaseOrder,
    PurchaseOrderItem,
    GoodsReceipt,
    Invoice,
    Payment,
    ProcessEvent,
)

from backend.services.procurement_engine import (
    analyze_purchase_order,
)

from backend.services.root_cause import (
    generate_root_cause_analysis,
)

from backend.services.action_planner import (
    generate_action_plan,
)

from backend.services.ai_service import (
    generate_procurement_analysis,
    generate_process_intelligence as generate_ai_process_intelligence,
    generate_root_cause_explanation,
)

from backend.services.process_intelligence import (
    generate_process_intelligence,
)

from backend.services.process_mining import (
    generate_process_mining_analysis,
)

from backend.services.execution_service import (
    execute_action_plan,
)

from backend.services.audit_service import (
    create_audit_log,
    get_audit_logs,
)

from backend.services.chatbot_service import (
    generate_nexus_chat_response,
)

from backend.services.celonis_service import (
    get_celonis_status,
    get_process_configuration,
    get_process_events,
    build_celonis_event_log,
    build_celonis_dataframe,
    generate_celonis_process_summary,
    generate_celonis_export_payload,
)

from predictive_intelligence.predictive_risk import (
    predict_procurement_risk,
)

from predictive_intelligence.ml_risk_model import (
    ml_model,
)

from simulation.scenario_engine import (
    generate_scenario_comparison,
)


router = APIRouter()


approval_store: Dict[str, dict] = {}


class ApprovalRequest(BaseModel):
    decision: str
    reviewer: str
    comment: str = ""


class AssistantRequest(BaseModel):
    question: str
    purchase_order_id: str | None = None


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def get_purchase_order_context(
    purchase_order_id: str,
    db: Session,
):
    purchase_order = (
        db.query(PurchaseOrder)
        .filter(
            PurchaseOrder.purchase_order_id
            == purchase_order_id
        )
        .first()
    )

    if not purchase_order:
        raise HTTPException(
            status_code=404,
            detail="Purchase order not found",
        )

    supplier = (
        db.query(Supplier)
        .filter(
            Supplier.supplier_id
            == purchase_order.supplier_id
        )
        .first()
    )

    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found",
        )

    requisition = (
        db.query(PurchaseRequisition)
        .filter(
            PurchaseRequisition.requisition_id
            == purchase_order.requisition_id
        )
        .first()
    )

    if not requisition:
        raise HTTPException(
            status_code=404,
            detail="Purchase requisition not found",
        )

    return (
        purchase_order,
        supplier,
        requisition,
    )


def build_control_tower_data(
    purchase_order_id: str,
    db: Session,
):
    (
        purchase_order,
        supplier,
        requisition,
    ) = get_purchase_order_context(
        purchase_order_id,
        db,
    )

    procurement_assessment = analyze_purchase_order(
        purchase_order=purchase_order,
        supplier=supplier,
        requisition=requisition,
    )

    predictive_analysis = predict_procurement_risk(
        procurement_assessment
    )

    ml_analysis = ml_model.predict(
        procurement_assessment
    )

    root_cause = generate_root_cause_analysis(
        purchase_order=purchase_order,
        supplier=supplier,
        requisition=requisition,
    )

    action_plan = generate_action_plan(
        root_cause
    )

    approval = approval_store.get(
        purchase_order_id,
        {
            "purchase_order_id": purchase_order_id,
            "approval_status": (
                "PENDING_HUMAN_APPROVAL"
            ),
            "execution_status": (
                "PENDING_HUMAN_APPROVAL"
            ),
            "human_review_required": (
                action_plan[
                    "human_review_required"
                ]
            ),
        },
    )

    execution_status = approval.get(
        "execution_status"
    )

    if execution_status == "EXECUTED":
        action_plan["execution_status"] = "EXECUTED"

    elif execution_status == (
        "APPROVED_FOR_EXECUTION"
    ):
        action_plan[
            "execution_status"
        ] = "APPROVED_FOR_EXECUTION"

    elif execution_status == "REJECTED":
        action_plan["execution_status"] = "REJECTED"

    else:
        action_plan[
            "execution_status"
        ] = action_plan.get(
            "execution_status",
            "PENDING_HUMAN_APPROVAL",
        )

    audit = get_audit_logs(
        purchase_order_id
    )

    return {
        "purchase_order": {
            "purchase_order_id": (
                purchase_order.purchase_order_id
            ),
            "requisition_id": (
                purchase_order.requisition_id
            ),
            "supplier_id": (
                purchase_order.supplier_id
            ),
            "total_amount": float(
                purchase_order.total_amount
                or 0
            ),
            "currency": (
                purchase_order.currency
            ),
            "status": purchase_order.status,
        },
        "procurement_assessment": (
            procurement_assessment
        ),
        "predictive_analysis": (
            predictive_analysis
        ),
        "ml_analysis": ml_analysis,
        "root_cause_analysis": root_cause,
        "action_plan": action_plan,
        "approval": approval,
        "audit": {
            "purchase_order_id": (
                purchase_order_id
            ),
            "audit_logs": audit,
        },
    }


@router.get("/suppliers")
def get_suppliers(
    db: Session = Depends(get_db),
):
    suppliers = db.query(Supplier).all()

    return [
        {
            "supplier_id": supplier.supplier_id,
            "supplier_name": supplier.supplier_name,
            "contact_name": supplier.contact_name,
            "email": supplier.email,
            "country": supplier.country,
            "city": supplier.city,
            "reliability_score": (
                supplier.reliability_score
            ),
        }
        for supplier in suppliers
    ]


@router.get("/products")
def get_products(
    db: Session = Depends(get_db),
):
    products = db.query(Product).all()

    return [
        {
            "product_id": product.product_id,
            "product_name": product.product_name,
            "category": product.category,
            "unit_price": product.unit_price,
            "supplier_id": product.supplier_id,
        }
        for product in products
    ]


@router.get("/purchase-requisitions")
def get_purchase_requisitions(
    db: Session = Depends(get_db),
):
    requisitions = (
        db.query(PurchaseRequisition).all()
    )

    return [
        {
            "requisition_id": (
                requisition.requisition_id
            ),
            "employee_id": requisition.employee_id,
            "department": requisition.department,
            "product_id": requisition.product_id,
            "quantity": requisition.quantity,
            "estimated_amount": (
                requisition.estimated_amount
            ),
            "status": requisition.status,
            "created_at": requisition.created_at,
        }
        for requisition in requisitions
    ]


@router.get("/purchase-orders")
def get_purchase_orders(
    db: Session = Depends(get_db),
):
    purchase_orders = db.query(
        PurchaseOrder
    ).all()

    return [
        {
            "purchase_order_id": (
                purchase_order.purchase_order_id
            ),
            "requisition_id": (
                purchase_order.requisition_id
            ),
            "supplier_id": (
                purchase_order.supplier_id
            ),
            "order_date": (
                purchase_order.order_date
            ),
            "total_amount": (
                purchase_order.total_amount
            ),
            "currency": (
                purchase_order.currency
            ),
            "status": purchase_order.status,
        }
        for purchase_order in purchase_orders
    ]


@router.get("/purchase-order-items")
def get_purchase_order_items(
    db: Session = Depends(get_db),
):
    items = db.query(
        PurchaseOrderItem
    ).all()

    return [
        {
            "po_item_id": item.po_item_id,
            "purchase_order_id": (
                item.purchase_order_id
            ),
            "product_id": item.product_id,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "line_amount": item.line_amount,
        }
        for item in items
    ]


@router.get("/goods-receipts")
def get_goods_receipts(
    db: Session = Depends(get_db),
):
    receipts = db.query(
        GoodsReceipt
    ).all()

    return [
        {
            "goods_receipt_id": (
                receipt.goods_receipt_id
            ),
            "purchase_order_id": (
                receipt.purchase_order_id
            ),
            "warehouse": receipt.warehouse,
            "receipt_date": (
                receipt.receipt_date
            ),
            "received_quantity": (
                receipt.received_quantity
            ),
        }
        for receipt in receipts
    ]


@router.get("/invoices")
def get_invoices(
    db: Session = Depends(get_db),
):
    invoices = db.query(Invoice).all()

    return [
        {
            "invoice_id": invoice.invoice_id,
            "purchase_order_id": (
                invoice.purchase_order_id
            ),
            "invoice_number": (
                invoice.invoice_number
            ),
            "invoice_date": invoice.invoice_date,
            "invoice_amount": (
                invoice.invoice_amount
            ),
            "status": invoice.status,
        }
        for invoice in invoices
    ]


@router.get("/payments")
def get_payments(
    db: Session = Depends(get_db),
):
    payments = db.query(Payment).all()

    return [
        {
            "payment_id": payment.payment_id,
            "invoice_id": payment.invoice_id,
            "payment_date": payment.payment_date,
            "payment_amount": (
                payment.payment_amount
            ),
            "status": payment.status,
        }
        for payment in payments
    ]


@router.get("/dashboard/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
):
    total_suppliers = db.query(
        func.count(
            Supplier.supplier_id
        )
    ).scalar()

    total_products = db.query(
        func.count(
            Product.product_id
        )
    ).scalar()

    total_requisitions = db.query(
        func.count(
            PurchaseRequisition.requisition_id
        )
    ).scalar()

    total_purchase_orders = db.query(
        func.count(
            PurchaseOrder.purchase_order_id
        )
    ).scalar()

    total_purchase_order_value = db.query(
        func.coalesce(
            func.sum(
                PurchaseOrder.total_amount
            ),
            0,
        )
    ).scalar()

    total_invoices = db.query(
        func.count(
            Invoice.invoice_id
        )
    ).scalar()

    total_payments = db.query(
        func.count(
            Payment.payment_id
        )
    ).scalar()

    total_payment_value = db.query(
        func.coalesce(
            func.sum(
                Payment.payment_amount
            ),
            0,
        )
    ).scalar()

    return {
        "suppliers": total_suppliers,
        "products": total_products,
        "purchase_requisitions": (
            total_requisitions
        ),
        "purchase_orders": (
            total_purchase_orders
        ),
        "purchase_order_value": float(
            total_purchase_order_value
            or 0
        ),
        "invoices": total_invoices,
        "payments": total_payments,
        "payment_value": float(
            total_payment_value
            or 0
        ),
    }


@router.get(
    "/procurement/analyze/{purchase_order_id}"
)
def analyze_procurement(
    purchase_order_id: str,
    db: Session = Depends(get_db),
):
    (
        purchase_order,
        supplier,
        requisition,
    ) = get_purchase_order_context(
        purchase_order_id,
        db,
    )

    return analyze_purchase_order(
        purchase_order=purchase_order,
        supplier=supplier,
        requisition=requisition,
    )


@router.get(
    "/procurement/ai-analyze/{purchase_order_id}"
)
def ai_analyze_procurement(
    purchase_order_id: str,
    db: Session = Depends(get_db),
):
    (
        purchase_order,
        supplier,
        requisition,
    ) = get_purchase_order_context(
        purchase_order_id,
        db,
    )

    procurement_result = analyze_purchase_order(
        purchase_order=purchase_order,
        supplier=supplier,
        requisition=requisition,
    )

    ai_analysis = generate_procurement_analysis(
        procurement_result
    )

    return {
        "procurement_assessment": (
            procurement_result
        ),
        "ai_analysis": ai_analysis,
    }


@router.get("/process-intelligence")
def get_process_intelligence(
    db: Session = Depends(get_db),
):
    return generate_process_intelligence(db)


@router.get("/process-intelligence/ai")
def get_process_intelligence_ai(
    db: Session = Depends(get_db),
):
    process_data = generate_process_intelligence(
        db
    )

    ai_analysis = (
        generate_ai_process_intelligence(
            process_data
        )
    )

    return {
        "process_intelligence": process_data,
        "ai_analysis": ai_analysis,
    }


@router.get("/process-mining")
def get_process_mining(
    db: Session = Depends(get_db),
):
    return generate_process_mining_analysis(db)


@router.get("/process-mining/summary")
def get_process_mining_summary(
    db: Session = Depends(get_db),
):
    result = generate_process_mining_analysis(
        db
    )

    return {
        "status": result.get("status"),
        "event_count": result.get(
            "event_count",
            0,
        ),
        "case_count": result.get(
            "case_count",
            0,
        ),
        "activity_count": result.get(
            "activity_count",
            0,
        ),
        "average_case_duration_hours": (
            result.get(
                "average_case_duration_hours",
                0,
            )
        ),
        "bottlenecks": result.get(
            "potential_bottleneck_activities",
            [],
        ),
        "variants": result.get(
            "variants",
            [],
        )[:10],
        "transitions": result.get(
            "directly_following_graph",
            [],
        )[:20],
    }


@router.get("/celonis/status")
def celonis_status():
    return get_celonis_status()


@router.get("/celonis/configuration")
def celonis_configuration():
    return get_process_configuration()


@router.get("/celonis/events")
def celonis_events(
    db: Session = Depends(get_db),
):
    events = get_process_events(db)

    return {
        "status": (
            "PROCESS_DATA_AVAILABLE"
            if events
            else "NO_PROCESS_DATA"
        ),
        "total_events": len(events),
        "event_log": build_celonis_event_log(db),
    }


@router.get("/celonis/summary")
def celonis_summary(
    db: Session = Depends(get_db),
):
    return generate_celonis_process_summary(db)


@router.get("/celonis/export")
def celonis_export(
    db: Session = Depends(get_db),
):
    return generate_celonis_export_payload(db)


@router.get("/celonis/dataframe")
def celonis_dataframe(
    db: Session = Depends(get_db),
):
    dataframe = build_celonis_dataframe(db)

    return {
        "status": (
            "PROCESS_DATA_AVAILABLE"
            if not dataframe.empty
            else "NO_PROCESS_DATA"
        ),
        "columns": dataframe.columns.tolist(),
        "rows": dataframe.to_dict(
            orient="records"
        ),
        "total_rows": len(dataframe),
    }


@router.get("/celonis/process-map")
def celonis_process_map(
    db: Session = Depends(get_db),
):
    result = generate_process_mining_analysis(
        db
    )

    return {
        "status": result.get(
            "status",
            "NO_PROCESS_DATA",
        ),
        "process": "PROCURE_TO_PAY",
        "case_count": result.get(
            "case_count",
            0,
        ),
        "event_count": result.get(
            "event_count",
            0,
        ),
        "activity_count": result.get(
            "activity_count",
            0,
        ),
        "transitions": result.get(
            "directly_following_graph",
            [],
        ),
    }


@router.get(
    "/procurement/root-cause/{purchase_order_id}"
)
def root_cause_procurement(
    purchase_order_id: str,
    db: Session = Depends(get_db),
):
    (
        purchase_order,
        supplier,
        requisition,
    ) = get_purchase_order_context(
        purchase_order_id,
        db,
    )

    root_cause_result = (
        generate_root_cause_analysis(
            purchase_order=purchase_order,
            supplier=supplier,
            requisition=requisition,
        )
    )

    ai_explanation = (
        generate_root_cause_explanation(
            root_cause_result
        )
    )

    return {
        "root_cause_analysis": (
            root_cause_result
        ),
        "ai_explanation": ai_explanation,
    }


@router.get(
    "/procurement/action-plan/{purchase_order_id}"
)
def procurement_action_plan(
    purchase_order_id: str,
    db: Session = Depends(get_db),
):
    (
        purchase_order,
        supplier,
        requisition,
    ) = get_purchase_order_context(
        purchase_order_id,
        db,
    )

    root_cause_result = (
        generate_root_cause_analysis(
            purchase_order=purchase_order,
            supplier=supplier,
            requisition=requisition,
        )
    )

    action_plan = generate_action_plan(
        root_cause_result
    )

    return {
        "root_cause_analysis": (
            root_cause_result
        ),
        "action_plan": action_plan,
    }


@router.post(
    "/procurement/approval/{purchase_order_id}"
)
def approve_procurement(
    purchase_order_id: str,
    approval: ApprovalRequest,
    db: Session = Depends(get_db),
):
    decision = approval.decision.strip().upper()

    if decision not in {
        "APPROVE",
        "REJECT",
    }:
        raise HTTPException(
            status_code=400,
            detail=(
                "Decision must be APPROVE "
                "or REJECT"
            ),
        )

    reviewer = approval.reviewer.strip()

    if not reviewer:
        raise HTTPException(
            status_code=400,
            detail="Reviewer name is required",
        )

    (
        purchase_order,
        supplier,
        requisition,
    ) = get_purchase_order_context(
        purchase_order_id,
        db,
    )

    root_cause_result = (
        generate_root_cause_analysis(
            purchase_order=purchase_order,
            supplier=supplier,
            requisition=requisition,
        )
    )

    action_plan = generate_action_plan(
        root_cause_result
    )

    if not action_plan.get(
        "human_review_required"
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "This procurement transaction "
                "does not require human approval."
            ),
        )

    if decision == "APPROVE":
        execution_status = (
            "APPROVED_FOR_EXECUTION"
        )
        purchase_order.status = "APPROVED"
    else:
        execution_status = "REJECTED"
        purchase_order.status = "REJECTED"

    db.commit()

    approval_result = {
        "purchase_order_id": purchase_order_id,
        "decision": decision,
        "reviewer": reviewer,
        "comment": approval.comment.strip(),
        "approval_status": execution_status,
        "execution_status": execution_status,
        "human_review_required": True,
        "approval_route": (
            action_plan["approval_route"]
        ),
        "recommended_action": (
            action_plan["recommended_action"]
        ),
    }

    approval_store[
        purchase_order_id
    ] = approval_result

    create_audit_log(
        purchase_order_id=purchase_order_id,
        event_type="HUMAN_APPROVAL",
        status=execution_status,
        actor=reviewer,
        details={
            "decision": decision,
            "comment": approval.comment.strip(),
            "approval_route": (
                action_plan["approval_route"]
            ),
            "recommended_action": (
                action_plan[
                    "recommended_action"
                ]
            ),
        },
    )

    return {
        "message": (
            "Procurement transaction approved "
            "for execution."
            if decision == "APPROVE"
            else "Procurement transaction rejected."
        ),
        "approval": approval_result,
    }


@router.get(
    "/procurement/approval/{purchase_order_id}"
)
def get_procurement_approval(
    purchase_order_id: str,
    db: Session = Depends(get_db),
):
    (
        purchase_order,
        _,
        _,
    ) = get_purchase_order_context(
        purchase_order_id,
        db,
    )

    approval = approval_store.get(
        purchase_order_id
    )

    if not approval:
        return {
            "purchase_order_id": (
                purchase_order_id
            ),
            "approval_status": (
                "PENDING_HUMAN_APPROVAL"
            ),
            "execution_status": (
                "PENDING_HUMAN_APPROVAL"
            ),
            "human_review_required": True,
        }

    return approval


@router.post(
    "/procurement/execute/{purchase_order_id}"
)
def execute_procurement(
    purchase_order_id: str,
    db: Session = Depends(get_db),
):
    (
        purchase_order,
        supplier,
        requisition,
    ) = get_purchase_order_context(
        purchase_order_id,
        db,
    )

    approval = approval_store.get(
        purchase_order_id
    )

    if not approval:
        raise HTTPException(
            status_code=400,
            detail=(
                "Human approval is required "
                "before execution."
            ),
        )

    if approval.get("decision") != "APPROVE":
        raise HTTPException(
            status_code=400,
            detail=(
                "Procurement transaction has not "
                "been approved for execution."
            ),
        )

    if approval.get(
        "execution_status"
    ) == "EXECUTED":
        raise HTTPException(
            status_code=400,
            detail=(
                "Procurement transaction has "
                "already been executed."
            ),
        )

    root_cause_result = (
        generate_root_cause_analysis(
            purchase_order=purchase_order,
            supplier=supplier,
            requisition=requisition,
        )
    )

    action_plan = generate_action_plan(
        root_cause_result
    )

    execution_result = execute_action_plan(
        purchase_order_id=purchase_order_id,
        action_plan=action_plan,
    )

    execution_status = execution_result.get(
        "execution_status",
        "EXECUTED",
    )

    approval_store[
        purchase_order_id
    ]["execution_status"] = execution_status

    action_plan["execution_status"] = (
        execution_status
    )

    execution_message = execution_result.get(
        "execution_message",
        execution_result.get(
            "message",
            "Procurement action plan executed.",
        ),
    )

    create_audit_log(
        purchase_order_id=purchase_order_id,
        event_type="PROCUREMENT_EXECUTION",
        status=execution_status,
        actor="NEXUS_EXECUTION_ENGINE",
        details={
            "executed_actions": (
                execution_result.get(
                    "executed_actions",
                    [],
                )
            ),
            "execution_message": (
                execution_message
            ),
        },
    )

    return {
        "purchase_order_id": (
            purchase_order_id
        ),
        "approval": approval_store[
            purchase_order_id
        ],
        "action_plan": action_plan,
        "execution": {
            **execution_result,
            "execution_message": (
                execution_message
            ),
        },
    }


@router.get(
    "/procurement/audit/{purchase_order_id}"
)
def get_procurement_audit(
    purchase_order_id: str,
    db: Session = Depends(get_db),
):
    get_purchase_order_context(
        purchase_order_id,
        db,
    )

    return {
        "purchase_order_id": (
            purchase_order_id
        ),
        "audit_logs": get_audit_logs(
            purchase_order_id
        ),
    }


@router.get(
    "/procurement/simulation/{purchase_order_id}"
)
def procurement_simulation(
    purchase_order_id: str,
    db: Session = Depends(get_db),
):
    (
        purchase_order,
        supplier,
        requisition,
    ) = get_purchase_order_context(
        purchase_order_id,
        db,
    )

    procurement_result = analyze_purchase_order(
        purchase_order=purchase_order,
        supplier=supplier,
        requisition=requisition,
    )

    simulation_result = (
        generate_scenario_comparison(
            procurement_result
        )
    )

    return {
        "procurement_assessment": (
            procurement_result
        ),
        "simulation": simulation_result,
    }


@router.get(
    "/procurement/predictive-risk/{purchase_order_id}"
)
def predictive_risk(
    purchase_order_id: str,
    db: Session = Depends(get_db),
):
    (
        purchase_order,
        supplier,
        requisition,
    ) = get_purchase_order_context(
        purchase_order_id,
        db,
    )

    procurement_result = analyze_purchase_order(
        purchase_order=purchase_order,
        supplier=supplier,
        requisition=requisition,
    )

    prediction = predict_procurement_risk(
        procurement_result
    )

    ml_prediction = ml_model.predict(
        procurement_result
    )

    return {
        "procurement_assessment": (
            procurement_result
        ),
        "predictive_analysis": prediction,
        "ml_analysis": ml_prediction,
    }


@router.post("/ml/train")
def train_ml_model(
    db: Session = Depends(get_db),
):
    suppliers = db.query(Supplier).all()

    supplier_lookup = {
        supplier.supplier_id: supplier
        for supplier in suppliers
    }

    requisitions = db.query(
        PurchaseRequisition
    ).all()

    requisition_lookup = {
        requisition.requisition_id: requisition
        for requisition in requisitions
    }

    purchase_orders = db.query(
        PurchaseOrder
    ).all()

    records = []

    for purchase_order in purchase_orders:
        supplier = supplier_lookup.get(
            purchase_order.supplier_id
        )

        requisition = requisition_lookup.get(
            purchase_order.requisition_id
        )

        if not supplier or not requisition:
            continue

        assessment = analyze_purchase_order(
            purchase_order=purchase_order,
            supplier=supplier,
            requisition=requisition,
        )

        records.append(assessment)

    return ml_model.train(records)


@router.get("/ml/status")
def get_ml_status():
    return {
        "trained": ml_model.is_trained,
        "algorithm": "ISOLATION_FOREST",
        "purpose": (
            "Procurement anomaly detection"
        ),
    }


@router.get(
    "/procurement/ml-risk/{purchase_order_id}"
)
def ml_procurement_risk(
    purchase_order_id: str,
    db: Session = Depends(get_db),
):
    (
        purchase_order,
        supplier,
        requisition,
    ) = get_purchase_order_context(
        purchase_order_id,
        db,
    )

    assessment = analyze_purchase_order(
        purchase_order=purchase_order,
        supplier=supplier,
        requisition=requisition,
    )

    prediction = ml_model.predict(
        assessment
    )

    return {
        "procurement_assessment": assessment,
        "ml_prediction": prediction,
    }


@router.post("/assistant/chat")
def nexus_assistant(
    request: AssistantRequest,
    db: Session = Depends(get_db),
):
    process_mining = (
        generate_process_mining_analysis(
            db
        )
    )

    process_intelligence = (
        generate_process_intelligence(
            db
        )
    )

    context = {
        "process_mining": process_mining,
        "process_intelligence": (
            process_intelligence
        ),
    }

    if request.purchase_order_id:
        (
            purchase_order,
            supplier,
            requisition,
        ) = get_purchase_order_context(
            request.purchase_order_id,
            db,
        )

        assessment = analyze_purchase_order(
            purchase_order=purchase_order,
            supplier=supplier,
            requisition=requisition,
        )

        prediction = predict_procurement_risk(
            assessment
        )

        ml_prediction = ml_model.predict(
            assessment
        )

        context[
            "purchase_order"
        ] = {
            "purchase_order_id": (
                purchase_order.purchase_order_id
            ),
            "status": purchase_order.status,
            "amount": float(
                purchase_order.total_amount
                or 0
            ),
            "supplier_id": (
                supplier.supplier_id
            ),
            "supplier_name": (
                supplier.supplier_name
            ),
        }

        context[
            "procurement_assessment"
        ] = assessment

        context[
            "predictive_analysis"
        ] = prediction

        context[
            "ml_analysis"
        ] = ml_prediction

    answer = generate_nexus_chat_response(
        request.question,
        context,
    )

    return {
        "question": request.question,
        "answer": answer,
        "context_available": {
            "process_mining": True,
            "process_intelligence": True,
            "purchase_order": bool(
                request.purchase_order_id
            ),
            "ml": ml_model.is_trained,
        },
    }


@router.get(
    "/procurement/control-tower/{purchase_order_id}"
)
def procurement_control_tower(
    purchase_order_id: str,
    db: Session = Depends(get_db),
):
    return build_control_tower_data(
        purchase_order_id,
        db,
    )