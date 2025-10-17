# n8n Integration Guide for AI Happenings

Complete guide for integrating AI Happenings with n8n workflows.

## Prerequisites

- n8n installed and running
- AI Happenings webhook server running
- Required API keys (AgentBill, OpenAI)

## Quick Start

### 1. Start AI Happenings Server

```bash
cd ai-happenings/src
python n8n_webhook.py
```

Server will start on `http://localhost:5000`

### 2. Create n8n Workflow

#### Basic Workflow Structure

```
[Manual Trigger/Schedule]
    ↓
[HTTP Request - AI Happenings]
    ↓
[Process Results]
    ↓
[Actions: LinkedIn/Email/Database]
```

## n8n Node Configurations

### Option 1: Complete Pipeline

**HTTP Request Node Settings:**
- Method: `POST`
- URL: `http://localhost:5000/run-pipeline`
- Authentication: None
- Body Content Type: JSON
- Body:
```json
{
  "agentbill_api_key": "{{$env.AGENTBILL_API_KEY}}",
  "openai_api_key": "{{$env.OPENAI_API_KEY}}",
  "customer_id": "n8n-production",
  "debug": false
}
```

**Response Structure:**
```json
{
  "success": true,
  "timestamp": "2025-01-17T10:00:00",
  "duration_seconds": 45.2,
  "metrics": {
    "articles_scraped": 15,
    "articles_analyzed": 15,
    "top_articles_count": 10
  },
  "top_articles": [...],
  "summary_report": "...",
  "priority_report": "..."
}
```

### Option 2: Step-by-Step Pipeline

#### Step 1: Scrape Articles

```json
// POST http://localhost:5000/scrape-only
{
  "agentbill_api_key": "{{$env.AGENTBILL_API_KEY}}",
  "customer_id": "n8n-scrape"
}
```

#### Step 2: Analyze Articles

```json
// POST http://localhost:5000/analyze-articles
{
  "articles": "{{$json.articles}}",
  "openai_api_key": "{{$env.OPENAI_API_KEY}}",
  "agentbill_api_key": "{{$env.AGENTBILL_API_KEY}}"
}
```

#### Step 3: Prioritize Articles

```json
// POST http://localhost:5000/prioritize-articles
{
  "articles": "{{$json.articles}}",
  "agentbill_api_key": "{{$env.AGENTBILL_API_KEY}}",
  "top_count": 10
}
```

## Example Workflows

### Workflow 1: Daily LinkedIn Posts

```
Schedule Trigger (Daily 9 AM)
    ↓
HTTP Request (Get Top Posts)
    ↓
Split In Batches (Process each post)
    ↓
LinkedIn Node (Post to LinkedIn)
    ↓
Set Node (Mark as posted)
```

**Get Top Posts Request:**
```json
{
  "count": 5,
  "agentbill_api_key": "{{$env.AGENTBILL_API_KEY}}",
  "openai_api_key": "{{$env.OPENAI_API_KEY}}"
}
```

**Access Post Data:**
- Post text: `{{$json.posts[0].post_text}}`
- Article title: `{{$json.posts[0].article_title}}`
- Article link: `{{$json.posts[0].article_link}}`

### Workflow 2: Email Digest

```
Schedule Trigger (Weekly Monday 8 AM)
    ↓
HTTP Request (Run Pipeline)
    ↓
Function Node (Format Email)
    ↓
Send Email Node
```

**Email Template:**
```javascript
// Function Node
const topArticles = $json.top_articles.slice(0, 5);
const summary = $json.summary_report;

let html = `
<h1>Weekly AI Happenings Digest</h1>
<h2>Executive Summary</h2>
<p>${summary}</p>
<h2>Top 5 Articles This Week</h2>
`;

topArticles.forEach((article, index) => {
  html += `
    <h3>${index + 1}. ${article.title}</h3>
    <p><strong>Source:</strong> ${article.source}</p>
    <p><strong>Priority Score:</strong> ${article.priority_score}/100</p>
    <p>${article.linkedin_post}</p>
    <p><a href="${article.link}">Read More</a></p>
    <hr>
  `;
});

return [{ json: { html_content: html } }];
```

### Workflow 3: Database Storage

```
Schedule Trigger (Hourly)
    ↓
HTTP Request (Run Pipeline)
    ↓
Split In Batches (Top Articles)
    ↓
Postgres/MySQL Node (Insert Article)
```

