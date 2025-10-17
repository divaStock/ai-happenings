"""
Production-Grade Web Scraper Module for AI Happenings
Scrapes technology news sites with configurable research topics and RSS support
"""

import asyncio
import httpx
import feedparser
import yaml
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Set
from datetime import datetime
from pathlib import Path
import time
import hashlib


class WebScraper:
    """Production-grade scraper with configurable research topics and RSS support."""

    def __init__(self, agentbill_tracker, config_path: str = None):
        """
        Initialize web scraper with AgentBill tracking and config.

        Args:
            agentbill_tracker: AgentBill instance for tracking operations
            config_path: Path to config file (defaults to config/scraper_config.yaml)
        """
        self.agentbill = agentbill_tracker
        self.config = self._load_config(config_path)
        self.seen_urls: Set[str] = set()  # For deduplication

        # Extract config sections
        self.keywords = self._load_keywords()
        self.sources = self._load_sources()
        self.settings = self.config.get('scraping_settings', {})
        self.scoring_weights = self.config.get('scoring_weights', {})

        print(f"🔧 Scraper initialized with {len(self.sources)} sources")
        print(f"📋 Research Topic: {self.config['research_topics']['primary_topic']}")
        print(f"🔍 Total keywords: {sum(len(v) for v in self.keywords.values())}")

    def _load_config(self, config_path: str = None) -> Dict:
        """Load scraper configuration from YAML file."""
        if config_path is None:
            # Default to config/scraper_config.yaml relative to project root
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "scraper_config.yaml"

        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                print(f"✅ Loaded config from: {config_path}")
                return config
        except FileNotFoundError:
            print(f"⚠️  Config file not found: {config_path}")
            print("   Using default configuration...")
            return self._get_default_config()
        except Exception as e:
            print(f"⚠️  Error loading config: {e}")
            print("   Using default configuration...")
            return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """Return default configuration if config file not found."""
        return {
            'research_topics': {
                'primary_topic': 'AI and Technology',
                'primary_keywords': ['ai', 'artificial intelligence', 'machine learning'],
                'secondary_keywords': [],
                'tertiary_keywords': [],
                'technology_keywords': [],
                'business_keywords': []
            },
            'news_sources': {
                'tech_sites': [
                    {'name': 'TechCrunch', 'url': 'https://techcrunch.com/category/artificial-intelligence/',
                     'type': 'web', 'selector': 'article', 'priority': 'high'}
                ],
                'ai_sites': []
            },
            'scraping_settings': {
                'timeout': 30,
                'delay_between_requests': 1.5,
                'max_retries': 3,
                'max_articles_per_source': 30,
                'min_relevance_score': 0.3
            },
            'scoring_weights': {
                'primary_keyword': 10.0,
                'secondary_keyword': 5.0,
                'tertiary_keyword': 2.0,
                'title_multiplier': 2.0
            }
        }

    def _load_keywords(self) -> Dict[str, List[str]]:
        """Extract keywords from config."""
        topics = self.config.get('research_topics', {})
        return {
            'primary': [k.lower() for k in topics.get('primary_keywords', [])],
            'secondary': [k.lower() for k in topics.get('secondary_keywords', [])],
            'tertiary': [k.lower() for k in topics.get('tertiary_keywords', [])],
            'technology': [k.lower() for k in topics.get('technology_keywords', [])],
            'business': [k.lower() for k in topics.get('business_keywords', [])]
        }

    def _load_sources(self) -> List[Dict]:
        """Extract and flatten sources from config."""
        sources = []
        news_sources = self.config.get('news_sources', {})

        for category in news_sources.values():
            if isinstance(category, list):
                sources.extend(category)

        return sources

    async def scrape_source(self, source: Dict) -> List[Dict]:
        """
        Scrape a single news source with retry logic.

        Args:
            source: Dictionary containing source information

        Returns:
            List of article dictionaries
        """
        max_retries = self.settings.get('max_retries', 3)
        retry_delay = self.settings.get('retry_delay', 5)

        for attempt in range(max_retries):
            try:
                if source.get('type') == 'rss':
                    return await self._scrape_rss(source)
                else:
                    return await self._scrape_web(source)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:  # Rate limited
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (attempt + 1)
                        print(f"   🔄 Rate limited, retrying {source['name']} in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        continue
                raise
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"   🔄 Error, retrying {source['name']}... (Attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(retry_delay)
                    continue
                raise

        return []

    async def _scrape_web(self, source: Dict) -> List[Dict]:
        """Scrape a web page source."""
        start_time = time.time()
        articles = []

        try:
            self.agentbill.track_signal(
                event_name="scraping_started",
                revenue=0,
                data={
                    "source": source["name"],
                    "url": source["url"],
                    "type": "web",
                    "timestamp": datetime.now().isoformat()
                }
            )

            headers = {
                "User-Agent": self.settings.get('user_agent', 'Mozilla/5.0'),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": self.settings.get('accept_language', 'en-US,en;q=0.9'),
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive"
            }

            timeout = self.settings.get('timeout', 30)
            delay = self.settings.get('delay_between_requests', 1.5)

            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                await asyncio.sleep(delay)
                response = await client.get(source["url"], headers=headers)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')
                article_elements = soup.select(source["selector"])

                max_articles = self.settings.get('max_articles_per_source', 30)

                for element in article_elements[:max_articles]:
                    article = self._parse_article(element, source["name"])
                    if article and self._is_new_article(article):
                        relevance_score = self._calculate_relevance_score(article)
                        article['relevance_score'] = relevance_score

                        min_score = self.settings.get('min_relevance_score', 0.3)
                        if relevance_score >= min_score:
                            articles.append(article)
                            self.seen_urls.add(article['link'])

            duration_ms = int((time.time() - start_time) * 1000)

            self.agentbill.track_signal(
                event_name="scraping_completed",
                revenue=0,
                data={
                    "source": source["name"],
                    "articles_found": len(articles),
                    "duration_ms": duration_ms,
                    "type": "web",
                    "success": True
                }
            )

        except httpx.HTTPStatusError as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self.agentbill.track_signal(
                event_name="scraping_failed",
                revenue=0,
                data={
                    "source": source["name"],
                    "error": str(e),
                    "status_code": e.response.status_code if hasattr(e, 'response') else None,
                    "duration_ms": duration_ms,
                    "type": "web"
                }
            )
            print(f"⚠️  Error scraping {source['name']}: HTTP {e.response.status_code if hasattr(e, 'response') else 'error'}")
            print(f"   Continuing with other sources...")

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self.agentbill.track_signal(
                event_name="scraping_failed",
                revenue=0,
                data={
                    "source": source["name"],
                    "error": str(e),
                    "duration_ms": duration_ms,
                    "type": "web"
                }
            )
            print(f"⚠️  Error scraping {source['name']}: {e}")
            print(f"   Continuing with other sources...")

        return articles

    async def _scrape_rss(self, source: Dict) -> List[Dict]:
        """Scrape an RSS feed source."""
        start_time = time.time()
        articles = []

        try:
            self.agentbill.track_signal(
                event_name="scraping_started",
                revenue=0,
                data={
                    "source": source["name"],
                    "url": source["url"],
                    "type": "rss",
                    "timestamp": datetime.now().isoformat()
                }
            )

            # Fetch RSS feed
            feed = feedparser.parse(source["url"])

            max_items = self.settings.get('rss_max_items', 50)

            for entry in feed.entries[:max_items]:
                article = {
                    "title": entry.get('title', ''),
                    "link": entry.get('link', ''),
                    "excerpt": entry.get('summary', '')[:500],
                    "source": source["name"],
                    "scraped_at": datetime.now().isoformat(),
                    "content": "",
                    "published": entry.get('published', '')
                }

                if article['link'] and self._is_new_article(article):
                    relevance_score = self._calculate_relevance_score(article)
                    article['relevance_score'] = relevance_score

                    min_score = self.settings.get('min_relevance_score', 0.3)
                    if relevance_score >= min_score:
                        articles.append(article)
                        self.seen_urls.add(article['link'])

            duration_ms = int((time.time() - start_time) * 1000)

            self.agentbill.track_signal(
                event_name="scraping_completed",
                revenue=0,
                data={
                    "source": source["name"],
                    "articles_found": len(articles),
                    "duration_ms": duration_ms,
                    "type": "rss",
                    "success": True
                }
            )

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self.agentbill.track_signal(
                event_name="scraping_failed",
                revenue=0,
                data={
                    "source": source["name"],
                    "error": str(e),
                    "duration_ms": duration_ms,
                    "type": "rss"
                }
            )
            print(f"⚠️  Error scraping RSS {source['name']}: {e}")
            print(f"   Continuing with other sources...")

        return articles

    def _parse_article(self, element, source_name: str) -> Optional[Dict]:
        """Parse article element into structured data."""
        try:
            title_elem = element.find(['h1', 'h2', 'h3', 'a'])
            title = title_elem.get_text(strip=True) if title_elem else None

            link_elem = element.find('a', href=True)
            link = link_elem['href'] if link_elem else None

            # Make link absolute if relative
            if link and not link.startswith('http'):
                base_domain = source_name.lower().replace(' ', '').replace('ai', '').replace('rss', '')
                link = f"https://{base_domain}.com{link}"

            excerpt_elem = element.find(['p', 'div'], class_=lambda x: x and ('excerpt' in str(x).lower() or 'description' in str(x).lower()))
            excerpt = excerpt_elem.get_text(strip=True)[:500] if excerpt_elem else ""

            min_length = self.settings.get('min_article_length', 100)
            if not title or not link or len(title) < 10:
                return None

            return {
                "title": title,
                "link": link,
                "excerpt": excerpt,
                "source": source_name,
                "scraped_at": datetime.now().isoformat(),
                "content": ""
            }

        except Exception as e:
            return None

    def _is_new_article(self, article: Dict) -> bool:
        """Check if article hasn't been seen before."""
        if not self.settings.get('deduplicate', True):
            return True
        return article['link'] not in self.seen_urls

    def _calculate_relevance_score(self, article: Dict) -> float:
        """
        Calculate relevance score based on keyword matches.

        Returns:
            Float between 0.0 and 1.0
        """
        title = article.get('title', '').lower()
        excerpt = article.get('excerpt', '').lower()

        score = 0.0
        matches = 0
        title_multiplier = self.scoring_weights.get('title_multiplier', 2.0)

        # Check each keyword category
        for category, keywords in self.keywords.items():
            if not keywords:
                continue

            weight_key = f"{category}_keyword"
            weight = self.scoring_weights.get(weight_key, 1.0)

            for keyword in keywords:
                # Check title (worth more)
                if keyword in title:
                    score += weight * title_multiplier
                    matches += 1
                # Check excerpt
                elif keyword in excerpt:
                    score += weight
                    matches += 1

        # Normalize score to 0-1 range
        # Use a logarithmic scale to reward any matches
        if matches > 0:
            # Score is now between 0-1, with diminishing returns for more matches
            normalized_score = min(score / 50.0, 1.0)  # 50 is a reasonable threshold for high relevance
        else:
            normalized_score = 0.0

        return round(normalized_score, 3)

    async def scrape_all_sources(self) -> List[Dict]:
        """
        Scrape all configured sources concurrently.

        Returns:
            Combined list of articles from all sources
        """
        start_time = time.time()

        self.agentbill.track_signal(
            event_name="batch_scraping_started",
            revenue=0,
            data={
                "num_sources": len(self.sources),
                "sources": [s["name"] for s in self.sources],
                "research_topic": self.config['research_topics']['primary_topic']
            }
        )

        tasks = [self.scrape_source(source) for source in self.sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_articles = []
        successful_sources = 0
        failed_sources = 0
        articles_by_source = {}

        for i, result in enumerate(results):
            source_name = self.sources[i]['name']
            if isinstance(result, list):
                all_articles.extend(result)
                successful_sources += 1
                articles_by_source[source_name] = len(result)
            else:
                failed_sources += 1
                articles_by_source[source_name] = 0

        # Sort by relevance if configured
        if self.config.get('output_settings', {}).get('sort_by_relevance', True):
            all_articles.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

        # Limit output if configured
        max_output = self.config.get('output_settings', {}).get('max_articles_output', 50)
        all_articles = all_articles[:max_output]

        duration_ms = int((time.time() - start_time) * 1000)

        print(f"\n📊 Scraping Summary:")
        print(f"   ✓ Successful sources: {successful_sources}/{len(self.sources)}")
        if failed_sources > 0:
            print(f"   ⚠️  Failed sources: {failed_sources}/{len(self.sources)}")
        print(f"   📰 Total articles found: {len(all_articles)}")
        if all_articles:
            avg_relevance = sum(a.get('relevance_score', 0) for a in all_articles) / len(all_articles)
            print(f"   🎯 Average relevance: {avg_relevance:.2f}")
            print(f"   🏆 Top relevance: {max(a.get('relevance_score', 0) for a in all_articles):.2f}")

        # Show articles per source
        print(f"\n   Articles by source:")
        for source, count in articles_by_source.items():
            if count > 0:
                print(f"   • {source}: {count}")

        self.agentbill.track_signal(
            event_name="batch_scraping_completed",
            revenue=0,
            data={
                "total_articles": len(all_articles),
                "duration_ms": duration_ms,
                "sources_scraped": len(self.sources),
                "successful_sources": successful_sources,
                "failed_sources": failed_sources,
                "avg_relevance_score": sum(a.get('relevance_score', 0) for a in all_articles) / len(all_articles) if all_articles else 0
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
            timeout = self.settings.get('timeout', 30)
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                response = await client.get(article["link"])
                soup = BeautifulSoup(response.text, 'html.parser')

                # Remove unwanted elements
                for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
                    element.decompose()

                # Try to find main content
                content_div = soup.find(['article', 'main', 'div'], class_=lambda x: x and ('content' in str(x).lower() or 'article' in str(x).lower()))

                if content_div:
                    paragraphs = content_div.find_all('p')
                    content = ' '.join([p.get_text(strip=True) for p in paragraphs])
                else:
                    paragraphs = soup.find_all('p')
                    content = ' '.join([p.get_text(strip=True) for p in paragraphs[:15]])

                max_length = self.settings.get('max_content_length', 5000)
                article["content"] = content[:max_length]

        except Exception as e:
            article["content"] = article.get("excerpt", "")

        return article
