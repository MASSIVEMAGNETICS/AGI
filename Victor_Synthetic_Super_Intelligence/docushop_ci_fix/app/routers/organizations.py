from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_db
from app.models.user import Organization

router = APIRouter()


@router.post("/", response_model=Organization, status_code=status.HTTP_201_CREATED)
async def create_organization(org: Organization, db=Depends(get_db)):
    """Create a new organization"""
    org_dict = org.model_dump()
    result = await db.organizations.insert_one(org_dict)

    if not result.inserted_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create organization",
        )

    return org


@router.get("/{org_id}", response_model=Organization)
async def get_organization(org_id: str, db=Depends(get_db)):
    """Get organization by ID"""
    org = await db.organizations.find_one({"id": org_id})

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )

    return Organization(**org)


@router.get("/", response_model=List[Organization])
async def list_organizations(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    """List all organizations"""
    cursor = db.organizations.find().skip(skip).limit(limit)
    orgs = await cursor.to_list(length=limit)
    return [Organization(**org) for org in orgs]


@router.put("/{org_id}", response_model=Organization)
async def update_organization(org_id: str, org_update: dict, db=Depends(get_db)):
    """Update organization"""
    org_update["updated_at"] = datetime.utcnow()

    result = await db.organizations.update_one({"id": org_id}, {"$set": org_update})

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )

    updated_org = await db.organizations.find_one({"id": org_id})
    return Organization(**updated_org)
