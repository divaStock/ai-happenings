"""
Web Scraper Module for AI Happenings
Scrapes technology news sites for content related to Agentic Commerce and AI Marketplaces
"""

import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
import time


class WebScraper:
    """Scrapes technology news sites for relevant articles."""

    def __init__(self, agentbill_tracker):
        """
        Initialize web scraper with AgentBill tracking.

        Args:
            agentbill_tracker: AgentBill instance for tracking operations
        """
        self.agentbill = agentbill_tracker
        self.sources = [
            {
                "name": "TechCrunch",
                "url": "https://techcrunch.com/category/artificial-intelligence/",
                "selector": "article"
            },
            {
                "name": "VentureBeat AI",
                "url": "https://venturebeat.com/category/ai/",
                "selector": "article"
            },
            {
                "name": "MIT Technology Review",
                "url": "https://www.technologyreview.com/topic/artificial-intelligence/",
                "selector": "article"
            },
            {
                "name": "The Verge AI",
                "url": "https://www.theverge.com/ai-artificial-intelligence",
                "selector": "article"
            },
            {
                "name": "Ars Technica AI",
                "url": "https://arstechnica.com/ai/",
                "selector": "article"
            },
            {
                "name": "Wired AI",
                "url": "https://www.wired.com/tag/artificial-intelligence/",
                "selector": "article"
            },
            {
                "name": "AI News",
                "url": "https://www.artificialintelligence-news.com/",
                "selector": "article"
            },
            {
                "name": "Analytics India Magazine",
                "url": "https://analyticsindiamag.com/category/artificial-intelligence/",
                "selector": "article"
            }
        ]
        self.keywords = [
            "agentic commerce",
            "ai marketplace",
            "ai agents",
            "autonomous agents",
            "commerce automation",
            "ai shopping",
            "intelligent commerce",
            "agent economy"
        ]

    async def scrape_source(self, source: Dict) -> List[Dict]:
        """
        Scrape a single news source.

        Args:
            source: Dictionary containing source information

        Returns:
            List of article dictionaries
        """
        start_time = time.time()
        articles = []

        try:
            # Track scraping event
            self.agentbill.track_signal(
                event_name="scraping_started",
                revenue=0,
                data={
                    "source": source["name"],
                    "url": source["url"],
                    "timestamp": datetime.now().isoformat()
                }
            )

            # Add custom headers to avoid bot detection and rate limiting
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }

            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                # Add small delay between requests to avoid rate limiting
                await asyncio.sleep(1)
                response = await client.get(source["url"], headers=headers)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')
                article_elements = soup.select(source["selector"])

                for element in article_elements[:20]:  # Limit to 20 articles per source
                    article = self._parse_article(element, source["name"])
                    if article and self._is_relevant(article):
                        articles.append(article)

            duration_ms = int((time.time() - start_time) * 1000)

            # Track successful scraping
            self.agentbill.track_signal(
                event_name="scraping_completed",
                revenue=0,
                data={
                    "source": source["name"],
                    "articles_found": len(articles),
                    "duration_ms": duration_ms,
                    "success": True
                }
            )

        except httpx.HTTPStatusError as e:
            duration_ms = int((time.time() - start_time) * 1000)

            # Track scraping error
            self.agentbill.track_signal(
                event_name="scraping_failed",
                revenue=0,
                data={
                    "source": source["name"],
                    "error": str(e),
                    "status_code": e.response.status_code if hasattr(e, 'response') else None,
                    "duration_ms": duration_ms
                }
            )
            print(f"⚠️  Error scraping {source['name']}: HTTP {e.response.status_code if hasattr(e, 'response') else 'error'} - {e}")
            print(f"   Continuing with other sources...")

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)

            # Track scraping error
            self.agentbill.track_signal(
                event_name="scraping_failed",
                revenue=0,
                data={
                    "source": source["name"],
                    "error": str(e),
                    "duration_ms": duration_ms
                }
            )
            print(f"⚠️  Error scraping {source['name']}: {e}")
            print(f"   Continuing with other sources...")

        return articles

    def _parse_article(self, element, source_name: str) -> Optional[Dict]:
        """
        Parse article element into structured data.

        Args:
            element: BeautifulSoup element
            source_name: Name of the source

        Returns:
            Dictionary containing article data
        """
        try:
            title_elem = element.find(['h1', 'h2', 'h3', 'a'])
            title = title_elem.get_text(strip=True) if title_elem else None

            link_elem = element.find('a', href=True)
            link = link_elem['href'] if link_elem else None

            # Make link absolute if relative
            if link and not link.startswith('http'):
                link = f"https://{source_name.lower().replace(' ', '')}.com{link}"

            excerpt_elem = element.find(['p', 'div'], class_=lambda x: x and ('excerpt' in str(x).lower() or 'description' in str(x).lower()))
            excerpt = excerpt_elem.get_text(strip=True)[:500] if excerpt_elem else ""

            if not title or not link:
                return None

            return {
                "title": title,
                "link": link,
                "excerpt": excerpt,
                "source": source_name,
                "scraped_at": datetime.now().isoformat(),
                "content": ""  # Will be filled by content extraction
            }

        except Exception as e:
            print(f"Error parsing article: {e}")
            return None

    def _is_relevant(self, article: Dict) -> bool:
        """
        Check if article is relevant based on keywords.

        Args:
            article: Article dictionary

        Returns:
            True if relevant, False otherwise
        """
        text = (article.get("title", "") + " " + article.get("excerpt", "")).lower()
        return any(keyword.lower() in text for keyword in self.keywords)

    async def scrape_all_sources(self) -> List[Dict]:
        """
        Scrape all configured sources concurrently.

        Returns:
            Combined list of articles from all sources
        """
        start_time = time.time()

        # Track overall scraping operation
        self.agentbill.track_signal(
            event_name="batch_scraping_started",
            revenue=0,
            data={
                "num_sources": len(self.sources),
                "sources": [s["name"] for s in self.sources]
            }
        )

        tasks = [self.scrape_source(source) for source in self.sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_articles = []
        successful_sources = 0
        failed_sources = 0

        for i, result in enumerate(results):
            if isinstance(result, list):
                all_articles.extend(result)
                successful_sources += 1
            else:
                failed_sources += 1

        print(f"\n📊 Scraping Summary:")
        print(f"   ✓ Successful sources: {successful_sources}/{len(self.sources)}")
        if failed_sources > 0:
            print(f"   ⚠️  Failed sources: {failed_sources}/{len(self.sources)}")
        print(f"   📰 Total articles found: {len(all_articles)}")

        duration_ms = int((time.time() - start_time) * 1000)

        # Track batch completion
        self.agentbill.track_signal(
            event_name="batch_scraping_completed",
            revenue=0,
            data={
                "total_articles": len(all_articles),
                "duration_ms": duration_ms,
                "sources_scraped": len(self.sources)
            }
        )

        return all_articles

    async def extract_full_content(self, article: Dict) -> Dict:
        """
        Extract full article content from URL.

        Args:
            article: Article dictionary with 'link'

        Returns:
            Article dictionary with 'content' field populated
        """
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(article["link"])
                soup = BeautifulSoup(response.text, 'html.parser')

                # Remove unwanted elements
                for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                    element.decompose()

                # Try to find main content
                content_div = soup.find(['article', 'main', 'div'], class_=lambda x: x and ('content' in str(x).lower() or 'article' in str(x).lower()))

                if content_div:
                    paragraphs = content_div.find_all('p')
                    content = ' '.join([p.get_text(strip=True) for p in paragraphs])
                else:
                    paragraphs = soup.find_all('p')
                    content = ' '.join([p.get_text(strip=True) for p in paragraphs[:10]])

                article["content"] = content[:5000]  # Limit content size

        except Exception as e:
            print(f"Error extracting content from {article['link']}: {e}")
            article["content"] = article.get("excerpt", "")

        return article
