# AI Happenings - Deployment Checklist

## ✅ Pre-Deployment Verification

### 1. Environment Setup
- [ ] Python 3.9+ installed
- [ ] Virtual environment created (`python -m venv venv` or `uv venv`)
- [ ] AgentBill SDK installed from TestPyPI
- [ ] All dependencies installed (`pip install -r requirements.txt`)

### 2. API Keys Configuration
- [ ] AgentBill API key obtained from https://agentbill.com
- [ ] OpenAI API key obtained from https://platform.openai.com
- [ ] `.env` file created from `.env.example`
- [ ] All required keys added to `.env`:
  ```bash
  AGENTBILL_API_KEY=your-agentbill-key
  OPENAI_API_KEY=your-openai-key
  CUSTOMER_ID=your-customer-id
  DAILY_CREDIT_LIMIT=1000
  ```

### 3. Test Basic Functionality
```bash
# Test 1: Run basic pipeline
cd src
python main.py

# Test 2: Run with balance tracking
python main_with_balance.py

# Test 3: Start webhook server
python n8n_webhook.py

# Test 4: Health check
curl http://localhost:5000/health
```

### 4. Verify AgentBill Integration
- [ ] Check AgentBill dashboard for events
- [ ] Verify `pipeline_started` event logged
- [ ] Verify `scraping_started` events for each source
- [ ] Verify `analysis_completed` events
- [ ] Verify action balance tracking events
- [ ] Verify credit consumption tracking

### 5. Docker Deployment (Optional)
```bash
# Build and start
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f ai-happenings

# Stop
docker-compose down
```

## 🎯 Deployment Options

### Option A: Standalone Development
**Use Case:** Testing and development
**Command:** `cd src && python main.py`
**Pros:** Quick to run, easy debugging
**Cons:** No action balance tracking

### Option B: With Action Balance ⭐ RECOMMENDED
**Use Case:** Production monitoring
**Command:** `cd src && python main_with_balance.py`
**Pros:** Full cost tracking, daily limits, detailed reports
**Cons:** Slightly more verbose output

### Option C: Docker Container
**Use Case:** Production deployment, n8n integration
**Command:** `docker-compose up -d`
**Pros:** Isolated, scalable, production-ready
**Cons:** Requires Docker installation

### Option D: n8n Webhook Server
**Use Case:** n8n workflow automation
**Command:** `cd src && python n8n_webhook.py`
**Pros:** REST API, flexible endpoints, n8n compatible
**Cons:** Requires running server

## 📊 Expected Results

### Typical Run Statistics
- **Sources Scraped:** 3 (TechCrunch, VentureBeat, MIT Tech Review)
- **Articles Found:** ~15-20
- **Articles Analyzed:** ~15
- **Top Articles Returned:** 10
- **Duration:** ~45-60 seconds
- **Credit Cost:** ~175-180 credits

### Sample Output (with Balance Tracking)
```
╔══════════════════════════════════════════════════════════╗
║              ACTION BALANCE REPORT                       ║
╠══════════════════════════════════════════════════════════╣
║  Total Cost: 178.5 credits                               ║
║  Remaining: 821.5 credits                                ║
║  Total Actions: 35                                       ║
╠══════════════════════════════════════════════════════════╣
║  ACTION BREAKDOWN                                        ║
╠══════════════════════════════════════════════════════════╣
║  scrape_source       x  3  =     3.0 credits             ║
║  extract_content     x 15  =     7.5 credits             ║
║  analyze_article     x 15  =   150.0 credits             ║
║  prioritize_batch    x  1  =     2.0 credits             ║
║  generate_summary    x  1  =    15.0 credits             ║
╚══════════════════════════════════════════════════════════╝
```

## 🔗 n8n Integration Testing

### 1. Start Webhook Server
```bash
cd src
python n8n_webhook.py
# Server running on http://localhost:5000
```

### 2. Test All Endpoints
```bash
# Health check
curl http://localhost:5000/health

# Full pipeline
curl -X POST http://localhost:5000/run-pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "agentbill_api_key": "your-key",
    "openai_api_key": "your-key",
    "customer_id": "test-customer"
  }'

# Scrape only
curl -X POST http://localhost:5000/scrape-only \
  -H "Content-Type: application/json" \
  -d '{
    "agentbill_api_key": "your-key"
  }'

# Get top posts (convenience endpoint)
curl -X POST http://localhost:5000/get-top-posts \
  -H "Content-Type: application/json" \
  -d '{
    "agentbill_api_key": "your-key",
    "openai_api_key": "your-key",
    "limit": 5
  }'
```

### 3. Create n8n Workflow
1. Add Schedule Trigger (e.g., daily at 9 AM)
2. Add HTTP Request node:
   - URL: `http://localhost:5000/run-pipeline`
   - Method: POST
   - Body: JSON with API keys
3. Add Split In Batches node for `{{$json.top_articles}}`
4. Add LinkedIn node to post each article
5. Activate workflow

