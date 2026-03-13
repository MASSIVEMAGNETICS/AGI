from datetime import datetime
from typing import Any, Dict, Optional


async def log_audit_event(
    event: str,
    user_id: str,
    document_id: Optional[str] = None,
    template_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    delta: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Log an audit event

    This creates an immutable audit log entry.
    In production, this would write to a WORM (write-once-read-many) storage.
    """
    audit_entry = {
        "event": event,
        "user_id": user_id,
        "timestamp": datetime.utcnow(),
        "ip_address": ip_address,
        "delta": delta or {},
        "metadata": metadata or {},
    }

    if document_id:
        audit_entry["metadata"]["document_id"] = document_id

    if template_id:
        audit_entry["metadata"]["template_id"] = template_id

    # TODO: Write to immutable audit log storage
    # For MVP, this is returned for inclusion in document/template records

    return audit_entry
