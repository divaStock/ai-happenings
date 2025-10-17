"""
AI Happenings with Action Balance Tracking
Enhanced version with comprehensive action balance monitoring
"""

import asyncio
import os
from datetime import datetime
from typing import Dict
from dotenv import load_dotenv
from agentbill import AgentBill
from scrapers.web_scraper import WebScraper
from analyzers.ai_analyzer import AIAnalyzer
from prioritizers.article_prioritizer import ArticlePrioritizer
from utils.action_tracker import ActionBalanceTracker, UsageLimiter
from utils.post_storage import PostStorage

# Load environment variables from .env file
load_dotenv()


class AIHappeningsWithBalance:
    """Enhanced AI Happenings with action balance tracking."""

    def __init__(self, config: Dict):
        """
        Initialize AI Happenings with balance tracking.

        Args:
            config: Configuration dictionary
        """
        self.config = config

        # Initialize AgentBill
        self.agentbill = AgentBill.init({
            "api_key": config["agentbill_api_key"],
            "customer_id": config.get("customer_id", "ai-happenings"),
            "debug": config.get("debug", True)
        })

        # Initialize action balance tracker
        self.action_tracker = ActionBalanceTracker(self.agentbill)

        # Initialize usage limiter
        daily_limit = config.get("daily_credit_limit", 1000)
        self.usage_limiter = UsageLimiter(self.agentbill, daily_limit)

        # Initialize modules
        self.scraper = WebScraper(self.agentbill)
        self.analyzer = AIAnalyzer(config["openai_api_key"], self.agentbill)
        self.prioritizer = ArticlePrioritizer(self.agentbill)

        # Initialize post storage
        self.storage = PostStorage(output_dir=config.get("output_dir", "outputs"))

    async def run_pipeline_with_balance(self) -> Dict:
        """
        Run pipeline with action balance tracking.

        Returns:
            Pipeline results with balance information
        """
        pipeline_start = datetime.now()

        print("\n" + "="*70)
        print("AI HAPPENINGS - Action Balance Tracking Enabled")
        print("="*70)

        # Track pipeline start action
        self.action_tracker.track_action("pipeline_start", {
            "customer_id": self.config.get("customer_id")
        })

        # Estimate pipeline cost
        planned_actions = {
            "scrape_source": 3,  # 3 sources
            "analyze_article": 15,  # Estimated 15 articles
            "prioritize_batch": 1
        }

        estimation = self.action_tracker.estimate_action_cost(planned_actions)
        print(f"\n📊 Estimated Cost: {estimation['total_estimated_cost']} credits")

        # Check if within limits
        if not self.usage_limiter.check_limit(estimation['total_estimated_cost']):
            result = {
                "success": False,
                "error": "Daily credit limit would be exceeded",
                "remaining_balance": self.usage_limiter.get_remaining_balance(),
                "required_credits": estimation['total_estimated_cost']
            }

            self.agentbill.track_signal(
                event_name="pipeline_blocked_by_limit",
                revenue=0,
                data=result
            )

            return result

        print(f"✓ Within daily limit. Remaining: {self.usage_limiter.get_remaining_balance()} credits")

        try:
            # Step 1: Scraping
            print("\n📡 Step 1: Scraping articles...")
            articles = await self.scraper.scrape_all_sources()

            for _ in range(len(self.scraper.sources)):
                self.action_tracker.track_action("scrape_source")
                self.usage_limiter.consume_credits(1)

            print(f"   ✓ Found {len(articles)} articles")
            print(f"   💰 Credits used: {len(self.scraper.sources)}")

            if not articles:
                return self._create_result(False, "No articles found")

            # Step 2: Content extraction
            print("\n📄 Step 2: Extracting content...")
            for article in articles:
                await self.scraper.extract_full_content(article)
                self.action_tracker.track_action("extract_content", {
                    "article_title": article.get("title", "")[:50]
                })
                self.usage_limiter.consume_credits(0.5)

            print(f"   ✓ Extracted {len(articles)} articles")
            print(f"   💰 Credits used: {len(articles) * 0.5}")

            # Step 3: AI Analysis
            print("\n🤖 Step 3: Analyzing with AI...")

            # Check balance before expensive operation
            analysis_cost = len(articles) * 10
            if not self.usage_limiter.check_limit(analysis_cost):
                print(f"   ⚠️  Insufficient credits. Limiting to available balance...")
                max_articles = int(self.usage_limiter.get_remaining_balance() / 10)
                articles = articles[:max_articles]
                print(f"   → Analyzing only {max_articles} articles")

            analyzed_articles = await self.analyzer.batch_analyze(articles)

            for article in analyzed_articles:
                self.action_tracker.track_action("analyze_article", {
                    "model": "gpt-4",
                    "tokens": article.get("analysis", {}).get("tokens_used", 0)
                })
                self.usage_limiter.consume_credits(10)

            print(f"   ✓ Analyzed {len(analyzed_articles)} articles")
            print(f"   💰 Credits used: {len(analyzed_articles) * 10}")

            # Step 4: Prioritization
            print("\n🎯 Step 4: Prioritizing...")
            prioritized = self.prioritizer.prioritize_articles(analyzed_articles)

            self.action_tracker.track_action("prioritize_batch", {
                "article_count": len(prioritized)
            })
            self.usage_limiter.consume_credits(2)

            print(f"   ✓ Prioritized {len(prioritized)} articles")
            print(f"   💰 Credits used: 2")

            # Step 5: Summary generation
            print("\n📝 Step 5: Generating summary...")
            top_articles = self.prioritizer.get_top_articles(prioritized, 10)
            summary = await self.analyzer.generate_summary_report(top_articles)

            self.action_tracker.track_action("generate_summary")
            self.usage_limiter.consume_credits(15)

            print(f"   ✓ Summary generated")
            print(f"   💰 Credits used: 15")

            # Generate balance report
            print("\n" + "="*70)
            print(self.action_tracker.get_balance_report())

            # Create result
            pipeline_end = datetime.now()
            duration = (pipeline_end - pipeline_start).total_seconds()

            # Format posts for output
            formatted_posts = [self._format_article(a) for a in top_articles]

            # Save posts to persistent storage
            print("\n💾 Step 6: Saving LinkedIn posts to storage...")
            storage_result = self.storage.save_posts(
                posts=formatted_posts,
                metadata={
                    "duration_seconds": duration,
                    "articles_scraped": len(articles),
                    "articles_analyzed": len(analyzed_articles),
                    "total_cost": self.action_tracker.get_session_cost(),
                    "remaining_balance": self.usage_limiter.get_remaining_balance(),
                    "customer_id": self.config.get("customer_id")
                }
            )
            print(f"   ✓ Saved to JSON: {storage_result['json_file']}")
            print(f"   ✓ Saved to combined text: {storage_result['combined_text_file']}")
            print(f"   ✓ Saved {len(storage_result['text_files'])} individual text files")

            result = {
                "success": True,
                "timestamp": pipeline_start.isoformat(),
                "duration_seconds": duration,
                "metrics": {
                    "articles_scraped": len(articles),
                    "articles_analyzed": len(analyzed_articles),
                    "top_articles_count": len(top_articles)
                },
                "action_balance": {
                    "total_actions": len(self.action_tracker.session_actions),
                    "total_cost": self.action_tracker.get_session_cost(),
                    "remaining_daily_balance": self.usage_limiter.get_remaining_balance(),
                    "breakdown": self.action_tracker.get_action_breakdown()
                },
                "top_articles": formatted_posts,
                "summary_report": summary,
                "storage": storage_result
            }

            # Track completion
            self.agentbill.track_signal(
                event_name="pipeline_completed_with_balance",
                revenue=0.10,
                data={
                    "duration_seconds": duration,
                    "total_cost": self.action_tracker.get_session_cost(),
                    "articles_processed": len(articles)
                }
            )

            return result

        except Exception as e:
            return self._create_result(False, str(e))

    def _format_article(self, article: Dict) -> Dict:
        """Format article for output."""
        return {
            "rank": article.get("priority_rank", 0),
            "title": article.get("title", ""),
            "source": article.get("source", ""),
            "link": article.get("link", ""),
            "priority_score": round(article.get("priority_score", 0), 2),
            "relevance_score": article.get("analysis", {}).get("relevance_score", 0),
            "linkedin_post": article.get("analysis", {}).get("linkedin_post", "")
        }

    def _create_result(self, success: bool, error: str = None) -> Dict:
        """Create result dictionary."""
        result = {
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "action_balance": {
                "total_cost": self.action_tracker.get_session_cost(),
                "remaining_balance": self.usage_limiter.get_remaining_balance()
            }
        }

        if error:
            result["error"] = error

        return result


async def main():
    """Main entry point with balance tracking."""
    config = {
        "agentbill_api_key": os.getenv("AGENTBILL_API_KEY", ""),
        "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
        "customer_id": os.getenv("CUSTOMER_ID", "ai-happenings-balanced"),
        "daily_credit_limit": float(os.getenv("DAILY_CREDIT_LIMIT", "1000")),
        "debug": True
    }

    if not config["agentbill_api_key"] or not config["openai_api_key"]:
        print("❌ Error: Missing required API keys")
        return

    app = AIHappeningsWithBalance(config)
    result = await app.run_pipeline_with_balance()

    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)

    if result["success"]:
        print(f"✓ Pipeline completed successfully!")
        print(f"\n💰 ACTION BALANCE SUMMARY:")
        print(f"   Total Credits Used: {result['action_balance']['total_cost']}")
        print(f"   Remaining Balance: {result['action_balance']['remaining_daily_balance']}")
        print(f"\n📊 Top {len(result.get('top_articles', []))} Articles Ready!")
    else:
        print(f"❌ Pipeline failed: {result.get('error')}")
        print(f"💰 Credits Used: {result['action_balance']['total_cost']}")

    print("\n" + "="*70)


if __name__ == "__main__":
    asyncio.run(main())
