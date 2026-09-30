"""Criterion: Listening audio uses natural cached HD audio — a listening test has
an audio playback URL that returns audio/mpeg, and transcript reveal remains optional
(the module test question payload carries the script but audio_url is independent)."""

import httpx


def test_listening_module_test_audio_returns_mpeg(client: httpx.Client):
    create_payload = {
        "skill": "Listening",
        "level": "Easy",
        "create_new": True,
        "question_count": 10,
        "voice": "australian",
    }
    resp = client.post("/pte/module-tests", json=create_payload)
    assert resp.status_code == 200, resp.text
    test = resp.json()
    test_id = test["id"]

    listening_question = next(
        (q for q in test["questions"] if q.get("listening_script")), None
    )
    assert listening_question is not None, "expected at least one listening question with a script"

    # Transcript reveal is optional client-side: the API only needs to expose the script
    # text on the question payload (already true above) and a working audio URL.
    audio_url = listening_question.get("audio_url")
    assert audio_url, "listening question missing audio_url"

    audio_resp = httpx.get(f"http://localhost:8001{audio_url}", timeout=30.0)
    assert audio_resp.status_code == 200, audio_resp.text
    assert audio_resp.headers.get("content-type", "").startswith("audio/mpeg"), audio_resp.headers

    # Second call should be served from cache and still be audio/mpeg.
    audio_resp2 = httpx.get(f"http://localhost:8001{audio_url}", timeout=30.0)
    assert audio_resp2.status_code == 200
    assert audio_resp2.headers.get("content-type", "").startswith("audio/mpeg")
