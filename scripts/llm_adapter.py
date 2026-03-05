"""Multi-provider LLM adapter for the ContinualKit agent pipeline.

Supported providers (set via AGENT_LLM_PROVIDER env var):
  openai       — OpenAI API (default model: gpt-4o-mini)
  groq         — Groq API, OpenAI-compatible (default model: llama-3.3-70b-versatile)
  anthropic    — Anthropic API (default model: claude-haiku-4-5-20251001)
  huggingface  — HuggingFace Inference API (default model: Qwen/Qwen2.5-72B-Instruct)
  ollama       — Local Ollama, OpenAI-compatible (default model: llama3.2)
               ⚠ Ollama requires a running local server — not available in GitHub Actions CI.
               Use it for local development and testing of the agent pipeline.

Configuration (via env vars or GitHub Actions secrets):
  AGENT_LLM_PROVIDER   — provider name (default: groq)
  AGENT_LLM_MODEL      — model name (default: provider default, see above)
  AGENT_LLM_KEY        — API key (not required for ollama)
  OLLAMA_BASE_URL      — Ollama server URL (default: http://localhost:11434/v1)

Usage:
  python scripts/llm_adapter.py --system "..." --user "..." > response.json
  python scripts/llm_adapter.py --system "..." --user "..." --temperature 0.2
"""

import argparse
import json
import os
import sys

# ── Provider defaults ──────────────────────────────────────────────────────────

PROVIDER_DEFAULTS = {
    "openai": {
        "model": "gpt-4o-mini",
        "base_url": None,  # uses SDK default
    },
    "groq": {
        "model": "llama-3.3-70b-versatile",
        "base_url": "https://api.groq.com/openai/v1",
    },
    "anthropic": {
        "model": "claude-haiku-4-5-20251001",
        "base_url": None,
    },
    "huggingface": {
        "model": "Qwen/Qwen2.5-72B-Instruct",
        "base_url": "https://api-inference.huggingface.co/v1",
    },
    "ollama": {
        "model": "llama3.2",
        "base_url": None,  # resolved at runtime from OLLAMA_BASE_URL
    },
}

# ── OpenAI-compatible providers (openai SDK with custom base_url) ──────────────

OPENAI_COMPATIBLE = {"openai", "groq", "huggingface", "ollama"}


def call_openai_compatible(
    provider: str,
    model: str,
    system: str,
    user: str,
    temperature: float,
) -> str:
    try:
        from openai import OpenAI
    except ImportError:
        print(
            "❌ openai package not installed. Run: pip install openai", file=sys.stderr
        )
        sys.exit(1)

    api_key = os.environ.get("AGENT_LLM_KEY", "ollama")  # ollama accepts any string
    defaults = PROVIDER_DEFAULTS[provider]

    if provider == "ollama":
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    else:
        base_url = defaults["base_url"]

    client = OpenAI(api_key=api_key, base_url=base_url)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
        temperature=temperature,
    )
    return response.choices[0].message.content


# ── Anthropic ─────────────────────────────────────────────────────────────────


def call_anthropic(model: str, system: str, user: str, temperature: float) -> str:
    try:
        import anthropic
    except ImportError:
        print(
            "❌ anthropic package not installed. Run: pip install anthropic",
            file=sys.stderr,
        )
        sys.exit(1)

    api_key = os.environ.get("AGENT_LLM_KEY")
    if not api_key:
        print("❌ AGENT_LLM_KEY is required for Anthropic provider.", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model=model,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": user}],
        temperature=temperature,
    )

    # Extract JSON from the response text
    text = message.content[0].text
    # Anthropic doesn't have a native json_object mode — extract from markdown if needed
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    return text


# ── Main ──────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-provider LLM adapter.")
    parser.add_argument("--system", required=True, help="System prompt")
    parser.add_argument("--user", required=True, help="User message")
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument(
        "--out", default="/tmp/llm_response.json", help="Output file path"
    )
    args = parser.parse_args()

    provider = os.environ.get("AGENT_LLM_PROVIDER", "groq").lower()
    if provider not in PROVIDER_DEFAULTS:
        print(
            f"❌ Unknown provider: {provider!r}. Choose from: {list(PROVIDER_DEFAULTS)}",
            file=sys.stderr,
        )
        sys.exit(1)

    model = os.environ.get("AGENT_LLM_MODEL") or PROVIDER_DEFAULTS[provider]["model"]

    print(f"Provider: {provider} | Model: {model}", file=sys.stderr)

    if provider == "ollama":
        print(
            "⚠ Ollama requires a running local server. "
            "Not available in GitHub Actions CI — use for local dev only.",
            file=sys.stderr,
        )

    if provider in OPENAI_COMPATIBLE:
        result = call_openai_compatible(
            provider, model, args.system, args.user, args.temperature
        )
    elif provider == "anthropic":
        result = call_anthropic(model, args.system, args.user, args.temperature)
    else:
        print(f"❌ Provider {provider!r} is not yet implemented.", file=sys.stderr)
        sys.exit(1)

    # Validate JSON
    try:
        parsed = json.loads(result)
    except json.JSONDecodeError as e:
        print(f"❌ LLM did not return valid JSON: {e}", file=sys.stderr)
        print(f"Raw response: {result[:500]}", file=sys.stderr)
        sys.exit(1)

    with open(args.out, "w") as f:
        json.dump(parsed, f, indent=2)

    print(f"✅ Response written to {args.out}", file=sys.stderr)
    print(result)  # stdout = the JSON


if __name__ == "__main__":
    main()
