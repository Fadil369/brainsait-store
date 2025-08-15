"""
Product management API endpoints
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import and_, asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.dependencies import (
    delete_cache,
    get_cache,
    get_current_admin_user,
    get_current_user,
    get_language,
    get_optional_user,
    get_tenant_id,
    set_cache,
    verify_rate_limit,
)
from app.core.cache import cache_manager, cache_result, cache_invalidate
from app.core.localization import get_localized_field, get_localized_message
from app.models.products import Brand, Category, Product, ProductReview, ProductVariant
from app.models.users import User
from app.schemas.products import (
    BrandCreate,
    BrandResponse,
    BrandUpdate,
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    CategoryWithChildren,
    PaginatedProductsResponse,
    ProductCreate,
    ProductFilters,
    ProductListResponse,
    ProductResponse,
    ProductReviewCreate,
    ProductReviewResponse,
    ProductReviewUpdate,
    ProductSort,
    ProductUpdate,
    ProductVariantCreate,
    ProductVariantResponse,
    ProductVariantUpdate,
)

router = APIRouter()


# Category endpoints
@router.get("/categories", response_model=List[CategoryWithChildren])
async def list_categories(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    language: str = Depends(get_language),
    active_only: bool = Query(True),
    parent_id: Optional[UUID] = Query(None),
):
    """List product categories with hierarchy"""

    # Check cache
    cache_key = f"categories:{tenant_id}:{language}:{active_only}:{parent_id}"
    cached_data = await get_cache(cache_key)
    if cached_data:
        return cached_data

    # Build query
    query = select(Category).where(Category.tenant_id == tenant_id)

    if active_only:
        query = query.where(Category.is_active == True)

    if parent_id:
        query = query.where(Category.parent_id == parent_id)
    else:
        query = query.where(Category.parent_id.is_(None))

    query = query.order_by(Category.sort_order, Category.name)

    result = await db.execute(query)
    categories = result.scalars().all()

    # Build response with children
    response = []
    for category in categories:
        # Get children
        children_query = (
            select(Category)
            .where(
                and_(
                    Category.tenant_id == tenant_id,
                    Category.parent_id == category.id,
                    Category.is_active == True if active_only else True,
                )
            )
            .order_by(Category.sort_order, Category.name)
        )

        children_result = await db.execute(children_query)
        children = children_result.scalars().all()

        category_dict = CategoryWithChildren.from_orm(category).__dict__
        category_dict["children"] = [
            CategoryResponse.from_orm(child).__dict__ for child in children
        ]
        response.append(category_dict)

    # Cache for 1 hour
    await set_cache(cache_key, response, 3600)

    return response


@router.post("/categories", response_model=CategoryResponse)
@cache_invalidate("categories:*")  # Invalidate categories cache
async def create_category(
    category_data: CategoryCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_admin_user),
):
    """Create new product category"""

    # Check if slug exists
    existing_query = select(Category).where(
        and_(Category.tenant_id == tenant_id, Category.slug == category_data.slug)
    )
    result = await db.execute(existing_query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this slug already exists",
        )

    # Calculate level if parent exists
    level = 0
    if category_data.parent_id:
        parent_query = select(Category).where(
            and_(
                Category.tenant_id == tenant_id, Category.id == category_data.parent_id
            )
        )
        parent_result = await db.execute(parent_query)
        parent = parent_result.scalar_one_or_none()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent category not found",
            )
        level = parent.level + 1

    # Create category
    category = Category(tenant_id=tenant_id, level=level, **category_data.dict())

    db.add(category)
    await db.commit()
    await db.refresh(category)

    # Clear cache
    await delete_cache(f"categories:{tenant_id}:*")

    return CategoryResponse.from_orm(category)


@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Get category by ID"""

    query = select(Category).where(
        and_(Category.tenant_id == tenant_id, Category.id == category_id)
    )
    result = await db.execute(query)
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    return CategoryResponse.from_orm(category)


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    category_data: CategoryUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_admin_user),
):
    """Update category"""

    query = select(Category).where(
        and_(Category.tenant_id == tenant_id, Category.id == category_id)
    )
    result = await db.execute(query)
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    # Check slug uniqueness if changed
    if category_data.slug and category_data.slug != category.slug:
        existing_query = select(Category).where(
            and_(
                Category.tenant_id == tenant_id,
                Category.slug == category_data.slug,
                Category.id != category_id,
            )
        )
        existing_result = await db.execute(existing_query)
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this slug already exists",
            )

    # Update fields
    update_data = category_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    await db.commit()
    await db.refresh(category)

    # Clear cache
    await delete_cache(f"categories:{tenant_id}:*")

    return CategoryResponse.from_orm(category)


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_admin_user),
):
    """Delete category"""

    query = select(Category).where(
        and_(Category.tenant_id == tenant_id, Category.id == category_id)
    )
    result = await db.execute(query)
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    # Check for child categories
    children_query = select(Category).where(Category.parent_id == category_id)
    children_result = await db.execute(children_query)
    if children_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category with child categories",
        )

    # Check for products
    products_query = select(Product).where(Product.category_id == category_id)
    products_result = await db.execute(products_query)
    if products_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category with products",
        )

    await db.delete(category)
    await db.commit()

    # Clear cache
    await delete_cache(f"categories:{tenant_id}:*")

    return {"message": "Category deleted successfully"}


