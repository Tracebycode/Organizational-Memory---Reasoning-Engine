"""
Decision Extractor Agent.

Uses Ollama (phi3) to parse raw conversation text and extract
structured decision information: decision, reason, alternatives,
impacts, and source.
"""

import json
import logging
import re
from typing import Optional

import httpx

from schema import DecisionPayload

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Ollama configuration
# ---------------------------------------------------------------------------
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "phi3:mini"

# ---------------------------------------------------------------------------
# System prompt — instructs the LLM to behave as a decision extraction agent
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a Decision Extraction Agent.

Your job is to analyze raw conversation text and extract structured decision information.

You MUST respond with ONLY a valid JSON object — no markdown, no explanation, no extra text.

The JSON must have exactly these keys:
{
  "decision": "<concise statement of the decision made>",
  "reason": "<the rationale or justification given>",
  "alternatives": ["<option 1>", "<option 2>", ...],
  "impacts": ["<impact area 1>", "<impact area 2>", ...],
  "source": "conversation"
}

Rules:
- "decision" should be a short, clear statement (e.g. "Use Redis").
- "reason" should capture WHY the decision was made.
- "alternatives" should list options that were considered but NOT chosen.
- "impacts" should list areas affected by this decision (e.g. "database load", "API latency").
- "source" should always be "conversation" for conversational input.
- If information is not explicitly stated, infer it reasonably from context.
- Do NOT wrap the JSON in markdown code fences.
"""


class DecisionExtractor:
    """Extracts structured decision data from raw conversation text via Ollama."""

    def __init__(
        self,
        base_url: str = OLLAMA_BASE_URL,
        model: str = OLLAMA_MODEL,
        timeout: float = 60.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    async def extract(self, conversation_text: str) -> DecisionPayload:
        """
        Send the conversation text to Ollama and parse the structured response.

        Args:
            conversation_text: Raw conversation string.

        Returns:
            DecisionPayload with extracted fields.

        Raises:
            ExtractionError: If the LLM call or JSON parsing fails.
        """
        raw_response = await self._call_ollama(conversation_text)
        return self._parse_response(raw_response)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _call_ollama(self, conversation_text: str) -> str:
        """Call the Ollama /api/generate endpoint."""
        payload = {
            "model": self.model,
            "prompt": f"Extract the decision from this conversation:\n\n{conversation_text}",
            "system": SYSTEM_PROMPT,
            "stream": False,
            "options": {
                "temperature": 0.1,  # near-deterministic for structured output
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")

        except httpx.ConnectError:
            raise ExtractionError(
                "Cannot connect to Ollama. Ensure it is running on "
                f"{self.base_url} and the '{self.model}' model is pulled."
            )
        except httpx.HTTPStatusError as exc:
            raise ExtractionError(
                f"Ollama returned HTTP {exc.response.status_code}: "
                f"{exc.response.text}"
            )
        except Exception as exc:
            raise ExtractionError(f"Ollama request failed: {exc}")

    def _parse_response(self, raw: str) -> DecisionPayload:
        """
        Parse the raw LLM output into a DecisionPayload.

        Handles common LLM quirks: markdown fences, trailing commas, etc.
        """
        cleaned = self._strip_markdown_fences(raw).strip()

        if not cleaned:
            raise ExtractionError("LLM returned an empty response")

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            # Attempt to extract a JSON object from noisy output
            parsed = self._extract_json_from_text(cleaned)

        if parsed is None:
            raise ExtractionError(
                f"Could not parse LLM output as JSON.\nRaw output:\n{raw}"
            )

        # Normalise fields ------------------------------------------------
        return DecisionPayload(
            decision=parsed.get("decision", "Unknown decision"),
            reason=parsed.get("reason", "No reason provided"),
            alternatives=self._ensure_list(parsed.get("alternatives", [])),
            impacts=self._ensure_list(parsed.get("impacts", [])) or ["general"],
            source=parsed.get("source", "conversation"),
        )

    # ------------------------------------------------------------------
    # Text cleanup utilities
    # ------------------------------------------------------------------

    @staticmethod
    def _strip_markdown_fences(text: str) -> str:
        """Remove ```json ... ``` wrappers if present."""
        text = re.sub(r"^```(?:json)?\s*\n?", "", text, flags=re.MULTILINE)
        text = re.sub(r"\n?```\s*$", "", text, flags=re.MULTILINE)
        return text

    @staticmethod
    def _extract_json_from_text(text: str) -> Optional[dict]:
        """Try to find and parse the first JSON object in arbitrary text."""
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                return None
        return None

    @staticmethod
    def _ensure_list(value) -> list:
        """Coerce a value into a list of strings."""
        if isinstance(value, list):
            return [str(v) for v in value]
        if isinstance(value, str):
            return [value]
        return []


# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------

class ExtractionError(Exception):
    """Raised when decision extraction fails."""
    pass
