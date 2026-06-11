from engine.data_service import (
    carriers,
    engineer_parts,
    inventory,
    load_dataset,
    recommendations,
    routes,
    sla_risk,
    suppliers,
)


def delivery_risk_agent():
    rows = sla_risk()["rows"][:12]
    return [
        {
            "agent": "Delivery Risk Agent",
            "job_id": row["job_id"],
            "shipment_id": row["shipment_id"],
            "risk_score": round(row["breach_probability"] * 100),
            "breach_probability": row["breach_probability"],
            "reason": "ETA exceeds target window; carrier delay and parts availability are contributing factors.",
            "recommended_action": row["recommended_action"],
        }
        for row in rows
    ]


def route_optimization_agent():
    rows = routes()["rows"][:12]
    output = []
    for row in rows:
        miles_saved = max(4, round(row["distance_miles"] * 0.11))
        time_saved = max(12, round(row["actual_time"] * 14))
        output.append(
            {
                "agent": "Route Optimization Agent",
                "current_route": row["route_id"],
                "optimized_route": f"{row['route_id']}-OPT",
                "miles_saved": miles_saved,
                "time_saved": time_saved,
                "cost_saved": round(miles_saved * 2.85, 2),
                "route_score": row["route_score"],
            }
        )
    return output


def inventory_risk_agent():
    rows = inventory()["riskRows"][:12]
    return [
        {
            "agent": "Inventory Risk Agent",
            "part_name": row["part_name"],
            "current_stock": row["available_qty"],
            "reorder_point": "Below threshold" if row["stockout_flag"] else "Near threshold",
            "days_of_cover": row["days_of_cover"],
            "recommended_replenishment_qty": max(120, row["reserved_qty"] + 180),
        }
        for row in rows
    ]


def supplier_risk_agent():
    rows = suppliers()["rows"][:10]
    return [
        {
            "agent": "Supplier Risk Agent",
            "supplier_id": row["supplier_id"],
            "supplier_risk_score": row["risk_score"],
            "lead_time_trend": f"{row['average_lead_time']} day average",
            "defect_rate": row["defect_rate"],
            "suggested_alternate_supplier": "S-002" if row["supplier_id"] != "S-002" else "S-005",
        }
        for row in rows
    ]


def carrier_allocation_agent():
    rows = carriers()["rows"][:10]
    best = sorted(load_dataset("carriers"), key=lambda row: (row["on_time_rate"], -row["cost_per_mile"]), reverse=True)[0]
    return [
        {
            "agent": "Carrier Allocation Agent",
            "current_carrier": row["carrier_id"],
            "recommended_carrier": best["carrier_id"],
            "cost_impact": f"{round((best['cost_per_mile'] - row['cost_per_mile']) * 100, 1)}%",
            "SLA_impact": f"+{round(best['on_time_rate'] - row['on_time_rate'], 1)} pts",
            "reliability_score": best["reliability_score"],
        }
        for row in rows
    ]


def cost_optimization_agent():
    transport = load_dataset("transport")
    empty_miles = sum(row["empty_miles"] for row in transport)
    cost = sum(row["total_cost"] for row in transport)
    return [
        {
            "agent": "Cost Optimization Agent",
            "empty_miles_reduction": round(empty_miles * 0.18),
            "load_consolidation": "Consolidate 34 part movements across Coventry and Manchester lanes.",
            "carrier_switching_opportunity": "Move 22% of C-006 volume to C-002.",
            "fuel_cost_saving": round(cost * 0.045, 2),
        }
    ]


def shipment_visibility_agent():
    events = load_dataset("wms_events")
    shipments = load_dataset("shipments")[:10]
    output = []
    for shipment in shipments:
        related = [event for event in events if event["shipment_id"] == shipment["shipment_id"]]
        last_event = related[-1]["event_type"] if related else "No WMS event"
        output.append(
            {
                "agent": "Shipment Visibility Agent",
                "shipment_id": shipment["shipment_id"],
                "last_known_event": last_event,
                "missing_event": "Shipment Loaded" if last_event != "Shipment Loaded" else "Proof of delivery",
                "ETA_risk": "High" if shipment["SLA_breach_flag"] else "Medium",
                "escalation_recommendation": "Notify transport control tower and confirm carrier milestone.",
            }
        )
    return output