# Brand endpoints
@router.get("/brands", response_model=List[BrandResponse])
async def list_brands(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    active_only: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """List product brands"""

    query = select(Brand).where(Brand.tenant_id == tenant_id)

    if active_only:
        query = query.where(Brand.is_active == True)

    query = query.order_by(Brand.name).offset(skip).limit(limit)

    result = await db.execute(query)
    brands = result.scalars().all()

    return [BrandResponse.from_orm(brand) for brand in brands]


@router.post("/brands", response_model=BrandResponse)
async def create_brand(
    brand_data: BrandCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_admin_user),
):
    """Create new brand"""

    # Check if slug exists
    existing_query = select(Brand).where(
        and_(Brand.tenant_id == tenant_id, Brand.slug == brand_data.slug)
    )
    result = await db.execute(existing_query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brand with this slug already exists",
        )

    brand = Brand(tenant_id=tenant_id, **brand_data.dict())
    db.add(brand)
    await db.commit()
    await db.refresh(brand)

    return BrandResponse.from_orm(brand)


# Product endpoints
@router.get("/products", response_model=PaginatedProductsResponse)
async def list_products(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    language: str = Depends(get_language),
    current_user: Optional[User] = Depends(get_optional_user),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort: ProductSort = Query(ProductSort.CREATED_DESC),
    category_ids: Optional[List[UUID]] = Query(None),
    brand_ids: Optional[List[UUID]] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    tags: Optional[List[str]] = Query(None),
    in_stock_only: bool = Query(False),
    featured_only: bool = Query(False),
    search: Optional[str] = Query(None, max_length=255),
    status: Optional[str] = Query(None),
):
    """List products with filters and pagination"""

    # Rate limiting
    await verify_rate_limit(request)

    # Base query
    query = (
        select(Product)
        .options(selectinload(Product.category), selectinload(Product.brand))
        .where(Product.tenant_id == tenant_id)
    )

    # Admin can see all products, users see only active
    if not current_user or not current_user.is_admin:
        query = query.where(and_(Product.is_active == True, Product.status == "active"))
    elif status:
        query = query.where(Product.status == status)

    # Apply filters
    if category_ids:
        query = query.where(Product.category_id.in_(category_ids))

    if brand_ids:
        query = query.where(Product.brand_id.in_(brand_ids))

    if min_price is not None:
        query = query.where(Product.price >= min_price)

    if max_price is not None:
        query = query.where(Product.price <= max_price)

    if tags:
        for tag in tags:
            query = query.where(
                or_(Product.tags.contains([tag]), Product.tags_ar.contains([tag]))
            )

    if in_stock_only:
        query = query.where(Product.stock_quantity > 0)

    if featured_only:
        query = query.where(Product.is_featured == True)

    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Product.name.ilike(search_term),
                Product.name_ar.ilike(search_term),
                Product.description.ilike(search_term),
                Product.description_ar.ilike(search_term),
                Product.sku.ilike(search_term),
            )
        )

    # Apply sorting
    if sort == ProductSort.NAME_ASC:
        query = query.order_by(asc(Product.name))
    elif sort == ProductSort.NAME_DESC:
        query = query.order_by(desc(Product.name))
    elif sort == ProductSort.PRICE_ASC:
        query = query.order_by(asc(Product.price))
    elif sort == ProductSort.PRICE_DESC:
        query = query.order_by(desc(Product.price))
    elif sort == ProductSort.CREATED_ASC:
        query = query.order_by(asc(Product.created_at))
    elif sort == ProductSort.CREATED_DESC:
        query = query.order_by(desc(Product.created_at))
    elif sort == ProductSort.POPULARITY:
        query = query.order_by(desc(Product.purchase_count), desc(Product.view_count))

    # Count total items
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # Apply pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)

    # Execute query
    result = await db.execute(query)
    products = result.scalars().all()

    # Calculate pagination info
    pages = (total + per_page - 1) // per_page
    has_next = page < pages
    has_prev = page > 1

    return PaginatedProductsResponse(
        items=[ProductListResponse.from_orm(product) for product in products],
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
        has_next=has_next,
        has_prev=has_prev,
    )


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    language: str = Depends(get_language),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Get product by ID"""

    query = (
        select(Product)
        .options(
            selectinload(Product.category),
            selectinload(Product.brand),
            selectinload(Product.variants),
        )
        .where(and_(Product.tenant_id == tenant_id, Product.id == product_id))
    )

    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    # Check visibility for non-admin users
    if not current_user or not current_user.is_admin:
        if not product.is_active or product.status != "active":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )

    # Increment view count (don't await to not block response)
    product.view_count += 1
    await db.commit()

    return ProductResponse.from_orm(product)


@router.post("/products", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_admin_user),
):
    """Create new product"""

    # Check if SKU exists
    existing_query = select(Product).where(
        and_(Product.tenant_id == tenant_id, Product.sku == product_data.sku)
    )
    result = await db.execute(existing_query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this SKU already exists",
        )

    # Check if slug exists
    existing_slug_query = select(Product).where(
        and_(Product.tenant_id == tenant_id, Product.slug == product_data.slug)
    )
    slug_result = await db.execute(existing_slug_query)
    if slug_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this slug already exists",
        )

    # Validate category and brand if provided
    if product_data.category_id:
        category_query = select(Category).where(
            and_(
                Category.tenant_id == tenant_id, Category.id == product_data.category_id
            )
        )
        category_result = await db.execute(category_query)
        if not category_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )

    if product_data.brand_id:
        brand_query = select(Brand).where(
            and_(Brand.tenant_id == tenant_id, Brand.id == product_data.brand_id)
        )
        brand_result = await db.execute(brand_query)
        if not brand_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found"
            )

    # Create product
    product = Product(tenant_id=tenant_id, **product_data.dict())

    # Set published date if active
    if product_data.is_active and product_data.status == "active":
        from datetime import datetime

        product.published_at = datetime.utcnow()

    db.add(product)
    await db.commit()
    await db.refresh(product)

    return ProductResponse.from_orm(product)


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    product_data: ProductUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_admin_user),
):
    """Update product"""

    query = select(Product).where(
        and_(Product.tenant_id == tenant_id, Product.id == product_id)
    )
    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    # Check uniqueness constraints
    update_data = product_data.dict(exclude_unset=True)

    if "sku" in update_data and update_data["sku"] != product.sku:
        existing_sku_query = select(Product).where(
            and_(
                Product.tenant_id == tenant_id,
                Product.sku == update_data["sku"],
                Product.id != product_id,
            )
        )
        sku_result = await db.execute(existing_sku_query)
        if sku_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this SKU already exists",
            )

    if "slug" in update_data and update_data["slug"] != product.slug:
        existing_slug_query = select(Product).where(
            and_(
                Product.tenant_id == tenant_id,
                Product.slug == update_data["slug"],
                Product.id != product_id,
            )
        )
        slug_result = await db.execute(existing_slug_query)
        if slug_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this slug already exists",
            )

    # Update fields
    was_published = product.is_active and product.status == "active"

    for field, value in update_data.items():
        setattr(product, field, value)

    # Set published date if becoming active
    is_published = product.is_active and product.status == "active"
    if is_published and not was_published:
        from datetime import datetime

        product.published_at = datetime.utcnow()
    elif not is_published and was_published:
        product.published_at = None

    await db.commit()
    await db.refresh(product)

    return ProductResponse.from_orm(product)


@router.delete("/products/{product_id}")
async def delete_product(
    product_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_admin_user),
):
    """Delete product"""

    query = select(Product).where(
        and_(Product.tenant_id == tenant_id, Product.id == product_id)
    )
    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    await db.delete(product)
    await db.commit()

    return {"message": "Product deleted successfully"}
