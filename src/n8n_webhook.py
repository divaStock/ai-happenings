"""
n8n Webhook Handler for AI Happenings
Provides REST API endpoints for n8n integration
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import asyncio
import os
from main import AIHappenings
from datetime import datetime
from utils.post_storage import PostStorage


# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for n8n integration


def create_config_from_request(request_data: dict) -> dict:
    """
    Create configuration from request data or environment variables.

    Args:
        request_data: Request JSON data

    Returns:
        Configuration dictionary
    """
    return {
        "agentbill_api_key": request_data.get("agentbill_api_key") or os.getenv("AGENTBILL_API_KEY", ""),
        "openai_api_key": request_data.get("openai_api_key") or os.getenv("OPENAI_API_KEY", ""),
        "customer_id": request_data.get("customer_id") or os.getenv("CUSTOMER_ID", "n8n-integration"),
        "debug": request_data.get("debug", True)
    }


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "AI Happenings",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/run-pipeline', methods=['POST'])
def run_pipeline():
    """
    Run the complete AI Happenings pipeline.

    Request Body (optional):
    {
        "agentbill_api_key": "your-key",
        "openai_api_key": "your-key",
        "customer_id": "your-customer-id",
        "debug": true
    }

    Returns:
        JSON response with pipeline results
    """
    try:
        # Get configuration from request or environment
        request_data = request.get_json() or {}
        config = create_config_from_request(request_data)

        # Validate required keys
        if not config["agentbill_api_key"] or not config["openai_api_key"]:
            return jsonify({
                "success": False,
                "error": "Missing required API keys (agentbill_api_key, openai_api_key)",
                "timestamp": datetime.now().isoformat()
            }), 400

        # Initialize and run pipeline
        app_instance = AIHappenings(config)

        # Run async pipeline in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(app_instance.run_pipeline())
        loop.close()

        # Return result
        return jsonify(result), 200 if result["success"] else 500

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route('/scrape-only', methods=['POST'])
def scrape_only():
    """
    Run only the scraping step.

    Returns:
        JSON response with scraped articles
    """
    try:
        request_data = request.get_json() or {}
        config = create_config_from_request(request_data)

        if not config["agentbill_api_key"]:
            return jsonify({
                "success": False,
                "error": "Missing agentbill_api_key"
            }), 400

        from agentbill import AgentBill
        from scrapers.web_scraper import WebScraper

        agentbill = AgentBill.init({
            "api_key": config["agentbill_api_key"],
            "customer_id": config.get("customer_id", "n8n-scrape-only"),
            "debug": config.get("debug", True)
        })

        scraper = WebScraper(agentbill)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        articles = loop.run_until_complete(scraper.scrape_all_sources())
        loop.close()

        return jsonify({
            "success": True,
            "articles_count": len(articles),
            "articles": articles,
            "timestamp": datetime.now().isoformat()
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/analyze-articles', methods=['POST'])
def analyze_articles():
    """
    Analyze provided articles with AI.

    Request Body:
    {
        "articles": [...],
        "openai_api_key": "your-key",
        "agentbill_api_key": "your-key"
    }

    Returns:
        JSON response with analyzed articles
    """
    try:
        request_data = request.get_json()

        if not request_data or "articles" not in request_data:
            return jsonify({
                "success": False,
                "error": "Missing 'articles' in request body"
            }), 400

        config = create_config_from_request(request_data)

        if not config["openai_api_key"] or not config["agentbill_api_key"]:
            return jsonify({
                "success": False,
                "error": "Missing required API keys"
            }), 400

        from agentbill import AgentBill
        from analyzers.ai_analyzer import AIAnalyzer

        agentbill = AgentBill.init({
            "api_key": config["agentbill_api_key"],
            "customer_id": config.get("customer_id", "n8n-analyze"),
            "debug": config.get("debug", True)
        })

        analyzer = AIAnalyzer(config["openai_api_key"], agentbill)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        analyzed = loop.run_until_complete(analyzer.batch_analyze(request_data["articles"]))
        loop.close()

        return jsonify({
            "success": True,
            "articles_count": len(analyzed),
            "articles": analyzed,
            "timestamp": datetime.now().isoformat()
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/prioritize-articles', methods=['POST'])
def prioritize_articles():
    """
    Prioritize provided articles.

    Request Body:
    {
        "articles": [...],
        "agentbill_api_key": "your-key",
        "top_count": 10
    }

    Returns:
        JSON response with prioritized articles
    """
    try:
        request_data = request.get_json()

        if not request_data or "articles" not in request_data:
            return jsonify({
                "success": False,
                "error": "Missing 'articles' in request body"
            }), 400

        config = create_config_from_request(request_data)

        if not config["agentbill_api_key"]:
            return jsonify({
                "success": False,
                "error": "Missing agentbill_api_key"
            }), 400

        from agentbill import AgentBill
        from prioritizers.article_prioritizer import ArticlePrioritizer

        agentbill = AgentBill.init({
            "api_key": config["agentbill_api_key"],
            "customer_id": config.get("customer_id", "n8n-prioritize"),
            "debug": config.get("debug", True)
        })

        prioritizer = ArticlePrioritizer(agentbill)
        prioritized = prioritizer.prioritize_articles(request_data["articles"])

        top_count = request_data.get("top_count", 10)
        top_articles = prioritizer.get_top_articles(prioritized, top_count)

        return jsonify({
            "success": True,
            "total_articles": len(prioritized),
            "top_articles_count": len(top_articles),
            "top_articles": top_articles,
            "timestamp": datetime.now().isoformat()
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/get-top-posts', methods=['POST'])
def get_top_posts():
    """
    Get top LinkedIn-ready posts.

    Request Body:
    {
        "count": 5,
        (optional API keys and config)
    }

    Returns:
        JSON response with top LinkedIn posts
    """
    try:
        request_data = request.get_json() or {}
        config = create_config_from_request(request_data)

        if not config["agentbill_api_key"] or not config["openai_api_key"]:
            return jsonify({
                "success": False,
                "error": "Missing required API keys"
            }), 400

        count = request_data.get("count", 5)

        # Run pipeline and get top articles
        app_instance = AIHappenings(config)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(app_instance.run_pipeline())
        loop.close()

        if not result["success"]:
            return jsonify(result), 500

        top_posts = result["top_articles"][:count]

        # Format for easy LinkedIn posting
        formatted_posts = []
        for post in top_posts:
            formatted_posts.append({
                "rank": post["rank"],
                "post_text": post["linkedin_post"],
                "article_title": post["title"],
                "article_link": post["link"],
                "source": post["source"],
                "priority_score": post["priority_score"]
            })

        return jsonify({
            "success": True,
            "posts_count": len(formatted_posts),
            "posts": formatted_posts,
            "timestamp": datetime.now().isoformat()
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/get-saved-posts', methods=['GET'])
def get_saved_posts():
    """
    Get the most recent saved posts.

    Query Parameters:
        format: json|text|combined (default: json)

    Returns:
        JSON response with saved posts or file download
    """
    try:
        storage = PostStorage()
        format_type = request.args.get('format', 'json')

        if format_type == 'json':
            latest_file = storage.get_latest_posts('json')
            if not latest_file:
                return jsonify({
                    "success": False,
                    "error": "No saved posts found"
                }), 404

            posts_data = storage.load_posts_from_json(latest_file)
            return jsonify({
                "success": True,
                "data": posts_data
            }), 200

        elif format_type == 'combined':
            latest_file = storage.get_latest_posts('combined')
            if not latest_file:
                return jsonify({
                    "success": False,
                    "error": "No saved posts found"
                }), 404

            return send_file(latest_file, as_attachment=True)

        else:
            return jsonify({
                "success": False,
                "error": f"Invalid format: {format_type}. Use json|text|combined"
            }), 400

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/list-saved-runs', methods=['GET'])
def list_saved_runs():
    """
    List all saved post runs.

    Returns:
        JSON response with list of all saved runs
    """
    try:
        storage = PostStorage()
        runs = storage.list_saved_runs()
        stats = storage.get_storage_stats()

        return jsonify({
            "success": True,
            "runs": runs,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║         AI HAPPENINGS - n8n Webhook Server              ║
    ╠══════════════════════════════════════════════════════════╣
    ║  Server running on: http://localhost:{port}              ║
    ║                                                          ║
    ║  Available Endpoints:                                    ║
    ║  ├─ GET  /health               - Health check           ║
    ║  ├─ POST /run-pipeline         - Run full pipeline      ║
    ║  ├─ POST /scrape-only          - Scrape articles only   ║
    ║  ├─ POST /analyze-articles     - Analyze articles       ║
    ║  ├─ POST /prioritize-articles  - Prioritize articles    ║
    ║  ├─ POST /get-top-posts        - Get LinkedIn posts     ║
    ║  ├─ GET  /get-saved-posts      - Get saved posts        ║
    ║  └─ GET  /list-saved-runs      - List all saved runs    ║
    ║                                                          ║
    ║  n8n Webhook URL:                                        ║
    ║  http://localhost:{port}/run-pipeline                    ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    app.run(host='0.0.0.0', port=port, debug=True)
