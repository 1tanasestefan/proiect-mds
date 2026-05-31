from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

from agent_experience import _fallback_experience
from agent_logistics import _fallback_logistics, _inject_booking_links
from app.services.planning import generate_trip_plan
from models import AgentOneOutput, FinalTripPlan, TripLogistics, UserInput


GENERIC_LOCATIONS = {
    "",
    "activity",
    "city center",
    "city centre",
    "downtown",
    "old town",
    "destination",
    "local area",
}


SCENARIOS: list[dict[str, Any]] = [
    {
        "name": "lisbon_culinary_midrange",
        "description": "Mid-range culinary city break with realistic budget and walkable activity anchors.",
        "input": {
            "budget": "medium",
            "lifestyle": "relaxed",
            "vacationType": "culinary",
            "origin": "Bucharest, Romania",
            "destination": "Lisbon, Portugal",
            "travelers": 2,
            "start_date": "2026-06-01",
            "end_date": "2026-06-04",
            "price_range_per_person": "$700-$1400",
        },
    },
    {
        "name": "barcelona_nightlife_budget",
        "description": "Budget nightlife itinerary that should avoid luxury-heavy logistics.",
        "input": {
            "budget": "low",
            "lifestyle": "nightlife",
            "vacationType": "city",
            "origin": "Pitesti, Romania",
            "destination": "Barcelona, Spain",
            "travelers": 3,
            "start_date": "2026-09-10",
            "end_date": "2026-09-13",
            "price_range_per_person": "$450-$900",
        },
    },
    {
        "name": "rome_culture_luxury",
        "description": "Luxury culture trip that should produce premium stays and richer assumptions.",
        "input": {
            "budget": "luxury",
            "lifestyle": "culture",
            "vacationType": "sightseeing",
            "origin": "Bucharest, Romania",
            "destination": "Rome, Italy",
            "travelers": 2,
            "start_date": "2026-10-05",
            "end_date": "2026-10-09",
            "price_range_per_person": "$1800-$3500",
        },
    },
]


@dataclass(frozen=True)
class EvalMetric:
    name: str
    score: float
    weight: float
    details: str

    @property
    def weighted_score(self) -> float:
        return round(self.score * self.weight, 4)


@dataclass(frozen=True)
class ScenarioReport:
    name: str
    description: str
    mode: str
    score: float
    passed: bool
    metrics: list[EvalMetric]


@dataclass(frozen=True)
class EvalReport:
    mode: str
    threshold: float
    score: float
    passed: bool
    scenarios: list[ScenarioReport]


def _metric(name: str, score: float, weight: float, details: str) -> EvalMetric:
    return EvalMetric(name=name, score=round(max(0.0, min(score, 1.0)), 4), weight=weight, details=details)


def _safe_ratio(value: float, target: float) -> float:
    if target <= 0:
        return 1.0
    return max(0.0, min(value / target, 1.0))


def _activities(experience: AgentOneOutput):
    for day in experience.itinerary:
        for activity in day.activities:
            yield day, activity


