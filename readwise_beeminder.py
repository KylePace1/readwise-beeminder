#!/usr/bin/env python3
"""
Readwise Reader to Beeminder Sync Script
Tracks archived articles/videos from Readwise Reader to Beeminder
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import requests

# Configuration
READWISE_TOKEN = os.environ.get("READWISE_TOKEN")
BEEMINDER_USERNAME = "kyle"  # Replace with your Beeminder username
BEEMINDER_GOAL = "learning"  # Replace with your goal name
BEEMINDER_AUTH_TOKEN = os.environ.get("BEEMINDER_TOKEN")

# Tag filtering - only track items with this tag
DEFAULT_TAG = "learning"  # Set to None to track all archived items

# State file to track last run
STATE_FILE = Path.home() / ".readwise_beeminder_state.json"

# API Endpoints
READWISE_API_BASE = "https://readwise.io/api/v3"
BEEMINDER_API_BASE = "https://www.beeminder.com/api/v1"


def get_last_beeminder_datapoint():
    """Get the timestamp of the last datapoint from Beeminder"""
    if not BEEMINDER_AUTH_TOKEN:
        return None

    try:
        url = f"{BEEMINDER_API_BASE}/users/{BEEMINDER_USERNAME}/goals/{BEEMINDER_GOAL}/datapoints.json"
        params = {
            'auth_token': BEEMINDER_AUTH_TOKEN,
            'count': 1,  # Just get the most recent one
            'sort': 'timestamp'
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            datapoints = response.json()
            if datapoints and len(datapoints) > 0:
                # Return timestamp of most recent datapoint
                return datapoints[-1].get('timestamp')
        return None
    except Exception as e:
        print(f"Warning: Could not fetch last Beeminder datapoint: {e}")
        return None


def load_last_run_time():
    """Load the last run timestamp from state file or Beeminder"""
    # Try state file first
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                timestamp = state.get('last_run_timestamp')
                if timestamp:
                    return timestamp
        except Exception as e:
            print(f"Warning: Could not load state file: {e}")

    # Fall back to checking last Beeminder datapoint
    last_datapoint = get_last_beeminder_datapoint()
    if last_datapoint:
        print(f"No local state found, using last Beeminder datapoint timestamp")
        return last_datapoint

    return None


def save_last_run_time(timestamp):
    """Save the current run timestamp to state file"""
    try:
        state = {'last_run_timestamp': timestamp}
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)
    except Exception as e:
        print(f"Warning: Could not save state file: {e}")


def get_archived_items(since_timestamp=None, filter_tag=None):
    """
    Fetch archived items from Readwise Reader

    Args:
        since_timestamp: Unix timestamp to fetch items updated since
        filter_tag: Optional tag to filter items by

    Returns:
        List of archived documents
    """
    if not READWISE_TOKEN:
        print("Error: READWISE_TOKEN environment variable not set")
        print("Get your token from: https://readwise.io/access_token")
        print("Set it with: export READWISE_TOKEN='your_token_here'")
        sys.exit(1)

    headers = {
        'Authorization': f'Token {READWISE_TOKEN}'
    }

    params = {
        'location': 'archive',  # Only get archived items
    }

    # Add timestamp filter if provided
    # Note: updatedAfter filters items that were moved to archive OR updated in that timeframe
    if since_timestamp:
        # Readwise API uses ISO format for updatedAfter
        since_date = datetime.fromtimestamp(since_timestamp).isoformat()
        params['updatedAfter'] = since_date

        # We'll need to filter on our end by checking when item actually moved to archive
        # This is tracked in the 'reading_progress' field

    url = f"{READWISE_API_BASE}/list/"

    try:
        print(f"Fetching archived items from Readwise Reader...")
        if since_timestamp:
            print(f"Looking for items archived since: {datetime.fromtimestamp(since_timestamp)}")

        all_items = []
        next_page_cursor = None

        while True:
            if next_page_cursor:
                params['pageCursor'] = next_page_cursor

            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()
            results = data.get('results', [])
            all_items.extend(results)

            # Check if there are more pages
            next_page_cursor = data.get('nextPageCursor')
            if not next_page_cursor:
                break

            print(f"Fetched {len(all_items)} items so far...")

        print(f"✓ Found {len(all_items)} archived items")

        # Filter by tag if specified
        if filter_tag:
            filtered_items = []
            for item in all_items:
                tags = item.get('tags', [])
                # Tags might be a list of tag objects or strings
                tag_names = [tag.get('name', tag) if isinstance(tag, dict) else tag for tag in tags]
                if filter_tag in tag_names:
                    filtered_items.append(item)

            print(f"✓ Filtered to {len(filtered_items)} items with tag '{filter_tag}'")
            return filtered_items

        return all_items

    except requests.exceptions.RequestException as e:
        print(f"Error fetching from Readwise: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        sys.exit(1)


def post_to_beeminder(value, comment=None, dry_run=False):
    """
    Post datapoint to Beeminder

    Args:
        value: Number to post
        comment: Optional comment for the datapoint
        dry_run: If True, don't actually post
    """
    if not BEEMINDER_AUTH_TOKEN:
        print("Error: BEEMINDER_TOKEN environment variable not set")
        print("Get your token from: https://www.beeminder.com/api/v1/auth_token.json")
        print("Set it with: export BEEMINDER_TOKEN='your_token_here'")
        sys.exit(1)

    url = f"{BEEMINDER_API_BASE}/users/{BEEMINDER_USERNAME}/goals/{BEEMINDER_GOAL}/datapoints.json"

    data = {
        'auth_token': BEEMINDER_AUTH_TOKEN,
        'value': value,
        'timestamp': int(time.time()),
    }

    if comment:
        data['comment'] = comment

    if dry_run:
        print(f"[DRY RUN] Would post to Beeminder: {value} items")
        if comment:
            print(f"[DRY RUN] Comment: {comment}")
        return True

    try:
        print(f"Posting to Beeminder: {value} items")
        response = requests.post(url, data=data)

        if response.status_code == 200:
            print(f"✓ Successfully posted {value} items to Beeminder goal '{BEEMINDER_GOAL}'")
            return True
        else:
            print(f"✗ Error posting to Beeminder: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Error posting to Beeminder: {e}")
        return False


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Sync archived Readwise Reader items to Beeminder',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  %(prog)s --dry-run              # Test without posting (uses default tag: {DEFAULT_TAG})
  %(prog)s --tag videos           # Track items tagged 'videos' instead
  %(prog)s --reset                # Reset state and check last 24 hours
  %(prog)s --hours 48             # Check last 48 hours (ignores saved state)
        """
    )

    parser.add_argument('--dry-run', action='store_true',
                        help='Test mode - do not post to Beeminder')
    parser.add_argument('--tag', type=str,
                        help=f'Only count items with this tag (default: {DEFAULT_TAG})')
    parser.add_argument('--reset', action='store_true',
                        help='Reset state file and check last 24 hours')
    parser.add_argument('--hours', type=int,
                        help='Check last N hours (overrides saved state)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show detailed output')

    return parser.parse_args()


