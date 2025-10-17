# LinkedIn Posts Storage Guide

Complete guide for managing persistent storage of LinkedIn posts in AI Happenings.

## 📦 Storage Overview

AI Happenings automatically saves all generated LinkedIn posts to disk in **three formats**:

1. **JSON** - Structured data with metadata
2. **Individual Text Files** - One file per post
3. **Combined Text File** - All posts in a single file

## 📁 Directory Structure

```
outputs/
├── json/                           # JSON files with complete data
│   ├── linkedin_posts_2025-10-17_14-30-45.json
│   └── linkedin_posts_2025-10-17_16-45-12.json
├── text/                           # Individual post text files
│   ├── batch_2025-10-17_14-30-45/
│   │   ├── 01_revolutionary_ai_marketplace.txt
│   │   ├── 02_agentic_commerce_takes_center.txt
│   │   └── ...
│   └── batch_2025-10-17_16-45-12/
│       └── ...
└── combined/                       # All posts combined
    ├── all_posts_2025-10-17_14-30-45.txt
    └── all_posts_2025-10-17_16-45-12.txt
```

## 🚀 Automatic Storage

### Posts are saved automatically when running:

**1. Standard Pipeline:**
```bash
cd src
python main.py
```

**2. Pipeline with Balance Tracking:**
```bash
cd src
python main_with_balance.py
```

**3. n8n Webhook:**
```bash
# POST to http://localhost:5000/run-pipeline
```

### Storage Output Example:
```
💾 Saving LinkedIn posts to storage...
   ✓ Saved to JSON: outputs/json/linkedin_posts_2025-10-17_14-30-45.json
   ✓ Saved to combined text: outputs/combined/all_posts_2025-10-17_14-30-45.txt
   ✓ Saved 10 individual text files
```

## 📄 File Formats

### JSON Format

**File:** `outputs/json/linkedin_posts_YYYY-MM-DD_HH-MM-SS.json`

```json
{
  "generated_at": "2025-10-17_14-30-45",
  "metadata": {
    "duration_seconds": 54.2,
    "articles_scraped": 15,
    "articles_analyzed": 15,
    "customer_id": "ai-happenings",
    "total_cost": 177.5,
    "remaining_balance": 822.5
  },
  "total_posts": 10,
  "posts": [
    {
      "rank": 1,
      "title": "Revolutionary AI Marketplace Launches",
      "source": "TechCrunch",
      "link": "https://techcrunch.com/...",
      "priority_score": 95.5,
      "relevance_score": 9.5,
      "linkedin_post": "🚀 Exciting developments in AI marketplace technology...",
      "scraped_at": "2025-10-17T14:30:12"
    },
    {
      "rank": 2,
      "title": "Agentic Commerce Takes Center Stage",
      "source": "VentureBeat",
      "link": "https://venturebeat.com/...",
      "priority_score": 92.3,
      "relevance_score": 9.2,
      "linkedin_post": "💡 The future of commerce is autonomous..."
    }
  ]
}
```

### Individual Text Files

**Directory:** `outputs/text/batch_YYYY-MM-DD_HH-MM-SS/`
**Files:** `01_article_title.txt`, `02_article_title.txt`, etc.

```
POST #1

Title: Revolutionary AI Marketplace Launches
Source: TechCrunch
Link: https://techcrunch.com/...
Priority Score: 95.5/100
Relevance Score: 9.5/10

LINKEDIN POST:
----------------------------------------
🚀 Exciting developments in AI marketplace technology...
[Full LinkedIn post content]
----------------------------------------
```

### Combined Text File

**File:** `outputs/combined/all_posts_YYYY-MM-DD_HH-MM-SS.txt`

```
================================================================================
AI HAPPENINGS - LINKEDIN POSTS
Generated: 2025-10-17_14-30-45
Total Posts: 10

Metadata:
  duration_seconds: 54.2
  articles_scraped: 15
  articles_analyzed: 15
================================================================================

POST #1

Title: Revolutionary AI Marketplace Launches
...

--------------------------------------------------------------------------------

POST #2

Title: Agentic Commerce Takes Center Stage
...

--------------------------------------------------------------------------------
```

## 🔍 Retrieving Saved Posts

### Via n8n Webhook API

#### Get Latest Posts (JSON)
```bash
curl http://localhost:5000/get-saved-posts?format=json
```

Response:
```json
{
  "success": true,
  "data": {
    "generated_at": "2025-10-17_14-30-45",
    "total_posts": 10,
    "posts": [...]
  }
}
```

#### Download Latest Combined Text File
```bash
curl http://localhost:5000/get-saved-posts?format=combined -O
```

#### List All Saved Runs
```bash
curl http://localhost:5000/list-saved-runs
```

Response:
```json
{
  "success": true,
  "runs": {
    "json_files": ["outputs/json/linkedin_posts_..."],
    "text_batches": ["outputs/text/batch_..."],
    "combined_files": ["outputs/combined/all_posts_..."],
    "total_runs": 5
  },
  "stats": {
    "total_runs": 5,
    "json_files_count": 5,
    "text_batches_count": 5,
    "combined_files_count": 5,
    "total_size_bytes": 524288,
    "total_size_mb": 0.5
  }
}
```

### Via Python Code

