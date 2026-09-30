import json
import os
import re
from typing import Any

from emergentintegrations.llm.chat import LlmChat, StreamDone, TextDelta, UserMessage


def _clean_json(text: str) -> dict[str, Any] | list[Any]:
    candidate = text.strip()
    candidate = re.sub(r"^```(?:json)?\s*|\s*```$", "", candidate, flags=re.IGNORECASE)
    return json.loads(candidate)


async def _ask(prompt: str, system_message: str, provider: str = "openai", model: str = "gpt-5.4", tools: list[dict[str, Any]] | None = None) -> str:
    key = os.environ.get("EMERGENT_LLM_KEY")
    if not key:
        raise RuntimeError("EMERGENT_LLM_KEY is not configured")
    chat = LlmChat(api_key=key, session_id="pte-prep-session", system_message=system_message).with_model(provider, model)
    if tools:
        chat = chat.with_tools(tools)
    chunks: list[str] = []
    async for event in chat.stream_message(UserMessage(text=prompt)):
        if isinstance(event, TextDelta):
            chunks.append(event.content)
        elif isinstance(event, StreamDone) and event.content:
            if not chunks:
                chunks.append(event.content)
    return "".join(chunks)


async def review_answer(task: dict[str, Any], answer: str, difficulty: str, audio_duration_seconds: int | None = None) -> dict[str, Any]:
    visual = task.get("visual")
    describe_image_rubric = ""
    if task.get("task_type") == "Describe Image":
        describe_image_rubric = f""" Apply this Describe Image practice rubric: Content checks whether the response accurately covers the chart title, all meaningful trends, comparisons, and a logical conclusion; Pronunciation estimates intelligibility from the transcript quality only; Oral fluency estimates pace and phrasing from transcript length and recorded duration. This is an automated practice estimate, not an official Pearson score or human confirmation. Visual data: {visual}. Score exactly these traits in this order: Content, Pronunciation, Oral fluency."""
    prompt = f"""Review this PTE practice response. Return JSON only with keys score (integer 10-90), traits (array of exactly 3 objects with label, score, color), and feedback (array of exactly 3 concise strings). This is an estimated practice score, never an official Pearson score. Use the documented PTE traits where relevant. Task: {task['title']} / {task['skill']} / {difficulty}. Prompt: {task['prompt']}. Response: {answer}. Audio duration seconds: {audio_duration_seconds or 'not recorded'}.{describe_image_rubric}"""
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


async def generate_grounded_topic(skill: str, difficulty: str, source_context: str = "") -> dict[str, str]:
    prompt = f"""Use current, broadly reported educational, technology, science, business, or environment topics to suggest one copyright-safe source theme for an original {skill} PTE practice test at {difficulty} level. {source_context} Return JSON only with keys topic and context. Keep context factual, short, and suitable for new original questions; do not copy source wording or PTE exam content."""
    raw = await _ask(
        prompt,
        "You produce copyright-safe, current-topic ideas for English exam practice. Return valid JSON only.",
        provider="gemini",
        model="gemini-3-flash-preview",
        tools=[{"googleSearch": {}}],
    )
    result = _clean_json(raw)
    if not isinstance(result, dict) or not result.get("topic") or not result.get("context"):
        raise ValueError("Grounded topic generation returned invalid content")
    return {"topic": str(result["topic"])[:120], "context": str(result["context"])[:700]}