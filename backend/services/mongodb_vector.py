import motor.motor_asyncio
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import numpy as np
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

class MongoVectorService:
    """Service for MongoDB Vector Search integration"""
    
    def __init__(self, mongodb_uri: str, database_name: str):
        self.mongodb_uri = mongodb_uri
        self.database_name = database_name
        self.client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
        self.database = None
        self.translations_collection = None
        self.sessions_collection = None
        
    async def initialize(self):
        """Initialize MongoDB connection and collections"""
        try:
            # Handle MongoDB URI with potential special characters
            if '@' in self.mongodb_uri and '://' in self.mongodb_uri:
                # Parse and properly encode username/password if present
                parts = self.mongodb_uri.split('://')
                if len(parts) == 2:
                    protocol = parts[0]
                    rest = parts[1]
                    if '@' in rest:
                        auth_part, host_part = rest.split('@', 1)
                        if ':' in auth_part:
                            username, password = auth_part.split(':', 1)
                            encoded_username = quote_plus(username)
                            encoded_password = quote_plus(password)
                            self.mongodb_uri = f"{protocol}://{encoded_username}:{encoded_password}@{host_part}"
            
            self.client = motor.motor_asyncio.AsyncIOMotorClient(self.mongodb_uri)
            self.database = self.client[self.database_name]
            
            # Initialize collections
            self.translations_collection = self.database.translations
            self.sessions_collection = self.database.sessions
            
            # Ensure vector search index exists
            await self._ensure_vector_indexes()
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("MongoDB Vector Search initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB: {str(e)}")
            raise
    
    async def _ensure_vector_indexes(self):
        """Ensure vector search indexes exist"""
        try:
            # Check if vector search index exists
            indexes = await self.translations_collection.list_indexes().to_list(length=None)
            vector_index_exists = any(
                index.get('name') == 'vector_search_index' 
                for index in indexes
            )
            
            if not vector_index_exists:
                logger.info("Creating vector search index...")
                # Note: In production, this should be created via MongoDB Atlas UI
                # as it requires specific configuration for vector search
                await self.translations_collection.create_index([
                    ("embedding", "2dsphere")
                ], name="vector_search_index")
            
            # Ensure text indexes for term suggestions
            await self.translations_collection.create_index([
                ("term", "text"),
                ("explanation", "text"),
                ("category", "text")
            ], name="text_search_index")
            
            # Ensure performance indexes
            await self.translations_collection.create_index("session_id")
            await self.translations_collection.create_index("created_at")
            await self.translations_collection.create_index("category")
            
        except Exception as e:
            logger.warning(f"Index creation warning: {str(e)}")
    
    async def search_similar_terms(
        self, 
        query_text: str, 
        limit: int = 5, 
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for similar terms using vector similarity
        
        Args:
            query_text: Text to search for
            limit: Maximum number of results
            threshold: Minimum similarity threshold
            
        Returns:
            List of similar terms with similarity scores
        """
        try:
            # For this implementation, we'll use text search as a fallback
            # In production with MongoDB Atlas, you'd use $vectorSearch
            
            # First try exact term match
            exact_matches = await self.translations_collection.find({
                "term": {"$regex": f"^{query_text}$", "$options": "i"}
            }).limit(limit).to_list(length=None)
            
            if exact_matches:
                results = []
                for match in exact_matches:
                    results.append({
                        "term": match["term"],
                        "explanation": match["explanation"],
                        "category": match["category"],
                        "score": 1.0,  # Exact match
                        "metadata": match.get("metadata", {})
                    })
                return results
            
            # Then try text search
            text_matches = await self.translations_collection.find({
                "$text": {"$search": query_text}
            }).limit(limit).to_list(length=None)
            
            results = []
            for match in text_matches:
                # Calculate a simple similarity score based on text match
                score = self._calculate_text_similarity(query_text, match["term"])
                if score >= threshold:
                    results.append({
                        "term": match["term"],
                        "explanation": match["explanation"],
                        "category": match["category"],
                        "score": score,
                        "metadata": match.get("metadata", {})
                    })
            
            return sorted(results, key=lambda x: x["score"], reverse=True)
            
        except Exception as e:
            logger.error(f"Vector search error: {str(e)}")
            return []
    
    async def store_translation(
        self,
        term: str,
        explanation: str,
        category: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> str:
        """
        Store a translation entry with its vector embedding
        
        Args:
            term: Technical term
            explanation: Business explanation
            category: Term category
            embedding: Vector embedding
            metadata: Additional metadata
            
        Returns:
            Document ID
        """
        try:
            document = {
                "term": term,
                "explanation": explanation,
                "category": category,
                "embedding": embedding,
                "metadata": metadata,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Check if term already exists
            existing = await self.translations_collection.find_one({"term": term})
            
            if existing:
                # Update existing entry
                result = await self.translations_collection.update_one(
                    {"term": term},
                    {
                        "$set": {
                            "explanation": explanation,
                            "category": category,
                            "embedding": embedding,
                            "updated_at": datetime.utcnow()
                        },
                        "$addToSet": {
                            "sessions": metadata.get("session_id")
                        }
                    }
                )
                return str(existing["_id"])
            else:
                # Insert new entry
                result = await self.translations_collection.insert_one(document)
                return str(result.inserted_id)
                
        except Exception as e:
            logger.error(f"Translation storage error: {str(e)}")
            raise
    
    async def get_term_suggestions(self, partial_term: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get term suggestions based on partial input
        
        Args:
            partial_term: Partial term to search for
            limit: Maximum number of suggestions
            
        Returns:
            List of term suggestions
        """
        try:
            # Use regex for partial matching
            pattern = f".*{partial_term}.*"
            
            matches = await self.translations_collection.find({
                "term": {"$regex": pattern, "$options": "i"}
            }).limit(limit).to_list(length=None)
            
            suggestions = []
            for match in matches:
                suggestions.append({
                    "term": match["term"],
                    "category": match["category"],
                    "confidence": self._calculate_suggestion_confidence(partial_term, match["term"]),
                    "usage_count": len(match.get("sessions", []))
                })
            
            return sorted(suggestions, key=lambda x: x["confidence"], reverse=True)
            
        except Exception as e:
            logger.error(f"Term suggestions error: {str(e)}")
            return []
    
    async def get_category_stats(self) -> Dict[str, Any]:
        """Get statistics about term categories"""
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$category",
                        "count": {"$sum": 1},
                        "avg_confidence": {"$avg": "$metadata.confidence"}
                    }
                },
                {
                    "$sort": {"count": -1}
                }
            ]
            
            results = await self.translations_collection.aggregate(pipeline).to_list(length=None)
            
            stats = {
                "categories": [],
                "total_terms": 0
            }
            
            for result in results:
                category_data = {
                    "category": result["_id"],
                    "count": result["count"],
                    "avg_confidence": round(result.get("avg_confidence", 0), 2)
                }
                stats["categories"].append(category_data)
                stats["total_terms"] += result["count"]
            
            return stats
            
        except Exception as e:
            logger.error(f"Category stats error: {str(e)}")
            return {"categories": [], "total_terms": 0}
    
    async def get_popular_terms(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular terms based on usage"""
        try:
            pipeline = [
                {
                    "$addFields": {
                        "usage_count": {"$size": {"$ifNull": ["$sessions", []]}}
                    }
                },
                {
                    "$sort": {"usage_count": -1, "created_at": -1}
                },
                {
                    "$limit": limit
                },
                {
                    "$project": {
                        "term": 1,
                        "category": 1,
                        "usage_count": 1,
                        "confidence": "$metadata.confidence"
                    }
                }
            ]
            
            results = await self.translations_collection.aggregate(pipeline).to_list(length=None)
            return results
            
        except Exception as e:
            logger.error(f"Popular terms error: {str(e)}")
            return []
    
    async def store_session_data(self, session_id: str, session_data: Dict[str, Any]):
        """Store session analytics data"""
        try:
            document = {
                "session_id": session_id,
                "data": session_data,
                "created_at": datetime.utcnow()
            }
            
            await self.sessions_collection.insert_one(document)
            
        except Exception as e:
            logger.error(f"Session storage error: {str(e)}")
    
    async def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data"""
        try:
            session = await self.sessions_collection.find_one({"session_id": session_id})
            return session.get("data") if session else None
            
        except Exception as e:
            logger.error(f"Session retrieval error: {str(e)}")
            return None
    
    def _calculate_text_similarity(self, query: str, term: str) -> float:
        """Calculate simple text similarity score"""
        query_lower = query.lower()
        term_lower = term.lower()
        
        # Exact match
        if query_lower == term_lower:
            return 1.0
        
        # Contains query
        if query_lower in term_lower:
            return 0.9
        
        # Query contains term
        if term_lower in query_lower:
            return 0.8
        
        # Calculate Jaccard similarity on words
        query_words = set(query_lower.split())
        term_words = set(term_lower.split())
        
        if not query_words or not term_words:
            return 0.0
        
        intersection = len(query_words.intersection(term_words))
        union = len(query_words.union(term_words))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_suggestion_confidence(self, partial: str, full_term: str) -> float:
        """Calculate confidence score for term suggestions"""
        partial_lower = partial.lower()
        term_lower = full_term.lower()
        
        # Starts with partial
        if term_lower.startswith(partial_lower):
            return 0.95
        
        # Contains partial
        if partial_lower in term_lower:
            return 0.8
        
        # Word boundary match
        words = term_lower.split()
        for word in words:
            if word.startswith(partial_lower):
                return 0.7
        
        return 0.5
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check MongoDB health and connectivity"""
        try:
            # Test database connectivity
            await self.client.admin.command('ping')
            
            # Get collection stats
            translations_count = await self.translations_collection.count_documents({})
            sessions_count = await self.sessions_collection.count_documents({})
            
            return {
                "status": "healthy",
                "translations_count": translations_count,
                "sessions_count": sessions_count,
                "database": self.database_name
            }
            
        except Exception as e:
            logger.error(f"MongoDB health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e)
            } 