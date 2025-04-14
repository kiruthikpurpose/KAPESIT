import logging
import sys
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum, auto
import traceback
import json
from datetime import datetime
import os

class ErrorSeverity(Enum):
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()

@dataclass
class ErrorContext:
    timestamp: datetime
    severity: ErrorSeverity
    message: str
    error_type: str
    stack_trace: str
    additional_data: Dict[str, Any]
    component: str
    request_id: Optional[str] = None

class KAPESITError(Exception):
    def __init__(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        error_type: str = "GENERAL_ERROR",
        additional_data: Optional[Dict[str, Any]] = None,
        component: str = "UNKNOWN",
        request_id: Optional[str] = None
    ):
        self.context = ErrorContext(
            timestamp=datetime.utcnow(),
            severity=severity,
            message=message,
            error_type=error_type,
            stack_trace=traceback.format_exc(),
            additional_data=additional_data or {},
            component=component,
            request_id=request_id
        )
        super().__init__(message)

class ErrorHandler:
    def __init__(self, log_file: str = "kapesit.log"):
        self.logger = self._setup_logger(log_file)
        self.error_counts = {severity: 0 for severity in ErrorSeverity}
        self.error_history = []
        
    def _setup_logger(self, log_file: str) -> logging.Logger:
        logger = logging.getLogger("KAPESIT")
        logger.setLevel(logging.DEBUG)
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def handle_error(self, error: KAPESITError) -> None:
        """Handle and log errors with appropriate severity"""
        self.error_counts[error.context.severity] += 1
        self.error_history.append(error.context)
        
        # Log based on severity
        if error.context.severity == ErrorSeverity.DEBUG:
            self.logger.debug(self._format_error(error))
        elif error.context.severity == ErrorSeverity.INFO:
            self.logger.info(self._format_error(error))
        elif error.context.severity == ErrorSeverity.WARNING:
            self.logger.warning(self._format_error(error))
        elif error.context.severity == ErrorSeverity.ERROR:
            self.logger.error(self._format_error(error))
        else:  # CRITICAL
            self.logger.critical(self._format_error(error))
            
        # For critical errors, also send alert
        if error.context.severity == ErrorSeverity.CRITICAL:
            self._send_alert(error)
    
    def _format_error(self, error: KAPESITError) -> str:
        """Format error for logging"""
        return json.dumps({
            "timestamp": error.context.timestamp.isoformat(),
            "severity": error.context.severity.name,
            "message": error.context.message,
            "error_type": error.context.error_type,
            "component": error.context.component,
            "request_id": error.context.request_id,
            "stack_trace": error.context.stack_trace,
            "additional_data": error.context.additional_data
        }, indent=2)
    
    def _send_alert(self, error: KAPESITError) -> None:
        """Send critical error alerts (placeholder for actual implementation)"""
        # TODO: Implement actual alerting system (email, Slack, etc.)
        pass
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        return {
            "total_errors": sum(self.error_counts.values()),
            "error_counts": {k.name: v for k, v in self.error_counts.items()},
            "recent_errors": [
                {
                    "timestamp": error.timestamp.isoformat(),
                    "severity": error.severity.name,
                    "message": error.message,
                    "component": error.component
                }
                for error in self.error_history[-10:]  # Last 10 errors
            ]
        }
    
    def clear_error_history(self) -> None:
        """Clear error history"""
        self.error_counts = {severity: 0 for severity in ErrorSeverity}
        self.error_history = []

# Global error handler instance
error_handler = ErrorHandler()

def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler"""
    if issubclass(exc_type, KAPESITError):
        error_handler.handle_error(exc_value)
    else:
        # Convert unexpected exceptions to KAPESITError
        error = KAPESITError(
            message=str(exc_value),
            severity=ErrorSeverity.CRITICAL,
            error_type=exc_type.__name__,
            stack_trace="".join(traceback.format_tb(exc_traceback)),
            component="SYSTEM"
        )
        error_handler.handle_error(error)

# Set global exception handler
sys.excepthook = handle_exception 