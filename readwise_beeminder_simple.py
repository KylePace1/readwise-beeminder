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
    """Check if we've already posted to Beeminder today"""
    if not BEEMINDER_AUTH_TOKEN:
        return False

    try:
        url = f"{BEEMINDER_API_BASE}/users/{BEEMINDER_USERNAME}/goals/{BEEMINDER_GOAL}/datapoints.json"
        params = {'auth_token': BEEMINDER_AUTH_TOKEN, 'count': 10}
        response = requests.get(url, params=params)

        if response.status_code == 200:
            datapoints = response.json()
            today = datetime.now().strftime('%Y%m%d')

            for dp in datapoints:
                daystamp = dp.get('daystamp', '')
                comment = dp.get('comment', '')
                # Check if posted today AND contains our auto-track signature
                if daystamp == today and 'Auto-tracked from Readwise Reader' in comment and 'items today' in comment:
                    print(f"Found existing post for today: {comment}")
                    return True
        return False
    except Exception as e:
        print(f"Warning checking duplicates: {e}")
        return False


def get_items_archived_today(filter_tag=None):
    """Get count of items archived TODAY"""
    if not READWISE_TOKEN:
        print("Error: READWISE_TOKEN not set")
        sys.exit(1)

    headers = {'Authorization': f'Token {READWISE_TOKEN}'}
    params = {'location': 'archive'}

    # Calculate today's start time (midnight)
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    params['updatedAfter'] = today_start.isoformat()

    try:
        print(f"Fetching items archived today...")
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

        print(f"✓ Found {len(all_items)} archived items today")

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
    """Post to Beeminder"""
    if not BEEMINDER_AUTH_TOKEN:
        print("Error: BEEMINDER_TOKEN not set")
        sys.exit(1)

    url = f"{BEEMINDER_API_BASE}/users/{BEEMINDER_USERNAME}/goals/{BEEMINDER_GOAL}/datapoints.json"
    comment = f"Auto-tracked from Readwise Reader ({value} items today)"

    if dry_run:
        print(f"[DRY RUN] Would post: {value} items")
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
            print(f"✓ Posted {value} items to Beeminder")
            return True
        else:
            print(f"✗ Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Daily Readwise to Beeminder sync')
    parser.add_argument('--dry-run', action='store_true', help='Test mode')
    parser.add_argument('--tag', type=str, help=f'Tag to filter (default: {DEFAULT_TAG})')
    parser.add_argument('--force', action='store_true', help='Post even if already posted today')
    args = parser.parse_args()

    tag = args.tag or DEFAULT_TAG

    print("=== Readwise Reader to Beeminder (Daily Sync) ===")
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

    # Get items
    items = get_items_archived_today(filter_tag=tag)
    count = len(items)

    print(f"\nItems archived today: {count}")

    if count > 0:
        for item in items[:5]:
            print(f"  - {item.get('title', 'Untitled')[:60]}...")
        if count > 5:
            print(f"  ... and {count - 5} more")

    # Post to Beeminder
    if count >= 0:  # Post even if 0 to track the day
        print()
        post_to_beeminder(count, dry_run=args.dry_run)

    print("\n=== Sync Complete ===")


if __name__ == "__main__":
    main()