def main():
    """Main execution function"""
    args = parse_arguments()

    # Use DEFAULT_TAG if no --tag specified
    tag_to_use = args.tag if args.tag else DEFAULT_TAG

    print("=== Readwise Reader to Beeminder Sync ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if args.dry_run:
        print("MODE: DRY RUN (no data will be posted)")
    if tag_to_use:
        print(f"FILTER: Only items tagged '{tag_to_use}'")
    print()

    # Handle reset
    if args.reset:
        if STATE_FILE.exists():
            STATE_FILE.unlink()
            print("✓ State file reset")

    # Load last run time
    last_run = load_last_run_time()

    # Override with --hours if specified
    if args.hours:
        last_run = int((datetime.now() - timedelta(hours=args.hours)).timestamp())
        print(f"Checking last {args.hours} hours")
    elif last_run:
        print(f"Last run: {datetime.fromtimestamp(last_run).strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("First run - will check last 24 hours")
        # Default to 24 hours ago for first run
        last_run = int((datetime.now() - timedelta(hours=24)).timestamp())

    # Fetch archived items
    items = get_archived_items(since_timestamp=last_run, filter_tag=tag_to_use)

    # Count items
    count = len(items)
    print(f"\nItems archived since last run: {count}")

    # Show sample of items if any were found
    if count > 0 and (args.verbose or count <= 5):
        print("\nArchived items:")
        display_count = count if args.verbose else min(5, count)
        for item in items[:display_count]:
            title = item.get('title', 'Untitled')
            url = item.get('source_url', 'No URL')
            print(f"  - {title[:60]}...")
            if args.verbose:
                print(f"    URL: {url}")
                tags = item.get('tags', [])
                if tags:
                    tag_names = [tag.get('name', tag) if isinstance(tag, dict) else tag for tag in tags]
                    print(f"    Tags: {', '.join(tag_names)}")

        if count > display_count:
            print(f"  ... and {count - display_count} more")
    elif count > 0:
        print(f"\n(Use --verbose to see all items)")

    # Post to Beeminder if we have items
    if count > 0:
        print()
        comment = f"Auto-tracked from Readwise Reader ({count} items)"
        if tag_to_use:
            comment += f" [tag: {tag_to_use}]"
        success = post_to_beeminder(count, comment=comment, dry_run=args.dry_run)

        if success and not args.dry_run:
            # Save current timestamp as last run
            save_last_run_time(int(time.time()))
            print(f"\n✓ State saved for next run")
    else:
        print("\nNo new items to track")

    print("\n=== Sync Complete ===")


if __name__ == "__main__":
    main()
