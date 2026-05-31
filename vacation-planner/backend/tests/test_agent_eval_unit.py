import asyncio

from agent_eval import report_to_dict, run_eval


def test_offline_agent_eval_passes_threshold():
    report = asyncio.run(run_eval(mode="offline", threshold=0.75))

    assert report.passed is True
    assert report.score >= 0.75
    assert len(report.scenarios) == 3
    assert all(scenario.metrics for scenario in report.scenarios)


def test_agent_eval_report_is_json_serializable():
    report = asyncio.run(run_eval(mode="offline", threshold=0.75))
    payload = report_to_dict(report)

    assert payload["mode"] == "offline"
    assert payload["passed"] is True
    assert payload["scenarios"][0]["metrics"][0]["name"].startswith("experience.")
