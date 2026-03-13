from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class UserRole(str, Enum):
    """User roles for RBAC"""

    ADMIN = "admin"
    TEMPLATE_DESIGNER = "template_designer"
    CLINICIAN = "clinician"
    STAFF = "staff"
    AUDITOR = "auditor"


class User(BaseModel):
    """User model"""

    id: str = Field(default_factory=lambda: f"usr-{datetime.utcnow().timestamp()}")
    email: str
    name: str
    role: UserRole
    org_id: str
    provider_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "doctor@hospital.com",
                "name": "Dr. John Smith",
                "role": "clinician",
                "org_id": "org-uh-elyria",
            }
        }


class Organization(BaseModel):
    """Organization model"""

    id: str = Field(default_factory=lambda: f"org-{datetime.utcnow().timestamp()}")
    name: str
    assets: Dict[str, Any] = Field(default_factory=dict)  # logos, fonts, colors
    settings: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "University Hospitals Elyria Medical Center",
                "assets": {
                    "logo": "assets/logo.svg",
                    "colors": {"primary": "#003366", "secondary": "#6699CC"},
                },
            }
        }
