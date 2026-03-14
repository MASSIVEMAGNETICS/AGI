from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_db
from app.models.template import Template

router = APIRouter()


@router.post("/", response_model=Template, status_code=status.HTTP_201_CREATED)
async def create_template(org_id: str, template: Template, db=Depends(get_db)):
    """Create a new template"""
    template.org_id = org_id
    template_dict = template.model_dump()

    result = await db.templates.insert_one(template_dict)

    if not result.inserted_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create template",
        )

    return template


@router.get("/{template_id}", response_model=Template)
async def get_template(org_id: str, template_id: str, db=Depends(get_db)):
    """Get template by ID"""
    template = await db.templates.find_one({"id": template_id, "org_id": org_id})

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )

    return Template(**template)


@router.get("/", response_model=List[Template])
async def list_templates(
    org_id: str, skip: int = 0, limit: int = 100, db=Depends(get_db)
):
    """List all templates for an organization"""
    cursor = db.templates.find({"org_id": org_id}).skip(skip).limit(limit)
    templates = await cursor.to_list(length=limit)
    return [Template(**t) for t in templates]


@router.put("/{template_id}", response_model=Template)
async def update_template(
    org_id: str, template_id: str, template_update: dict, db=Depends(get_db)
):
    """Update template"""
    template_update["updated_at"] = datetime.utcnow()

    result = await db.templates.update_one(
        {"id": template_id, "org_id": org_id}, {"$set": template_update}
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )

    updated_template = await db.templates.find_one({"id": template_id})
    return Template(**updated_template)


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(org_id: str, template_id: str, db=Depends(get_db)):
    """Delete template"""
    result = await db.templates.delete_one({"id": template_id, "org_id": org_id})

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )
