"""
AI Analyzer Module for AI Happenings
Uses OpenAI to analyze and summarize articles for LinkedIn posts
"""

import time
from typing import Dict, List
from openai import OpenAI


class AIAnalyzer:
    """Analyzes and summarizes articles using OpenAI with AgentBill tracking."""

    def __init__(self, openai_api_key: str, agentbill_tracker):
        """
        Initialize AI analyzer with OpenAI and AgentBill.

        Args:
            openai_api_key: OpenAI API key
            agentbill_tracker: AgentBill instance for tracking
        """
        self.agentbill = agentbill_tracker
        self.client = self.agentbill.wrap_openai(OpenAI(api_key=openai_api_key))

    async def analyze_article(self, article: Dict) -> Dict:
        """
        Analyze a single article and create LinkedIn post.

        Args:
            article: Article dictionary with title, content, etc.

        Returns:
            Article with analysis and summary added
        """
        start_time = time.time()

        try:
            # Track analysis start
            self.agentbill.track_signal(
                event_name="article_analysis_started",
                revenue=0,
                data={
                    "article_title": article.get("title", "")[:100],
                    "source": article.get("source", "")
                }
            )

            # Create analysis prompt
            prompt = self._create_analysis_prompt(article)

            # Call OpenAI (automatically tracked by AgentBill)
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert AI and commerce technology analyst who creates engaging LinkedIn posts."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )

            summary = response.choices[0].message.content

            # Extract relevance score from response
            relevance_score = self._extract_relevance_score(summary)

            duration_ms = int((time.time() - start_time) * 1000)
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0

            # Track successful analysis
            self.agentbill.track_signal(
                event_name="article_analysis_completed",
                revenue=0.01,  # Cost per analysis
                data={
                    "article_title": article.get("title", "")[:100],
                    "tokens_used": tokens_used,
                    "duration_ms": duration_ms,
                    "relevance_score": relevance_score,
                    "model": "gpt-4"
                }
            )

            article["analysis"] = {
                "linkedin_post": summary,
                "relevance_score": relevance_score,
                "analyzed_at": time.time(),
                "tokens_used": tokens_used
            }

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)

            # Track analysis error
            self.agentbill.track_signal(
                event_name="article_analysis_failed",
                revenue=0,
                data={
                    "article_title": article.get("title", "")[:100],
                    "error": str(e),
                    "duration_ms": duration_ms
                }
            )

            article["analysis"] = {
                "linkedin_post": "",
                "relevance_score": 0,
                "error": str(e)
            }

        return article

    def _create_analysis_prompt(self, article: Dict) -> str:
        """
        Create analysis prompt for OpenAI.

        Args:
            article: Article dictionary

        Returns:
            Formatted prompt string
        """
        return f"""Analyze this article about AI and commerce technology:

Title: {article.get('title', 'N/A')}
Source: {article.get('source', 'N/A')}
Content: {article.get('content', article.get('excerpt', 'N/A'))[:2000]}

Tasks:
1. Assess relevance to "Agentic Commerce" and "AI Marketplaces" (score 0-10)
2. Create an engaging LinkedIn post (150-200 words) that:
   - Highlights the key innovation or trend
   - Explains why it matters for businesses
   - Includes relevant hashtags (#AgenticCommerce #AIMarketplace #AI)
   - Has a professional yet engaging tone
   - Ends with a thought-provoking question

Format your response as:
RELEVANCE_SCORE: [0-10]
---
[LinkedIn Post Content]
"""

    def _extract_relevance_score(self, summary: str) -> float:
        """
        Extract relevance score from AI response.

        Args:
            summary: AI response string

        Returns:
            Relevance score (0-10)
        """
        try:
            if "RELEVANCE_SCORE:" in summary:
                score_line = summary.split("RELEVANCE_SCORE:")[1].split("\n")[0]
                score = float(score_line.strip())
                return min(max(score, 0), 10)  # Clamp between 0-10
        except:
            pass
        return 5.0  # Default medium relevance

    async def batch_analyze(self, articles: List[Dict]) -> List[Dict]:
        """
        Analyze multiple articles in batch.

        Args:
            articles: List of article dictionaries

        Returns:
            List of analyzed articles
        """
        start_time = time.time()

        self.agentbill.track_signal(
            event_name="batch_analysis_started",
            revenue=0,
            data={
                "num_articles": len(articles)
            }
        )

        analyzed_articles = []
        for article in articles:
            analyzed = await self.analyze_article(article)
            analyzed_articles.append(analyzed)

        duration_ms = int((time.time() - start_time) * 1000)

        self.agentbill.track_signal(
            event_name="batch_analysis_completed",
            revenue=len(articles) * 0.01,  # Total cost
            data={
                "num_articles": len(articles),
                "duration_ms": duration_ms,
                "avg_duration_per_article": duration_ms / len(articles) if articles else 0
            }
        )

        return analyzed_articles

    async def generate_summary_report(self, articles: List[Dict]) -> str:
        """
        Generate an overall summary report of all articles.

        Args:
            articles: List of analyzed articles

        Returns:
            Summary report string
        """
        if not articles:
            return "No articles to summarize."

        try:
            # Create summary prompt
            articles_text = "\n\n".join([
                f"Article {i+1}: {article.get('title', 'N/A')} (Relevance: {article.get('analysis', {}).get('relevance_score', 0)}/10)"
                for i, article in enumerate(articles[:10])  # Top 10
            ])

            prompt = f"""You are analyzing technology trends. Here are the top articles about Agentic Commerce and AI Marketplaces:

{articles_text}

Create a brief executive summary (100-150 words) that:
1. Identifies the top 3 emerging trends
2. Highlights the most significant development
3. Suggests what businesses should watch for

Format as a professional report."""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a technology trend analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300
            )

            summary = response.choices[0].message.content

            self.agentbill.track_signal(
                event_name="summary_report_generated",
                revenue=0.005,
                data={
                    "num_articles_summarized": len(articles),
                    "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else 0
                }
            )

            return summary

        except Exception as e:
            self.agentbill.track_signal(
                event_name="summary_report_failed",
                revenue=0,
                data={"error": str(e)}
            )
            return f"Error generating summary: {str(e)}"
