import math
import random
from functools import lru_cache


REGIONS = [
    {"name": "North West", "lat": 53.4808, "lng": -2.2426, "cost": 12.45, "excess": 24, "utilization": 72},
    {"name": "Scotland", "lat": 55.8642, "lng": -4.2518, "cost": 7.68, "excess": 15, "utilization": 68},
    {"name": "Wales", "lat": 51.4816, "lng": -3.1791, "cost": 5.82, "excess": 11, "utilization": 69},
    {"name": "London", "lat": 51.5072, "lng": -0.1276, "cost": 8.74, "excess": 17, "utilization": 78},
    {"name": "Midlands", "lat": 52.4862, "lng": -1.8904, "cost": 6.95, "excess": 13, "utilization": 76},
    {"name": "North East", "lat": 54.9783, "lng": -1.6178, "cost": 4.62, "excess": 9, "utilization": 74},
    {"name": "South West", "lat": 50.7184, "lng": -3.5339, "cost": 5.64, "excess": 11, "utilization": 73},
]

JOB_TYPES = ["HomeCare Repair", "Boiler Breakdown", "Annual Service Visit", "Smart Meter Install", "Emergency Repair"]
ROOT_CAUSES = [
    {"name": "Poor Routing", "value": 35, "annualCost": 2.77},
    {"name": "Repeat Visits", "value": 22, "annualCost": 1.74},
    {"name": "Traffic Delays", "value": 15, "annualCost": 1.18},
    {"name": "Parts Issues", "value": 12, "annualCost": 0.95},
    {"name": "Utilization", "value": 10, "annualCost": 0.79},
    {"name": "Others", "value": 6, "annualCost": 0.47},
]


def gbp_m(value):
    return f"£{value:.1f}M"


def pct(value):
    return f"{value:.1f}%"


def weighted_choice(items, weights, rng):
    total = sum(weights)
    marker = rng.uniform(0, total)
    upto = 0
    for item, weight in zip(items, weights):
        if upto + weight >= marker:
            return item
        upto += weight
    return items[-1]


def month_label(index):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    year = 2025 + index // 12
    return f"{months[index % 12]} {str(year)[2:]}"


@lru_cache(maxsize=1)
def synthetic_transport_rows():
    rng = random.Random(20260617)
    rows = []
    for index in range(5000):
        region = weighted_choice(REGIONS, [18, 12, 9, 14, 12, 8, 9], rng)
        job_type = weighted_choice(JOB_TYPES, [27, 18, 24, 20, 11], rng)
        distance = max(8, rng.gauss(64 + region["excess"] * 0.72, 18))
        travel_hours = distance / rng.uniform(28, 42)
        traffic_delay = max(0, rng.gauss(region["excess"] * 1.7, 12))
        repeat = rng.random() < (0.10 + region["excess"] / 220)
        parts_available = rng.random() > (0.08 + region["excess"] / 260)
        fuel_cost = distance * 0.22
        vehicle_cost = distance * 0.18
        labour_cost = travel_hours * 38
        traffic_cost = traffic_delay / 60 * 38
        total = fuel_cost + vehicle_cost + labour_cost + traffic_cost + (22 if repeat else 0)
        rows.append(
            {
                "date": f"2026-06-{(index % 28) + 1:02d}",
                "region": region["name"],
                "engineer_id": f"ENG-{(index % 7000) + 1:05d}",
                "job_id": f"JOB-{index + 1:07d}",
                "job_type": job_type,
                "customer_latitude": round(region["lat"] + rng.uniform(-0.42, 0.42), 5),
                "customer_longitude": round(region["lng"] + rng.uniform(-0.58, 0.58), 5),
                "engineer_latitude": round(region["lat"] + rng.uniform(-0.34, 0.34), 5),
                "engineer_longitude": round(region["lng"] + rng.uniform(-0.46, 0.46), 5),
                "distance_travelled": round(distance, 1),
                "travel_time": round(travel_hours * 60 + traffic_delay, 0),
                "fuel_cost": round(fuel_cost, 2),
                "vehicle_cost": round(vehicle_cost, 2),
                "labour_travel_cost": round(labour_cost, 2),
                "traffic_delay": round(traffic_delay, 0),
                "total_transport_cost": round(total, 2),
                "job_outcome": "Repeat Visit Required" if repeat else "Completed",
                "repeat_visit_flag": repeat,
                "parts_available": parts_available,
            }
        )
    return rows


