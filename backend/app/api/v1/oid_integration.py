"""
BrainSAIT OID System Integration API
Bridges the store system with the existing OID tree for healthcare provider management
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

import requests
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_tenant_id
from app.core.config import settings
from app.core.database import get_db
from app.models.oid import HealthcareProvider, OIDNode
from app.models.store import Order, Product
from app.schemas.oid import (
    HealthcareProviderCreate,
    HealthcareProviderResponse,
    OIDIntegrationMetrics,
    OIDNodeCreate,
    OIDNodeResponse,
    OIDNodeUpdate,
    OIDSyncStatus,
    OIDTreeResponse,
)
from app.services.nphies_integration import NPHIESService
from app.services.obsidian_mcp import ObsidianMCPService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
obsidian_service = ObsidianMCPService()
nphies_service = NPHIESService()


@router.get("/tree", response_model=OIDTreeResponse)
async def get_oid_tree(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    include_metrics: bool = False,
    lang: str = "en",
):
    """Get complete OID tree structure for tenant"""

    try:
        # Get all OID nodes for tenant
        query = (
            select(OIDNode)
            .where(OIDNode.tenant_id == tenant_id)
            .order_by(OIDNode.oid_path)
        )

        result = await db.execute(query)
        nodes = result.scalars().all()

        # Build tree structure
        tree_nodes = []
        for node in nodes:
            node_data = {
                "id": node.id,
                "oid_path": node.oid_path,
                "parent_id": node.parent_id,
                "name": node.name_ar if lang == "ar" and node.name_ar else node.name,
                "description": (
                    node.description_ar
                    if lang == "ar" and node.description_ar
                    else node.description
                ),
                "node_type": node.node_type,
                "status": node.status,
                "metadata": node.metadata or {},
                "neural_capabilities": node.neural_capabilities or [],
                "performance_metrics": (
                    node.performance_metrics or {} if include_metrics else {}
                ),
                "created_at": node.created_at,
                "updated_at": node.updated_at,
            }

            # Add children if any
            children_query = select(OIDNode).where(OIDNode.parent_id == node.id)
            children_result = await db.execute(children_query)
            children = children_result.scalars().all()

            node_data["children"] = [
                {
                    "id": child.id,
                    "oid_path": child.oid_path,
                    "name": (
                        child.name_ar if lang == "ar" and child.name_ar else child.name
                    ),
                    "node_type": child.node_type,
                    "status": child.status,
                }
                for child in children
            ]

            tree_nodes.append(OIDNodeResponse(**node_data))

        # Get integration statistics
        total_nodes = len(nodes)
        active_nodes = len([n for n in nodes if n.status == "active"])
        healthcare_nodes = len(
            [n for n in nodes if n.node_type == "healthcare_provider"]
        )

        return OIDTreeResponse(
            nodes=tree_nodes,
            total_nodes=total_nodes,
            active_nodes=active_nodes,
            healthcare_nodes=healthcare_nodes,
            last_sync=datetime.utcnow(),
            tenant_id=tenant_id,
        )

    except Exception as e:
        logger.error(f"Error fetching OID tree: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch OID tree")


@router.get("/nodes/{node_id}", response_model=OIDNodeResponse)
async def get_oid_node(
    node_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    lang: str = "en",
):
    """Get specific OID node details"""

    query = select(OIDNode).where(
        and_(OIDNode.id == node_id, OIDNode.tenant_id == tenant_id)
    )

    result = await db.execute(query)
    node = result.scalar_first()

    if not node:
        raise HTTPException(status_code=404, detail="OID node not found")

    # Get linked products
    linked_products = []
    if node.metadata and "linked_products" in node.metadata:
        product_ids = node.metadata["linked_products"]
        if product_ids:
            products_query = select(Product).where(Product.id.in_(product_ids))
            products_result = await db.execute(products_query)
            products = products_result.scalars().all()

            linked_products = [
                {
                    "id": str(p.id),
                    "name": p.name,
                    "category": p.category,
                    "price_sar": float(p.price_sar),
                }
                for p in products
            ]

    return OIDNodeResponse(
        id=node.id,
        oid_path=node.oid_path,
        parent_id=node.parent_id,
        name=node.name_ar if lang == "ar" and node.name_ar else node.name,
        description=(
            node.description_ar
            if lang == "ar" and node.description_ar
            else node.description
        ),
        node_type=node.node_type,
        status=node.status,
        metadata=node.metadata or {},
        neural_capabilities=node.neural_capabilities or [],
        performance_metrics=node.performance_metrics or {},
        linked_products=linked_products,
        created_at=node.created_at,
        updated_at=node.updated_at,
    )


@router.post("/nodes", response_model=OIDNodeResponse)
async def create_oid_node(
    node_data: OIDNodeCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
):
    """Create new OID node"""

    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")

    try:
        # Validate OID path format
        if not validate_oid_path(node_data.oid_path):
            raise HTTPException(status_code=400, detail="Invalid OID path format")

        # Check if OID path already exists
        existing_query = select(OIDNode).where(
            and_(OIDNode.oid_path == node_data.oid_path, OIDNode.tenant_id == tenant_id)
        )

        existing_result = await db.execute(existing_query)
        if existing_result.scalar_first():
            raise HTTPException(status_code=400, detail="OID path already exists")

        # Validate parent node if specified
        if node_data.parent_id:
            parent_query = select(OIDNode).where(
                and_(OIDNode.id == node_data.parent_id, OIDNode.tenant_id == tenant_id)
            )
            parent_result = await db.execute(parent_query)
            if not parent_result.scalar_first():
                raise HTTPException(status_code=400, detail="Parent node not found")

        # Create new OID node
        node = OIDNode(
            tenant_id=tenant_id,
            oid_path=node_data.oid_path,
            parent_id=node_data.parent_id,
            name=node_data.name,
            name_ar=node_data.name_ar,
            description=node_data.description,
            description_ar=node_data.description_ar,
            node_type=node_data.node_type,
            metadata=node_data.metadata or {},
            neural_capabilities=node_data.neural_capabilities or [],
        )

        db.add(node)
        await db.commit()
        await db.refresh(node)

        # Sync to Obsidian MCP
        background_tasks.add_task(sync_oid_node_to_obsidian, node.id, "created")

        # If healthcare provider, register with NPHIES
        if node.node_type == "healthcare_provider":
            background_tasks.add_task(register_healthcare_provider_nphies, node.id)

        return OIDNodeResponse(
            id=node.id,
            oid_path=node.oid_path,
            parent_id=node.parent_id,
            name=node.name,
            description=node.description,
            node_type=node.node_type,
            status=node.status,
            metadata=node.metadata,
            neural_capabilities=node.neural_capabilities,
            performance_metrics={},
            created_at=node.created_at,
            updated_at=node.updated_at,
        )

    except Exception as e:
        logger.error(f"Error creating OID node: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create OID node")


@router.post("/nodes/{node_id}/link-product/{product_id}")
async def link_product_to_oid_node(
    node_id: UUID,
    product_id: UUID,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
):
    """Link a store product to an OID node"""

    try:
        # Verify OID node exists
        node_query = select(OIDNode).where(
            and_(OIDNode.id == node_id, OIDNode.tenant_id == tenant_id)
        )

        node_result = await db.execute(node_query)
        node = node_result.scalar_first()

        if not node:
            raise HTTPException(status_code=404, detail="OID node not found")

        # Verify product exists
        product_query = select(Product).where(
            and_(Product.id == product_id, Product.tenant_id == tenant_id)
        )

        product_result = await db.execute(product_query)
        product = product_result.scalar_first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Update product metadata with OID reference
        if not product.metadata:
            product.metadata = {}
        product.metadata["oid_node_id"] = str(node_id)
        product.metadata["oid_path"] = node.oid_path

        # Update OID node metadata with product reference
        if not node.metadata:
            node.metadata = {}
        if "linked_products" not in node.metadata:
            node.metadata["linked_products"] = []

        if str(product_id) not in node.metadata["linked_products"]:
            node.metadata["linked_products"].append(str(product_id))

        # Update timestamps
        node.updated_at = datetime.utcnow()
        product.updated_at = datetime.utcnow()

        await db.commit()

        # Sync changes to Obsidian
        background_tasks.add_task(
            sync_product_oid_link_to_obsidian, product_id, node_id
        )

        return {
            "message": "Product linked to OID node successfully",
            "product_id": str(product_id),
            "node_id": str(node_id),
            "oid_path": node.oid_path,
        }

    except Exception as e:
        logger.error(f"Error linking product to OID node: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to link product to OID node"
        )


@router.get("/healthcare-providers", response_model=List[HealthcareProviderResponse])
async def get_healthcare_providers(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    status: Optional[str] = None,
    lang: str = "en",
):
    """Get healthcare providers linked to OID system"""

    query = (
        select(HealthcareProvider)
        .join(OIDNode)
        .where(HealthcareProvider.tenant_id == tenant_id)
    )

    if status:
        query = query.where(HealthcareProvider.status == status)

    result = await db.execute(query)
    providers = result.scalars().all()

    return [
        HealthcareProviderResponse(
            id=provider.id,
            oid_node_id=provider.oid_node_id,
            provider_name=(
                provider.provider_name_ar
                if lang == "ar" and provider.provider_name_ar
                else provider.provider_name
            ),
            license_number=provider.license_number,
            nphies_id=provider.nphies_id,
            contact_info=provider.contact_info or {},
            services=provider.services or [],
            status=provider.status,
            created_at=provider.created_at,
        )
        for provider in providers
    ]


@router.post("/healthcare-providers", response_model=HealthcareProviderResponse)
async def create_healthcare_provider(
    provider_data: HealthcareProviderCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
):
    """Create new healthcare provider with OID node"""

    try:
        # Create OID node for healthcare provider
        oid_path = generate_healthcare_provider_oid(
            tenant_id, provider_data.license_number
        )

        oid_node = OIDNode(
            tenant_id=tenant_id,
            oid_path=oid_path,
            name=provider_data.provider_name,
            name_ar=provider_data.provider_name_ar,
            description=f"Healthcare Provider: {provider_data.provider_name}",
            node_type="healthcare_provider",
            metadata={
                "license_number": provider_data.license_number,
                "services": provider_data.services or [],
            },
        )

        db.add(oid_node)
        await db.flush()  # Get OID node ID

        # Create healthcare provider record
        provider = HealthcareProvider(
            tenant_id=tenant_id,
            oid_node_id=oid_node.id,
            provider_name=provider_data.provider_name,
            provider_name_ar=provider_data.provider_name_ar,
            license_number=provider_data.license_number,
            contact_info=provider_data.contact_info or {},
            services=provider_data.services or [],
        )

        db.add(provider)
        await db.commit()
        await db.refresh(provider)

        # Register with NPHIES
        background_tasks.add_task(register_provider_with_nphies, provider.id)

        # Sync to Obsidian
        background_tasks.add_task(sync_healthcare_provider_to_obsidian, provider.id)

        return HealthcareProviderResponse(
            id=provider.id,
            oid_node_id=provider.oid_node_id,
            provider_name=provider.provider_name,
            license_number=provider.license_number,
            contact_info=provider.contact_info,
            services=provider.services,
            status=provider.status,
            created_at=provider.created_at,
        )

    except Exception as e:
        logger.error(f"Error creating healthcare provider: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to create healthcare provider"
        )


@router.get("/metrics", response_model=OIDIntegrationMetrics)
async def get_oid_integration_metrics(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
):
    """Get OID system integration metrics"""

    try:
        # Get OID nodes metrics
        nodes_query = select(
            func.count(OIDNode.id).label("total_nodes"),
            func.sum(func.case([(OIDNode.status == "active", 1)], else_=0)).label(
                "active_nodes"
            ),
            func.sum(
                func.case([(OIDNode.node_type == "healthcare_provider", 1)], else_=0)
            ).label("healthcare_nodes"),
        ).where(OIDNode.tenant_id == tenant_id)

        nodes_result = await db.execute(nodes_query)
        nodes_metrics = nodes_result.first()

        # Get product integration metrics
        products_query = select(
            func.count(Product.id).label("total_products"),
            func.sum(
                func.case(
                    [
                        (
                            func.json_extract(Product.metadata, "$.oid_node_id").isnot(
                                None
                            ),
                            1,
                        )
                    ],
                    else_=0,
                )
            ).label("linked_products"),
        ).where(Product.tenant_id == tenant_id)

        products_result = await db.execute(products_query)
        products_metrics = products_result.first()

        # Get order metrics for healthcare products
        healthcare_orders_query = (
            select(
                func.count(Order.id).label("healthcare_orders"),
                func.sum(Order.total_amount).label("healthcare_revenue"),
            )
            .join(Product)
            .where(
                and_(
                    Order.tenant_id == tenant_id,
                    func.json_extract(Product.metadata, "$.oid_node_id").isnot(None),
                )
            )
        )

        orders_result = await db.execute(healthcare_orders_query)
        orders_metrics = orders_result.first()

        return OIDIntegrationMetrics(
            total_oid_nodes=nodes_metrics.total_nodes or 0,
            active_oid_nodes=nodes_metrics.active_nodes or 0,
            healthcare_providers=nodes_metrics.healthcare_nodes or 0,
            total_products=products_metrics.total_products or 0,
            linked_products=products_metrics.linked_products or 0,
            healthcare_orders=orders_metrics.healthcare_orders or 0,
            healthcare_revenue=float(orders_metrics.healthcare_revenue or 0),
            integration_health_score=calculate_integration_health_score(
                nodes_metrics.active_nodes or 0,
                nodes_metrics.total_nodes or 0,
                products_metrics.linked_products or 0,
                products_metrics.total_products or 0,
            ),
            last_sync=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(f"Error fetching OID integration metrics: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch integration metrics"
        )


@router.post("/sync/obsidian")
async def sync_to_obsidian(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
):
    """Manually trigger sync to Obsidian MCP"""

    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")

    background_tasks.add_task(full_obsidian_sync, tenant_id)

    return {
        "message": "Obsidian sync initiated",
        "tenant_id": str(tenant_id),
        "initiated_by": current_user.email,
    }


# Helper functions


def validate_oid_path(oid_path: str) -> bool:
    """Validate OID path format"""
    if not oid_path.startswith("1.3.6.1.4.1.61026"):
        return False

    parts = oid_path.split(".")
    return all(part.isdigit() for part in parts)


def generate_healthcare_provider_oid(tenant_id: UUID, license_number: str) -> str:
    """Generate OID path for healthcare provider"""
    # Base OID for healthcare providers: 1.3.6.1.4.1.61026.1.2
    tenant_segment = str(abs(hash(str(tenant_id))) % 10000)
    license_segment = str(abs(hash(license_number)) % 10000)

    return f"1.3.6.1.4.1.61026.1.2.{tenant_segment}.{license_segment}"


def calculate_integration_health_score(
    active_nodes: int, total_nodes: int, linked_products: int, total_products: int
) -> float:
    """Calculate integration health score"""
    if total_nodes == 0 or total_products == 0:
        return 0.0

    node_health = (active_nodes / total_nodes) * 50
    integration_health = (linked_products / total_products) * 50

    return round(node_health + integration_health, 2)


# Background tasks


async def sync_oid_node_to_obsidian(node_id: UUID, action: str):
    """Sync OID node to Obsidian MCP"""
    try:
        await obsidian_service.sync_oid_node(node_id, action)
        logger.info(f"OID node {node_id} synced to Obsidian ({action})")
    except Exception as e:
        logger.error(f"Failed to sync OID node {node_id} to Obsidian: {e}")


async def sync_product_oid_link_to_obsidian(product_id: UUID, node_id: UUID):
    """Sync product-OID link to Obsidian"""
    try:
        await obsidian_service.sync_product_oid_link(product_id, node_id)
        logger.info(f"Product {product_id} - OID {node_id} link synced to Obsidian")
    except Exception as e:
        logger.error(f"Failed to sync product-OID link to Obsidian: {e}")


async def register_healthcare_provider_nphies(node_id: UUID):
    """Register healthcare provider with NPHIES"""
    try:
        await nphies_service.register_provider_from_oid(node_id)
        logger.info(f"Healthcare provider {node_id} registered with NPHIES")
    except Exception as e:
        logger.error(f"Failed to register provider {node_id} with NPHIES: {e}")


async def register_provider_with_nphies(provider_id: UUID):
    """Register provider with NPHIES system"""
    try:
        await nphies_service.register_provider(provider_id)
        logger.info(f"Provider {provider_id} registered with NPHIES")
    except Exception as e:
        logger.error(f"Failed to register provider {provider_id} with NPHIES: {e}")


async def sync_healthcare_provider_to_obsidian(provider_id: UUID):
    """Sync healthcare provider to Obsidian"""
    try:
        await obsidian_service.sync_healthcare_provider(provider_id)
        logger.info(f"Healthcare provider {provider_id} synced to Obsidian")
    except Exception as e:
        logger.error(
            f"Failed to sync healthcare provider {provider_id} to Obsidian: {e}"
        )


async def full_obsidian_sync(tenant_id: UUID):
    """Perform full sync to Obsidian MCP"""
    try:
        await obsidian_service.full_tenant_sync(tenant_id)
        logger.info(f"Full Obsidian sync completed for tenant {tenant_id}")
    except Exception as e:
        logger.error(f"Full Obsidian sync failed for tenant {tenant_id}: {e}")
