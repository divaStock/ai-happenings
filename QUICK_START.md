# Quick Start Guide - AI Happenings

Get up and running in 5 minutes!

## Prerequisites

- Python 3.9+
- OpenAI API key
- AgentBill API key

## Installation (3 steps)

### 1. Install Dependencies
```bash
cd ai-happenings

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install AgentBill from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple agentbill

# Install other dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys
```bash
cp .env.example .env
```

Edit `.env` and add your keys:
```
AGENTBILL_API_KEY=your-agentbill-api-key
OPENAI_API_KEY=your-openai-api-key
CUSTOMER_ID=quickstart-test
```

### 3. Run!

**Option A: Standalone (complete pipeline)**
```bash
cd src
python main.py
```

**Option B: Webhook Server (for n8n)**
```bash
cd src
python n8n_webhook.py
```

## Test It Works

### Test Standalone
```bash
cd src
python main.py
```

You should see:
```
📡 Step 1: Scraping articles...
   ✓ Found X articles
🤖 Step 2: Analyzing with AI...
   ✓ Analyzed X articles
🎯 Step 3: Prioritizing...
   ✓ Top 10 articles selected
```

### Test Webhook Server
```bash
# Terminal 1: Start server
cd src
python n8n_webhook.py

# Terminal 2: Test health endpoint
curl http://localhost:5000/health
```

Expected response:
```json
{"status": "healthy", "service": "AI Happenings"}
```

## Use with n8n

### 1. Start Webhook Server
```bash
cd src
python n8n_webhook.py
```

### 2. Create n8n HTTP Request Node
- URL: `http://localhost:5000/run-pipeline`
- Method: POST
- Body:
```json
{
  "agentbill_api_key": "{{$env.AGENTBILL_API_KEY}}",
  "openai_api_key": "{{$env.OPENAI_API_KEY}}"
}
```

### 3. Access Results in n8n
- Top articles: `{{$json.top_articles}}`
- Summary: `{{$json.summary_report}}`
- Metrics: `{{$json.metrics}}`

## What It Does

1. **Scrapes** - Fetches articles from tech news sites about AI and commerce
2. **Analyzes** - Uses GPT-4 to create LinkedIn-ready posts
3. **Prioritizes** - Ranks articles by relevance and engagement potential
4. **Tracks** - Logs all operations to AgentBill dashboard

## Output Example

```json
{
  "success": true,
  "top_articles": [
    {
      "rank": 1,
      "title": "New AI Marketplace Platform Launches",
      "source": "TechCrunch",
      "linkedin_post": "🚀 Exciting news in AI commerce...",
      "priority_score": 95.5,
      "link": "https://..."
    }
  ]
}
```

## Common Issues

### "ModuleNotFoundError: No module named 'agentbill'"
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple agentbill
```

### "Missing API keys"
Check your `.env` file has correct keys set.

### "No articles found"
Normal on first run if sites are rate-limiting. Try again in a few minutes.

## Next Steps

- ✅ Check [README.md](README.md) for full documentation
- ✅ Read [N8N_INTEGRATION_GUIDE.md](N8N_INTEGRATION_GUIDE.md) for n8n workflows
- ✅ View AgentBill dashboard for usage metrics
- ✅ Customize news sources in `src/scrapers/web_scraper.py`

## Get Help

- Main docs: [README.md](README.md)
- n8n integration: [N8N_INTEGRATION_GUIDE.md](N8N_INTEGRATION_GUIDE.md)
- AgentBill: https://agentbill.com/support

Happy scraping! 🤖📰
