"""
AI Happenings - Main Application
Orchestrates scraping, analysis, and prioritization with AgentBill tracking
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv
from agentbill import AgentBill
from scrapers.web_scraper import WebScraper
from analyzers.ai_analyzer import AIAnalyzer
from prioritizers.article_prioritizer import ArticlePrioritizer
from utils.post_storage import PostStorage

# Load environment variables from .env file
load_dotenv()


class AIHappenings:
    """Main application class for AI Happenings."""

    def __init__(self, config: Dict):
        """
        Initialize AI Happenings application.

        Args:
            config: Configuration dictionary with API keys and settings
        """
        self.config = config

        # Initialize AgentBill
        self.agentbill = AgentBill.init({
            "api_key": config["agentbill_api_key"],
            "customer_id": config.get("customer_id", "ai-happenings"),
            "debug": config.get("debug", True)
        })

        # Initialize modules with AgentBill tracking
        self.scraper = WebScraper(self.agentbill)
        self.analyzer = AIAnalyzer(config["openai_api_key"], self.agentbill)
        self.prioritizer = ArticlePrioritizer(self.agentbill)

        # Initialize post storage
        self.storage = PostStorage(output_dir=config.get("output_dir", "outputs"))

    async def run_pipeline(self) -> Dict:
        """
        Run the complete AI Happenings pipeline.

        Returns:
            Dictionary with pipeline results
        """
        pipeline_start = datetime.now()

        # Track pipeline start
        self.agentbill.track_signal(
            event_name="pipeline_started",
            revenue=0,
            data={
                "timestamp": pipeline_start.isoformat(),
                "config": {
                    "customer_id": self.config.get("customer_id"),
                    "debug": self.config.get("debug", False)
                }
            }
        )

        try:
            # Step 1: Scrape articles
            print("\n📡 Step 1: Scraping articles from technology sites...")
            articles = await self.scraper.scrape_all_sources()
            print(f"   ✓ Found {len(articles)} relevant articles")

            if not articles:
                result = {
                    "success": False,
                    "error": "No articles found",
                    "timestamp": pipeline_start.isoformat()
                }

                self.agentbill.track_signal(
                    event_name="pipeline_failed",
                    revenue=0,
                    data=result
                )

                return result

            # Step 2: Extract full content
            print("\n📄 Step 2: Extracting full article content...")
            for i, article in enumerate(articles):
                await self.scraper.extract_full_content(article)
                if (i + 1) % 5 == 0:
                    print(f"   Processed {i + 1}/{len(articles)} articles...")

            # Step 3: Analyze with AI
            print("\n🤖 Step 3: Analyzing articles with AI...")
            analyzed_articles = await self.analyzer.batch_analyze(articles)
            print(f"   ✓ Analyzed {len(analyzed_articles)} articles")

            # Step 4: Prioritize
            print("\n🎯 Step 4: Prioritizing articles...")
            prioritized_articles = self.prioritizer.prioritize_articles(analyzed_articles)
            print(f"   ✓ Prioritized {len(prioritized_articles)} articles")

            # Step 5: Get top articles
            top_articles = self.prioritizer.get_top_articles(prioritized_articles, count=10)
            print(f"\n✨ Top {len(top_articles)} articles selected for LinkedIn posts")

            # Generate summary report
            summary_report = await self.analyzer.generate_summary_report(top_articles)
            priority_report = self.prioritizer.generate_priority_report(prioritized_articles)

            pipeline_end = datetime.now()
            duration = (pipeline_end - pipeline_start).total_seconds()

            # Format posts for output
            formatted_posts = [self._format_article_output(article) for article in top_articles]

            # Save posts to persistent storage
            print("\n💾 Saving LinkedIn posts to storage...")
            storage_result = self.storage.save_posts(
                posts=formatted_posts,
                metadata={
                    "duration_seconds": duration,
                    "articles_scraped": len(articles),
                    "articles_analyzed": len(analyzed_articles),
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
                    "articles_prioritized": len(prioritized_articles),
                    "top_articles_count": len(top_articles)
                },
                "top_articles": formatted_posts,
                "summary_report": summary_report,
                "priority_report": priority_report,
                "storage": storage_result
            }

            # Track pipeline completion
            self.agentbill.track_signal(
                event_name="pipeline_completed",
                revenue=0.10,  # Total pipeline cost
                data={
                    "duration_seconds": duration,
                    "articles_processed": len(articles),
                    "top_articles_count": len(top_articles),
                    "success": True
                }
            )

            return result

        except Exception as e:
            pipeline_end = datetime.now()
            duration = (pipeline_end - pipeline_start).total_seconds()

            result = {
                "success": False,
                "error": str(e),
                "timestamp": pipeline_start.isoformat(),
                "duration_seconds": duration
            }

            # Track pipeline failure
            self.agentbill.track_signal(
                event_name="pipeline_failed",
                revenue=0,
                data={
                    "error": str(e),
                    "duration_seconds": duration
                }
            )

            return result

    def _format_article_output(self, article: Dict) -> Dict:
        """
        Format article for output.

        Args:
            article: Article dictionary

        Returns:
            Formatted article dictionary
        """
        return {
            "rank": article.get("priority_rank", 0),
            "title": article.get("title", ""),
            "source": article.get("source", ""),
            "link": article.get("link", ""),
            "priority_score": round(article.get("priority_score", 0), 2),
            "relevance_score": article.get("analysis", {}).get("relevance_score", 0),
            "linkedin_post": article.get("analysis", {}).get("linkedin_post", ""),
            "scraped_at": article.get("scraped_at", "")
        }

    def get_statistics(self) -> Dict:
        """
        Get application statistics.

        Returns:
            Statistics dictionary
        """
        # This would query AgentBill dashboard or local cache
        return {
            "total_pipelines_run": 0,  # Would come from AgentBill
            "total_articles_processed": 0,
            "total_ai_calls": 0,
            "total_cost": 0.0
        }


async def main():
    """Main entry point for standalone execution."""
    # Load configuration
    config = {
        "agentbill_api_key": os.getenv("AGENTBILL_API_KEY", ""),
        "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
        "customer_id": os.getenv("CUSTOMER_ID", "ai-happenings-demo"),
        "debug": True
    }

    # Validate configuration
    if not config["agentbill_api_key"] or not config["openai_api_key"]:
        print("❌ Error: Missing required API keys")
        print("   Set AGENTBILL_API_KEY and OPENAI_API_KEY environment variables")
        return

    print("=" * 70)
    print("AI HAPPENINGS - Agentic Commerce & AI Marketplace News Tracker")
    print("=" * 70)

    # Initialize and run
    app = AIHappenings(config)
    result = await app.run_pipeline()

    # Display results
    print("\n" + "=" * 70)
    print("PIPELINE RESULTS")
    print("=" * 70)

    if result["success"]:
        print(f"✓ Success!")
        print(f"Duration: {result['duration_seconds']:.2f} seconds")
        print(f"\nMetrics:")
        print(f"  - Articles Scraped: {result['metrics']['articles_scraped']}")
        print(f"  - Articles Analyzed: {result['metrics']['articles_analyzed']}")
        print(f"  - Top Articles: {result['metrics']['top_articles_count']}")

        print(f"\n📊 TOP {len(result['top_articles'])} ARTICLES FOR LINKEDIN:")
        print("-" * 70)

        for article in result['top_articles']:
            print(f"\n{article['rank']}. {article['title']}")
            print(f"   Source: {article['source']} | Score: {article['priority_score']}/100")
            print(f"   Link: {article['link']}")
            print(f"\n   LinkedIn Post:")
            print(f"   {article['linkedin_post'][:200]}...")
            print("-" * 70)

        print(f"\n📈 SUMMARY REPORT:")
        print(result['summary_report'])

    else:
        print(f"❌ Pipeline failed: {result.get('error', 'Unknown error')}")

    print("\n" + "=" * 70)
    print("Check your AgentBill dashboard for detailed analytics!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
