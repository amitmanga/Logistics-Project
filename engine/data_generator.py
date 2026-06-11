import csv
import json
import random
from datetime import datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "inputs"
random.seed(42)

REGIONS = ["Scotland", "Wales", "London", "Midlands", "North", "South"]
DEPOTS = ["D-LON", "D-MID", "D-NTH", "D-SCO", "D-WAL", "D-STH"]
WAREHOUSES = ["W-COV", "W-MAN", "W-GLA", "W-LON"]
BUSINESS_UNITS = ["Utility Field Services", "Smart Metering", "Energy Services"]
JOB_TYPES = ["Repair", "Service", "Install", "Emergency", "Smart Meter Exchange"]
SKILLS = ["Gas Safe", "Boiler", "Smart Meter", "Electrical", "EV Charger"]
PRIORITIES = ["Critical", "High", "Medium", "Low"]
CARRIERS = ["C-001", "C-002", "C-003", "C-004", "C-005", "C-006"]
SUPPLIERS = ["S-001", "S-002", "S-003", "S-004", "S-005", "S-006", "S-014"]
PART_CATEGORIES = ["Boiler", "Valve", "Meter", "Pump", "Sensor", "Pipework", "EV"]
STATUSES = ["Created", "Picked", "Packed", "Dispatched", "In Transit", "Delayed", "Delivered", "Exception"]
WMS_EVENTS = [
    "ASN Received",
    "Goods Received",
    "Putaway Completed",
    "Stock Adjustment",
    "Pick Started",
    "Pick Completed",
    "Pack Completed",
    "Shipment Created",
    "Shipment Loaded",
    "Shipment Dispatched",
    "Return Received",
    "Cycle Count Completed",
]

POSTCODE_PREFIX = {
    "London": ["E", "N", "SE", "SW", "W"],
    "Midlands": ["B", "CV", "DE", "LE", "NG"],
    "North": ["M", "LS", "NE", "L", "YO"],
    "Scotland": ["G", "EH", "AB", "DD", "IV"],
    "Wales": ["CF", "SA", "LL", "NP", "SY"],
    "South": ["BN", "PO", "SO", "RG", "OX"],
}


def postcode(region):
    return f"{random.choice(POSTCODE_PREFIX[region])}{random.randint(1, 99)} {random.randint(1, 9)}{random.choice('ABCDEFGHJK')}{random.choice('ABCDEFGHJK')}"


def dt(base, days=0, hours=0, minutes=0):
    return (base + timedelta(days=days, hours=hours, minutes=minutes)).isoformat(timespec="minutes")


