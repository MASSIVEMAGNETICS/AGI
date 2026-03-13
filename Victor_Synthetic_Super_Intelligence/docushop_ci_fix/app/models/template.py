from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ElementType(str, Enum):
    """Types of elements that can be placed in a template"""

    TEXT = "text"
    RICHTEXT = "richtext"
    IMAGE = "image"
    TABLE = "table"
    SIGNATURE = "signature"
    AUTOFIELD = "autofield"
    LOGO = "logo"
    QR = "qr"
    BARCODE = "barcode"


class VariableType(str, Enum):
    """Types of variables for autofill"""

    STRING = "string"
    DATE = "date"
    NUMBER = "number"
    EMAIL = "email"
    PHONE = "phone"
    ENUM = "enum"


class TemplateElement(BaseModel):
    """An element in a template page"""

    id: str
    type: ElementType
    x: float
    y: float
    w: float
    h: float
    rotation: float = 0.0
    props: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "logo-1",
                "type": "image",
                "x": 40,
                "y": 24,
                "w": 120,
                "h": 40,
                "props": {"src": "assets/logo.svg"},
            }
        }


class TemplateVariable(BaseModel):
    """A variable definition for a template"""

    name: str
    type: VariableType
    required: bool = False
    validation: Optional[str] = None  # regex pattern
    enum_values: Optional[List[str]] = None
    default_value: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {"name": "patient_name", "type": "string", "required": True}
        }


class TemplatePage(BaseModel):
    """A page in a template"""

    page_number: int
    size: str = "letter"  # letter, a4, legal
    width: float = 612  # points (8.5" * 72)
    height: float = 792  # points (11" * 72)
    elements: List[TemplateElement] = Field(default_factory=list)


class Template(BaseModel):
    """Template model for document generation"""

    id: str = Field(default_factory=lambda: f"tpl-{datetime.utcnow().timestamp()}")
    org_id: str
    name: str
    description: Optional[str] = None
    pages: List[TemplatePage] = Field(default_factory=list)
    variables: List[TemplateVariable] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    access_control: Dict[str, Any] = Field(
        default_factory=dict
    )  # org-wide, department, role
    is_published: bool = False
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "org_id": "org-uh-elyria",
                "name": "Doctor Note - Excuse for School/Work",
                "created_by": "usr-123",
            }
        }