def executive_summary():
    return {
        "kpis": [
            {"label": "Annual Transportation Cost", "value": "£51.9M", "delta": 12.6, "tone": "bad"},
            {"label": "Target Cost", "value": "£44.0M", "delta": -15.2, "tone": "good"},
            {"label": "Potential Savings", "value": "£7.9M", "delta": 15.2, "tone": "good"},
            {"label": "Cost Reduction", "value": "15.2%", "delta": 15.2, "tone": "good"},
            {"label": "Annual Mileage", "value": "115.5M Miles", "delta": 8.8, "tone": "bad"},
            {"label": "Excess Mileage", "value": "17.3M Miles", "delta": -23.0, "tone": "good"},
            {"label": "CO2 Emissions", "value": "31,185 Tons", "delta": 5.4, "tone": "bad"},
            {"label": "CO2 Reduction Potential", "value": "4,671 Tons", "delta": 15.0, "tone": "good"},
        ],
        "insights": [
            "North West region is contributing 24% of excess mileage. Route clustering can reduce transportation costs by £1.2M annually.",
            "Engineer utilization is below target in Scotland and Wales regions, creating avoidable deadhead travel and overtime.",
            "Repeat visits contribute £2.1M of avoidable transportation spend, mainly from parts unavailability and skill mismatch.",
            "AI nearest-engineer allocation reduces average mileage from 75 to 58 miles per day while increasing jobs from 5.2 to 6.7.",
        ],
        "benefits": [
            {"metric": "Cost reduction", "before": 51.9, "after": 43.8, "unit": "£M"},
            {"metric": "Mileage reduction", "before": 115.5, "after": 88.9, "unit": "M miles"},
            {"metric": "Productivity", "before": 5.2, "after": 6.7, "unit": "jobs/day"},
            {"metric": "SLA performance", "before": 86, "after": 94, "unit": "%"},
        ],
    }


def monthly_trend():
    output = []
    for index in range(24):
        seasonal = math.sin(index / 2.2) * 0.18
        current = 4.18 + seasonal + (0.14 if index in {10, 11, 22, 23} else 0)
        optimized = current * (0.842 + math.sin(index / 3) * 0.01)
        output.append({"month": month_label(index), "current": round(current, 2), "optimized": round(optimized, 2)})
    return output


def cost_breakdown():
    return [
        {"region": item["name"], "fuel": round(item["cost"] * 0.22, 2), "vehicle": round(item["cost"] * 0.18, 2), "labour": round(item["cost"] * 0.46, 2), "traffic": round(item["cost"] * 0.14, 2)}
        for item in REGIONS
    ]


def top_cost_drivers():
    cumulative = 0
    rows = []
    for item in ROOT_CAUSES:
        cumulative += item["value"]
        rows.append({**item, "cumulative": cumulative})
    return rows


def region_map():
    return [
        {
            "id": item["name"].upper().replace(" ", "-"),
            "name": item["name"],
            "lat": item["lat"],
            "lng": item["lng"],
            "cost": item["cost"],
            "excess": item["excess"],
            "utilization": item["utilization"],
            "risk": "High" if item["excess"] >= 15 else "Medium" if item["excess"] >= 10 else "Low",
        }
        for item in REGIONS
    ]


def route_paths():
    before = [
        {"engineer": "ENG-00421", "path": [[53.48, -2.24], [53.70, -2.60], [53.25, -2.05], [53.82, -1.92], [53.40, -2.75]], "miles": 82},
        {"engineer": "ENG-01048", "path": [[51.51, -0.13], [51.28, -0.51], [51.70, 0.04], [51.45, -0.72], [51.60, 0.20]], "miles": 76},
        {"engineer": "ENG-02318", "path": [[55.86, -4.25], [56.05, -3.90], [55.70, -4.65], [56.18, -4.35], [55.58, -3.82]], "miles": 93},
    ]
    after = [
        {"engineer": "ENG-00421", "path": [[53.48, -2.24], [53.25, -2.05], [53.40, -2.20], [53.58, -2.32], [53.70, -2.60]], "miles": 58},
        {"engineer": "ENG-01048", "path": [[51.51, -0.13], [51.45, -0.20], [51.60, 0.20], [51.70, 0.04], [51.74, -0.15]], "miles": 55},
        {"engineer": "ENG-02318", "path": [[55.86, -4.25], [55.70, -4.10], [55.58, -3.82], [55.90, -3.70], [56.05, -3.90]], "miles": 64},
    ]
    return {"before": before, "after": after}


