"""Run one Support Relay role as a remote Band agent backed by Codex."""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from band import Agent, Emit, configure_logging
from band.adapters import CodexAdapter, CodexAdapterConfig
from band.config import load_agent_config


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROMPTS_DIR = PROJECT_ROOT / "prompts"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a Support Relay Band role.")
    parser.add_argument(
        "role",
        choices=("support_lead", "technical_specialist"),
        help="The matching top-level key in agent_config.yaml.",
    )
    return parser.parse_args()


async def run(role: str) -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    configure_logging(root_level="INFO")

    prompt_path = PROMPTS_DIR / f"{role}.md"
    agent_id, api_key = load_agent_config(
        role, config_path=PROJECT_ROOT / "agent_config.yaml"
    )
    adapter = CodexAdapter(
        config=CodexAdapterConfig(
            transport="stdio",
            cwd=str(PROJECT_ROOT),
            custom_section=prompt_path.read_text(encoding="utf-8"),
            approval_mode="manual",
        ),
        # Task events preserve the Codex thread mapping for each Band room.
        emit={Emit.TOOL_CALLS, Emit.TASK_EVENTS},
    )
    agent = Agent.create(
        adapter=adapter,
        agent_id=agent_id,
        api_key=api_key,
        rest_url=os.getenv("BAND_REST_URL", "https://app.band.ai"),
        ws_url=os.getenv("BAND_WS_URL", "wss://app.band.ai/api/v1/socket/websocket"),
    )

    logging.getLogger(__name__).info("Starting Band role: %s", role)
    await agent.run()


def main() -> None:
    args = parse_args()
    asyncio.run(run(args.role))


if __name__ == "__main__":
    main()

