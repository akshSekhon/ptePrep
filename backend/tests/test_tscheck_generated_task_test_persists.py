"""Criterion: Generating a Read Aloud test creates a 10-question saved test that
remains selectable after returning to its library (module-tests list)."""

import httpx


def test_generated_read_aloud_test_persists_in_library(client: httpx.Client):
    # Create a new 10-question Read Aloud task test.
    create_payload = {
        "skill": "Speaking",
        "task_type": "Read Aloud",
        "level": "Easy",
        "create_new": True,
        "question_count": 10,
        "voice": "australian",
    }
    resp = client.post("/pte/module-tests", json=create_payload)
    assert resp.status_code == 200, resp.text
    test = resp.json()
    assert len(test["questions"]) == 10
    assert test["skill"] == "Speaking"
    assert test["task_type"] == "Read Aloud"
    test_id = test["id"]

    # Simulate "returning to the library" — list module-tests filtered the same way
    # the frontend TaskTestLibrary does, and confirm the generated test is present.
    list_resp = client.get(
        "/pte/module-tests",
        params={"skill": "Speaking", "task_type": "Read Aloud", "level": "Easy"},
    )
    assert list_resp.status_code == 200, list_resp.text
    tests = list_resp.json()
    ids = [item["id"] for item in tests]
    assert test_id in ids, f"generated test {test_id} missing from library listing: {ids}"

    # Fetching it directly by id also works (selectable).
    get_resp = client.get(f"/pte/module-tests/{test_id}")
    assert get_resp.status_code == 200, get_resp.text
    assert get_resp.json()["id"] == test_id
