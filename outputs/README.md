# LinkedIn Posts Storage

This directory stores all generated LinkedIn posts in multiple formats.

## Directory Structure

```
outputs/
├── json/           # JSON files with complete post data
├── text/           # Individual text files per post (organized by batch)
└── combined/       # Combined text files with all posts
```

## File Naming Conventions

### JSON Files
- Format: `linkedin_posts_YYYY-MM-DD_HH-MM-SS.json`
- Example: `linkedin_posts_2025-10-17_14-30-45.json`
- Contains: All posts with metadata, scores, and links

### Text Batches
- Format: `batch_YYYY-MM-DD_HH-MM-SS/`
- Example: `batch_2025-10-17_14-30-45/`
- Contains: Individual text files (01_article_title.txt, 02_article_title.txt, etc.)

### Combined Text Files
- Format: `all_posts_YYYY-MM-DD_HH-MM-SS.txt`
- Example: `all_posts_2025-10-17_14-30-45.txt`
- Contains: All posts in a single readable text file

## Usage

### Automatic Storage
Posts are automatically saved when you run:
- `python main.py`
- `python main_with_balance.py`
- POST to `/run-pipeline` endpoint

### Retrieve Saved Posts

#### Via API (n8n webhook server):
```bash
# Get latest posts as JSON
curl http://localhost:5000/get-saved-posts?format=json

# Download latest combined text file
curl http://localhost:5000/get-saved-posts?format=combined -O

# List all saved runs
curl http://localhost:5000/list-saved-runs
```

#### Via Python:
```python
from utils.post_storage import PostStorage

storage = PostStorage()

# Get latest JSON file path
latest_json = storage.get_latest_posts('json')

# Load posts from JSON
posts_data = storage.load_posts_from_json()

# List all saved runs
runs = storage.list_saved_runs()

# Get storage statistics
stats = storage.get_storage_stats()
```

## Storage Management

### Cleanup Old Files
```python
from utils.post_storage import PostStorage

storage = PostStorage()
storage.cleanup_old_files(keep_last=10)  # Keep only last 10 runs
```

### Storage Statistics
```python
stats = storage.get_storage_stats()
print(f"Total runs: {stats['total_runs']}")
print(f"Storage size: {stats['total_size_mb']} MB")
```

## Example Output

### JSON Format:
```json
{
  "generated_at": "2025-10-17_14-30-45",
  "total_posts": 10,
  "metadata": {
    "duration_seconds": 54.2,
    "articles_scraped": 15,
    "articles_analyzed": 15
  },
  "posts": [
    {
      "rank": 1,
      "title": "Revolutionary AI Marketplace Launches",
      "source": "TechCrunch",
      "link": "https://...",
      "priority_score": 95.5,
      "relevance_score": 9.5,
      "linkedin_post": "🚀 Exciting developments in AI..."
    }
  ]
}
```

### Text Format:
```
POST #1

Title: Revolutionary AI Marketplace Launches
Source: TechCrunch
Link: https://...
Priority Score: 95.5/100
Relevance Score: 9.5/10

LINKEDIN POST:
----------------------------------------
🚀 Exciting developments in AI...
----------------------------------------
```

## Notes

- Files are automatically timestamped for easy tracking
- Each run creates 3 types of output (JSON, individual texts, combined text)
- Old files can be manually deleted or cleaned up using the cleanup function
- All files use UTF-8 encoding for proper emoji and special character support
