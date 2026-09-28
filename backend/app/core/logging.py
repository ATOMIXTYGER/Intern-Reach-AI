import logging
import sys
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger("internreach")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)

def log_agent_execution(
    agent_name: str,
    action: str,
    model: str,
    duration_ms: float,
    success: bool,
    tokens: Optional[int] = None,
    error: Optional[str] = None
):
    """Logs structured telemetry for agent runs without exposing PII/secrets."""
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": "agent_execution",
        "agent": agent_name,
        "action": action,
        "model": model,
        "duration_ms": duration_ms,
        "success": success,
        "tokens": tokens,
        "error": error
    }
    logger.info(json.dumps(payload))

def log_security_event(
    event_type: str,
    user_id: Optional[str],
    ip_address: Optional[str],
    details: Dict[str, Any]
):
    """Logs security relevant events (SSRF attempts, prompt injection, failed auth)"""
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": "security_audit",
        "event_type": event_type,
        "user_id": user_id,
        "ip": ip_address,
        "details": details
    }
    logger.warning(json.dumps(payload))
