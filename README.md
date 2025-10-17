# AI Happenings 🤖📰

AI-powered news aggregation and analysis system for **Agentic Commerce** and **AI Marketplaces**. Automatically scrapes technology news, analyzes content with AI, generates LinkedIn-ready posts, and prioritizes articles - all tracked with AgentBill SDK.

## Features

✨ **Web Scraping** - Automatically scrapes leading tech news sites
🤖 **AI Analysis** - Uses OpenAI GPT-4 to analyze and summarize articles
📝 **LinkedIn Posts** - Generates engaging LinkedIn posts automatically
🎯 **Smart Prioritization** - Ranks articles by relevance, recency, and engagement potential
📊 **AgentBill Tracking** - Comprehensive usage and cost tracking for all operations
🔗 **n8n Integration** - RESTful API for seamless n8n workflow integration

## Architecture

```
ai-happenings/
├── src/
│   ├── scrapers/
│   │   └── web_scraper.py       # Web scraping module
│   ├── analyzers/
│   │   └── ai_analyzer.py       # AI analysis & summarization
│   ├── prioritizers/
│   │   └── article_prioritizer.py # Article ranking
│   ├── main.py                  # Main application
│   └── n8n_webhook.py           # n8n webhook server
├── config/                      # Configuration files
├── logs/                        # Application logs
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
└── README.md                    # This file
```

## Installation

### 1. Clone/Navigate to Project
```bash
cd ai-happenings
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Install agentbill from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple agentbill

# Install other dependencies
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your API keys
```

Required API Keys:
- `AGENTBILL_API_KEY` - Get from [AgentBill](https://agentbill.com)
- `OPENAI_API_KEY` - Get from [OpenAI](https://platform.openai.com)

## Usage

### Standalone Execution

Run the complete pipeline:

```bash
cd src
python main.py
```

Output includes:
- Scraped articles from tech news sites
- AI-analyzed summaries
- LinkedIn-ready posts
- Priority rankings
- Summary reports

### n8n Integration

#### 1. Start Webhook Server
```bash
cd src
python n8n_webhook.py
```

Server starts on `http://localhost:5000`

#### 2. Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/run-pipeline` | POST | Run complete pipeline |
| `/scrape-only` | POST | Scrape articles only |
| `/analyze-articles` | POST | Analyze articles with AI |
| `/prioritize-articles` | POST | Prioritize articles |
| `/get-top-posts` | POST | Get top LinkedIn posts |

#### 3. n8n Workflow Setup

**Step 1: Create Webhook Node**
- Add "Webhook" node in n8n
- Set Method: POST
- Set Path: `ai-happenings`

**Step 2: Add HTTP Request Node**
- URL: `http://localhost:5000/run-pipeline`
- Method: POST
- Body (JSON):
```json
{
  "agentbill_api_key": "{{$env.AGENTBILL_API_KEY}}",
  "openai_api_key": "{{$env.OPENAI_API_KEY}}",
  "customer_id": "my-n8n-workflow",
  "debug": true
}
```

**Step 3: Process Results**
Add nodes to handle the response:
- `{{$json.top_articles}}` - Array of top articles
- `{{$json.summary_report}}` - Executive summary
- `{{$json.metrics}}` - Pipeline metrics

**Example n8n Workflow:**
```
Webhook (Schedule/Manual)
    ↓
HTTP Request (AI Happenings API)
    ↓
Split In Batches (Top Articles)
    ↓
LinkedIn Post (Auto-post to LinkedIn)
    ↓
Send Email (Summary Report)
```

## API Examples

### Complete Pipeline
```bash
curl -X POST http://localhost:5000/run-pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "agentbill_api_key": "your-key",
    "openai_api_key": "your-key",
    "customer_id": "test-run"
  }'
```

### Get Top Posts Only
```bash
curl -X POST http://localhost:5000/get-top-posts \
  -H "Content-Type: application/json" \
  -d '{
    "agentbill_api_key": "your-key",
    "openai_api_key": "your-key",
    "count": 5
  }'
```

Response:
```json
{
  "success": true,
  "posts_count": 5,
  "posts": [
    {
      "rank": 1,
      "post_text": "🚀 Exciting developments in AI...",
      "article_title": "New AI Marketplace Platform Launches",
      "article_link": "https://...",
      "priority_score": 95.5
    }
  ]
}
```

## AgentBill Tracking

All operations are tracked with AgentBill SDK:

### Tracked Events:
- `pipeline_started` - Pipeline execution begins
- `pipeline_completed` - Pipeline finishes successfully
- `scraping_started` / `scraping_completed` - Web scraping
- `article_analysis_started` / `article_analysis_completed` - AI analysis
- `prioritization_completed` - Article prioritization
- `batch_analysis_completed` - Batch operations
- Various error events

### Revenue Tracking:
- Article analysis: $0.01 per article
- Summary report: $0.005
- Complete pipeline: $0.10

### Viewing Metrics:
Check your AgentBill dashboard for:
- Total API calls
- Token usage
- Cost breakdown
- Performance metrics
- Error rates

## Configuration

### Environment Variables

```bash
# Required
AGENTBILL_API_KEY=your-agentbill-key
OPENAI_API_KEY=your-openai-key

# Optional
CUSTOMER_ID=ai-happenings-prod
PORT=5000
DEBUG=true
```

### Customization

#### Add News Sources
Edit `src/scrapers/web_scraper.py`:
```python
self.sources = [
    {
        "name": "Your Source",
        "url": "https://example.com/ai-news",
        "selector": "article"
    }
]
```

#### Modify Keywords
Edit `src/scrapers/web_scraper.py`:
```python
self.keywords = [
    "agentic commerce",
    "ai marketplace",
    # Add your keywords
]
```

#### Adjust AI Model
Edit `src/analyzers/ai_analyzer.py`:
```python
model="gpt-4"  # or "gpt-3.5-turbo" for lower cost
```

## Output Format

### Top Articles Structure
```json
{
  "rank": 1,
  "title": "Article Title",
  "source": "TechCrunch",
  "link": "https://...",
  "priority_score": 95.5,
  "relevance_score": 9.5,
  "linkedin_post": "🚀 AI innovation is transforming...",
  "scraped_at": "2025-01-17T10:30:00"
}
```

## Troubleshooting

### Issue: No articles found
- Check internet connection
- Verify news site URLs are accessible
- Check if keywords match available content

### Issue: API key errors
- Verify API keys in `.env` file
- Check AgentBill dashboard for key status
- Ensure OpenAI key has sufficient credits

### Issue: n8n connection refused
- Ensure webhook server is running (`python n8n_webhook.py`)
- Check port 5000 is not in use
- Verify firewall settings

## Development

### Run Tests
```bash
pytest tests/ -v
```

### Add New Features
1. Create module in appropriate directory
2. Initialize with AgentBill tracker
3. Add tracking signals for key operations
4. Update `main.py` to integrate

### Logging
Logs are written to `logs/` directory with timestamps.

## Production Deployment

### Using Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 src.n8n_webhook:app
```

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src.n8n_webhook:app"]
```

## License

MIT License

## Support

For issues or questions:
- AgentBill: https://agentbill.com/support
- OpenAI: https://platform.openai.com/docs

## Roadmap

- [ ] Add more news sources
- [ ] Support for Anthropic Claude
- [ ] Automated LinkedIn posting
- [ ] Email digest functionality
- [ ] Dashboard UI
- [ ] Scheduling system

---

**Built with ❤️ using AgentBill SDK for complete usage tracking**