```python
from utils.post_storage import PostStorage

# Initialize storage
storage = PostStorage()

# Get latest posts as JSON
latest_json = storage.get_latest_posts('json')
posts_data = storage.load_posts_from_json(latest_json)

print(f"Total posts: {posts_data['total_posts']}")
for post in posts_data['posts']:
    print(f"- {post['title']}")

# Get storage statistics
stats = storage.get_storage_stats()
print(f"Total runs: {stats['total_runs']}")
print(f"Storage size: {stats['total_size_mb']} MB")

# List all saved runs
runs = storage.list_saved_runs()
print(f"JSON files: {len(runs['json_files'])}")
```

## 🧹 Storage Management

### Cleanup Old Files

Keep only the most recent runs and delete older ones:

```python
from utils.post_storage import PostStorage

storage = PostStorage()

# Keep last 10 runs, delete older ones
storage.cleanup_old_files(keep_last=10)
```

### Get Storage Statistics

```python
stats = storage.get_storage_stats()

print(f"Total runs: {stats['total_runs']}")
print(f"JSON files: {stats['json_files_count']}")
print(f"Text batches: {stats['text_batches_count']}")
print(f"Combined files: {stats['combined_files_count']}")
print(f"Total storage: {stats['total_size_mb']} MB")
```

### Manual Cleanup

Simply delete files or directories:

```bash
# Delete specific batch
rm -rf outputs/text/batch_2025-10-17_14-30-45

# Delete all JSON files
rm outputs/json/*.json

# Clear everything
rm -rf outputs/json/* outputs/text/* outputs/combined/*
```

## 🔗 n8n Integration Examples

### Example 1: Run Pipeline and Store Posts

```
┌─────────────────┐
│ Schedule Trigger│  Daily at 9 AM
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  HTTP Request   │  POST http://localhost:5000/run-pipeline
│                 │  Returns: { "storage": {...} }
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Set Variable    │  Extract storage.json_file path
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Email           │  Notify: "Posts saved to {json_file}"
└─────────────────┘
```

### Example 2: Retrieve and Post to LinkedIn

```
┌─────────────────┐
│ Schedule Trigger│  Daily at 10 AM
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  HTTP Request   │  GET http://localhost:5000/get-saved-posts?format=json
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Split In Batches│  {{$json.data.posts}}
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ LinkedIn Node   │  Post {{$json.linkedin_post}}
└─────────────────┘
```

### Example 3: Monitor Storage

```
┌─────────────────┐
│ Schedule Trigger│  Weekly
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  HTTP Request   │  GET http://localhost:5000/list-saved-runs
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ IF Node         │  {{$json.stats.total_size_mb}} > 100
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Slack Notify    │  "Storage cleanup needed: {total_size_mb} MB"
└─────────────────┘
```

## ⚙️ Configuration

### Custom Output Directory

```python
# In config
config = {
    "agentbill_api_key": "...",
    "openai_api_key": "...",
    "output_dir": "/custom/path/outputs"  # Custom directory
}

app = AIHappenings(config)
```

### Storage Module Options

```python
from utils.post_storage import PostStorage

# Custom output directory
storage = PostStorage(output_dir="/custom/path")

# Default: "outputs" in current directory
storage = PostStorage()
```

## 📊 Use Cases

### Use Case 1: Archive All Posts
Keep permanent records of all generated posts for compliance or analytics.

### Use Case 2: Post Scheduling
Generate posts in advance, save them, then schedule posting throughout the day/week.

### Use Case 3: A/B Testing
Save multiple versions, test engagement, refine prompts based on results.

### Use Case 4: Content Calendar
Build a content library over time, review and curate the best posts.

### Use Case 5: Team Collaboration
Share the outputs directory with team members for review before posting.

## 🔐 Security Considerations

### What's Stored:
- ✅ Article titles and links (public information)
- ✅ Generated LinkedIn posts
- ✅ Metadata (timestamps, scores)
- ✅ Performance metrics

### What's NOT Stored:
- ❌ API keys (never saved to disk)
- ❌ User credentials
- ❌ Sensitive configuration

### Backup Recommendations:
1. Exclude `outputs/` from public repositories (already in .gitignore)
2. Include in private backups for disaster recovery
3. Consider encryption for sensitive deployments
4. Regular cleanup to minimize data retention

## 💡 Best Practices

1. **Regular Cleanup** - Set up automated cleanup to keep only recent runs
2. **Backup Important Posts** - Move critical posts to separate archive
3. **Monitor Storage Size** - Set up alerts when storage exceeds threshold
4. **Use Descriptive Customer IDs** - Helps identify runs in metadata
5. **Review Before Posting** - Always review generated posts from storage before publishing

## 🐛 Troubleshooting

### Posts Not Saving

**Problem:** No files created in outputs/

**Solutions:**
- Check write permissions on outputs/ directory
- Verify pipeline completed successfully
- Check logs for errors
- Ensure PostStorage initialized correctly

### Cannot Find Latest Posts

**Problem:** `get_latest_posts()` returns None

**Solutions:**
- Check if any files exist in outputs/
- Verify correct format parameter ('json', 'text', 'combined')
- Check file permissions

### Storage Growing Too Large

**Problem:** outputs/ directory using too much disk space

**Solutions:**
```python
# Automatic cleanup
storage.cleanup_old_files(keep_last=5)

# Or manual deletion
rm -rf outputs/json/* outputs/text/* outputs/combined/*
```

## 📞 Support

See the main documentation for additional help:
- **README.md** - General documentation
- **QUICK_REFERENCE.md** - Command reference
- **N8N_INTEGRATION_GUIDE.md** - n8n examples

---

**💾 Every post is automatically saved - never lose your generated content!**
