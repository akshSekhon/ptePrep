"""Criterion: Dashboard progress is data-driven — counts and skill scores reflect
stored attempts/test results instead of fixed placeholder values."""

import httpx


def test_dashboard_reflects_new_attempt(client: httpx.Client):
    before = client.get("/pte/dashboard")
    assert before.status_code == 200, before.text
    before_data = before.json()
    before_completed = before_data["completed_tasks"]

    # Pick a real task id to submit a fresh attempt against.
    tasks_resp = client.get("/pte/tasks", params={"level": "Easy"})
    assert tasks_resp.status_code == 200, tasks_resp.text
    tasks = tasks_resp.json()
    assert tasks, "no tasks available to attempt"
    task = tasks[0]

    attempt_payload = {
        "task_id": task["id"],
        "answer_text": "tscheck dashboard driven answer with enough words to be scored fairly and consistently.",
        "difficulty": "Easy",
        "source": "text",
    }
    attempt_resp = httpx.post(
        "http://localhost:8001/api/pte/attempts", json=attempt_payload, timeout=30.0
    )
    assert attempt_resp.status_code == 200, attempt_resp.text
    attempt = attempt_resp.json()
    assert attempt["task_id"] == task["id"]

    after = client.get("/pte/dashboard")
    assert after.status_code == 200, after.text
    after_data = after.json()

    # completed_tasks must have grown by exactly one attempt just created (data-driven,
    # not a fixed placeholder).
    assert after_data["completed_tasks"] == before_completed + 1, (
        before_data,
        after_data,
    )
    # The skill score for the attempted task's skill should reflect a real score.
    skill = task["skill"]
    assert after_data["skill_scores"][skill] > 0
