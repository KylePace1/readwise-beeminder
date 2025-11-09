# Changelog

## [1.1.0] - 2025-11-09

### Fixed
- **Duplicate tracking issue**: Script now uses Beeminder's last datapoint timestamp when local state file is unavailable
- This fixes the issue where GitHub Actions would re-post the same items on every run
- State management now works correctly in both local and CI environments

### How it Works
1. First checks for local state file (`~/.readwise_beeminder_state.json`)
2. If not found, queries Beeminder API for the timestamp of the last datapoint
3. Uses that timestamp to only fetch items archived since then
4. Prevents duplicate posts in GitHub Actions

### Technical Details
- Added `get_last_beeminder_datapoint()` function
- Modified `load_last_run_time()` to fall back to Beeminder API
- No changes needed to workflow or secrets

## [1.0.0] - 2025-11-09

### Initial Release
- Track archived Readwise Reader items tagged with "learning"
- Post count to Beeminder automatically
- State management to avoid double-counting
- Dry-run mode for testing
- Tag filtering support
- GitHub Actions workflow for daily automation
- Comprehensive documentation
