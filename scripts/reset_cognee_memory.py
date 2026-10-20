"""Delete only the local Cognee datasets created by Support Relay.

Run with ``--dry-run`` to see the datasets that would be removed, then pass
``--yes`` to reset them without an interactive prompt.
"""

from __future__ import annotations

import argparse
import asyncio

import cognee

from cognee_memory import dataset_for


SUPPORT_RELAY_DATASET_PREFIX = "support_relay_"


async def find_datasets(customer_ids: list[str] | None):
    datasets = await cognee.datasets.list_datasets()
    if customer_ids:
        requested_names = {dataset_for(customer_id) for customer_id in customer_ids}
        return [dataset for dataset in datasets if dataset.name in requested_names]
    return [
        dataset
        for dataset in datasets
        if dataset.name.startswith(SUPPORT_RELAY_DATASET_PREFIX)
    ]


async def reset(customer_ids: list[str] | None, dry_run: bool) -> int:
    datasets = await find_datasets(customer_ids)
    if not datasets:
        print("No matching Support Relay Cognee datasets found.")
        return 0

    print("Support Relay Cognee datasets selected for removal:")
    for dataset in datasets:
        print(f"- {dataset.name} ({dataset.id})")

    if dry_run:
        print("Dry run only; no memory was removed.")
        return 0

    for dataset in datasets:
        await cognee.datasets.empty_dataset(dataset.id)
        print(f"Removed {dataset.name}.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reset local Cognee memory created by Support Relay."
    )
    parser.add_argument(
        "--customer-id",
        action="append",
        help="Reset only this customer. Repeat the option for multiple customers.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List matching datasets without deleting them.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirm deletion without an interactive prompt.",
    )
    args = parser.parse_args()

    if not args.dry_run and not args.yes:
        confirmation = input(
            "This permanently removes Support Relay's selected local Cognee memory. "
            "Type RESET to continue: "
        )
        if confirmation != "RESET":
            print("Reset cancelled.")
            return

    raise SystemExit(asyncio.run(reset(args.customer_id, args.dry_run)))


if __name__ == "__main__":
    main()
