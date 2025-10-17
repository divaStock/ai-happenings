# Action Balance Tracking Guide

Complete guide for understanding and managing action balance in AI Happenings.

## What is Action Balance?

Action Balance is a credit-based system that tracks the cost of each operation in AI Happenings. Every action consumes a certain number of credits, allowing you to:

- Monitor usage in real-time
- Set daily limits
- Estimate costs before execution
- Optimize spending
- Track ROI per operation

## Action Costs

| Action | Cost (Credits) | Description |
|--------|---------------|-------------|
| `scrape_source` | 1 | Scrape one news source |
| `extract_content` | 0.5 | Extract full article content |
| `analyze_article` | 10 | AI analysis with GPT-4 |
| `generate_summary` | 15 | Generate executive summary |
| `prioritize_batch` | 2 | Prioritize all articles |
| `api_call` | 5 | Generic API call |

## Usage

### Running with Balance Tracking

```bash
cd src
python main_with_balance.py
```

### Output Example

```
╔══════════════════════════════════════════════════════════╗
║              ACTION BALANCE REPORT                       ║
╠══════════════════════════════════════════════════════════╣
║  Session Start: 2025-01-17 10:00:00                     ║
║  Duration: 45.2s                                         ║
║  Total Actions: 35                                       ║
║  Total Cost: 178.5 credits                               ║
╠══════════════════════════════════════════════════════════╣
║  ACTION BREAKDOWN                                        ║
╠══════════════════════════════════════════════════════════╣
║  scrape_source       x  3  =     3.0 credits             ║
║  extract_content     x 15  =     7.5 credits             ║
║  analyze_article     x 15  =   150.0 credits             ║
║  prioritize_batch    x  1  =     2.0 credits             ║
║  generate_summary    x  1  =    15.0 credits             ║
╠══════════════════════════════════════════════════════════╣
║  COST EFFICIENCY                                         ║
╠══════════════════════════════════════════════════════════╣
║  Actions/sec: 0.77                                       ║
║  Credits/sec: 3.95                                       ║
╚══════════════════════════════════════════════════════════╝
```

## Setting Daily Limits

### Environment Variable
```bash
export DAILY_CREDIT_LIMIT=1000
```

### In Code
```python
config = {
    "agentbill_api_key": "your-key",
    "openai_api_key": "your-key",
    "daily_credit_limit": 1000
}

app = AIHappeningsWithBalance(config)
```

### What Happens When Limit is Reached?

1. Pipeline checks estimated cost before starting
2. If exceeds limit, pipeline is blocked
3. Error returned with remaining balance
4. AgentBill tracks limit exceeded event

## Cost Estimation

Before running pipeline, estimate costs:

```python
from utils.action_tracker import ActionBalanceTracker

tracker = ActionBalanceTracker(agentbill)

planned_actions = {
    "scrape_source": 3,
    "analyze_article": 15,
    "prioritize_batch": 1
}

estimation = tracker.estimate_action_cost(planned_actions)
print(f"Estimated cost: {estimation['total_estimated_cost']} credits")
```

Output:
```json
{
  "planned_actions": {
    "scrape_source": 3,
    "analyze_article": 15,
    "prioritize_batch": 1
  },
  "estimated_costs": {
    "scrape_source": {"count": 3, "unit_cost": 1, "total_cost": 3},
    "analyze_article": {"count": 15, "unit_cost": 10, "total_cost": 150},
    "prioritize_batch": {"count": 1, "unit_cost": 2, "total_cost": 2}
  },
  "total_estimated_cost": 155
}
```

## n8n Integration with Balance

### Endpoint with Balance Info

All endpoints return balance information:

```json
{
  "success": true,
  "action_balance": {
    "total_cost": 178.5,
    "remaining_daily_balance": 821.5,
    "total_actions": 35,
    "breakdown": {
      "scrape_source": {"count": 3, "total_cost": 3.0},
      "analyze_article": {"count": 15, "total_cost": 150.0}
    }
  }
}
```

### n8n Workflow with Balance Monitoring

```javascript
// Check remaining balance before running
const balance = {{$json.action_balance.remaining_daily_balance}};

if (balance < 100) {
  // Send alert
  return {json: {alert: "Low balance warning", balance}};
}

// Continue with next action
```

## AgentBill Dashboard Metrics

All action balance events are tracked in AgentBill:

