# Readwise Reader to Beeminder Sync

A Python script that automatically tracks your archived articles and videos from Readwise Reader to Beeminder, helping you maintain accountability for your learning goals.

## Features

- Fetches archived items from Readwise Reader API
- Posts count to Beeminder automatically
- Tracks state to avoid double-counting
- Supports dry-run mode for testing
- Handles pagination for large archives
- Simple configuration via environment variables

## Prerequisites

- Python 3.6+
- A Readwise account with Reader access
- A Beeminder account with a goal set up

## Installation

1. Install required packages:
```bash
pip install requests
```

2. Get your API tokens:
   - **Readwise Token**: Visit https://readwise.io/access_token
   - **Beeminder Token**: Visit https://www.beeminder.com/api/v1/auth_token.json

3. Set environment variables:
```bash
export READWISE_TOKEN='your_readwise_token_here'
export BEEMINDER_TOKEN='your_beeminder_token_here'
```

   To make these permanent, add them to your `~/.zprofile` or `~/.bash_profile`:
```bash
echo 'export READWISE_TOKEN="your_token"' >> ~/.zprofile
echo 'export BEEMINDER_TOKEN="your_token"' >> ~/.zprofile
```

4. Edit the script configuration:
   - Open `readwise_beeminder.py`
   - Update `BEEMINDER_USERNAME` (line 17)
   - Update `BEEMINDER_GOAL` (line 18)

## Usage

### Command-Line Options

```bash
./readwise_beeminder.py [OPTIONS]

Options:
  --dry-run              Test without posting to Beeminder
  --tag TAG              Only count items with this tag
  --reset                Reset state and check last 24 hours
  --hours HOURS          Check last N hours (ignores saved state)
  --verbose, -v          Show detailed output with URLs and tags
  --help, -h             Show help message
```

### Common Usage Examples

**First Run (Test Mode)**
```bash
./readwise_beeminder.py --dry-run
```
Fetches items from last 24 hours and shows what would be posted without actually posting.

**Regular Run**
```bash
./readwise_beeminder.py
```
Fetches items since last run, posts to Beeminder, saves state.

**Track Only Videos**
```bash
./readwise_beeminder.py --tag videos
```
Only counts items tagged with "videos".

**Check Last Week**
```bash
./readwise_beeminder.py --hours 168 --dry-run
```
Shows what you archived in the last 7 days (168 hours).

**Reset and Start Fresh**
```bash
./readwise_beeminder.py --reset
```
Clears saved state and checks last 24 hours.

**Verbose Output**
```bash
./readwise_beeminder.py --verbose
```
Shows all items with URLs and tags.

## Automation

### Option 1: Daily Cron Job (macOS/Linux)

Run automatically every day at 11 PM:

```bash
crontab -e
```

Add this line:
```cron
0 23 * * * cd /Users/kylepace && /usr/bin/python3 readwise_beeminder.py >> /tmp/readwise_beeminder.log 2>&1
```

### Option 2: GitHub Actions (Recommended)

The included workflow file [.github/workflows/readwise-tracker.yml](.github/workflows/readwise-tracker.yml) runs automatically every day.

**Setup:**
1. Push your repository to GitHub
2. Add secrets in your repo settings (Settings → Secrets → Actions):
   - `READWISE_TOKEN`: Your Readwise API token
   - `BEEMINDER_TOKEN`: Your Beeminder API token
3. The workflow runs daily at midnight PST/PDT
4. You can also trigger it manually from the Actions tab

**To run manually on GitHub:**
- Go to Actions → Track Readwise Reader → Run workflow

### Option 3: Manual

Run it whenever you want to update your Beeminder goal.

## How It Works

1. **State Management**: The script saves a timestamp in `~/.readwise_beeminder_state.json` after each successful run
2. **Incremental Sync**: On subsequent runs, it only fetches items archived since the last run
3. **First Run**: If no state file exists, it defaults to checking the last 24 hours
4. **Pagination**: Automatically handles pagination to fetch all archived items
5. **Beeminder Update**: Posts the count as a single datapoint with a descriptive comment

## Configuration Options

You can modify these variables in the script:

- `BEEMINDER_USERNAME`: Your Beeminder username
- `BEEMINDER_GOAL`: The slug of your Beeminder goal (e.g., "learning-videos")
- `STATE_FILE`: Where to store the last run timestamp (default: `~/.readwise_beeminder_state.json`)

## Troubleshooting

### "Error: READWISE_TOKEN environment variable not set"
Make sure you've exported the token in your current shell session, or added it to your profile.

### "Error: BEEMINDER_TOKEN environment variable not set"
Same as above - check your environment variables.

### No items found
- Verify you have items in your Reader archive
- Check if the state file timestamp is too recent
- Try deleting `~/.readwise_beeminder_state.json` to reset

### API Errors
- Check that your tokens are valid
- Verify the Beeminder goal slug is correct
- Ensure your Readwise subscription includes API access

## Advanced Usage

### Track Different Categories to Different Goals

Create multiple copies of the script with different configurations:

**readwise_videos.py** - Track only videos
```bash
# Change BEEMINDER_GOAL to "videos"
./readwise_videos.py --tag videos
```

**readwise_articles.py** - Track only articles
```bash
# Change BEEMINDER_GOAL to "articles"
./readwise_articles.py --tag articles
```

### Filter by Multiple Tags

Edit the script to check for multiple tags:
```python
# In get_archived_items(), change the filter logic:
required_tags = ['learning', 'important']
if all(tag in tag_names for tag in required_tags):
    filtered_items.append(item)
```

### Track Reading Time Instead of Count

If Readwise API provides reading time, you can modify the script to sum it:
```python
# Replace count logic with:
total_minutes = sum(item.get('reading_time_minutes', 0) for item in items)
post_to_beeminder(total_minutes, comment="Reading time in minutes")
```

## API Documentation

- **Readwise Reader API**: https://readwise.io/reader_api
- **Beeminder API**: https://api.beeminder.com

## License

Free to use and modify for personal use.

## Related Scripts

- `bootdev_beeminder_simple.py` - Tracks Boot.dev XP to Beeminder