def optimization_workbench():
    return {
        "before": {"averageMileage": 75, "averageJobs": 5.2, "transportationCost": 51.9},
        "after": {"averageMileage": 58, "averageJobs": 6.7, "transportationCost": 43.8, "savings": 8.1},
        "engine": [
            {"step": "KMeans Clustering", "description": "Clusters 500,000 monthly jobs into engineer micro-territories using latitude, longitude, job type, and demand density.", "confidence": 93},
            {"step": "Vehicle Routing Logic", "description": "Sequences jobs to minimize route distance, travel time, and late SLA exposure.", "confidence": 89},
            {"step": "Nearest Engineer Allocation", "description": "Assigns jobs to the closest qualified engineer with parts and shift capacity.", "confidence": 91},
            {"step": "Travel Time Optimization", "description": "Applies traffic and weather delay multipliers by hour and region.", "confidence": 87},
        ],
        "mileageReduction": [
            {"metric": "Before", "miles": 75},
            {"metric": "After", "miles": 58},
        ],
        "waterfall": [
            {"name": "Current Cost", "value": 51.9},
            {"name": "Routing", "value": -2.9},
            {"name": "Allocation", "value": -1.8},
            {"name": "Repeat Visits", "value": -2.1},
            {"name": "Traffic", "value": -1.3},
            {"name": "Optimized Cost", "value": 43.8},
        ],
        "utilization": [
            {"region": item["name"], "before": item["utilization"], "after": min(92, item["utilization"] + 11)}
            for item in REGIONS
        ],
        "routes": route_paths(),
    }


def root_cause():
    return {
        "causes": ROOT_CAUSES,
        "featureImportance": [
            {"feature": "Distance to first job", "importance": 0.31},
            {"feature": "Repeat visit probability", "importance": 0.22},
            {"feature": "Traffic delay minutes", "importance": 0.17},
            {"feature": "Parts availability", "importance": 0.13},
            {"feature": "Engineer utilization", "importance": 0.10},
            {"feature": "Skill match score", "importance": 0.07},
        ],
        "fishbone": {
            "head": "High Transportation Cost",
            "bones": ["Poor Routing", "Repeat Visits", "Traffic Delays", "Incorrect Engineer Allocation", "Parts Shortages", "Low Utilization"],
        },
    }


def agents():
    return [
        {"agent": "Transportation Cost Agent", "issue": "High mileage in North West", "impact": "£1.2M excess annual spend", "recommendation": "Re-cluster engineers into 3 micro territories", "expectedSaving": "£0.9M", "confidence": 91, "priority": "High"},
        {"agent": "Route Optimization Agent", "issue": "Long first-leg travel in Scotland", "impact": "£0.8M excess annual spend", "recommendation": "Create morning route pools around Glasgow, Edinburgh, Aberdeen", "expectedSaving": "£0.6M", "confidence": 88, "priority": "High"},
        {"agent": "Engineer Allocation Agent", "issue": "Skill mismatch causing avoidable transfers", "impact": "£0.7M annual cost", "recommendation": "Assign boiler breakdowns only to Gas Safe engineers with kit availability", "expectedSaving": "£0.5M", "confidence": 86, "priority": "Medium"},
        {"agent": "Traffic Risk Agent", "issue": "Peak-hour London jobs overrun plan", "impact": "£0.5M delay cost", "recommendation": "Move non-urgent ASV jobs outside 08:00-10:00 window", "expectedSaving": "£0.4M", "confidence": 84, "priority": "Medium"},
        {"agent": "Parts Availability Agent", "issue": "Repeat visits from missing heat exchanger parts", "impact": "£0.9M repeat travel", "recommendation": "Pre-position critical parts in London, Wales, North West depots", "expectedSaving": "£0.7M", "confidence": 90, "priority": "High"},
        {"agent": "Control Tower Agent", "issue": "Weather warning in Scotland and North East", "impact": "£0.3M risk this week", "recommendation": "Reserve emergency engineer capacity and reprioritize vulnerable customers", "expectedSaving": "£0.2M", "confidence": 82, "priority": "Medium"},
    ]


