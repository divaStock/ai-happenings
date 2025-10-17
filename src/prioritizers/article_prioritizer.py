"""
Article Prioritizer Module for AI Happenings
Prioritizes articles based on relevance, recency, and engagement potential
"""

from typing import List, Dict
from datetime import datetime, timedelta
import time


class ArticlePrioritizer:
    """Prioritizes articles using multiple scoring factors."""

    def __init__(self, agentbill_tracker):
        """
        Initialize prioritizer with AgentBill tracking.

        Args:
            agentbill_tracker: AgentBill instance for tracking
        """
        self.agentbill = agentbill_tracker

        # Scoring weights
        self.weights = {
            "relevance": 0.5,      # AI relevance score
            "recency": 0.25,       # How recent the article is
            "source_quality": 0.15, # Quality of source
            "engagement": 0.10     # Potential engagement
        }

        # Source quality scores
        self.source_scores = {
            "TechCrunch": 9.0,
            "VentureBeat AI": 8.5,
            "MIT Technology Review": 10.0,
            "The Verge": 8.0,
            "Wired": 8.5,
            "default": 7.0
        }

    def calculate_priority_score(self, article: Dict) -> float:
        """
        Calculate comprehensive priority score for an article.

        Args:
            article: Article dictionary with analysis

        Returns:
            Priority score (0-100)
        """
        try:
            # Get relevance score from AI analysis
            relevance_score = article.get("analysis", {}).get("relevance_score", 5.0)

            # Calculate recency score
            recency_score = self._calculate_recency_score(article)

            # Get source quality score
            source_score = self.source_scores.get(
                article.get("source", ""),
                self.source_scores["default"]
            )

            # Calculate engagement potential
            engagement_score = self._calculate_engagement_score(article)

            # Weighted sum
            total_score = (
                relevance_score * self.weights["relevance"] * 10 +
                recency_score * self.weights["recency"] * 10 +
                source_score * self.weights["source_quality"] * 10 +
                engagement_score * self.weights["engagement"] * 10
            )

            return min(max(total_score, 0), 100)

        except Exception as e:
            print(f"Error calculating priority score: {e}")
            return 50.0  # Default medium priority

    def _calculate_recency_score(self, article: Dict) -> float:
        """
        Calculate score based on article recency.

        Args:
            article: Article dictionary

        Returns:
            Recency score (0-10)
        """
        try:
            scraped_at = article.get("scraped_at")
            if not scraped_at:
                return 5.0

            scraped_time = datetime.fromisoformat(scraped_at.replace('Z', '+00:00'))
            age_hours = (datetime.now().astimezone() - scraped_time).total_seconds() / 3600

            # Scoring: newer is better
            if age_hours < 6:
                return 10.0
            elif age_hours < 24:
                return 8.0
            elif age_hours < 48:
                return 6.0
            elif age_hours < 72:
                return 4.0
            else:
                return 2.0

        except:
            return 5.0

    def _calculate_engagement_score(self, article: Dict) -> float:
        """
        Calculate potential engagement score based on content characteristics.

        Args:
            article: Article dictionary

        Returns:
            Engagement score (0-10)
        """
        score = 5.0  # Base score

        title = article.get("title", "").lower()
        linkedin_post = article.get("analysis", {}).get("linkedin_post", "").lower()

        # Positive indicators
        engagement_keywords = [
            "breakthrough", "revolutionary", "game-changing",
            "announces", "launches", "unveils",
            "first", "new", "innovative",
            "record", "major", "significant"
        ]

        for keyword in engagement_keywords:
            if keyword in title or keyword in linkedin_post:
                score += 0.5

        # Check for questions (good for engagement)
        if "?" in linkedin_post:
            score += 1.0

        # Check for hashtags
        if "#" in linkedin_post:
            score += 0.5

        return min(score, 10.0)

    def prioritize_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Prioritize and rank articles.

        Args:
            articles: List of analyzed articles

        Returns:
            Sorted list of articles with priority scores
        """
        start_time = time.time()

        self.agentbill.track_signal(
            event_name="prioritization_started",
            revenue=0,
            data={
                "num_articles": len(articles)
            }
        )

        # Calculate priority score for each article
        for article in articles:
            priority_score = self.calculate_priority_score(article)
            article["priority_score"] = priority_score
            article["priority_rank"] = 0  # Will be set after sorting

        # Sort by priority score (highest first)
        sorted_articles = sorted(
            articles,
            key=lambda x: x.get("priority_score", 0),
            reverse=True
        )

        # Assign ranks
        for i, article in enumerate(sorted_articles, 1):
            article["priority_rank"] = i

        duration_ms = int((time.time() - start_time) * 1000)

        # Track successful prioritization
        self.agentbill.track_signal(
            event_name="prioritization_completed",
            revenue=0,
            data={
                "num_articles": len(articles),
                "duration_ms": duration_ms,
                "top_score": sorted_articles[0].get("priority_score", 0) if sorted_articles else 0
            }
        )

        return sorted_articles

    def get_top_articles(self, articles: List[Dict], count: int = 5) -> List[Dict]:
        """
        Get top N articles by priority.

        Args:
            articles: List of prioritized articles
            count: Number of top articles to return

        Returns:
            List of top articles
        """
        self.agentbill.track_signal(
            event_name="top_articles_selected",
            revenue=0,
            data={
                "num_selected": min(count, len(articles)),
                "total_articles": len(articles)
            }
        )

        return articles[:count]

    def categorize_by_priority(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Categorize articles into priority tiers.

        Args:
            articles: List of articles with priority scores

        Returns:
            Dictionary with priority categories
        """
        categorized = {
            "high_priority": [],      # Score >= 80
            "medium_priority": [],    # Score 60-79
            "low_priority": [],       # Score < 60
        }

        for article in articles:
            score = article.get("priority_score", 0)

            if score >= 80:
                categorized["high_priority"].append(article)
            elif score >= 60:
                categorized["medium_priority"].append(article)
            else:
                categorized["low_priority"].append(article)

        self.agentbill.track_signal(
            event_name="articles_categorized",
            revenue=0,
            data={
                "high_priority": len(categorized["high_priority"]),
                "medium_priority": len(categorized["medium_priority"]),
                "low_priority": len(categorized["low_priority"])
            }
        )

        return categorized

    def generate_priority_report(self, articles: List[Dict]) -> str:
        """
        Generate a priority report summary.

        Args:
            articles: List of prioritized articles

        Returns:
            Priority report string
        """
        if not articles:
            return "No articles to report."

        categories = self.categorize_by_priority(articles)

        report = f"""
Priority Report - AI Happenings
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
================================

Total Articles: {len(articles)}

High Priority (Score >= 80): {len(categories['high_priority'])}
Medium Priority (Score 60-79): {len(categories['medium_priority'])}
Low Priority (Score < 60): {len(categories['low_priority'])}

TOP 5 ARTICLES:
"""

        for i, article in enumerate(articles[:5], 1):
            report += f"""
{i}. {article.get('title', 'N/A')[:80]}
   Source: {article.get('source', 'N/A')}
   Priority Score: {article.get('priority_score', 0):.1f}/100
   Relevance: {article.get('analysis', {}).get('relevance_score', 0):.1f}/10
   Link: {article.get('link', 'N/A')}
"""

        return report
