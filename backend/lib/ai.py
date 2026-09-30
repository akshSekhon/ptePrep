import json
import os
import re
from typing import Any

from emergentintegrations.llm.chat import LlmChat, StreamDone, TextDelta, UserMessage


def _clean_json(text: str) -> dict[str, Any] | list[Any]:
    candidate = text.strip()
    candidate = re.sub(r"^```(?:json)?\s*|\s*```$", "", candidate, flags=re.IGNORECASE)
    return json.loads(candidate)


async def _ask(prompt: str, system_message: str) -> str:
    key = os.environ.get("EMERGENT_LLM_KEY")
    if not key:
        raise RuntimeError("EMERGENT_LLM_KEY is not configured")
    chat = LlmChat(api_key=key, session_id="pte-prep-session", system_message=system_message).with_model("openai", "gpt-5.4")
    chunks: list[str] = []
    async for event in chat.stream_message(UserMessage(text=prompt)):
        if isinstance(event, TextDelta):
            chunks.append(event.content)
        elif isinstance(event, StreamDone) and event.content:
            if not chunks:
                chunks.append(event.content)
    return "".join(chunks)


async def review_answer(task: dict[str, Any], answer: str, difficulty: str, audio_duration_seconds: int | None = None) -> dict[str, Any]:
    prompt = f"""Review this PTE practice response. Return JSON only with keys score (integer 10-90), traits (array of exactly 3 objects with label, score, color), and feedback (array of exactly 3 concise strings). This is an estimated practice score, never an official Pearson score. Use the documented PTE traits where relevant. Task: {task['title']} / {task['skill']} / {difficulty}. Prompt: {task['prompt']}. Response: {answer}. Audio duration seconds: {audio_duration_seconds or 'not recorded'}."""
    system = "You are a careful PTE practice coach. Score consistently and give actionable, kind feedback. Never claim an official score. Use color hex values #0284c7, #0d9488, and #d97706 for the three traits."
    raw = await _ask(prompt, system)
    result = _clean_json(raw)
    if not isinstance(result, dict):
        raise ValueError("AI review was not an object")
    return result


async def generate_mock_prompts(tasks: list[dict[str, Any]], difficulty: str) -> list[dict[str, str]]:
    task_names = ", ".join(item["title"] for item in tasks)
    prompt = f"Create one original, copyright-safe PTE practice prompt for each of these 20 task types at {difficulty} difficulty: {task_names}. Return a JSON array in the same order with objects containing prompt and instructions only. Do not mention Pearson or copy official questions."
    raw = await _ask(prompt, "You create original English exam-preparation prompts. Return valid JSON only.")
    result = _clean_json(raw)
    if not isinstance(result, list) or len(result) != len(tasks):
        raise ValueError("AI mock generation returned the wrong number of prompts")
    return [{"prompt": str(item["prompt"]), "instructions": str(item["instructions"])} for item in result]