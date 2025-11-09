# GitHub Actions Setup for Readwise Tracker

## Your Tokens (for GitHub Secrets)

When you push this to GitHub, add these as repository secrets:

### Steps:
1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these two secrets:

**Secret 1: READWISE_TOKEN**
```
kaQFKN8iLoDbOWKhklocHpxmfJBpWtRjyxSOiNQLkKOp1ulq2m
```

**Secret 2: BEEMINDER_TOKEN**
```
9BErv46PRvNEbXPCMZDT
```

## Verify Setup

After adding secrets:
1. Go to **Actions** tab
2. Click **Track Readwise Reader** workflow
3. Click **Run workflow** → **Run workflow**
4. Watch it run!

## What Happens Next

- The workflow runs automatically every day at midnight PST
- You can manually trigger it anytime from the Actions tab
- It will post your daily archived items count to Beeminder goal: `learning`

## Test Locally First

Before setting up GitHub Actions, verify it works locally:

```bash
# Test with dry-run
./readwise_beeminder.py --dry-run

# Test with verbose output
./readwise_beeminder.py --dry-run --verbose

# When ready, run for real
./readwise_beeminder.py
```

## Troubleshooting

**If no items are found:**
- Make sure you have items in your Readwise Reader archive
- Try `--hours 720` to check the last 30 days
- Archive a test article and run again

**GitHub Actions fails:**
- Check that both secrets are added correctly
- Verify the secret names match exactly: `READWISE_TOKEN` and `BEEMINDER_TOKEN`
- Check the Actions logs for specific errors
