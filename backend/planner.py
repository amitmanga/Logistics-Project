from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Scenario:
    demand_surge: int
    weather_impact: int
    depot_capacity: int
    ev_priority: bool
    protect_vulnerable_sla: bool
    shift_cover: str
    parts_availability: str


BASE_QUEUE = [
    {
        "region": "London and South East",
        "workType": "Gas emergency",
        "baseJobs": 312,
        "baseGap": 18,
        "risk": "High",
        "ulezShare": 0.58,
        "action": "Pull from Midlands",
    },
    {
        "region": "Midlands",
        "workType": "Boiler repair",
        "baseJobs": 246,
        "baseGap": 7,
        "risk": "Medium",
        "ulezShare": 0.18,
        "action": "Split routes",
    },
    {
        "region": "Scotland",
        "workType": "Storm response",
        "baseJobs": 194,
        "baseGap": 11,
        "risk": "High",
        "ulezShare": 0.08,
        "action": "Extend cover",
    },
    {
        "region": "North",
        "workType": "Smart meter",
        "baseJobs": 221,
        "baseGap": -4,
        "risk": "Low",
        "ulezShare": 0.22,
        "action": "Hold plan",
    },
    {
        "region": "Wales and South West",
        "workType": "Service visit",
        "baseJobs": 168,
        "baseGap": -2,
        "risk": "Low",
        "ulezShare": 0.1,
        "action": "Hold plan",
    },
]

RISK_SCORE = {"Low": 1, "Medium": 2, "High": 3}
RISK_LABEL = {1: "Low", 2: "Medium", 3: "High"}


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def parse_scenario(payload: dict[str, Any]) -> Scenario:
    return Scenario(
        demand_surge=int(payload.get("demandSurge", 38)),
        weather_impact=int(payload.get("weatherImpact", 24)),
        depot_capacity=int(payload.get("depotCapacity", 86)),
        ev_priority=bool(payload.get("evPriority", True)),
        protect_vulnerable_sla=bool(payload.get("protectVulnerableSla", True)),
        shift_cover=str(payload.get("shiftCover", "Standard weekday")),
        parts_availability=str(payload.get("partsAvailability", "Normal stock")),
    )


def calculate_metrics(scenario: Scenario) -> dict[str, Any]:
    shift_modifier = {
        "Standard weekday": 0,
        "Extended emergency cover": -9,
        "Weekend reduced cover": 14,
    }.get(scenario.shift_cover, 0)
    parts_modifier = {
        "Normal stock": 0,
        "Boiler parts shortage": 12,
        "Meter kit shortage": 8,
    }.get(scenario.parts_availability, 0)

    open_jobs = 1010 + round(scenario.demand_surge * 7.2) + round(scenario.weather_impact * 1.8)
    at_risk = (
        28
        + round(scenario.demand_surge * 1.08)
        + round(scenario.weather_impact * 0.72)
        + parts_modifier
        + shift_modifier
        - (16 if scenario.protect_vulnerable_sla else 0)
    )
    same_day_sla = (
        97.2
        - scenario.demand_surge * 0.1
        - scenario.weather_impact * 0.05
        + (1.7 if scenario.protect_vulnerable_sla else -0.8)
        - max(0, 90 - scenario.depot_capacity) * 0.09
        - parts_modifier * 0.08
        - max(0, shift_modifier) * 0.08
    )
    fleet_utilisation = (
        74
        + round(scenario.demand_surge * 0.17)
        + round(scenario.weather_impact * 0.06)
        + (3 if scenario.ev_priority else -2)
        + max(0, 86 - scenario.depot_capacity) * 0.12
    )

    return {
        "openJobs": open_jobs,
        "sameDaySla": round(clamp(same_day_sla, 76, 99), 1),
        "atRiskAppointments": int(clamp(at_risk, 12, 180)),
        "fleetUtilisation": int(clamp(fleet_utilisation, 58, 96)),
    }


