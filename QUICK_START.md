# Quick Start Guide

## 1. Clone or Navigate to Repository

```bash
cd ~/readwise-beeminder
```

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## 3. Set Up Environment Variables

```bash
# Copy template
cp .env.template .env

# Edit with your tokens
nano .env
```

Add your tokens:
```bash
export READWISE_TOKEN='your_token_here'
export BEEMINDER_TOKEN='your_token_here'
```

Then load them:
```bash
source .env
```

## 4. Configure Script

Edit `readwise_beeminder.py` lines 18-23:
- `BEEMINDER_USERNAME`: Your Beeminder username
- `BEEMINDER_GOAL`: Your goal slug
- `DEFAULT_TAG`: Tag to track (default: "learning")

## 5. Test It

```bash
# Dry run - doesn't post to Beeminder
./readwise_beeminder.py --dry-run --hours 720 --verbose
```

## 6. Run for Real

```bash
./readwise_beeminder.py
```

## 7. Set Up Automation (Optional)

### GitHub Actions (Recommended)
See [GITHUB_SETUP.md](GITHUB_SETUP.md)

### Cron Job
```bash
crontab -e
# Add: 0 23 * * * cd ~/readwise-beeminder && source ~/.zprofile && python3 readwise_beeminder.py
```

## Usage Examples

```bash
# Test without posting
./readwise_beeminder.py --dry-run

# Check specific time range
./readwise_beeminder.py --dry-run --hours 48

# Track different tag
./readwise_beeminder.py --tag videos

# Show detailed output
./readwise_beeminder.py --verbose

# Reset state
./readwise_beeminder.py --reset
```

## Workflow

1. Read something in Readwise Reader
2. Tag it with "learning" (or your configured tag)
3. Archive it when done
4. Run script (or wait for automation)
5. Check Beeminder!

---

For full documentation, see [DOCUMENTATION.md](DOCUMENTATION.md)
