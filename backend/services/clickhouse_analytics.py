import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import aiohttp

logger = logging.getLogger(__name__)

class ClickHouseService:
    """Service for ClickHouse analytics integration"""
    
    def __init__(self, host: str, user: str = "default", password: str = "", port: int = 8123):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        # Use HTTPS for Azure ClickHouse, HTTP for local
        protocol = "https" if port == 8443 else "http"
        self.base_url = f"{protocol}://{host}:{port}"
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Table schemas
        self.tables = {
            "translation_events": """
                CREATE TABLE IF NOT EXISTS translation_events (
                    event_id String,
                    session_id String,
                    timestamp DateTime64(3),
                    term String,
                    category String,
                    confidence Float64,
                    processing_time Float64,
                    user_agent String,
                    success UInt8,
                    error_message String
                ) ENGINE = MergeTree()
                ORDER BY (timestamp, session_id)
                PARTITION BY toYYYYMM(timestamp)
            """,
            "session_metrics": """
                CREATE TABLE IF NOT EXISTS session_metrics (
                    session_id String,
                    start_time DateTime64(3),
                    end_time DateTime64(3),
                    total_translations UInt32,
                    avg_confidence Float64,
                    avg_processing_time Float64,
                    categories_used Array(String),
                    success_rate Float64,
                    user_agent String
                ) ENGINE = ReplacingMergeTree()
                ORDER BY session_id
            """,
            "realtime_metrics": """
                CREATE TABLE IF NOT EXISTS realtime_metrics (
                    metric_time DateTime64(3),
                    active_sessions UInt32,
                    translations_per_minute UInt32,
                    avg_response_time Float64,
                    error_rate Float64,
                    top_categories Array(String)
                ) ENGINE = MergeTree()
                ORDER BY metric_time
                PARTITION BY toYYYYMM(metric_time)
            """
        }
    
    async def initialize(self):
        """Initialize ClickHouse connection and create tables"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
            
            # Test connection
            await self._execute_query("SELECT 1")
            
            # Create tables
            for table_name, create_sql in self.tables.items():
                await self._execute_query(create_sql)
                logger.info(f"ClickHouse table '{table_name}' ready")
            
            logger.info("ClickHouse analytics service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ClickHouse: {str(e)}")
            raise
    
    async def _execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Execute ClickHouse query"""
        try:
            if not self.session:
                raise Exception("ClickHouse session not initialized")
            
            url = f"{self.base_url}/"
            
            # Prepare request parameters
            request_params = {
                "query": query,
                "format": "JSONEachRow"
            }
            
            # Prepare headers for authentication
            headers = {}
            if self.port == 8443:  # Azure ClickHouse uses basic auth in headers
                import base64
                auth_string = f"{self.user}:{self.password}"
                auth_bytes = auth_string.encode('ascii')
                auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
                headers['Authorization'] = f'Basic {auth_b64}'
            else:  # Local ClickHouse uses query parameters
                if self.user:
                    request_params["user"] = self.user
                if self.password:
                    request_params["password"] = self.password
            
            async with self.session.post(url, params=request_params, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"ClickHouse query error: {response.status} - {error_text}")
                    raise Exception(f"ClickHouse query failed: {error_text}")
                
                response_text = await response.text()
                
                # Parse JSONEachRow format
                results = []
                if response_text.strip():
                    import json
                    for line in response_text.strip().split('\n'):
                        if line.strip():
                            results.append(json.loads(line))
                
                return results
                
        except Exception as e:
            logger.error(f"ClickHouse query execution error: {str(e)}")
            raise
    
    async def log_translation_event(self, event_data: Dict[str, Any]):
        """Log a translation event to ClickHouse"""
        try:
            query = """
                INSERT INTO translation_events (
                    event_id, session_id, timestamp, term, category, 
                    confidence, processing_time, user_agent, success, error_message
                ) VALUES
            """
            
            # Generate event ID
            import uuid
            event_id = str(uuid.uuid4())
            
            # Prepare values
            values = f"""(
                '{event_id}',
                '{event_data.get('session_id', '')}',
                '{event_data.get('timestamp', datetime.utcnow()).strftime('%Y-%m-%d %H:%M:%S.%f')}',
                '{event_data.get('term', '').replace("'", "''")}',
                '{event_data.get('category', '')}',
                {event_data.get('confidence', 0.0)},
                {event_data.get('processing_time', 0.0)},
                '{event_data.get('user_agent', '').replace("'", "''")}',
                {1 if event_data.get('success', True) else 0},
                '{event_data.get('error_message', '').replace("'", "''")}'
            )"""
            
            await self._execute_query(query + values)
            
        except Exception as e:
            logger.error(f"Failed to log translation event: {str(e)}")
    
    async def get_session_analytics(self, session_id: str) -> Dict[str, Any]:
        """Get detailed analytics for a specific session"""
        try:
            query = f"""
                SELECT 
                    session_id,
                    count() as total_translations,
                    avg(confidence) as avg_confidence,
                    avg(processing_time) as avg_processing_time,
                    groupArray(DISTINCT category) as categories_used,
                    countIf(success = 1) / count() as success_rate,
                    min(timestamp) as first_activity,
                    max(timestamp) as last_activity,
                    (max(timestamp) - min(timestamp)) / 60 as duration_minutes
                FROM translation_events 
                WHERE session_id = '{session_id}'
                GROUP BY session_id
            """
            
            results = await self._execute_query(query)
            
            if results:
                return results[0]
            else:
                return {
                    "session_id": session_id,
                    "total_translations": 0,
                    "avg_confidence": 0.0,
                    "avg_processing_time": 0.0,
                    "categories_used": [],
                    "success_rate": 0.0,
                    "duration_minutes": 0.0
                }
                
        except Exception as e:
            logger.error(f"Session analytics error: {str(e)}")
            return {}
    
    async def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get real-time dashboard metrics"""
        try:
            # Get metrics for the last 24 hours
            metrics = {}
            
            # Total sessions and translations
            total_query = """
                SELECT 
                    countDistinct(session_id) as total_sessions,
                    count() as total_translations,
                    avg(confidence) as avg_confidence,
                    avg(processing_time) as avg_processing_time,
                    countIf(success = 1) / count() as success_rate
                FROM translation_events 
                WHERE timestamp >= now() - INTERVAL 24 HOUR
            """
            
            total_results = await self._execute_query(total_query)
            if total_results:
                metrics.update(total_results[0])
            
            # Top categories
            categories_query = """
                SELECT 
                    category,
                    count() as count,
                    avg(confidence) as avg_confidence
                FROM translation_events 
                WHERE timestamp >= now() - INTERVAL 24 HOUR
                GROUP BY category
                ORDER BY count DESC
                LIMIT 10
            """
            
            categories_results = await self._execute_query(categories_query)
            metrics["top_categories"] = categories_results
            
            # Top terms
            terms_query = """
                SELECT 
                    term,
                    count() as usage_count,
                    avg(confidence) as avg_confidence,
                    category
                FROM translation_events 
                WHERE timestamp >= now() - INTERVAL 24 HOUR
                GROUP BY term, category
                ORDER BY usage_count DESC
                LIMIT 10
            """
            
            terms_results = await self._execute_query(terms_query)
            metrics["top_terms"] = terms_results
            
            # Active sessions (last 5 minutes)
            active_query = """
                SELECT countDistinct(session_id) as active_sessions
                FROM translation_events 
                WHERE timestamp >= now() - INTERVAL 5 MINUTE
            """
            
            active_results = await self._execute_query(active_query)
            if active_results:
                metrics["active_sessions"] = active_results[0]["active_sessions"]
            
            # Translation volume over 24 hours
            volume_query = """
                SELECT 
                    toStartOfHour(timestamp) as hour,
                    count() as translations
                FROM translation_events 
                WHERE timestamp >= now() - INTERVAL 24 HOUR
                GROUP BY hour
                ORDER BY hour
            """
            
            volume_results = await self._execute_query(volume_query)
            metrics["translation_volume_24h"] = volume_results
            
            return metrics
            
        except Exception as e:
            logger.error(f"Dashboard metrics error: {str(e)}")
            return {}
    
    async def get_performance_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance metrics for the specified time period"""
        try:
            query = f"""
                SELECT 
                    toStartOfHour(timestamp) as hour,
                    count() as total_requests,
                    avg(processing_time) as avg_processing_time,
                    quantile(0.95)(processing_time) as p95_processing_time,
                    countIf(success = 0) / count() as error_rate,
                    avg(confidence) as avg_confidence
                FROM translation_events 
                WHERE timestamp >= now() - INTERVAL {hours} HOUR
                GROUP BY hour
                ORDER BY hour
            """
            
            results = await self._execute_query(query)
            return {"performance_data": results}
            
        except Exception as e:
            logger.error(f"Performance metrics error: {str(e)}")
            return {"performance_data": []}
    
    async def get_category_trends(self, days: int = 7) -> Dict[str, Any]:
        """Get category usage trends"""
        try:
            query = f"""
                SELECT 
                    toStartOfDay(timestamp) as day,
                    category,
                    count() as usage_count,
                    avg(confidence) as avg_confidence
                FROM translation_events 
                WHERE timestamp >= now() - INTERVAL {days} DAY
                GROUP BY day, category
                ORDER BY day, usage_count DESC
            """
            
            results = await self._execute_query(query)
            return {"category_trends": results}
            
        except Exception as e:
            logger.error(f"Category trends error: {str(e)}")
            return {"category_trends": []}
    
    async def store_realtime_metrics(self, metrics: Dict[str, Any]):
        """Store real-time metrics snapshot"""
        try:
            query = """
                INSERT INTO realtime_metrics (
                    metric_time, active_sessions, translations_per_minute,
                    avg_response_time, error_rate, top_categories
                ) VALUES
            """
            
            values = f"""(
                '{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')}',
                {metrics.get('active_sessions', 0)},
                {metrics.get('translations_per_minute', 0)},
                {metrics.get('avg_response_time', 0.0)},
                {metrics.get('error_rate', 0.0)},
                {metrics.get('top_categories', [])}
            )"""
            
            await self._execute_query(query + values)
            
        except Exception as e:
            logger.error(f"Failed to store realtime metrics: {str(e)}")
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics"""
        try:
            # Check recent activity
            health_query = """
                SELECT 
                    count() as events_last_hour,
                    countDistinct(session_id) as active_sessions_last_hour,
                    avg(processing_time) as avg_processing_time,
                    countIf(success = 0) as errors_last_hour
                FROM translation_events 
                WHERE timestamp >= now() - INTERVAL 1 HOUR
            """
            
            results = await self._execute_query(health_query)
            
            if results:
                health_data = results[0]
                
                # Determine health status
                error_rate = health_data.get('errors_last_hour', 0) / max(health_data.get('events_last_hour', 1), 1)
                avg_time = health_data.get('avg_processing_time', 0)
                
                status = "healthy"
                if error_rate > 0.1:  # More than 10% errors
                    status = "degraded"
                elif avg_time > 5000:  # More than 5 seconds average
                    status = "slow"
                elif health_data.get('events_last_hour', 0) == 0:
                    status = "idle"
                
                return {
                    "status": status,
                    "error_rate": error_rate,
                    "avg_processing_time": avg_time,
                    "active_sessions": health_data.get('active_sessions_last_hour', 0),
                    "events_last_hour": health_data.get('events_last_hour', 0)
                }
            
            return {"status": "unknown"}
            
        except Exception as e:
            logger.error(f"System health check error: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old data to manage storage"""
        try:
            cleanup_query = f"""
                ALTER TABLE translation_events 
                DELETE WHERE timestamp < now() - INTERVAL {days_to_keep} DAY
            """
            
            await self._execute_query(cleanup_query)
            logger.info(f"Cleaned up translation events older than {days_to_keep} days")
            
        except Exception as e:
            logger.error(f"Data cleanup error: {str(e)}")
    
    async def close(self):
        """Close ClickHouse connection"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("ClickHouse connection closed")
    
    def __del__(self):
        """Cleanup on deletion"""
        if hasattr(self, 'session') and self.session and not self.session.closed:
            asyncio.create_task(self.session.close()) 