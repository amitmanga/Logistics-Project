import json
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "datasets"


@lru_cache(maxsize=32)
def load_dataset(name):
    with (DATA_DIR / f"{name}.json").open(encoding="utf-8") as handle:
        return json.load(handle)


def all_data():
    return {
        "jobs": load_dataset("jobs"),
        "engineers": load_dataset("engineers"),
        "parts": load_dataset("parts"),
        "inventory": load_dataset("inventory"),
        "wms_events": load_dataset("wms_events"),
        "shipments": load_dataset("shipments"),
        "transport": load_dataset("transport"),
        "routes": load_dataset("routes"),
        "suppliers": load_dataset("suppliers"),
        "carriers": load_dataset("carriers"),
        "sla": load_dataset("sla"),
        "weather": load_dataset("weather"),
        "scenarios": load_dataset("scenarios"),
    }


def pct(numerator, denominator):
    return round((numerator / denominator) * 100, 1) if denominator else 0


def money(value):
    return round(value, 2)


def status_counts(rows, key):
    counts = Counter(row[key] for row in rows)
    return [{"name": name, "value": value} for name, value in counts.most_common()]


def trend(rows, date_key, value_fn, limit=14):
    buckets = defaultdict(float)
    for row in rows:
        date = row[date_key][:10]
        buckets[date] += value_fn(row)
    return [{"date": date, "value": round(value, 2)} for date, value in sorted(buckets.items())[:limit]]


def demand_forecast():
    jobs = load_dataset("jobs")
    buckets = defaultdict(int)
    for job in jobs:
        buckets[job["requested_date"][:10]] += 1
    output = []
    for index, date in enumerate(sorted(buckets)[:14]):
        actual = buckets[date]
        output.append(
            {
                "date": date[5:],
                "actual": actual,
                "forecast": round(actual * (1.05 + ((index % 4) - 1) * 0.035)),
            }
        )
    return output


def network_nodes():
    return [
        {"id": "W-COV", "name": "Coventry NDC", "type": "Warehouse", "lat": 52.4068, "lng": -1.5197, "risk": "Low"},
        {"id": "W-MAN", "name": "Manchester Warehouse", "type": "Warehouse", "lat": 53.4808, "lng": -2.2426, "risk": "Medium"},
        {"id": "W-GLA", "name": "Glasgow Warehouse", "type": "Warehouse", "lat": 55.8642, "lng": -4.2518, "risk": "Medium"},
        {"id": "D-LON", "name": "London Depot", "type": "Depot", "lat": 51.5072, "lng": -0.1276, "risk": "High"},
        {"id": "D-MID", "name": "Midlands Depot", "type": "Depot", "lat": 52.4862, "lng": -1.8904, "risk": "Medium"},
        {"id": "D-NTH", "name": "Northern Depot", "type": "Depot", "lat": 53.8008, "lng": -1.5491, "risk": "Low"},
        {"id": "S-014", "name": "Supplier S-014", "type": "Supplier", "lat": 52.9548, "lng": -1.1581, "risk": "High"},
    ]


def network_routes():
    return [
        ["W-COV", "D-LON"],
        ["W-COV", "D-MID"],
        ["W-MAN", "D-NTH"],
        ["W-GLA", "D-NTH"],
        ["S-014", "W-COV"],
        ["W-COV", "D-MID"],
    ]


