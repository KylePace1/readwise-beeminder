# ✅ Readwise "learning" Tag Tracker - Ready to Use!

## What This Does

Tracks archived items in Readwise Reader that have the **"learning"** tag and posts the count to your Beeminder goal.

## How to Use

### 1. Tag Items in Readwise Reader

When you read something in Readwise Reader, tag it with **"learning"** and archive it when done.

### 2. Run the Script

```bash
# Test it first (doesn't post to Beeminder)
./readwise_beeminder.py --dry-run

# When ready, run for real
./readwise_beeminder.py
```

That's it! The script automatically:
- Only counts items tagged "learning"
- Remembers last run (won't double-count)
- Posts to Beeminder goal: kyle/learning

## Configuration

Your script is set up with:
- **Tag**: "learning" (default)
- **Goal**: kyle/learning
- **Tokens**: Already configured in `~/.zprofile`

## Want to Track Different Tags?

Edit line 23 in [readwise_beeminder.py](readwise_beeminder.py):
```python
DEFAULT_TAG = "learning"  # Change to whatever tag you want
```

Or use the `--tag` flag:
```bash
./readwise_beeminder.py --tag videos  # Track "videos" instead
```

## Daily Automation

### GitHub Actions (Recommended)
1. Push to GitHub
2. Add secrets (see [setup_readwise_github.md](setup_readwise_github.md))
3. Runs automatically every day at midnight!

### Cron Job
```bash
crontab -e
# Add: 0 23 * * * cd /Users/kylepace && python3 readwise_beeminder.py
```

## Testing

```bash
# Check last 30 days
./readwise_beeminder.py --dry-run --hours 720

# Check last hour (after archiving something)
./readwise_beeminder.py --dry-run --hours 1 --verbose
```

## Quick Commands

```bash
./readwise_beeminder.py              # Run (tracks "learning" tag)
./readwise_beeminder.py --dry-run    # Test mode
./readwise_beeminder.py --verbose    # Show details
./readwise_beeminder.py --reset      # Start fresh
./readwise_beeminder.py --help       # Show all options
```

## Workflow

1. **Read** something in Readwise Reader
2. **Tag** it with "learning"
3. **Archive** when finished
4. **Run** the script (or wait for automation)
5. **Track** your progress on Beeminder!

---

**Next Step**: Archive an article in Readwise Reader with the "learning" tag, then run:
```bash
./readwise_beeminder.py --dry-run --hours 1
```
