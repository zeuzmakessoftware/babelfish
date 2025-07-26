import aiohttp
import asyncio
import logging
from typing import List, Dict, Optional, Any
import time

logger = logging.getLogger(__name__)

class TavilySearchService:
    """Service for Tavily real-time web search integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.tavily.com/search"
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Search configuration
        self.default_search_depth = "advanced"
        self.max_results = 10
        self.include_domains = [
            "stackoverflow.com",
            "github.com", 
            "docs.aws.amazon.com",
            "kubernetes.io",
            "docker.com",
            "microsoft.com",
            "google.com",
            "mozilla.org",
            "w3.org",
            "wikipedia.org"
        ]
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "Content-Type": "application/json"
                },
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self.session
    
    async def search_technical_term(
        self,
        term: str,
        search_depth: str = "advanced",
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for technical term definitions and documentation
        
        Args:
            term: Technical term to search for
            search_depth: Search depth (basic, advanced)
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with relevance scores
        """
        try:
            session = await self._get_session()
            
            # Construct search query optimized for technical content
            query = self._build_technical_query(term)
            
            payload = {
                "api_key": self.api_key,
                "query": query,
                "search_depth": search_depth,
                "include_answer": True,
                "include_raw_content": False,
                "max_results": max_results,
                "include_domains": self.include_domains[:5],  # Limit to top domains
                "exclude_domains": [
                    "reddit.com",
                    "pinterest.com", 
                    "facebook.com",
                    "twitter.com",
                    "instagram.com"
                ]
            }
            
            logger.info(f"Searching Tavily for: {query}")
            
            async with session.post(self.base_url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Tavily API error: {response.status} - {error_text}")
                    return []
                
                data = await response.json()
                return self._process_search_results(data, term)
                
        except Exception as e:
            logger.error(f"Tavily search error: {str(e)}")
            return []
    
    def _build_technical_query(self, term: str) -> str:
        """Build optimized search query for technical terms"""
        # Add technical context keywords to improve relevance
        technical_keywords = [
            "definition",
            "documentation", 
            "what is",
            "guide",
            "tutorial",
            "enterprise",
            "business"
        ]
        
        # Create compound query
        base_query = f'"{term}"'
        
        # Add context based on common technical patterns
        if any(keyword in term.lower() for keyword in ['api', 'service', 'framework']):
            base_query += " development programming"
        elif any(keyword in term.lower() for keyword in ['ops', 'deploy', 'infrastructure']):
            base_query += " operations deployment"
        elif any(keyword in term.lower() for keyword in ['cloud', 'aws', 'azure', 'gcp']):
            base_query += " cloud computing"
        elif any(keyword in term.lower() for keyword in ['data', 'analytics', 'ml', 'ai']):
            base_query += " data science machine learning"
        else:
            base_query += " technology definition"
        
        return base_query
    
    def _process_search_results(self, data: Dict[str, Any], original_term: str) -> List[Dict[str, Any]]:
        """Process and rank search results"""
        try:
            results = []
            raw_results = data.get('results', [])
            
            for result in raw_results:
                processed_result = {
                    "title": result.get('title', ''),
                    "url": result.get('url', ''),
                    "snippet": result.get('content', ''),
                    "relevance_score": self._calculate_relevance_score(
                        result, original_term
                    ),
                    "source_type": self._determine_source_type(result.get('url', '')),
                    "published_date": result.get('published_date'),
                    "raw_content": result.get('raw_content', '')
                }
                
                # Filter out low-quality results
                if processed_result["relevance_score"] > 0.3:
                    results.append(processed_result)
            
            # Sort by relevance score
            results.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Search result processing error: {str(e)}")
            return []
    
    def _calculate_relevance_score(self, result: Dict[str, Any], term: str) -> float:
        """Calculate relevance score for search result"""
        score = 0.0
        term_lower = term.lower()
        
        title = result.get('title', '').lower()
        content = result.get('content', '').lower()
        url = result.get('url', '').lower()
        
        # Title relevance (highest weight)
        if term_lower in title:
            score += 0.4
            if title.startswith(term_lower):
                score += 0.2
        
        # Content relevance
        content_matches = content.count(term_lower)
        score += min(content_matches * 0.1, 0.3)
        
        # URL relevance
        if term_lower in url:
            score += 0.1
        
        # Source quality bonus
        domain = self._extract_domain(url)
        if domain in self.include_domains:
            score += 0.2
        
        # Documentation bonus
        doc_indicators = ['docs', 'documentation', 'guide', 'tutorial', 'reference']
        if any(indicator in url or indicator in title for indicator in doc_indicators):
            score += 0.15
        
        return min(score, 1.0)
    
    def _determine_source_type(self, url: str) -> str:
        """Determine the type of source based on URL"""
        domain = self._extract_domain(url)
        
        if 'docs' in url or 'documentation' in url:
            return 'documentation'
        elif domain == 'stackoverflow.com':
            return 'qa_forum'
        elif domain == 'github.com':
            return 'repository'
        elif domain == 'wikipedia.org':
            return 'encyclopedia'
        elif 'blog' in url or 'medium.com' in domain:
            return 'blog'
        elif any(corp in domain for corp in ['aws.amazon.com', 'microsoft.com', 'google.com']):
            return 'corporate_docs'
        else:
            return 'web_article'
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc.lower()
        except:
            return ""
    
    async def search_related_terms(self, term: str, limit: int = 3) -> List[str]:
        """Search for related technical terms"""
        try:
            query = f'"{term}" related concepts similar technologies'
            
            session = await self._get_session()
            payload = {
                "api_key": self.api_key,
                "query": query,
                "search_depth": "basic",
                "include_answer": True,
                "max_results": 3
            }
            
            async with session.post(self.base_url, json=payload) as response:
                if response.status != 200:
                    return []
                
                data = await response.json()
                
                # Extract related terms from search results
                related_terms = []
                for result in data.get('results', []):
                    content = result.get('content', '')
                    extracted = self._extract_related_terms(content, term)
                    related_terms.extend(extracted)
                
                # Remove duplicates and limit results
                unique_terms = list(set(related_terms))[:limit]
                return unique_terms
                
        except Exception as e:
            logger.error(f"Related terms search error: {str(e)}")
            return []
    
    def _extract_related_terms(self, content: str, original_term: str) -> List[str]:
        """Extract related technical terms from content"""
        import re
        
        # Common technical term patterns
        patterns = [
            r'\b[A-Z][a-zA-Z]*[A-Z][a-zA-Z]*\b',  # CamelCase
            r'\b[a-z]+[-_][a-z]+\b',  # kebab-case, snake_case
            r'\b[A-Z]{2,}\b',  # Acronyms
        ]
        
        terms = []
        content_lower = content.lower()
        original_lower = original_term.lower()
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if (len(match) > 2 and 
                    match.lower() != original_lower and
                    match.lower() not in ['the', 'and', 'for', 'with', 'this', 'that']):
                    terms.append(match)
        
        return terms[:5]  # Limit to avoid noise
    
    async def get_trending_topics(self, category: str = "technology") -> List[Dict[str, Any]]:
        """Get trending technical topics"""
        try:
            query = f"trending {category} topics 2024 latest developments"
            
            session = await self._get_session()
            payload = {
                "api_key": self.api_key,
                "query": query,
                "search_depth": "basic",
                "max_results": 5,
                "include_answer": True
            }
            
            async with session.post(self.base_url, json=payload) as response:
                if response.status != 200:
                    return []
                
                data = await response.json()
                
                trending = []
                for result in data.get('results', []):
                    trending.append({
                        "title": result.get('title', ''),
                        "url": result.get('url', ''),
                        "snippet": result.get('content', '')[:200],
                        "source": self._extract_domain(result.get('url', ''))
                    })
                
                return trending
                
        except Exception as e:
            logger.error(f"Trending topics error: {str(e)}")
            return []
    
    async def validate_technical_accuracy(self, term: str, explanation: str) -> Dict[str, Any]:
        """Validate technical explanation accuracy against current sources"""
        try:
            # Search for authoritative sources about the term
            query = f'"{term}" definition documentation official'
            
            session = await self._get_session()
            payload = {
                "api_key": self.api_key,
                "query": query,
                "search_depth": "advanced",
                "max_results": 3,
                "include_domains": ["docs.aws.amazon.com", "kubernetes.io", "docker.com"]
            }
            
            async with session.post(self.base_url, json=payload) as response:
                if response.status != 200:
                    return {"accuracy_score": 0.5, "sources_checked": 0}
                
                data = await response.json()
                results = data.get('results', [])
                
                # Simple accuracy check based on keyword overlap
                accuracy_score = 0.0
                for result in results:
                    content = result.get('content', '').lower()
                    explanation_words = set(explanation.lower().split())
                    content_words = set(content.split())
                    
                    overlap = len(explanation_words.intersection(content_words))
                    total_words = len(explanation_words)
                    
                    if total_words > 0:
                        result_score = overlap / total_words
                        accuracy_score = max(accuracy_score, result_score)
                
                return {
                    "accuracy_score": min(accuracy_score, 1.0),
                    "sources_checked": len(results),
                    "authoritative_sources": [r.get('url') for r in results]
                }
                
        except Exception as e:
            logger.error(f"Accuracy validation error: {str(e)}")
            return {"accuracy_score": 0.5, "sources_checked": 0}
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def __del__(self):
        """Cleanup on deletion"""
        if hasattr(self, 'session') and self.session and not self.session.closed:
            asyncio.create_task(self.session.close()) 