## 💰 Cost Management

### Monitor Daily Usage
```bash
# Check remaining balance after each run
# Look for "Remaining Balance" in output
python main_with_balance.py | grep "Remaining Balance"
```

### Adjust Daily Limit
```bash
# In .env file
DAILY_CREDIT_LIMIT=2000  # Increase limit

# Or pass as environment variable
DAILY_CREDIT_LIMIT=500 python main_with_balance.py
```

### Cost Optimization Tips
1. **Use GPT-3.5-turbo** instead of GPT-4 (50% cost reduction)
   - Edit `src/analyzers/ai_analyzer.py`
   - Change `model="gpt-4"` to `model="gpt-3.5-turbo"`

2. **Pre-filter articles** before AI analysis
   - Implement keyword scoring
   - Filter low-relevance articles early

3. **Cache analyzed articles**
   - Store analysis results
   - Reuse for duplicate articles

4. **Batch processing**
   - Already implemented with AsyncIO
   - Processes multiple articles concurrently

## 🐛 Troubleshooting

### Issue: "No articles found"
**Solution:**
- Check internet connectivity
- Verify source websites are accessible
- Check if keywords match available content
- Try increasing keyword list

### Issue: "Daily credit limit exceeded"
**Solution:**
- Increase `DAILY_CREDIT_LIMIT` in .env
- Wait for daily reset
- Check AgentBill dashboard for actual usage

### Issue: "OpenAI API error"
**Solution:**
- Verify OpenAI API key is valid
- Check OpenAI account has credits
- Check for rate limiting (wait and retry)

### Issue: "AgentBill tracking not working"
**Solution:**
- Verify AgentBill API key
- Check `debug=True` in config
- Review logs in `logs/` directory
- Check AgentBill dashboard

### Issue: Webhook server not responding
**Solution:**
- Check if port 5000 is available
- Try different port: `PORT=8000 python n8n_webhook.py`
- Check firewall settings
- Verify Flask and dependencies installed

## 📈 Monitoring & Analytics

### AgentBill Dashboard Metrics
Login to https://agentbill.com/dashboard to view:
- Total credits consumed
- Cost breakdown by action type
- Usage trends over time
- Customer segmentation
- Event timeline

### Local Logs
Check `logs/` directory for:
- Scraping logs
- Analysis logs
- Error logs
- Debug information

### Action Balance Reports
Generated automatically with each run:
- Session summary
- Cost breakdown
- Efficiency metrics
- Remaining balance

## 🚀 Production Deployment

### Recommended Setup
1. Use Docker deployment for isolation
2. Enable action balance tracking
3. Set appropriate daily limits
4. Configure monitoring alerts
5. Schedule regular runs via n8n
6. Monitor AgentBill dashboard daily

### Environment Variables for Production
```bash
# .env for production
AGENTBILL_API_KEY=prod-key-here
OPENAI_API_KEY=prod-key-here
CUSTOMER_ID=production-customer
DAILY_CREDIT_LIMIT=5000
DEBUG=false
PORT=5000
```

### Docker Production Command
```bash
docker-compose -f docker-compose.yml up -d
```

### Scaling Considerations
- Increase `DAILY_CREDIT_LIMIT` for higher volumes
- Add more news sources in `web_scraper.py`
- Consider Redis caching for analyzed articles
- Use load balancer for multiple instances
- Implement queue system for batch processing

## 📚 Documentation Reference

| Document | Purpose |
|----------|---------|
| `README.md` | Complete project overview |
| `QUICK_START.md` | 5-minute setup guide |
| `N8N_INTEGRATION_GUIDE.md` | n8n workflow examples |
| `ACTION_BALANCE_GUIDE.md` | Balance tracking details |
| `COMPLETE_SETUP.md` | Comprehensive setup guide |
| `DEPLOYMENT_CHECKLIST.md` | This checklist |
| `PROJECT_SUMMARY.txt` | Project summary |

## ✅ Final Checklist

Before going live:
- [ ] All tests pass
- [ ] API keys configured
- [ ] AgentBill tracking verified
- [ ] Balance limits set appropriately
- [ ] n8n workflow tested (if using)
- [ ] Docker deployment tested (if using)
- [ ] Documentation reviewed
- [ ] Monitoring dashboard setup
- [ ] Backup/recovery plan in place
- [ ] Team trained on usage

## 🎉 You're Ready!

The AI Happenings application is production-ready with:
✅ Web scraping from 3 major tech sites
✅ AI-powered analysis and summarization
✅ Smart article prioritization
✅ LinkedIn post generation
✅ Complete AgentBill integration
✅ Action balance tracking
✅ n8n webhook integration
✅ Docker deployment
✅ Comprehensive documentation

**Need help?** Check the documentation or visit:
- AgentBill Support: https://agentbill.com/support
- OpenAI Docs: https://platform.openai.com/docs
- n8n Docs: https://docs.n8n.io

---

**Built with AgentBill SDK - Track every action, optimize every credit!**
