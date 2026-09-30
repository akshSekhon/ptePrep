"""Criterion: Multiple saved task tests can be deleted — the learner selects two or
more saved task tests and deletes them in one call; they no longer appear."""

import httpx


def test_multi_delete_removes_two_task_tests(client: httpx.Client):
    ids = []
    for _ in range(2):
        create_payload = {
            "skill": "Speaking",
            "task_type": "Read Aloud",
            "level": "Hard",
            "create_new": True,
            "question_count": 10,
            "voice": "australian",
        }
        resp = client.post("/pte/module-tests", json=create_payload)
        assert resp.status_code == 200, resp.text
        ids.append(resp.json()["id"])

    # Both fixture tests are individually fetchable before deletion.
    for test_id in ids:
        get_resp = client.get(f"/pte/module-tests/{test_id}")
        assert get_resp.status_code == 200, get_resp.text

    # Delete both selected tests in a single call, as the "Delete selected (N)" UI does.
    del_resp = client.post("/pte/module-tests/delete", json={"ids": ids})
    assert del_resp.status_code == 200, del_resp.text
    body = del_resp.json()
    assert body["deleted_count"] == 2, body

    # Neither remains fetchable afterwards.
    for test_id in ids:
        get_resp = client.get(f"/pte/module-tests/{test_id}")
        assert get_resp.status_code == 404, get_resp.text
