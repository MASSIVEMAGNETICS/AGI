from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DocumentStatus(str, Enum):
    """Document lifecycle status"""

    DRAFT = "draft"
    PENDING_SIGNATURE = "pending_signature"
    SIGNED = "signed"
    FINALIZED = "finalized"
    ARCHIVED = "archived"


class RenderedDocument(BaseModel):
    """A rendered version of a document"""

    url: str
    format: str  # pdf, docx
    sha256: str
    size_bytes: int
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AuditLogEntry(BaseModel):
    """Single audit log entry"""

    event: str  # created, edited, filled, signed, exported, viewed
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    delta: Optional[Dict[str, Any]] = None  # what changed
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Signature(BaseModel):
    """Electronic signature information"""

    signer_id: str
    signer_name: str
    signed_at: datetime = Field(default_factory=datetime.utcnow)
    signature_type: str  # typed, digital_certificate
    signature_data: Optional[str] = None  # base64 image or certificate
    ip_address: Optional[str] = None
    pin_verified: bool = False


class Document(BaseModel):
    """Document instance created from a template"""

    id: str = Field(default_factory=lambda: f"doc-{datetime.utcnow().timestamp()}")
    template_id: str
    org_id: str
    name: str
    filled_variables: Dict[str, Any] = Field(default_factory=dict)
    rendered_pdfs: List[RenderedDocument] = Field(default_factory=list)
    status: DocumentStatus = DocumentStatus.DRAFT
    signatures: List[Signature] = Field(default_factory=list)
    audit_trail: List[AuditLogEntry] = Field(default_factory=list)
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "template_id": "tpl-visit-note-001",
                "org_id": "org-uh-elyria",
                "name": "Doctor's Excuse - John Doe",
                "created_by": "usr-123",
            }
        }
