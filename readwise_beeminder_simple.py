#!/usr/bin/env python3
"""
Readwise Reader to Beeminder Sync Script (Simple Daily Version)
Posts once per day - counts items archived TODAY with the specified tag
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
import requests

# Configuration
READWISE_TOKEN = os.environ.get("READWISE_TOKEN")
BEEMINDER_USERNAME = "kyle"
BEEMINDER_GOAL = "learning"
BEEMINDER_AUTH_TOKEN = os.environ.get("BEEMINDER_TOKEN")
DEFAULT_TAG = "learning"

READWISE_API_BASE = "https://readwise.io/api/v3"
BEEMINDER_API_BASE = "https://www.beeminder.com/api/v1"


def already_posted_today():
    """Check if we've already posted to Beeminder today (in Beeminder's timezone)"""
    if not BEEMINDER_AUTH_TOKEN:
        return False

    try:
        # Get goal info to find timezone
        goal_url = f"{BEEMINDER_API_BASE}/users/{BEEMINDER_USERNAME}/goals/{BEEMINDER_GOAL}.json"
        goal_params = {'auth_token': BEEMINDER_AUTH_TOKEN}
        goal_response = requests.get(goal_url, params=goal_params)

        # Get timezone offset from goal (defaults to UTC if not found)
        goal_data = goal_response.json() if goal_response.status_code == 200 else {}
        # Beeminder uses 'timezone' field like 'America/Los_Angeles'
        # For simplicity, we'll just check the last few datapoints instead

        url = f"{BEEMINDER_API_BASE}/users/{BEEMINDER_USERNAME}/goals/{BEEMINDER_GOAL}/datapoints.json"
        params = {'auth_token': BEEMINDER_AUTH_TOKEN, 'count': 5, 'sort': 'id'}
        response = requests.get(url, params=params)

        if response.status_code == 200:
            datapoints = response.json()

            # Check the most recent datapoints for our signature
            # Don't rely on daystamp matching since timezones differ
            for dp in datapoints:
                comment = dp.get('comment', '')
                timestamp = dp.get('timestamp', 0)

                # Check if this was posted in the last 20 hours AND has our signature
                # This handles timezone differences (24h - 4h buffer = 20h)
                hours_ago = (datetime.now().timestamp() - timestamp) / 3600

                if hours_ago < 20 and 'Total archived items with tag' in comment:
                    print(f"Found recent post ({hours_ago:.1f}h ago): {comment}")
                    return True
        return False
    except Exception as e:
        print(f"Warning checking duplicates: {e}")
        return False


def get_total_archived_items(filter_tag=None):
    """Get TOTAL count of all archived items with the tag (not just today)"""
    if not READWISE_TOKEN:
        print("Error: READWISE_TOKEN not set")
        sys.exit(1)

    headers = {'Authorization': f'Token {READWISE_TOKEN}'}
    params = {'location': 'archive'}

    try:
        print(f"Fetching all archived items...")
        all_items = []
        next_cursor = None

        while True:
            if next_cursor:
                params['pageCursor'] = next_cursor

            response = requests.get(f"{READWISE_API_BASE}/list/", headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            all_items.extend(data.get('results', []))
            next_cursor = data.get('nextPageCursor')
            if not next_cursor:
                break

            print(f"Fetched {len(all_items)} items so far...")

        print(f"✓ Found {len(all_items)} total archived items")

        # Filter by tag
        if filter_tag:
            filtered = []
            for item in all_items:
                tags = item.get('tags', [])
                tag_names = [tag.get('name', tag) if isinstance(tag, dict) else tag for tag in tags]
                if filter_tag in tag_names:
                    filtered.append(item)
            print(f"✓ Filtered to {len(filtered)} items with tag '{filter_tag}'")
            return filtered

        return all_items

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def post_to_beeminder(value, dry_run=False):
    """Post total count to Beeminder"""
    if not BEEMINDER_AUTH_TOKEN:
        print("Error: BEEMINDER_TOKEN not set")
        sys.exit(1)

    url = f"{BEEMINDER_API_BASE}/users/{BEEMINDER_USERNAME}/goals/{BEEMINDER_GOAL}/datapoints.json"
    comment = f"Total archived items with tag '{DEFAULT_TAG}'"

    if dry_run:
        print(f"[DRY RUN] Would post total: {value}")
        print(f"[DRY RUN] Comment: {comment}")
        return True

    try:
        data = {
            'auth_token': BEEMINDER_AUTH_TOKEN,
            'value': value,
            'comment': comment
        }
        response = requests.post(url, data=data)

        if response.status_code == 200:
            print(f"✓ Posted total count: {value}")
            return True
        else:
            print(f"✗ Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Readwise total count to Beeminder')
    parser.add_argument('--dry-run', action='store_true', help='Test mode')
    parser.add_argument('--tag', type=str, help=f'Tag to filter (default: {DEFAULT_TAG})')
    parser.add_argument('--force', action='store_true', help='Post even if already posted today')
    args = parser.parse_args()

    tag = args.tag or DEFAULT_TAG

    print("=== Readwise Reader to Beeminder (Total Count) ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if args.dry_run:
        print("MODE: DRY RUN")
    print(f"FILTER: Tag '{tag}'")
    print()

    # Check if already posted
    if not args.force and not args.dry_run and already_posted_today():
        print("✓ Already posted today - skipping")
        print("(Use --force to post anyway)")
        return

    # Get ALL archived items with tag
    items = get_total_archived_items(filter_tag=tag)
    total_count = len(items)

    print(f"\nTotal archived items with tag '{tag}': {total_count}")

    if total_count > 0:
        print(f"\nMost recent items:")
        for item in items[:5]:
            print(f"  - {item.get('title', 'Untitled')[:60]}...")
        if total_count > 5:
            print(f"  ... and {total_count - 5} more")

    # Post total count to Beeminder
    print()
    post_to_beeminder(total_count, dry_run=args.dry_run)

    print("\n=== Sync Complete ===")


if __name__ == "__main__":
    main()