def calculate_queue(scenario: Scenario) -> list[dict[str, Any]]:
    demand_factor = 1 + scenario.demand_surge / 260
    weather_factor = 1 + scenario.weather_impact / 400
    capacity_relief = max(0, scenario.depot_capacity - 80) / 30

    rows = []
    for row in BASE_QUEUE:
        jobs = round(row["baseJobs"] * demand_factor * weather_factor)
        gap = round(row["baseGap"] + scenario.demand_surge / 18 + scenario.weather_impact / 24 - capacity_relief)
        score = RISK_SCORE[row["risk"]]

        if scenario.weather_impact > 55 and row["region"] in {"Scotland", "North"}:
            score += 1
        if scenario.parts_availability == "Boiler parts shortage" and row["workType"] == "Boiler repair":
            score += 1
        if scenario.parts_availability == "Meter kit shortage" and row["workType"] == "Smart meter":
            score += 1
        if scenario.protect_vulnerable_sla and row["workType"] == "Gas emergency":
            score = max(score, 3)
        if scenario.ev_priority and row["ulezShare"] > 0.4:
            gap -= 3

        score = int(clamp(score, 1, 3))
        action = row["action"]
        if score == 3 and gap > 8:
            action = "Escalate cover"
        elif score == 2 and gap > 4:
            action = "Rebalance crews"
        elif gap <= 0:
            action = "Hold plan"

        rows.append(
            {
                "region": row["region"],
                "workType": row["workType"],
                "jobs": jobs,
                "crewGap": f"{gap:+d} engineers",
                "risk": RISK_LABEL[score],
                "action": action,
            }
        )

    return sorted(rows, key=lambda item: (RISK_SCORE[item["risk"]], item["jobs"]), reverse=True)


def calculate_regions(queue: list[dict[str, Any]]) -> list[dict[str, Any]]:
    coordinates = {
        "Scotland": {"x": 55, "y": 25, "code": "SCO"},
        "North": {"x": 48, "y": 43, "code": "NTH"},
        "Midlands": {"x": 58, "y": 58, "code": "MID"},
        "London and South East": {"x": 66, "y": 72, "code": "LSE"},
        "Wales and South West": {"x": 38, "y": 71, "code": "WSW"},
    }

    regions = []
    for row in queue:
        risk_ratio = {"High": 0.075, "Medium": 0.052, "Low": 0.029}[row["risk"]]
        region = coordinates[row["region"]]
        regions.append(
            {
                **region,
                "name": row["region"],
                "jobs": row["jobs"],
                "atRisk": round(row["jobs"] * risk_ratio),
                "risk": row["risk"],
            }
        )
    return regions


def calculate_timeline(scenario: Scenario) -> list[dict[str, Any]]:
    depot_prep = clamp(34 + (100 - scenario.depot_capacity) * 0.25, 24, 64)
    first_jobs = clamp(62 + scenario.demand_surge * 0.18, 42, 92)
    restock = clamp(42 + scenario.weather_impact * 0.14, 26, 75)
    emergency_cover = clamp(66 + scenario.weather_impact * 0.2 + scenario.demand_surge * 0.08, 48, 96)

    if scenario.shift_cover == "Extended emergency cover":
        emergency_cover = clamp(emergency_cover + 8, 48, 98)
    if scenario.parts_availability != "Normal stock":
        restock = clamp(restock + 14, 26, 88)

    return [
        {"time": "06:00", "label": "Depot prep", "load": round(depot_prep)},
        {"time": "08:00", "label": "First jobs", "load": round(first_jobs)},
        {"time": "12:00", "label": "Parts restock", "load": round(restock)},
        {"time": "16:00", "label": "Emergency cover", "load": round(emergency_cover)},
    ]


def build_plan(payload: dict[str, Any]) -> dict[str, Any]:
    scenario = parse_scenario(payload)
    metrics = calculate_metrics(scenario)
    queue = calculate_queue(scenario)
    regions = calculate_regions(queue)
    timeline = calculate_timeline(scenario)
    selected = next(region for region in regions if region["name"] == "London and South East")

    return {
        "metrics": metrics,
        "queue": queue,
        "regions": regions,
        "timeline": timeline,
        "selectedRegion": selected,
        "assumptions": [
            "Indicative operational model for UK utility field logistics.",
            "Demand, weather, depot capacity, shift cover, and parts constraints drive risk.",
            "Python calculations are served by Flask and rendered by React.",
        ],
    }