def live_events():
    return [
        {"event": "Traffic Incident", "region": "North West", "riskScore": 91, "transportImpact": "£42k daily exposure", "recommendedAction": "Move 18 jobs to adjacent clusters", "savingsOpportunity": "£31k"},
        {"event": "Parts Shortage", "region": "Wales", "riskScore": 84, "transportImpact": "34 repeat visits likely", "recommendedAction": "Ship boiler kits from Midlands depot", "savingsOpportunity": "£24k"},
        {"event": "Fuel Cost Spike", "region": "UK", "riskScore": 76, "transportImpact": "£110k weekly exposure", "recommendedAction": "Prioritize low-mileage route plans", "savingsOpportunity": "£53k"},
        {"event": "Engineer Delay", "region": "London", "riskScore": 69, "transportImpact": "22 SLA windows at risk", "recommendedAction": "Reassign late jobs to nearby engineers", "savingsOpportunity": "£18k"},
        {"event": "Vehicle Breakdown", "region": "Scotland", "riskScore": 65, "transportImpact": "7 emergency visits delayed", "recommendedAction": "Activate standby van and consolidate ASV work", "savingsOpportunity": "£11k"},
        {"event": "Weather Alert", "region": "North East", "riskScore": 73, "transportImpact": "15% travel time uplift", "recommendedAction": "Protect emergency repair slots", "savingsOpportunity": "£16k"},
    ]


def simulate_financial(payload):
    fuel_price = float(payload.get("fuelPrice", 1.45))
    engineer_count = int(payload.get("engineerCount", 7000))
    jobs_volume = int(payload.get("jobsVolume", 500000))
    average_distance = float(payload.get("averageDistance", 75))
    traffic = float(payload.get("trafficPercent", 18))
    repeat_visit = float(payload.get("repeatVisitPercent", 12))
    vehicle_cost = float(payload.get("vehicleCost", 0.18))

    monthly_miles = jobs_volume * average_distance
    fuel_cost = monthly_miles * 0.151 * fuel_price
    vehicle = monthly_miles * vehicle_cost
    travel_hours = monthly_miles / 34 * (1 + traffic / 100)
    labour = travel_hours * 38
    repeat_cost = jobs_volume * repeat_visit / 100 * average_distance * 0.82
    annual_cost = (fuel_cost + vehicle + labour + repeat_cost) * 12
    optimized_cost = annual_cost * 0.848
    savings = annual_cost - optimized_cost
    investment = 2_400_000
    return {
        "annualCost": round(annual_cost / 1_000_000, 2),
        "costPerJob": round(annual_cost / (jobs_volume * 12), 2),
        "savings": round(savings / 1_000_000, 2),
        "roi": round((savings - investment) / investment * 100, 1),
        "paybackPeriod": round(investment / max(savings / 12, 1), 1),
        "carbonReduction": round(monthly_miles * 12 * 0.0000405 * 0.23),
        "optimizedCost": round(optimized_cost / 1_000_000, 2),
    }


def transport_optimization():
    rows = synthetic_transport_rows()
    return {
        "executive": executive_summary(),
        "analysis": {
            "sampleRows": rows[:30],
            "breakdown": cost_breakdown(),
            "monthlyTrend": monthly_trend(),
            "regionMap": region_map(),
            "costDrivers": top_cost_drivers(),
            "datasetProfile": [
                {"name": "Engineers", "value": "7,000"},
                {"name": "Jobs", "value": "500,000 / month"},
                {"name": "Routes", "value": "1M synthetic paths"},
                {"name": "History", "value": "24 months"},
                {"name": "Regions", "value": "100 service regions"},
            ],
        },
        "workbench": optimization_workbench(),
        "rootCause": root_cause(),
        "agents": agents(),
        "controlTower": live_events(),
        "defaultSimulation": simulate_financial({}),
    }