def _evaluate_experience(user_input: UserInput, experience: AgentOneOutput) -> list[EvalMetric]:
    day_count = len(experience.itinerary)
    expected_days = user_input.trip_days
    day_delta = abs(day_count - expected_days)
    day_score = 1.0 if day_delta == 0 else max(0.0, 1.0 - (day_delta / max(expected_days, 1)))

    activity_rows = list(_activities(experience))
    per_day_scores = [_safe_ratio(len(day.activities), 2) for day in experience.itinerary]
    activities_score = sum(per_day_scores) / max(len(per_day_scores), 1)

    titles = [activity.title.strip().lower() for _, activity in activity_rows if activity.title.strip()]
    unique_score = len(set(titles)) / max(len(titles), 1)

    specific_locations = 0
    for _, activity in activity_rows:
        location = (activity.location or "").strip().lower()
        if location not in GENERIC_LOCATIONS and len(location) >= 4:
            specific_locations += 1
    location_score = specific_locations / max(len(activity_rows), 1)

    complete_rows = 0
    for _, activity in activity_rows:
        if activity.time and activity.cost and activity.description:
            complete_rows += 1
    completeness_score = complete_rows / max(len(activity_rows), 1)

    destination_city = (user_input.destination or "").split(",")[0].strip().lower()
    relevance_text = " ".join(
        [experience.trip_title, experience.vibe_summary]
        + [f"{activity.title} {activity.description} {activity.location}" for _, activity in activity_rows]
    ).lower()
    destination_score = 1.0 if destination_city and destination_city in relevance_text else 0.7

    return [
        _metric("experience.days_match_request", day_score, 1.2, f"expected {expected_days}, got {day_count}"),
        _metric("experience.activities_per_day", activities_score, 1.0, "minimum target is 2 activities per day"),
        _metric("experience.unique_activity_titles", unique_score, 0.8, f"{len(set(titles))}/{len(titles)} titles are unique"),
        _metric("experience.specific_locations", location_score, 1.0, f"{specific_locations}/{len(activity_rows)} activities have specific locations"),
        _metric("experience.activity_fields_complete", completeness_score, 0.8, f"{complete_rows}/{len(activity_rows)} activities include time, cost, description"),
        _metric("experience.destination_relevance", destination_score, 0.7, f"destination city: {destination_city or 'missing'}"),
    ]


def _valid_http_links(values: Iterable[str]) -> float:
    links = [value for value in values if value]
    if not links:
        return 0.0
    valid = [value for value in links if value.startswith("http://") or value.startswith("https://")]
    return len(valid) / len(links)


def _evaluate_logistics(user_input: UserInput, logistics: TripLogistics) -> list[EvalMetric]:
    flight_count_score = 1.0 if 2 <= len(logistics.flights) <= 3 else _safe_ratio(len(logistics.flights), 2)
    stay_count_score = 1.0 if 2 <= len(logistics.accommodations) <= 3 else _safe_ratio(len(logistics.accommodations), 2)

    positive_flights = sum(1 for flight in logistics.flights if flight.estimated_price_usd > 0)
    positive_stays = sum(1 for stay in logistics.accommodations if stay.estimated_price_per_night_usd > 0 and stay.neighborhood)
    flight_quality = positive_flights / max(len(logistics.flights), 1)
    stay_quality = positive_stays / max(len(logistics.accommodations), 1)

    booking_score = _valid_http_links(
        [flight.booking_link for flight in logistics.flights]
        + [stay.booking_link for stay in logistics.accommodations]
    )

    if logistics.budget_breakdown:
        subtotal = logistics.budget_breakdown.subtotal_per_person_usd
        total = logistics.total_estimated_budget_usd
        subtotal_delta = abs(total - subtotal) / max(subtotal, 1)
        group_expected = subtotal * max(user_input.travelers or 1, 1)
        group_delta = abs(logistics.budget_breakdown.total_group_usd - group_expected) / max(group_expected, 1)
        budget_score = 1.0 if subtotal_delta <= 0.05 and group_delta <= 0.05 else 0.5
        budget_details = f"per-person delta {subtotal_delta:.1%}, group delta {group_delta:.1%}"
    else:
        budget_score = 0.0
        budget_details = "missing budget_breakdown"

    assumption_score = _safe_ratio(len(logistics.assumptions), 3)

    if logistics.transit_options:
        option_scores = []
        for option in logistics.transit_options.values():
            has_leg = len(option.legs) > 0
            has_center = option.map_center.lat != 0 or option.map_center.lng != 0
            option_scores.append(1.0 if has_leg and has_center else 0.5 if has_leg else 0.0)
        route_score = sum(option_scores) / max(len(option_scores), 1)
        route_details = f"{len(logistics.transit_options)} route option(s), confidence={logistics.confidence}"
    else:
        route_score = 0.65
        route_details = "no route data; acceptable for offline fallback, weaker than route-informed output"

    return [
        _metric("logistics.flight_option_count", flight_count_score, 0.8, f"{len(logistics.flights)} flight option(s)"),
        _metric("logistics.accommodation_option_count", stay_count_score, 0.8, f"{len(logistics.accommodations)} stay option(s)"),
        _metric("logistics.positive_flight_prices", flight_quality, 0.8, f"{positive_flights}/{len(logistics.flights)} flight prices are positive"),
        _metric("logistics.positive_stay_prices", stay_quality, 0.8, f"{positive_stays}/{len(logistics.accommodations)} stays have price and neighborhood"),
        _metric("logistics.booking_links", booking_score, 0.9, "flight and stay links must be concrete URLs"),
        _metric("logistics.budget_breakdown_consistency", budget_score, 1.1, budget_details),
        _metric("logistics.assumptions_present", assumption_score, 0.5, f"{len(logistics.assumptions)} assumption(s)"),
        _metric("logistics.routing_signal", route_score, 0.6, route_details),
    ]