### Tracked Events
- `action_scrape_source` - Source scraped
- `action_analyze_article` - Article analyzed
- `action_generate_summary` - Summary generated
- `cost_estimation_requested` - Cost estimated
- `balance_threshold_exceeded` - Threshold exceeded
- `daily_limit_exceeded` - Daily limit reached
- `credits_consumed` - Credits used
- `balance_report_generated` - Report generated

### Dashboard Views
1. **Cost Breakdown** - Cost by action type
2. **Usage Trends** - Credits over time
3. **Limit Monitoring** - Daily limit tracking
4. **Efficiency Metrics** - Actions vs. cost
5. **Customer Segmentation** - Cost by customer

## Optimizing Costs

### 1. Reduce AI Analysis
```python
# Use GPT-3.5-turbo instead of GPT-4
model="gpt-3.5-turbo"  # Reduces cost by 50%
```

### 2. Batch Processing
```python
# Analyze in larger batches
batch_size = 20  # More efficient than individual calls
```

### 3. Smart Filtering
```python
# Pre-filter articles before AI analysis
articles = [a for a in articles if relevance_check(a)]
```

### 4. Cache Results
```python
# Cache analyzed articles
if article_id in cache:
    return cache[article_id]
```

### 5. Schedule Off-Peak
```python
# Run during off-peak hours
# Potentially negotiate lower rates
```

## Monitoring & Alerts

### Set Up Alerts

```python
# Check threshold periodically
if not tracker.check_balance_threshold(threshold=800):
    send_alert("80% of daily limit reached!")
```

### Daily Reports

```bash
# Generate end-of-day report
python src/generate_balance_report.py
```

### Integration with Monitoring Tools

```python
# Export to Prometheus
metrics = tracker.export_session_data()
prometheus_client.gauge('action_balance_cost').set(metrics['total_cost'])
```

## API Reference

### ActionBalanceTracker

```python
tracker = ActionBalanceTracker(agentbill)

# Track action
tracker.track_action("action_name", metadata={})

# Get session cost
total_cost = tracker.get_session_cost()

# Get breakdown
breakdown = tracker.get_action_breakdown()

# Generate report
report = tracker.get_balance_report()

# Check threshold
within_limit = tracker.check_balance_threshold(800)

# Estimate cost
estimation = tracker.estimate_action_cost(planned_actions)

# Export data
data = tracker.export_session_data()
```

### UsageLimiter

```python
limiter = UsageLimiter(agentbill, daily_limit=1000)

# Check if within limit
can_proceed = limiter.check_limit(required_credits)

# Consume credits
limiter.consume_credits(credits)

# Get remaining balance
remaining = limiter.get_remaining_balance()
```

## Cost Calculation Examples

### Example 1: Small Pipeline (5 articles)
```
3 sources × 1 credit = 3
5 articles × 0.5 credit (extract) = 2.5
5 articles × 10 credits (analyze) = 50
1 batch × 2 credits (prioritize) = 2
1 summary × 15 credits = 15
---
Total: 72.5 credits
```

### Example 2: Medium Pipeline (15 articles)
```
3 sources × 1 = 3
15 articles × 0.5 (extract) = 7.5
15 articles × 10 (analyze) = 150
1 batch × 2 (prioritize) = 2
1 summary × 15 = 15
---
Total: 177.5 credits
```

### Example 3: Large Pipeline (50 articles)
```
3 sources × 1 = 3
50 articles × 0.5 (extract) = 25
50 articles × 10 (analyze) = 500
1 batch × 2 (prioritize) = 2
1 summary × 15 = 15
---
Total: 545 credits
```

## Best Practices

1. **Set Realistic Limits** - Based on expected usage
2. **Monitor Daily** - Check balance reports
3. **Use Estimations** - Before expensive operations
4. **Implement Alerts** - At 80% threshold
5. **Review Breakdown** - Identify cost drivers
6. **Optimize High-Cost Actions** - Focus on analysis costs
7. **Track ROI** - Cost vs. value generated
8. **Use AgentBill Dashboard** - Comprehensive analytics

## Troubleshooting

### High Costs
- Check which actions consume most credits
- Optimize AI model selection
- Implement caching
- Pre-filter articles

### Hitting Limits
- Increase daily limit if justified
- Schedule jobs across day
- Prioritize high-value operations
- Use cost estimation before runs

### Tracking Issues
- Verify AgentBill integration
- Check debug mode enabled
- Review AgentBill dashboard
- Examine logs directory

## Support

For action balance issues:
- Check AgentBill dashboard
- Review balance reports
- Contact AgentBill support
- See main README.md

---

**Track every action. Optimize every credit. Maximize every result.**