def engineer_parts_availability_agent():
    return [
        {
            "agent": "Engineer Parts Availability Agent",
            "job_id": row["job_id"],
            "engineer_id": row["engineer_id"],
            "required_part": row["required_part"],
            "available_in": row["availability"],
            "recommended_part_movement": row["recommended_movement"],
        }
        for row in engineer_parts()["rows"][:12]
    ]


def all_agent_recommendations():
    return {
        "recommendations": recommendations(),
        "agents": [
            {"name": "Delivery Risk Agent", "status": "Active", "impact": "12 high-risk SLA jobs flagged"},
            {"name": "Route Optimization Agent", "status": "Active", "impact": "18 miles and 42 minutes saved on R-102"},
            {"name": "Inventory Risk Agent", "status": "Active", "impact": "450 units replenishment recommended"},
            {"name": "Supplier Risk Agent", "status": "Watching", "impact": "S-014 reliability declining"},
            {"name": "Carrier Allocation Agent", "status": "Active", "impact": "22% carrier reallocation opportunity"},
            {"name": "Cost Optimization Agent", "status": "Active", "impact": "14% transport cost reduction opportunity"},
            {"name": "Shipment Visibility Agent", "status": "Active", "impact": "Missing WMS events highlighted"},
            {"name": "Engineer Parts Availability Agent", "status": "Active", "impact": "London pre-positioning recommended"},
        ],
        "deliveryRisk": delivery_risk_agent(),
        "routeOptimization": route_optimization_agent(),
        "inventoryRisk": inventory_risk_agent(),
        "supplierRisk": supplier_risk_agent(),
        "carrierAllocation": carrier_allocation_agent(),
        "costOptimization": cost_optimization_agent(),
        "shipmentVisibility": shipment_visibility_agent(),
        "engineerPartsAvailability": engineer_parts_availability_agent(),
    }


def scenario_simulation(payload):
    demand = int(payload.get("demandIncrease", 10))
    fuel = int(payload.get("fuelIncrease", 8))
    capacity = int(payload.get("carrierCapacityReduction", 5))
    supplier_delay = int(payload.get("supplierDelay", 3))
    warehouse_constraint = int(payload.get("warehouseConstraint", 10))
    weather = int(payload.get("weatherDisruption", 20))
    depot_stockout = int(payload.get("depotStockout", 5))
    engineer_absence = int(payload.get("engineerAbsence", 4))

    pressure = demand * 0.28 + capacity * 0.18 + supplier_delay * 0.8 + weather * 0.12 + depot_stockout * 0.35
    cost_pressure = fuel * 0.45 + demand * 0.18 + warehouse_constraint * 0.14 + capacity * 0.22
    productivity_pressure = engineer_absence * 1.5 + depot_stockout * 0.4

    return {
        "inputs": payload,
        "outputs": [
            {"metric": "SLA impact", "baseline": 93, "scenario": round(max(62, 93 - pressure), 1), "unit": "%"},
            {"metric": "Cost impact", "baseline": 4.62, "scenario": round(4.62 * (1 + cost_pressure / 100), 2), "unit": "$M"},
            {"metric": "OTIF impact", "baseline": 94, "scenario": round(max(60, 94 - pressure * 0.82), 1), "unit": "%"},
            {"metric": "Inventory impact", "baseline": 91, "scenario": round(max(55, 91 - depot_stockout * 1.4 - supplier_delay), 1), "unit": "%"},
            {
                "metric": "Engineer productivity impact",
                "baseline": 86,
                "scenario": round(max(50, 86 - productivity_pressure), 1),
                "unit": "%",
            },
            {"metric": "Carbon emission impact", "baseline": 100, "scenario": round(100 + demand * 0.42 + weather * 0.12, 1), "unit": "index"},
        ],
        "recommendations": [
            "Move high-priority parts to London and Midlands depots before dispatch cut-off.",
            "Reserve express carrier capacity for emergency and vulnerable customer jobs.",
            "Consolidate supplier inbound loads to Coventry NDC to reduce empty miles.",
        ],
    }