def write_dataset(name, rows):
    DATA_DIR.mkdir(exist_ok=True)
    json_path = DATA_DIR / f"{name}.json"
    csv_path = DATA_DIR / f"{name}.csv"
    json_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def generate():
    base = datetime(2026, 6, 1, 8, 0)

    suppliers = []
    for supplier_id in SUPPLIERS:
        reliability = round(random.uniform(72, 98), 1)
        suppliers.append(
            {
                "supplier_id": supplier_id,
                "supplier_name": f"UK Utility Supplier {supplier_id[-3:]}",
                "part_category": random.choice(PART_CATEGORIES),
                "average_lead_time": random.randint(2, 14),
                "on_time_delivery_rate": round(random.uniform(76, 98), 1),
                "defect_rate": round(random.uniform(0.4, 5.8), 1),
                "cost_score": random.randint(55, 96),
                "reliability_score": reliability,
                "risk_score": round(100 - reliability + random.uniform(0, 12), 1),
            }
        )

    carriers = []
    for carrier_id in CARRIERS:
        carriers.append(
            {
                "carrier_id": carrier_id,
                "carrier_name": f"Carrier Network {carrier_id[-3:]}",
                "region": random.choice(REGIONS + ["UK"]),
                "on_time_rate": round(random.uniform(78, 97), 1),
                "cost_per_mile": round(random.uniform(1.7, 4.9), 2),
                "damage_rate": round(random.uniform(0.2, 3.7), 1),
                "capacity_score": random.randint(58, 98),
                "service_score": random.randint(62, 98),
                "reliability_score": random.randint(60, 98),
            }
        )

    engineers = []
    for index in range(1, 121):
        region = random.choice(REGIONS)
        engineers.append(
            {
                "engineer_id": f"E-{index:04d}",
                "engineer_name": f"Engineer {index:03d}",
                "region": region,
                "depot_id": random.choice(DEPOTS),
                "skill_type": random.choice(SKILLS),
                "shift_start": "08:00",
                "shift_end": random.choice(["16:00", "17:00", "18:00"]),
                "availability_status": random.choices(["Available", "On Job", "Off Shift", "Sick"], [58, 30, 8, 4])[0],
                "van_id": f"V-{index:04d}",
                "current_location": postcode(region),
                "utilization_rate": random.randint(55, 96),
                "productivity_score": random.randint(60, 98),
            }
        )

    parts = []
    for index in range(1, 91):
        category = random.choice(PART_CATEGORIES)
        parts.append(
            {
                "part_id": f"BG-{category.upper()[:5]}-{index:03d}",
                "part_name": f"{category} component {index:03d}",
                "category": category,
                "supplier_id": random.choice(SUPPLIERS),
                "unit_cost": round(random.uniform(8, 520), 2),
                "criticality": random.choice(["Critical", "High", "Medium", "Low"]),
                "stock_level": random.randint(8, 1800),
                "reorder_point": random.randint(40, 460),
                "lead_time_days": random.randint(2, 18),
                "warehouse_id": random.choice(WAREHOUSES),
                "depot_id": random.choice(DEPOTS),
            }
        )

    inventory = []
    for index, part in enumerate(parts, start=1):
        available = part["stock_level"]
        reserved = random.randint(0, min(available, 420))
        in_transit = random.randint(0, 260)
        days_cover = round((available + in_transit - reserved) / random.uniform(22, 95), 1)
        inventory.append(
            {
                "inventory_id": f"INV-{index:04d}",
                "part_id": part["part_id"],
                "warehouse_id": part["warehouse_id"],
                "depot_id": part["depot_id"],
                "available_qty": available,
                "reserved_qty": reserved,
                "in_transit_qty": in_transit,
                "obsolete_qty": random.randint(0, 90),
                "stockout_flag": available < part["reorder_point"],
                "days_of_cover": max(0.2, days_cover),
            }
        )

    routes = []
    for index in range(1, 71):
        region = random.choice(REGIONS)
        distance = random.randint(18, 410)
        traffic = random.randint(8, 94)
        weather = random.randint(4, 92)
        routes.append(
            {
                "route_id": f"R-{index:03d}",
                "origin": random.choice(DEPOTS + WAREHOUSES),
                "destination": random.choice(DEPOTS + WAREHOUSES + [postcode(region)]),
                "region": region,
                "distance_miles": distance,
                "planned_time": round(distance / random.uniform(34, 52), 1),
                "actual_time": round(distance / random.uniform(26, 48) + traffic / 70, 1),
                "traffic_risk": traffic,
                "weather_risk": weather,
                "optimized_route_flag": random.choice([True, False]),
                "route_score": round(100 - distance / 8 - traffic * 0.25 - weather * 0.2, 1),
            }
        )

    shipments = []
    transport = []
    jobs = []
    sla = []
    wms_events = []
    for index in range(1, 501):
        region = random.choice(REGIONS)
        part = random.choice(parts)
        carrier = random.choice(carriers)
        route = random.choice(routes)
        planned_dispatch = base + timedelta(days=random.randint(0, 20), hours=random.randint(0, 10))
        delay = max(0, int(random.gauss(28, 55)))
        status = random.choices(STATUSES, [8, 9, 8, 11, 19, 12, 28, 5])[0]
        if status in ["Delayed", "Exception"]:
            delay += random.randint(45, 240)
        actual_dispatch = planned_dispatch + timedelta(minutes=random.randint(0, 55))
        planned_delivery = planned_dispatch + timedelta(hours=random.randint(4, 42))
        actual_delivery = planned_delivery + timedelta(minutes=delay)
        cost = round(route["distance_miles"] * carrier["cost_per_mile"] * random.uniform(0.86, 1.22), 2)
        shipment_id = f"SH-{index:05d}"
        shipment = {
            "shipment_id": shipment_id,
            "order_id": f"O-{index:05d}",
            "part_id": part["part_id"],
            "source_location": random.choice(WAREHOUSES),
            "destination_location": random.choice(DEPOTS + [postcode(region)]),
            "carrier_id": carrier["carrier_id"],
            "planned_dispatch_time": planned_dispatch.isoformat(timespec="minutes"),
            "actual_dispatch_time": actual_dispatch.isoformat(timespec="minutes"),
            "planned_delivery_time": planned_delivery.isoformat(timespec="minutes"),
            "actual_delivery_time": actual_delivery.isoformat(timespec="minutes"),
            "shipment_status": status,
            "delay_minutes": delay,
            "SLA_breach_flag": delay > 90,
            "cost": cost,
            "carbon_emission": round(route["distance_miles"] * random.uniform(0.55, 1.2), 1),
        }
        shipments.append(shipment)
        transport.append(
            {
                "transport_id": f"T-{index:05d}",
                "vehicle_id": f"VH-{random.randint(1, 180):04d}",
                "carrier_id": carrier["carrier_id"],
                "route_id": route["route_id"],
                "depot_id": random.choice(DEPOTS),
                "driver_id": f"DR-{random.randint(1, 220):04d}",
                "distance_miles": route["distance_miles"],
                "planned_duration": route["planned_time"],
                "actual_duration": route["actual_time"],
                "fuel_cost": round(route["distance_miles"] * random.uniform(0.32, 0.58), 2),
                "total_cost": cost,
                "capacity_utilization": random.randint(42, 98),
                "empty_miles": random.randint(0, max(1, route["distance_miles"] // 3)),
                "CO2_emission": shipment["carbon_emission"],
            }
        )
        job_id = f"J-{index:05d}"
        first_fix = random.random() > 0.22
        jobs.append(
            {
                "job_id": job_id,
                "customer_id": f"CU-{random.randint(1000, 9999)}",
                "region": region,
                "postcode": postcode(region),
                "job_type": random.choice(JOB_TYPES),
                "priority": random.choice(PRIORITIES),
                "SLA_window": random.choice(["4h", "Same Day", "Next Day", "48h"]),
                "requested_date": dt(base, random.randint(0, 18)),
                "scheduled_date": dt(base, random.randint(0, 20), random.randint(1, 9)),
                "engineer_id": random.choice(engineers)["engineer_id"],
                "required_part_id": part["part_id"],
                "job_status": random.choice(["Scheduled", "In Progress", "Completed", "At Risk", "Rescheduled"]),
                "completion_status": random.choice(["Complete", "Open", "Failed Visit", "Customer Cancelled"]),
                "first_time_fix_flag": first_fix,
                "delay_reason": random.choice(["None", "Parts unavailable", "Traffic", "Weather", "Carrier delay", "Engineer absence"]),
            }
        )
        breach_probability = min(0.96, max(0.04, delay / 260 + (0.15 if not first_fix else 0)))
        sla.append(
            {
                "sla_id": f"SLA-{index:05d}",
                "job_id": job_id,
                "shipment_id": shipment_id,
                "SLA_target_time": planned_delivery.isoformat(timespec="minutes"),
                "current_eta": actual_delivery.isoformat(timespec="minutes"),
                "risk_level": "High" if breach_probability > 0.55 else "Medium" if breach_probability > 0.28 else "Low",
                "breach_probability": round(breach_probability, 2),
                "recommended_action": random.choice(["Switch carrier", "Expedite shipment", "Pre-position part", "Reassign engineer"]),
            }
        )
        for event_index in range(random.randint(3, 8)):
            wms_events.append(
                {
                    "event_id": f"WMS-{index:05d}-{event_index}",
                    "shipment_id": shipment_id,
                    "warehouse_id": random.choice(WAREHOUSES),
                    "event_type": WMS_EVENTS[min(event_index, len(WMS_EVENTS) - 1)],
                    "event_timestamp": dt(planned_dispatch, 0, event_index * 2, random.randint(0, 59)),
                    "part_id": part["part_id"],
                    "quantity": random.randint(1, 24),
                    "status": random.choice(["Completed", "Open", "Exception"]),
                }
            )

    weather = []
    for day in range(21):
        for region in REGIONS:
            condition = random.choice(["Clear", "Rain", "Wind", "Storm", "Snow", "Fog"])
            weather.append(
                {
                    "date": (base + timedelta(days=day)).date().isoformat(),
                    "region": region,
                    "weather_condition": condition,
                    "temperature": random.randint(-1, 24),
                    "storm_risk": random.randint(4, 96) if condition in ["Storm", "Wind"] else random.randint(0, 40),
                    "snow_risk": random.randint(0, 75) if condition == "Snow" else random.randint(0, 18),
                    "travel_disruption_score": random.randint(5, 95),
                }
            )

    scenarios = [
        {
            "scenario_id": f"SCN-{index:03d}",
            "scenario_name": name,
            "demand_change_percent": demand,
            "fuel_cost_change_percent": fuel,
            "carrier_capacity_change_percent": capacity,
            "weather_disruption_level": weather_level,
            "expected_SLA": round(93 - demand * 0.18 - weather_level * 0.08 + capacity * 0.05, 1),
            "expected_cost": round(4.2 + fuel * 0.04 + demand * 0.02 - capacity * 0.01, 2),
            "expected_OTIF": round(94 - demand * 0.15 - weather_level * 0.07 + capacity * 0.04, 1),
        }
        for index, (name, demand, fuel, capacity, weather_level) in enumerate(
            [
                ("Baseline", 0, 0, 0, 10),
                ("Optimized", -4, -8, 8, 10),
                ("Peak Demand", 25, 4, -8, 18),
                ("Weather Disruption", 12, 7, -12, 70),
            ],
            start=1,
        )
    ]

    for name, rows in {
        "jobs": jobs,
        "engineers": engineers,
        "parts": parts,
        "inventory": inventory,
        "wms_events": wms_events,
        "shipments": shipments,
        "transport": transport,
        "routes": routes,
        "suppliers": suppliers,
        "carriers": carriers,
        "sla": sla,
        "weather": weather,
        "scenarios": scenarios,
    }.items():
        write_dataset(name, rows)


if __name__ == "__main__":
    generate()