def overview():
    data = all_data()
    jobs = data["jobs"]
    shipments = data["shipments"]
    inventory = data["inventory"]
    transport = data["transport"]
    sla = data["sla"]

    delivered = sum(1 for item in shipments if item["shipment_status"] == "Delivered")
    breached = sum(1 for item in shipments if item["SLA_breach_flag"])
    complete_jobs = sum(1 for item in jobs if item["completion_status"] == "Complete")
    first_fix = sum(1 for item in jobs if item["completion_status"] == "Complete" and item["first_time_fix_flag"])
    available_parts = sum(item["available_qty"] for item in inventory)
    total_parts = available_parts + sum(item["reserved_qty"] + item["in_transit_qty"] for item in inventory)
    total_cost = sum(item["total_cost"] for item in transport)
    total_shipments = len(shipments)

    kpis = [
        {"label": "Total Demand", "value": "1.25M", "delta": 12.4, "tone": "good"},
        {"label": "Total Jobs", "value": f"{len(jobs):,}", "delta": 8.1, "tone": "good"},
        {"label": "Total Shipments", "value": f"{total_shipments:,}", "delta": 8.7, "tone": "good"},
        {"label": "On-Time Delivery %", "value": f"{pct(total_shipments - breached, total_shipments)}%", "delta": 3.8, "tone": "good"},
        {"label": "SLA Compliance %", "value": f"{pct(sum(1 for item in sla if item['risk_level'] != 'High'), len(sla))}%", "delta": 2.1, "tone": "good"},
        {"label": "OTIF %", "value": f"{pct(delivered, total_shipments)}%", "delta": -3.3, "tone": "bad"},
        {"label": "Transportation Cost", "value": f"${total_cost / 1_000_000:.2f}M", "delta": -5.6, "tone": "bad"},
        {"label": "Cost per Shipment", "value": f"${total_cost / total_shipments:.2f}", "delta": -2.2, "tone": "good"},
        {"label": "Average Delivery Time", "value": "21.4h", "delta": -4.1, "tone": "good"},
        {"label": "Inventory Availability %", "value": f"{pct(available_parts, total_parts)}%", "delta": 4.4, "tone": "good"},
        {"label": "Parts Fill Rate", "value": "91.0%", "delta": 6.2, "tone": "good"},
        {"label": "Delayed Shipments", "value": f"{sum(1 for item in shipments if item['shipment_status'] == 'Delayed'):,}", "delta": -7.4, "tone": "bad"},
        {"label": "At-Risk SLA Jobs", "value": f"{sum(1 for item in sla if item['risk_level'] == 'High'):,}", "delta": -6.8, "tone": "bad"},
        {"label": "Engineer First-Time Fix Rate", "value": f"{pct(first_fix, complete_jobs)}%", "delta": 5.7, "tone": "good"},
        {"label": "Carbon Emission / CO2", "value": f"{sum(item['CO2_emission'] for item in transport) / 1000:.1f}t", "delta": -4.8, "tone": "good"},
    ]

    inventory_position = [
        {"name": "High", "value": sum(1 for item in inventory if item["days_of_cover"] >= 14)},
        {"name": "Medium", "value": sum(1 for item in inventory if 7 <= item["days_of_cover"] < 14)},
        {"name": "Low", "value": sum(1 for item in inventory if 2 <= item["days_of_cover"] < 7)},
        {"name": "Obsolete", "value": sum(1 for item in inventory if item["obsolete_qty"] > 40)},
    ]

    return {
        "kpis": kpis,
        "demandForecast": demand_forecast(),
        "shipmentStatus": status_counts(shipments, "shipment_status"),
        "inventoryPosition": inventory_position,
        "transportCostTrend": [
            {"date": f"Jun {index + 1:02d}", "value": round(sum(row["total_cost"] for row in transport[index * 60 : (index + 1) * 60]) / 1000, 2)}
            for index in range(8)
        ],
        "slaRiskTrend": status_counts(sla, "risk_level"),
        "network": {"nodes": network_nodes(), "routes": network_routes()},
        "alerts": alerts(),
        "recommendations": recommendations(),
        "improvements": improvements(),
    }


def alerts():
    return [
        {"type": "High Risk of Delay", "count": 12, "severity": "High"},
        {"type": "Inventory Below Threshold", "count": 23, "severity": "Medium"},
        {"type": "Capacity Constraints", "count": 8, "severity": "Medium"},
        {"type": "Supplier / Carrier Issues", "count": 15, "severity": "High"},
        {"type": "SLA At Risk", "count": 7, "severity": "High"},
    ]


def recommendations():
    return [
        "12 shipments are at high risk of SLA breach. Recommend switching to express carrier.",
        "Part BG-VALVE-002 has only 2 days of cover. Replenish 450 units.",
        "Route R-102 can be optimized to save 18 miles and 42 minutes.",
        "Supplier S-014 has declining reliability. Shift demand to alternate supplier.",
        "Carrier C-006 has high cost per mile. Recommend reallocating 22% volume.",
        "Engineer visits in London may fail due to parts shortage. Pre-position parts at London depot.",
    ]


def improvements():
    return [
        {"metric": "On-time delivery", "before": 82, "after": 94, "unit": "%"},
        {"metric": "SLA compliance", "before": 78, "after": 93, "unit": "%"},
        {"metric": "Transport cost", "before": 100, "after": 86, "unit": "index"},
        {"metric": "Empty miles", "before": 100, "after": 82, "unit": "index"},
        {"metric": "Shipment visibility", "before": 45, "after": 96, "unit": "%"},
        {"metric": "Parts availability", "before": 72, "after": 91, "unit": "%"},
        {"metric": "First-time fix rate", "before": 68, "after": 84, "unit": "%"},
        {"metric": "Manual planning effort", "before": 100, "after": 30, "unit": "index"},
        {"metric": "Exception response time", "before": 8, "after": 1, "unit": "hours"},
    ]


def demand():
    jobs = load_dataset("jobs")
    return {
        "forecast": demand_forecast(),
        "byJobType": status_counts(jobs, "job_type"),
        "byRegion": status_counts(jobs, "region"),
        "topRows": jobs[:25],
        "recommendations": recommendations()[:3],
    }


