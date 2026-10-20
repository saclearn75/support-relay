"""Small JSON-line bridge from Band's TypeScript agents to local Cognee memory."""

from __future__ import annotations

import argparse
import asyncio
import json
import re

import cognee


# The first live run used the requester display name rather than the ticket's
# customer ID. Normalize that input so any future retry writes to the canonical
# customer dataset. Ticket 001 was migrated into that dataset separately.
LEGACY_CUSTOMER_IDS = {"sac learn", "sac-learn", "sac_learn"}


def canonical_customer_id(customer_id: str) -> str:
    normalized = customer_id.strip().lower()
    return "acme-labs" if normalized in LEGACY_CUSTOMER_IDS else normalized


def dataset_for(customer_id: str) -> str:
    safe_id = re.sub(r"[^a-z0-9_-]+", "_", canonical_customer_id(customer_id)).strip("_")
    if not safe_id:
        raise ValueError("customer_id must contain letters or numbers")
    return f"support_relay_{safe_id}"


async def remember(customer_id: str, fact: str) -> None:
    await cognee.remember(data=fact, dataset_name=dataset_for(customer_id))
    print(json.dumps({"ok": True, "dataset": dataset_for(customer_id)}))


async def recall(customer_id: str, question: str) -> None:
    results = await cognee.recall(question, datasets=[dataset_for(customer_id)])
    print(json.dumps({"ok": True, "results": [str(result) for result in results]}))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=("remember", "recall"))
    parser.add_argument("--customer-id", required=True)
    parser.add_argument("--text", required=True)
    args = parser.parse_args()
    if args.operation == "remember":
        asyncio.run(remember(args.customer_id, args.text))
    else:
        asyncio.run(recall(args.customer_id, args.text))


if __name__ == "__main__":
    main()
