from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_db
from app.models.document import AuditLogEntry, Document, DocumentStatus, Signature
from app.services.pdf_generator import generate_pdf

router = APIRouter()


@router.post("/", response_model=Document, status_code=status.HTTP_201_CREATED)
async def create_document(
    org_id: str,
    template_id: str,
    filled_variables: Dict[str, Any],
    created_by: str,
    db=Depends(get_db),
):
    """Create a new document from a template"""
    # Verify template exists
    template = await db.templates.find_one({"id": template_id, "org_id": org_id})
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )

    # Create document
    doc = Document(
        template_id=template_id,
        org_id=org_id,
        name=f"Document from {template['name']}",
        filled_variables=filled_variables,
        created_by=created_by,
    )

    # Add audit log
    audit_entry = AuditLogEntry(
        event="created", user_id=created_by, metadata={"template_id": template_id}
    )
    doc.audit_trail.append(audit_entry)

    doc_dict = doc.model_dump()
    result = await db.documents.insert_one(doc_dict)

    if not result.inserted_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create document",
        )

    return doc


@router.get("/{doc_id}", response_model=Document)
async def get_document(org_id: str, doc_id: str, db=Depends(get_db)):
    """Get document by ID"""
    doc = await db.documents.find_one({"id": doc_id, "org_id": org_id})

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    return Document(**doc)


@router.get("/", response_model=List[Document])
async def list_documents(
    org_id: str, skip: int = 0, limit: int = 100, db=Depends(get_db)
):
    """List all documents for an organization"""
    cursor = db.documents.find({"org_id": org_id}).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    return [Document(**d) for d in docs]


@router.post("/{doc_id}/render")
async def render_document(
    org_id: str, doc_id: str, format: str = "pdf", db=Depends(get_db)
):
    """Render document to PDF or DOCX"""
    doc = await db.documents.find_one({"id": doc_id, "org_id": org_id})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    template = await db.templates.find_one({"id": doc["template_id"]})
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )

    # Generate PDF (simplified - actual implementation would use PDF service)
    if format == "pdf":
        pdf_url = await generate_pdf(template, doc["filled_variables"])
        return {"url": pdf_url, "format": "pdf"}

    return {"message": "Format not yet supported", "format": format}


@router.post("/{doc_id}/sign", response_model=Document)
async def sign_document(
    org_id: str,
    doc_id: str,
    signer_id: str,
    signer_name: str,
    signature_data: str,
    pin_verified: bool = False,
    db=Depends(get_db),
):
    """Apply electronic signature to document"""
    doc = await db.documents.find_one({"id": doc_id, "org_id": org_id})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    # Create signature
    signature = Signature(
        signer_id=signer_id,
        signer_name=signer_name,
        signature_data=signature_data,
        signature_type="typed",
        pin_verified=pin_verified,
    )

    # Add audit log
    audit_entry = AuditLogEntry(
        event="signed", user_id=signer_id, metadata={"signature_type": "typed"}
    )

    # Update document
    result = await db.documents.update_one(
        {"id": doc_id, "org_id": org_id},
        {
            "$push": {
                "signatures": signature.model_dump(),
                "audit_trail": audit_entry.model_dump(),
            },
            "$set": {
                "status": DocumentStatus.SIGNED.value,
                "updated_at": datetime.utcnow(),
            },
        },
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    updated_doc = await db.documents.find_one({"id": doc_id})
    return Document(**updated_doc)


@router.get("/{doc_id}/audit", response_model=List[AuditLogEntry])
async def get_audit_trail(org_id: str, doc_id: str, db=Depends(get_db)):
    """Get audit trail for a document"""
    doc = await db.documents.find_one({"id": doc_id, "org_id": org_id})

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    return [AuditLogEntry(**entry) for entry in doc.get("audit_trail", [])]