def inventory():
    rows = load_dataset("inventory")
    parts = {part["part_id"]: part for part in load_dataset("parts")}
    risky = sorted(rows, key=lambda row: (row["days_of_cover"], -row["reserved_qty"]))[:20]
    return {
        "position": overview()["inventoryPosition"],
        "ageing": [
            {"bucket": "0-7 days", "qty": sum(row["available_qty"] for row in rows if row["days_of_cover"] < 7)},
            {"bucket": "8-14 days", "qty": sum(row["available_qty"] for row in rows if 7 <= row["days_of_cover"] < 14)},
            {"bucket": "15-30 days", "qty": sum(row["available_qty"] for row in rows if 14 <= row["days_of_cover"] < 30)},
            {"bucket": "30+ days", "qty": sum(row["available_qty"] for row in rows if row["days_of_cover"] >= 30)},
        ],
        "riskRows": [{**row, "part_name": parts[row["part_id"]]["part_name"]} for row in risky],
        "recommendations": recommendations()[1:4],
    }


def shipments():
    rows = load_dataset("shipments")
    return {
        "status": status_counts(rows, "shipment_status"),
        "trend": trend(rows, "planned_delivery_time", lambda row: 1, limit=14),
        "milestones": load_dataset("wms_events")[:40],
        "rows": rows[:60],
        "recommendations": recommendations()[0:3],
    }


def transport_cost():
    rows = load_dataset("transport")
    return {
        "trend": [
            {"date": f"Jun {index + 1:02d}", "value": round(sum(row["total_cost"] for row in rows[index * 50 : (index + 1) * 50]) / 1000, 2)}
            for index in range(10)
        ],
        "waterfall": [
            {"name": "Baseline", "value": 4.62},
            {"name": "Route saving", "value": -0.34},
            {"name": "Load consolidation", "value": -0.18},
            {"name": "Carrier switch", "value": -0.13},
            {"name": "Fuel pressure", "value": 0.22},
            {"name": "Optimized", "value": 4.19},
        ],
        "rows": rows[:40],
        "recommendations": recommendations()[2:6],
    }


def routes():
    rows = load_dataset("routes")
    return {
        "rows": sorted(rows, key=lambda row: row["route_score"])[:40],
        "riskMatrix": [
            {"name": "Low traffic / Low weather", "count": sum(1 for row in rows if row["traffic_risk"] < 40 and row["weather_risk"] < 40)},
            {"name": "High traffic / Low weather", "count": sum(1 for row in rows if row["traffic_risk"] >= 40 and row["weather_risk"] < 40)},
            {"name": "Low traffic / High weather", "count": sum(1 for row in rows if row["traffic_risk"] < 40 and row["weather_risk"] >= 40)},
            {"name": "High traffic / High weather", "count": sum(1 for row in rows if row["traffic_risk"] >= 40 and row["weather_risk"] >= 40)},
        ],
        "recommendations": recommendations()[2:5],
    }


def suppliers():
    rows = load_dataset("suppliers")
    return {"rows": sorted(rows, key=lambda row: row["risk_score"], reverse=True), "recommendations": recommendations()[3:5]}


def carriers():
    rows = load_dataset("carriers")
    return {"rows": sorted(rows, key=lambda row: row["cost_per_mile"], reverse=True), "recommendations": recommendations()[4:6]}


def sla_risk():
    rows = load_dataset("sla")
    return {
        "matrix": status_counts(rows, "risk_level"),
        "rows": sorted(rows, key=lambda row: row["breach_probability"], reverse=True)[:50],
        "recommendations": recommendations()[0:4],
    }


def engineer_parts():
    jobs = load_dataset("jobs")
    inventory_lookup = {row["part_id"]: row for row in load_dataset("inventory")}
    rows = []
    for job in jobs[:80]:
        inventory_row = inventory_lookup.get(job["required_part_id"])
        availability = "Warehouse"
        if inventory_row and inventory_row["available_qty"] > 80:
            availability = "Depot"
        if inventory_row and inventory_row["available_qty"] > 240:
            availability = "Van / Depot"
        rows.append(
            {
                "job_id": job["job_id"],
                "engineer_id": job["engineer_id"],
                "required_part": job["required_part_id"],
                "availability": availability,
                "recommended_movement": "Pre-position to depot" if availability == "Warehouse" else "Confirm van stock",
            }
        )
    return {"rows": rows, "recommendations": recommendations()[1:6]}


def wms_events():
    rows = load_dataset("wms_events")
    return {"eventTypes": status_counts(rows, "event_type"), "rows": rows[:80], "recommendations": recommendations()[0:4]}


def data_management():
    return {
        "datasets": [
            {"name": path.stem, "format": path.suffix.replace(".", "").upper(), "records": len(load_dataset(path.stem))}
            for path in sorted(DATA_DIR.glob("*.json"))
        ]
    }