**Database Insert:**
```sql
INSERT INTO articles (
  title,
  source,
  link,
  linkedin_post,
  priority_score,
  relevance_score,
  scraped_at
) VALUES (
  '{{$json.title}}',
  '{{$json.source}}',
  '{{$json.link}}',
  '{{$json.linkedin_post}}',
  {{$json.priority_score}},
  {{$json.relevance_score}},
  '{{$json.scraped_at}}'
);
```

### Workflow 4: Slack Notifications

```
Schedule Trigger (Daily)
    ↓
HTTP Request (Get Top Posts)
    ↓
Function Node (Format Slack Message)
    ↓
Slack Node (Send to Channel)
```

**Slack Message Format:**
```javascript
const posts = $json.posts.slice(0, 3);

let blocks = [{
  "type": "header",
  "text": {
    "type": "plain_text",
    "text": "🤖 Today's Top AI Happenings"
  }
}];

posts.forEach((post, index) => {
  blocks.push({
    "type": "section",
    "text": {
      "type": "mrkdwn",
      "text": `*${index + 1}. ${post.article_title}*\n${post.post_text.substring(0, 200)}...\n<${post.article_link}|Read More> | Score: ${post.priority_score}/100`
    }
  });
  blocks.push({"type": "divider"});
});

return [{ json: { blocks } }];
```

## Environment Variables in n8n

Set these in n8n Settings > Environment Variables:

```
AGENTBILL_API_KEY=your-agentbill-key
OPENAI_API_KEY=your-openai-key
AI_HAPPENINGS_URL=http://localhost:5000
```

Access in workflows: `{{$env.VARIABLE_NAME}}`

## Error Handling

### Retry Logic

Add "Error Trigger" node after HTTP Request:

```
HTTP Request Node
    ↓ (on error)
Error Trigger
    ↓
Wait Node (5 minutes)
    ↓
HTTP Request Node (retry)
```

### Response Validation

Add IF node after HTTP Request:

```javascript
// Condition
{{$json.success}} === true

// If False → Send Error Notification
// If True → Continue Pipeline
```

## Testing

### Test Endpoint Health

```bash
curl http://localhost:5000/health
```

Expected Response:
```json
{
  "status": "healthy",
  "service": "AI Happenings",
  "version": "1.0.0"
}
```

### Test Complete Pipeline

```bash
curl -X POST http://localhost:5000/run-pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "agentbill_api_key": "test-key",
    "openai_api_key": "test-key",
    "debug": true
  }'
```

## Performance Tips

1. **Use Caching**: Store results in n8n database
2. **Rate Limiting**: Don't run too frequently (hourly/daily recommended)
3. **Batch Processing**: Use "Split In Batches" for large datasets
4. **Async Operations**: Use webhooks for long-running tasks

## Monitoring

### Track in AgentBill

All API calls are tracked automatically:
- Check AgentBill dashboard
- View costs per customer_id
- Monitor error rates
- Analyze usage patterns

### n8n Logging

Enable in n8n workflow settings:
- Log successful executions
- Log errors
- Monitor execution times

## Advanced: Webhook Triggers

### Setup Webhook in n8n

1. Add "Webhook" node
2. Set path: `ai-happenings-trigger`
3. Set method: POST

### Trigger from External System

```bash
curl -X POST https://your-n8n-instance.com/webhook/ai-happenings-trigger \
  -H "Content-Type: application/json" \
  -d '{"trigger": "manual_run"}'
```

## Troubleshooting

### Connection Refused
- Ensure AI Happenings server is running
- Check firewall settings
- Verify correct port (default: 5000)

### Empty Results
- Check if news sites are accessible
- Verify keywords match available content
- Review AgentBill logs for errors

### API Key Errors
- Verify keys in n8n environment variables
- Check AgentBill dashboard for key status
- Ensure OpenAI key has credits

## Complete Example Workflow JSON

Save as `ai-happenings-workflow.json`:

```json
{
  "name": "AI Happenings - Daily LinkedIn Posts",
  "nodes": [
    {
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "rule": {
          "interval": [{"field": "hours", "hoursInterval": 24}]
        }
      }
    },
    {
      "name": "Get Top Posts",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://localhost:5000/get-top-posts",
        "method": "POST",
        "jsonParameters": true,
        "bodyParametersJson": {
          "agentbill_api_key": "={{$env.AGENTBILL_API_KEY}}",
          "openai_api_key": "={{$env.OPENAI_API_KEY}}",
          "count": 5
        }
      }
    }
  ]
}
```

Import this into n8n to get started quickly!

## Support

For questions:
- AI Happenings: Check main README.md
- n8n Documentation: https://docs.n8n.io
- AgentBill Support: https://agentbill.com/support
