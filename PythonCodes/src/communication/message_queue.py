import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .secure_protocol import SecureProtocol
from ..utils.error_handling import KAPESITError, ErrorSeverity
from ..utils.config_manager import config_manager

class MessageQueue:
    def __init__(self, max_retries: int = 3, retry_delay: int = 5):
        self.secure_protocol = SecureProtocol()
        self.queues: Dict[str, List[Dict[str, Any]]] = {}
        self.retry_counts: Dict[str, int] = {}
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.cleanup_task = None
        
    async def start(self):
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
    async def stop(self):
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
    
    async def enqueue(self, session_id: str, message: Dict[str, Any], priority: int = 0):
        try:
            if session_id not in self.queues:
                self.queues[session_id] = []
                
            message_data = {
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "priority": priority,
                "retry_count": 0
            }
            
            # Insert based on priority
            insert_index = 0
            for i, queued_msg in enumerate(self.queues[session_id]):
                if queued_msg["priority"] < priority:
                    insert_index = i
                    break
                insert_index = i + 1
                
            self.queues[session_id].insert(insert_index, message_data)
            
        except Exception as e:
            raise KAPESITError(
                f"Message enqueue failed: {str(e)}",
                severity=ErrorSeverity.ERROR,
                component="MESSAGE_QUEUE"
            )
    
    async def dequeue(self, session_id: str) -> Optional[Dict[str, Any]]:
        try:
            if session_id not in self.queues or not self.queues[session_id]:
                return None
                
            message_data = self.queues[session_id].pop(0)
            return message_data["message"]
            
        except Exception as e:
            raise KAPESITError(
                f"Message dequeue failed: {str(e)}",
                severity=ErrorSeverity.ERROR,
                component="MESSAGE_QUEUE"
            )
    
    async def retry_message(self, session_id: str, message: Dict[str, Any]):
        try:
            if session_id not in self.retry_counts:
                self.retry_counts[session_id] = 0
                
            if self.retry_counts[session_id] < self.max_retries:
                self.retry_counts[session_id] += 1
                await self.enqueue(session_id, message, priority=1)
                await asyncio.sleep(self.retry_delay)
            else:
                self.retry_counts[session_id] = 0
                
        except Exception as e:
            raise KAPESITError(
                f"Message retry failed: {str(e)}",
                severity=ErrorSeverity.ERROR,
                component="MESSAGE_QUEUE"
            )
    
    async def _cleanup_loop(self):
        while True:
            try:
                current_time = datetime.utcnow()
                for session_id, queue in list(self.queues.items()):
                    # Remove messages older than 24 hours
                    queue[:] = [
                        msg for msg in queue
                        if current_time - datetime.fromisoformat(msg["timestamp"]) < timedelta(hours=24)
                    ]
                    
                    if not queue:
                        del self.queues[session_id]
                        if session_id in self.retry_counts:
                            del self.retry_counts[session_id]
                            
                await asyncio.sleep(3600)  # Run cleanup every hour
                
            except Exception as e:
                raise KAPESITError(
                    f"Cleanup loop failed: {str(e)}",
                    severity=ErrorSeverity.ERROR,
                    component="MESSAGE_QUEUE"
                )
    
    def get_queue_size(self, session_id: str) -> int:
        return len(self.queues.get(session_id, []))
    
    def get_total_messages(self) -> int:
        return sum(len(queue) for queue in self.queues.values()) 