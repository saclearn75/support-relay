"""Authenticate a configured Band remote agent without invoking Codex."""

from __future__ import annotations

import argparse
import asyncio
import logging
from pathlib import Path

from dotenv import load_dotenv
from band import Agent, configure_logging
from band.config import load_agent_config
from band.core import AgentToolsProtocol, SimpleAdapter
from band.core.types import PlatformMessage


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class NoopAdapter(SimpleAdapter[list]):
    """Minimum adapter required to verify a Band connection."""

    async def on_message(
        self,
        msg: PlatformMessage,
        tools: AgentToolsProtocol,
        history: list,
        participants_msg: str | None,
        contacts_msg: str | None,
        *,
        is_session_bootstrap: bool,
        room_id: str,
    ) -> None:
        return None


async def verify(role: str) -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    configure_logging(root_level="INFO")
    agent_id, api_key = load_agent_config(
        role, config_path=PROJECT_ROOT / "agent_config.yaml"
    )
    agent = Agent.create(adapter=NoopAdapter(), agent_id=agent_id, api_key=api_key)
    await agent.start()
    logging.getLogger(__name__).info("Authenticated Band agent: %s", agent.agent_name)
    await agent.stop()


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify one Band agent identity.")
    parser.add_argument("role", choices=("support_lead", "technical_specialist"))
    args = parser.parse_args()
    asyncio.run(verify(args.role))


if __name__ == "__main__":
    main()

