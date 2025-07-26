import asyncio
import json
import logging
from typing import Dict, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manager for WebSocket connections and real-time communication"""
    
    def __init__(self):
        # Active connections: session_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Connection metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Connection groups for broadcasting
        self.groups: Dict[str, Set[str]] = {
            "active_sessions": set(),
            "listening": set(),
            "processing": set()
        }
        
    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept new WebSocket connection"""
        try:
            await websocket.accept()
            
            self.active_connections[session_id] = websocket
            self.connection_metadata[session_id] = {
                "connected_at": datetime.utcnow(),
                "status": "connected",
                "last_activity": datetime.utcnow()
            }
            
            # Add to active sessions group
            self.groups["active_sessions"].add(session_id)
            
            logger.info(f"WebSocket connected: session {session_id}")
            
            # Send welcome message
            await self.send_personal_message(session_id, {
                "type": "connection_established",
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Connected to Babelfish Enterprise AI"
            })
            
            # Broadcast connection update
            await self.broadcast_to_group("active_sessions", {
                "type": "session_connected",
                "session_id": session_id,
                "total_active": len(self.active_connections)
            })
            
        except Exception as e:
            logger.error(f"WebSocket connection error for session {session_id}: {str(e)}")
            raise
    
    async def disconnect(self, websocket: WebSocket, session_id: str):
        """Handle WebSocket disconnection"""
        try:
            # Remove from all groups
            for group_name, group_sessions in self.groups.items():
                group_sessions.discard(session_id)
            
            # Clean up connection data
            if session_id in self.active_connections:
                del self.active_connections[session_id]
            
            if session_id in self.connection_metadata:
                # Log session duration
                metadata = self.connection_metadata[session_id]
                duration = datetime.utcnow() - metadata["connected_at"]
                logger.info(f"Session {session_id} disconnected after {duration.total_seconds():.2f} seconds")
                del self.connection_metadata[session_id]
            
            # Broadcast disconnection update
            await self.broadcast_to_group("active_sessions", {
                "type": "session_disconnected", 
                "session_id": session_id,
                "total_active": len(self.active_connections)
            })
            
            logger.info(f"WebSocket disconnected: session {session_id}")
            
        except Exception as e:
            logger.error(f"WebSocket disconnection error for session {session_id}: {str(e)}")
    
    async def send_personal_message(self, session_id: str, message: Dict[str, Any]):
        """Send message to specific session"""
        try:
            if session_id in self.active_connections:
                websocket = self.active_connections[session_id]
                await websocket.send_text(json.dumps(message))
                
                # Update last activity
                if session_id in self.connection_metadata:
                    self.connection_metadata[session_id]["last_activity"] = datetime.utcnow()
                    
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected during message send: {session_id}")
            await self.disconnect(None, session_id)
        except Exception as e:
            logger.error(f"Error sending message to session {session_id}: {str(e)}")
    
    async def broadcast_to_group(self, group_name: str, message: Dict[str, Any]):
        """Broadcast message to all sessions in a group"""
        if group_name not in self.groups:
            logger.warning(f"Unknown group: {group_name}")
            return
        
        failed_sessions = []
        
        for session_id in self.groups[group_name].copy():
            try:
                await self.send_personal_message(session_id, message)
            except Exception as e:
                logger.error(f"Failed to broadcast to session {session_id}: {str(e)}")
                failed_sessions.append(session_id)
        
        # Clean up failed sessions
        for session_id in failed_sessions:
            await self.disconnect(None, session_id)
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast message to all active connections"""
        await self.broadcast_to_group("active_sessions", message)
    
    def add_to_group(self, session_id: str, group_name: str):
        """Add session to a group"""
        if group_name not in self.groups:
            self.groups[group_name] = set()
        
        self.groups[group_name].add(session_id)
        logger.debug(f"Added session {session_id} to group {group_name}")
    
    def remove_from_group(self, session_id: str, group_name: str):
        """Remove session from a group"""
        if group_name in self.groups:
            self.groups[group_name].discard(session_id)
            logger.debug(f"Removed session {session_id} from group {group_name}")
    
    async def handle_session_status_change(self, session_id: str, status: str):
        """Handle session status changes (listening, processing, idle)"""
        try:
            # Remove from all status groups first
            for group in ["listening", "processing"]:
                self.remove_from_group(session_id, group)
            
            # Add to appropriate group
            if status in ["listening", "processing"]:
                self.add_to_group(session_id, status)
            
            # Update metadata
            if session_id in self.connection_metadata:
                self.connection_metadata[session_id]["status"] = status
                self.connection_metadata[session_id]["last_activity"] = datetime.utcnow()
            
            # Broadcast status change
            await self.broadcast_to_group("active_sessions", {
                "type": "session_status_change",
                "session_id": session_id,
                "status": status,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error handling status change for session {session_id}: {str(e)}")
    
    async def send_translation_update(self, session_id: str, update_data: Dict[str, Any]):
        """Send translation progress update to specific session"""
        message = {
            "type": "translation_update",
            "session_id": session_id,
            "data": update_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.send_personal_message(session_id, message)
    
    async def send_error_message(self, session_id: str, error: str, error_code: Optional[str] = None):
        """Send error message to specific session"""
        message = {
            "type": "error",
            "session_id": session_id,
            "error": error,
            "error_code": error_code,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.send_personal_message(session_id, message)
    
    async def send_system_notification(self, notification: str, level: str = "info"):
        """Send system notification to all active sessions"""
        message = {
            "type": "system_notification",
            "notification": notification,
            "level": level,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.broadcast_to_all(message)
    
    def get_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all active sessions"""
        sessions = {}
        
        for session_id, metadata in self.connection_metadata.items():
            sessions[session_id] = {
                **metadata,
                "groups": [
                    group for group, members in self.groups.items() 
                    if session_id in members
                ]
            }
        
        return sessions
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            "total_active_connections": len(self.active_connections),
            "group_counts": {
                group: len(members) for group, members in self.groups.items()
            },
            "average_session_duration": self._calculate_average_session_duration(),
            "oldest_connection": self._get_oldest_connection_time()
        }
    
    def _calculate_average_session_duration(self) -> float:
        """Calculate average session duration for active connections"""
        if not self.connection_metadata:
            return 0.0
        
        total_duration = 0.0
        current_time = datetime.utcnow()
        
        for metadata in self.connection_metadata.values():
            duration = (current_time - metadata["connected_at"]).total_seconds()
            total_duration += duration
        
        return total_duration / len(self.connection_metadata)
    
    def _get_oldest_connection_time(self) -> Optional[str]:
        """Get the timestamp of the oldest connection"""
        if not self.connection_metadata:
            return None
        
        oldest = min(
            self.connection_metadata.values(),
            key=lambda x: x["connected_at"]
        )
        
        return oldest["connected_at"].isoformat()
    
    async def cleanup_inactive_connections(self, timeout_minutes: int = 30):
        """Clean up connections that have been inactive for too long"""
        current_time = datetime.utcnow()
        timeout_delta = datetime.timedelta(minutes=timeout_minutes)
        
        inactive_sessions = []
        
        for session_id, metadata in self.connection_metadata.items():
            if current_time - metadata["last_activity"] > timeout_delta:
                inactive_sessions.append(session_id)
        
        for session_id in inactive_sessions:
            logger.info(f"Cleaning up inactive session: {session_id}")
            await self.disconnect(None, session_id)
        
        return len(inactive_sessions)
    
    async def ping_all_connections(self):
        """Send ping to all connections to check connectivity"""
        ping_message = {
            "type": "ping",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        failed_sessions = []
        
        for session_id in list(self.active_connections.keys()):
            try:
                await self.send_personal_message(session_id, ping_message)
            except Exception as e:
                logger.warning(f"Ping failed for session {session_id}: {str(e)}")
                failed_sessions.append(session_id)
        
        # Clean up failed sessions
        for session_id in failed_sessions:
            await self.disconnect(None, session_id)
        
        return len(self.active_connections) - len(failed_sessions) 