async def _run_scenario(scenario: dict[str, Any], mode: str, threshold: float) -> ScenarioReport:
    user_input = UserInput(**scenario["input"])
    if mode == "live":
        plan = await generate_trip_plan(user_input, user_id=None)
    else:
        experience = _fallback_experience(user_input)
        logistics = _inject_booking_links(
            _fallback_logistics(user_input, transit_options=None, experience_result=experience),
            user_input,
        )
        plan = FinalTripPlan(
            experience=experience,
            logistics=logistics,
            origin=user_input.origin,
            destination=user_input.destination,
            start_date=user_input.start_date,
            end_date=user_input.end_date,
            travelers=user_input.travelers,
            budget=user_input.budget,
            price_range_per_person=user_input.price_range_per_person,
        )

    metrics = _evaluate_experience(user_input, plan.experience) + _evaluate_logistics(user_input, plan.logistics)
    weighted_total = sum(metric.weighted_score for metric in metrics)
    total_weight = sum(metric.weight for metric in metrics)
    score = round(weighted_total / total_weight, 4)
    return ScenarioReport(
        name=scenario["name"],
        description=scenario["description"],
        mode=mode,
        score=score,
        passed=score >= threshold,
        metrics=metrics,
    )


async def run_eval(mode: str = "offline", threshold: float = 0.75) -> EvalReport:
    reports = [await _run_scenario(scenario, mode, threshold) for scenario in SCENARIOS]
    score = round(sum(report.score for report in reports) / max(len(reports), 1), 4)
    return EvalReport(
        mode=mode,
        threshold=threshold,
        score=score,
        passed=score >= threshold and all(report.passed for report in reports),
        scenarios=reports,
    )


def report_to_dict(report: EvalReport) -> dict[str, Any]:
    return asdict(report)


def report_to_markdown(report: EvalReport) -> str:
    status = "PASS" if report.passed else "FAIL"
    lines = [
        f"# VibeTrips Agent Evaluation",
        "",
        f"- Mode: `{report.mode}`",
        f"- Score: `{report.score:.2%}`",
        f"- Threshold: `{report.threshold:.2%}`",
        f"- Status: `{status}`",
        "",
    ]
    for scenario in report.scenarios:
        scenario_status = "PASS" if scenario.passed else "FAIL"
        lines.extend([
            f"## {scenario.name} - {scenario_status}",
            "",
            scenario.description,
            "",
            f"Score: `{scenario.score:.2%}`",
            "",
            "| Metric | Score | Weight | Details |",
            "| --- | ---: | ---: | --- |",
        ])
        for metric in scenario.metrics:
            details = metric.details.replace("|", "/")
            lines.append(f"| `{metric.name}` | {metric.score:.2%} | {metric.weight:.1f} | {details} |")
        lines.append("")
    return "\n".join(lines)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate VibeTrips experience and logistics agents.")
    parser.add_argument(
        "--mode",
        choices=["offline", "live"],
        default="offline",
        help="offline uses deterministic agent fallbacks; live calls the full planning orchestrator.",
    )
    parser.add_argument("--threshold", type=float, default=0.75, help="Minimum passing score between 0 and 1.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown.")
    parser.add_argument("--output", type=Path, help="Optional file path for the report.")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    report = asyncio.run(run_eval(mode=args.mode, threshold=args.threshold))
    rendered = json.dumps(report_to_dict(report), indent=2) if args.json else report_to_markdown(report)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)

    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
