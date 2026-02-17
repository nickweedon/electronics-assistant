#!/workspace/.claude/skills/partsbox-api/scripts/.venv/bin/python
"""
Update PartsBox storage location tags and descriptions.

This script adds structured metadata to storage locations to enable intelligent
component placement recommendations. It can update existing locations and create
new ones based on a JSON configuration file.

Usage:
    python update_storage_tags.py --mode dry-run
    python update_storage_tags.py --mode update-existing --batch-size 20
    python update_storage_tags.py --mode create-new --batch-size 20
    python update_storage_tags.py --mode full --batch-size 20
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add the partsbox-api scripts directory to Python path
scripts_dir = Path(__file__).parent.parent / ".claude" / "skills" / "partsbox-api" / "scripts"
sys.path.insert(0, str(scripts_dir))

from api_client import api_request


class StorageMetadataUpdater:
    def __init__(self, config_path: str, batch_size: int = 20):
        """Initialize the updater with configuration."""
        self.config_path = config_path
        self.batch_size = batch_size
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict:
        """Load storage metadata from JSON configuration."""
        with open(self.config_path, 'r') as f:
            return json.load(f)

    def _match_storage_type(self, storage_name: str) -> Optional[Tuple[str, Dict]]:
        """
        Match a storage location name to its storage type configuration.

        Returns (prefix, config) or None if no match.
        """
        for prefix, config in self.metadata['storage_types'].items():
            if storage_name.startswith(prefix):
                return (prefix, config)
        return None

    def fetch_existing_locations(self) -> List[Dict]:
        """Fetch all existing storage locations from PartsBox."""
        print("Fetching existing storage locations from PartsBox...", file=sys.stderr)

        response = api_request("storage/all", {"limit": 1000})

        if response.get("meta", {}).get("cursor"):
            print("WARNING: More than 1000 storage locations exist. May need pagination.",
                  file=sys.stderr)

        locations = response.get("data", [])
        print(f"Found {len(locations)} storage locations", file=sys.stderr)

        return locations

    def generate_update_plan(self, locations: List[Dict]) -> Dict:
        """
        Generate update plan for existing locations.

        Returns dict with:
        - matched: List of (location, storage_type, config) tuples
        - unmatched: List of location dicts that didn't match any type
        """
        matched = []
        unmatched = []

        for location in locations:
            name = location.get("storage/name", "")
            storage_id = location.get("storage/id")

            match = self._match_storage_type(name)
            if match:
                prefix, config = match
                matched.append({
                    "id": storage_id,
                    "name": name,
                    "prefix": prefix,
                    "config": config,
                    "current_tags": location.get("storage/tags", []),
                    "current_comments": location.get("storage/comments", "")
                })
            else:
                unmatched.append(location)

        return {
            "matched": matched,
            "unmatched": unmatched
        }

    def generate_create_plan(self) -> List[Dict]:
        """
        Generate plan for creating new locations.

        Returns list of location specs to create.
        """
        create_list = []

        for prefix, config in self.metadata['storage_types'].items():
            if not config.get("exists", True):  # Only process non-existing types
                if "grid" in config:
                    # Generate grid-based locations
                    rows = config["grid"]["rows"]
                    cols = config["grid"]["cols"]

                    for row in rows:
                        for col in cols:
                            name = f"{prefix}-{row}{col}"
                            create_list.append({
                                "name": name,
                                "prefix": prefix,
                                "config": config
                            })

        return create_list

    def dry_run(self) -> Dict:
        """
        Generate complete preview of all changes without executing.

        Returns JSON-serializable dict with update and create plans.
        """
        locations = self.fetch_existing_locations()
        update_plan = self.generate_update_plan(locations)
        create_plan = self.generate_create_plan()

        # Format for JSON output
        updates = []
        for item in update_plan["matched"]:
            updates.append({
                "action": "UPDATE",
                "id": item["id"],
                "name": item["name"],
                "storage_type": item["prefix"],
                "changes": {
                    "tags": {
                        "old": item["current_tags"],
                        "new": item["config"]["tags"]
                    },
                    "description": {
                        "old": item["current_comments"],
                        "new": item["config"]["description"]
                    }
                }
            })

        creates = []
        for item in create_plan:
            creates.append({
                "action": "CREATE",
                "name": item["name"],
                "storage_type": item["prefix"],
                "tags": item["config"]["tags"],
                "description": item["config"]["description"]
            })

        summary = {
            "summary": {
                "total_updates": len(updates),
                "total_creates": len(creates),
                "unmatched_locations": len(update_plan["unmatched"])
            },
            "updates": updates,
            "creates": creates,
            "unmatched_locations": [
                {"id": loc.get("@id"), "name": loc.get("storage/name")}
                for loc in update_plan["unmatched"]
            ]
        }

        return summary

    def update_location(self, storage_id: str, tags: List[str], description: str) -> bool:
        """
        Update a single storage location.

        Returns True on success, False on failure.
        """
        try:
            payload = {
                "storage/id": storage_id,
                "storage/tags": tags,
                "storage/description": description
            }

            response = api_request("storage/update", payload)
            return True
        except Exception as e:
            print(f"ERROR updating {storage_id}: {e}", file=sys.stderr)
            return False

    def create_location(self, name: str, tags: List[str], description: str) -> bool:
        """
        Create a new storage location.

        Returns True on success, False on failure.
        """
        try:
            payload = {
                "storage/name": name,
                "storage/tags": tags,
                "storage/description": description
            }

            response = api_request("storage/create", payload)
            return True
        except Exception as e:
            print(f"ERROR creating {name}: {e}", file=sys.stderr)
            return False

    def execute_updates(self, interactive: bool = True) -> Dict:
        """
        Execute updates on existing locations in batches.

        Returns summary of results.
        """
        locations = self.fetch_existing_locations()
        update_plan = self.generate_update_plan(locations)
        matched = update_plan["matched"]

        total = len(matched)
        batches = [matched[i:i + self.batch_size] for i in range(0, total, self.batch_size)]

        results = {"success": 0, "failed": 0, "skipped": 0}

        for batch_num, batch in enumerate(batches, 1):
            print(f"\n{'='*60}", file=sys.stderr)
            print(f"Batch {batch_num}/{len(batches)}: {len(batch)} locations", file=sys.stderr)
            print(f"Progress: {results['success']}/{total} updated", file=sys.stderr)
            print(f"{'='*60}", file=sys.stderr)

            # Show preview of batch
            names = [item["name"] for item in batch[:5]]
            if len(batch) > 5:
                names.append(f"... and {len(batch) - 5} more")
            print(f"Locations: {', '.join(names)}", file=sys.stderr)

            if interactive:
                response = input("\nContinue with this batch? [y/N]: ")
                if response.lower() != 'y':
                    print("Skipping batch", file=sys.stderr)
                    results["skipped"] += len(batch)
                    continue

            # Execute batch
            for item in batch:
                success = self.update_location(
                    item["id"],
                    item["config"]["tags"],
                    item["config"]["description"]
                )

                if success:
                    results["success"] += 1
                    print(f"✓ {item['name']}", file=sys.stderr)
                else:
                    results["failed"] += 1
                    print(f"✗ {item['name']}", file=sys.stderr)

        return results

    def execute_creates(self, interactive: bool = True) -> Dict:
        """
        Execute creation of new locations in batches.

        Returns summary of results.
        """
        create_plan = self.generate_create_plan()

        total = len(create_plan)
        batches = [create_plan[i:i + self.batch_size] for i in range(0, total, self.batch_size)]

        results = {"success": 0, "failed": 0, "skipped": 0}

        for batch_num, batch in enumerate(batches, 1):
            print(f"\n{'='*60}", file=sys.stderr)
            print(f"Batch {batch_num}/{len(batches)}: {len(batch)} new locations", file=sys.stderr)
            print(f"Progress: {results['success']}/{total} created", file=sys.stderr)
            print(f"{'='*60}", file=sys.stderr)

            # Show preview of batch
            names = [item["name"] for item in batch[:5]]
            if len(batch) > 5:
                names.append(f"... and {len(batch) - 5} more")
            print(f"Locations: {', '.join(names)}", file=sys.stderr)

            if interactive:
                response = input("\nContinue with this batch? [y/N]: ")
                if response.lower() != 'y':
                    print("Skipping batch", file=sys.stderr)
                    results["skipped"] += len(batch)
                    continue

            # Execute batch
            for item in batch:
                success = self.create_location(
                    item["name"],
                    item["config"]["tags"],
                    item["config"]["description"]
                )

                if success:
                    results["success"] += 1
                    print(f"✓ {item['name']}", file=sys.stderr)
                else:
                    results["failed"] += 1
                    print(f"✗ {item['name']}", file=sys.stderr)

        return results


def main():
    parser = argparse.ArgumentParser(
        description="Update PartsBox storage location metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview all changes
  %(prog)s --mode dry-run | jq . > preview.json

  # Update existing locations only
  %(prog)s --mode update-existing --batch-size 20

  # Create new locations only
  %(prog)s --mode create-new --batch-size 20

  # Do both updates and creates
  %(prog)s --mode full --batch-size 20

  # Non-interactive mode (no confirmation prompts)
  %(prog)s --mode full --batch-size 20 --no-interactive
        """
    )

    parser.add_argument(
        "--mode",
        choices=["dry-run", "update-existing", "create-new", "full"],
        default="dry-run",
        help="Execution mode (default: dry-run)"
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=20,
        help="Number of locations to process per batch (default: 20)"
    )

    parser.add_argument(
        "--config",
        default="/workspace/scripts/storage_metadata.json",
        help="Path to storage metadata JSON config (default: /workspace/scripts/storage_metadata.json)"
    )

    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Skip confirmation prompts (use with caution)"
    )

    args = parser.parse_args()

    # Verify config file exists
    if not os.path.exists(args.config):
        print(f"ERROR: Config file not found: {args.config}", file=sys.stderr)
        sys.exit(1)

    # Initialize updater
    updater = StorageMetadataUpdater(args.config, args.batch_size)

    try:
        if args.mode == "dry-run":
            # Dry run: output JSON to stdout
            preview = updater.dry_run()
            print(json.dumps(preview, indent=2))

        elif args.mode == "update-existing":
            # Update existing locations only
            print("=" * 60, file=sys.stderr)
            print("MODE: Update existing locations", file=sys.stderr)
            print("=" * 60, file=sys.stderr)

            results = updater.execute_updates(interactive=not args.no_interactive)

            print("\n" + "=" * 60, file=sys.stderr)
            print("RESULTS", file=sys.stderr)
            print("=" * 60, file=sys.stderr)
            print(f"Success: {results['success']}", file=sys.stderr)
            print(f"Failed:  {results['failed']}", file=sys.stderr)
            print(f"Skipped: {results['skipped']}", file=sys.stderr)

        elif args.mode == "create-new":
            # Create new locations only
            print("=" * 60, file=sys.stderr)
            print("MODE: Create new locations", file=sys.stderr)
            print("=" * 60, file=sys.stderr)

            results = updater.execute_creates(interactive=not args.no_interactive)

            print("\n" + "=" * 60, file=sys.stderr)
            print("RESULTS", file=sys.stderr)
            print("=" * 60, file=sys.stderr)
            print(f"Success: {results['success']}", file=sys.stderr)
            print(f"Failed:  {results['failed']}", file=sys.stderr)
            print(f"Skipped: {results['skipped']}", file=sys.stderr)

        elif args.mode == "full":
            # Do both updates and creates
            print("=" * 60, file=sys.stderr)
            print("MODE: Full execution (update + create)", file=sys.stderr)
            print("=" * 60, file=sys.stderr)

            print("\nPhase 1: Updating existing locations...", file=sys.stderr)
            update_results = updater.execute_updates(interactive=not args.no_interactive)

            print("\nPhase 2: Creating new locations...", file=sys.stderr)
            create_results = updater.execute_creates(interactive=not args.no_interactive)

            print("\n" + "=" * 60, file=sys.stderr)
            print("FINAL RESULTS", file=sys.stderr)
            print("=" * 60, file=sys.stderr)
            print(f"Updates - Success: {update_results['success']}, "
                  f"Failed: {update_results['failed']}, "
                  f"Skipped: {update_results['skipped']}", file=sys.stderr)
            print(f"Creates - Success: {create_results['success']}, "
                  f"Failed: {create_results['failed']}, "
                  f"Skipped: {create_results['skipped']}", file=sys.stderr)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
