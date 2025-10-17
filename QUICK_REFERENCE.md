# AI Happenings - Quick Reference Card

## 🚀 Common Commands

### Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple agentbill
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys
```

### Running the Application

```bash
# Standard run (no balance tracking)
cd src && python main.py

# With action balance tracking ⭐ RECOMMENDED
cd src && python main_with_balance.py

# Start webhook server for n8n
cd src && python n8n_webhook.py
```

### Docker Commands

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f ai-happenings

# Restart
docker-compose restart

# Check status
docker-compose ps
```

## 🔗 API Endpoints (n8n Webhook Server)

| Endpoint | Method | Purpose | Required Keys |
|----------|--------|---------|---------------|
| `/health` | GET | Health check | None |
| `/run-pipeline` | POST | Complete pipeline | AgentBill + OpenAI |
| `/scrape-only` | POST | Scrape articles only | AgentBill |
| `/analyze-articles` | POST | Analyze provided articles | AgentBill + OpenAI |
| `/prioritize-articles` | POST | Prioritize articles | AgentBill |
| `/get-top-posts` | POST | Get top LinkedIn posts | AgentBill + OpenAI |

### Quick Test
```bash
curl http://localhost:5000/health
```

## 💰 Action Costs

| Action | Cost (Credits) |
|--------|----------------|
| Scrape source | 1 |
| Extract content | 0.5 |
| Analyze article (GPT-4) | 10 |
| Generate summary | 15 |
| Prioritize batch | 2 |

**Typical Pipeline Cost:** ~178 credits for 15 articles

## ⚙️ Environment Variables

```bash
# Required
AGENTBILL_API_KEY=your-key        # From agentbill.com
OPENAI_API_KEY=your-key           # From platform.openai.com

# Optional
CUSTOMER_ID=your-customer-id      # Default: "ai-happenings"
DAILY_CREDIT_LIMIT=1000           # Default: 1000 credits
DEBUG=true                        # Default: true
PORT=5000                         # Default: 5000 (webhook server)
```

## 📊 Expected Output

### Success Indicators
✓ "Pipeline completed successfully"
✓ "Total Credits Used: X"
✓ "Top 10 Articles Ready"
✓ LinkedIn posts generated

### Key Metrics
- **Articles Scraped:** 15-20
- **Articles Analyzed:** 15
- **Duration:** 45-60 seconds
- **Cost:** 175-180 credits

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| No articles found | Check internet, verify sources accessible |
| API key error | Verify keys in .env file |
| Daily limit exceeded | Increase DAILY_CREDIT_LIMIT or wait for reset |
| Port 5000 in use | Change PORT in .env or docker-compose.yml |
| Import errors | Verify all dependencies installed |

## 📁 Important Files

```
ai-happenings/
├── src/
│   ├── main.py                    # Standard pipeline
│   ├── main_with_balance.py       # With balance tracking
│   ├── n8n_webhook.py             # API server
│   ├── scrapers/web_scraper.py    # Scraping logic
│   ├── analyzers/ai_analyzer.py   # AI analysis
│   ├── prioritizers/article_prioritizer.py  # Prioritization
│   └── utils/action_tracker.py    # Balance tracking
├── .env                           # Your API keys (create from .env.example)
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker image
├── docker-compose.yml             # Docker orchestration
└── logs/                          # Application logs
```

## 🎯 Common Use Cases

### Use Case 1: Daily News Digest
```bash
# Run with balance tracking
cd src
python main_with_balance.py

# Check balance report
# Look for "ACTION BALANCE REPORT" in output
```

### Use Case 2: n8n Automation
```bash
# Start webhook server
cd src
python n8n_webhook.py

# In n8n: HTTP Request to http://localhost:5000/run-pipeline
```

### Use Case 3: Docker Production
```bash
# Deploy
docker-compose up -d

# Monitor
docker-compose logs -f

# Access at http://localhost:5000
```

## 📈 Customization Quick Tips

### Add News Sources
**File:** `src/scrapers/web_scraper.py`
```python
self.sources.append({
    "name": "Your Site",
    "url": "https://example.com/ai-news",
    "selector": "article"
})
```

### Change AI Model
**File:** `src/analyzers/ai_analyzer.py`
```python
# Change from GPT-4 to GPT-3.5 (50% cheaper)
model="gpt-3.5-turbo"  # instead of "gpt-4"
```

### Modify Keywords
**File:** `src/scrapers/web_scraper.py`
```python
self.keywords = [
    "your",
    "custom",
    "keywords"
]
```

### Adjust Action Costs
**File:** `src/utils/action_tracker.py`
```python
self.action_costs = {
    "analyze_article": 5,  # Reduce if using GPT-3.5
    # ...
}
```

## 📚 Documentation

| Doc | When to Use |
|-----|-------------|
| `README.md` | Overview and features |
| `QUICK_START.md` | First-time setup (5 min) |
| `N8N_INTEGRATION_GUIDE.md` | Setting up n8n workflows |
| `ACTION_BALANCE_GUIDE.md` | Understanding costs |
| `COMPLETE_SETUP.md` | Complete deployment guide |
| `DEPLOYMENT_CHECKLIST.md` | Pre-production checklist |
| `QUICK_REFERENCE.md` | This document |

## 🔑 Getting API Keys

### AgentBill API Key
1. Visit https://agentbill.com
2. Sign up / Log in
3. Go to Settings → API Keys
4. Copy your API key

### OpenAI API Key
1. Visit https://platform.openai.com
2. Sign up / Log in
3. Go to API Keys section
4. Create new secret key
5. Copy your API key

## 💡 Pro Tips

1. **Always use balance tracking in production**
   ```bash
   python main_with_balance.py
   ```

2. **Monitor AgentBill dashboard daily**
   - Track costs
   - Identify optimization opportunities

3. **Set appropriate daily limits**
   ```bash
   DAILY_CREDIT_LIMIT=2000  # Adjust based on needs
   ```

4. **Use Docker for n8n integration**
   ```bash
   docker-compose up -d
   ```

5. **Check logs for debugging**
   ```bash
   tail -f logs/*.log
   ```

6. **Estimate costs before running**
   - 15 articles ≈ 178 credits
   - 30 articles ≈ 353 credits
   - 50 articles ≈ 545 credits

## 🎉 Quick Start (60 seconds)

```bash
# 1. Setup (15 sec)
cp .env.example .env
# Edit .env with your keys

# 2. Install (30 sec)
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple agentbill
pip install -r requirements.txt

# 3. Run (15 sec)
cd src && python main_with_balance.py
```

## 📞 Support

- **AgentBill Issues:** https://agentbill.com/support
- **OpenAI Issues:** https://platform.openai.com/docs
- **n8n Issues:** https://docs.n8n.io

---

**Keep this reference handy for quick access to common operations!**
