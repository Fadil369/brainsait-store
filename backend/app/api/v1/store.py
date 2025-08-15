"""
BrainSAIT Store API - Product and Store Management
Supporting Arabic/English content and ZATCA compliance
"""

import json
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_tenant_id
from app.core.database import get_db
from app.core.localization import LocalizedResponse, get_localized_text
from app.models.store import Cart, CartItem, Category, Order, OrderItem, Product
from app.schemas.store import (
    CartItemCreate,
    CartItemUpdate,
    CartResponse,
    CategoryResponse,
    OrderCreate,
    OrderResponse,
    ProductCreate,
    ProductResponse,
    ProductSearchResponse,
    ProductUpdate,
)

router = APIRouter()

# Product Management Endpoints


@router.get("/products", response_model=ProductSearchResponse)
async def get_products(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(
        None, description="Search in product name/description"
    ),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    status: Optional[str] = Query("active", description="Product status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    lang: str = Query("en", regex="^(en|ar)$", description="Language preference"),
):
    """Get products with filtering, search, and pagination"""

    # Build query
    query = select(Product).where(
        and_(Product.tenant_id == tenant_id, Product.status == status)
    )

    # Apply filters
    if category:
        query = query.where(Product.category == category)

    if min_price is not None:
        query = query.where(Product.price_sar >= min_price)

    if max_price is not None:
        query = query.where(Product.price_sar <= max_price)

    if search:
        search_term = f"%{search}%"
        if lang == "ar":
            query = query.where(
                or_(
                    Product.name_ar.ilike(search_term),
                    Product.description_ar.ilike(search_term),
                )
            )
        else:
            query = query.where(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                )
            )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    # Execute query
    result = await db.execute(query)
    products = result.scalars().all()

    # Convert to response models with localization
    product_responses = []
    for product in products:
        product_data = {
            "id": product.id,
            "name": (
                product.name_ar if lang == "ar" and product.name_ar else product.name
            ),
            "description": (
                product.description_ar
                if lang == "ar" and product.description_ar
                else product.description
            ),
            "price_sar": product.price_sar,
            "original_price_sar": product.original_price_sar,
            "category": product.category,
            "type": product.type,
            "status": product.status,
            "features": product.features or [],
            "demo_data": product.demo_data or {},
            "metadata": product.metadata or {},
            "created_at": product.created_at,
            "updated_at": product.updated_at,
        }
        product_responses.append(ProductResponse(**product_data))

    return ProductSearchResponse(
        products=product_responses,
        total=total,
        page=page,
        limit=limit,
        has_next=offset + limit < total,
        has_prev=page > 1,
    )


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    lang: str = Query("en", regex="^(en|ar)$"),
):
    """Get a specific product by ID"""

    query = select(Product).where(
        and_(Product.id == product_id, Product.tenant_id == tenant_id)
    )

    result = await db.execute(query)
    product = result.scalar_first()

    if not product:
        raise HTTPException(
            status_code=404, detail=get_localized_text("product_not_found", lang)
        )

    # Return localized product data
    return ProductResponse(
        id=product.id,
        name=product.name_ar if lang == "ar" and product.name_ar else product.name,
        description=(
            product.description_ar
            if lang == "ar" and product.description_ar
            else product.description
        ),
        price_sar=product.price_sar,
        original_price_sar=product.original_price_sar,
        category=product.category,
        type=product.type,
        status=product.status,
        features=product.features or [],
        demo_data=product.demo_data or {},
        metadata=product.metadata or {},
        created_at=product.created_at,
        updated_at=product.updated_at,
    )


@router.post("/products", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
):
    """Create a new product (admin only)"""

    # Check if user has admin privileges
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")

    # Create new product
    product = Product(
        tenant_id=tenant_id,
        name=product_data.name,
        name_ar=product_data.name_ar,
        description=product_data.description,
        description_ar=product_data.description_ar,
        price_sar=product_data.price_sar,
        original_price_sar=product_data.original_price_sar,
        category=product_data.category,
        type=product_data.type,
        features=product_data.features or [],
        demo_data=product_data.demo_data or {},
        metadata=product_data.metadata or {},
    )

    db.add(product)
    await db.commit()
    await db.refresh(product)

    return ProductResponse(
        id=product.id,
        name=product.name,
        description=product.description,
        price_sar=product.price_sar,
        original_price_sar=product.original_price_sar,
        category=product.category,
        type=product.type,
        status=product.status,
        features=product.features,
        demo_data=product.demo_data,
        metadata=product.metadata,
        created_at=product.created_at,
        updated_at=product.updated_at,
    )


@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    lang: str = Query("en", regex="^(en|ar)$"),
):
    """Get all product categories"""

    # Get distinct categories from products
    query = (
        select(Product.category, func.count(Product.id).label("product_count"))
        .where(and_(Product.tenant_id == tenant_id, Product.status == "active"))
        .group_by(Product.category)
    )

    result = await db.execute(query)
    categories = result.all()

    category_mapping = {
        "ai": {"en": "AI Solutions", "ar": "حلول الذكاء الاصطناعي"},
        "apps": {"en": "Applications", "ar": "التطبيقات"},
        "websites": {"en": "Websites", "ar": "المواقع الإلكترونية"},
        "templates": {"en": "Templates", "ar": "القوالب"},
        "ebooks": {"en": "eBooks", "ar": "الكتب الإلكترونية"},
        "courses": {"en": "Courses", "ar": "الدورات"},
        "tools": {"en": "Tools", "ar": "الأدوات"},
    }

    category_responses = []
    for category, count in categories:
        category_name = category_mapping.get(category, {}).get(lang, category.title())
        category_responses.append(
            CategoryResponse(id=category, name=category_name, product_count=count)
        )

    return category_responses


# Cart Management Endpoints


@router.get("/cart", response_model=CartResponse)
async def get_cart(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
):
    """Get user's cart contents"""

    # Get or create cart for user
    cart_query = select(Cart).where(
        and_(
            Cart.tenant_id == tenant_id,
            Cart.user_id == current_user.id,
            Cart.status == "active",
        )
    )

    cart_result = await db.execute(cart_query)
    cart = cart_result.scalar_first()

    if not cart:
        # Create new cart
        cart = Cart(tenant_id=tenant_id, user_id=current_user.id, status="active")
        db.add(cart)
        await db.commit()
        await db.refresh(cart)

    # Get cart items with product details
    items_query = select(CartItem).join(Product).where(CartItem.cart_id == cart.id)

    items_result = await db.execute(items_query)
    cart_items = items_result.scalars().all()

    # Calculate totals
    subtotal = sum(item.quantity * item.product.price_sar for item in cart_items)
    tax_rate = 0.15  # Saudi VAT 15%
    tax_amount = subtotal * tax_rate
    total = subtotal + tax_amount

    return CartResponse(
        id=cart.id,
        items=[
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "unit_price": item.product.price_sar,
                "total_price": item.quantity * item.product.price_sar,
            }
            for item in cart_items
        ],
        subtotal=subtotal,
        tax_amount=tax_amount,
        total=total,
        item_count=len(cart_items),
    )


@router.post("/cart/items")
async def add_to_cart(
    item_data: CartItemCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
):
    """Add item to cart"""

    # Verify product exists
    product_query = select(Product).where(
        and_(
            Product.id == item_data.product_id,
            Product.tenant_id == tenant_id,
            Product.status == "active",
        )
    )

    product_result = await db.execute(product_query)
    product = product_result.scalar_first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Get or create cart
    cart_query = select(Cart).where(
        and_(
            Cart.tenant_id == tenant_id,
            Cart.user_id == current_user.id,
            Cart.status == "active",
        )
    )

    cart_result = await db.execute(cart_query)
    cart = cart_result.scalar_first()

    if not cart:
        cart = Cart(tenant_id=tenant_id, user_id=current_user.id, status="active")
        db.add(cart)
        await db.commit()
        await db.refresh(cart)

    # Check if item already exists in cart
    existing_item_query = select(CartItem).where(
        and_(CartItem.cart_id == cart.id, CartItem.product_id == item_data.product_id)
    )

    existing_result = await db.execute(existing_item_query)
    existing_item = existing_result.scalar_first()

    if existing_item:
        # Update quantity
        existing_item.quantity += item_data.quantity
        existing_item.updated_at = datetime.utcnow()
    else:
        # Create new cart item
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
        )
        db.add(cart_item)

    await db.commit()

    return {"message": "Item added to cart successfully"}


@router.delete("/cart/items/{item_id}")
async def remove_from_cart(
    item_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
):
    """Remove item from cart"""

    # Find cart item
    item_query = (
        select(CartItem)
        .join(Cart)
        .where(
            and_(
                CartItem.id == item_id,
                Cart.tenant_id == tenant_id,
                Cart.user_id == current_user.id,
            )
        )
    )

    item_result = await db.execute(item_query)
    cart_item = item_result.scalar_first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    await db.delete(cart_item)
    await db.commit()

    return {"message": "Item removed from cart successfully"}


# Order Management Endpoints


@router.post("/orders", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
):
    """Create a new order from cart or direct items"""

    # Get cart items
    cart_query = select(Cart).where(
        and_(
            Cart.tenant_id == tenant_id,
            Cart.user_id == current_user.id,
            Cart.status == "active",
        )
    )

    cart_result = await db.execute(cart_query)
    cart = cart_result.scalar_first()

    if not cart:
        raise HTTPException(status_code=400, detail="No active cart found")

    # Get cart items
    items_query = select(CartItem).join(Product).where(CartItem.cart_id == cart.id)

    items_result = await db.execute(items_query)
    cart_items = items_result.scalars().all()

    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Calculate totals
    subtotal = sum(item.quantity * item.product.price_sar for item in cart_items)
    tax_rate = 0.15  # Saudi VAT 15%
    tax_amount = subtotal * tax_rate
    total = subtotal + tax_amount

    # Create order
    order = Order(
        tenant_id=tenant_id,
        user_id=current_user.id,
        customer_email=current_user.email,
        total_amount=total,
        tax_amount=tax_amount,
        status="pending",
        billing_address=order_data.billing_address,
        items=[
            {
                "product_id": str(item.product_id),
                "product_name": item.product.name,
                "quantity": item.quantity,
                "unit_price": float(item.product.price_sar),
                "total_price": float(item.quantity * item.product.price_sar),
            }
            for item in cart_items
        ],
    )

    db.add(order)

    # Create order items
    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            unit_price=cart_item.product.price_sar,
            total_price=cart_item.quantity * cart_item.product.price_sar,
        )
        db.add(order_item)

    # Clear cart
    cart.status = "completed"

    await db.commit()
    await db.refresh(order)

    return OrderResponse(
        id=order.id,
        customer_email=order.customer_email,
        total_amount=order.total_amount,
        tax_amount=order.tax_amount,
        status=order.status,
        items=order.items,
        billing_address=order.billing_address,
        created_at=order.created_at,
    )


@router.get("/orders", response_model=List[OrderResponse])
async def get_orders(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """Get user's orders"""

    offset = (page - 1) * limit

    query = (
        select(Order)
        .where(and_(Order.tenant_id == tenant_id, Order.user_id == current_user.id))
        .order_by(Order.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    result = await db.execute(query)
    orders = result.scalars().all()

    return [
        OrderResponse(
            id=order.id,
            customer_email=order.customer_email,
            total_amount=order.total_amount,
            tax_amount=order.tax_amount,
            status=order.status,
            items=order.items,
            billing_address=order.billing_address,
            created_at=order.created_at,
        )
        for order in orders
    ]


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    current_user=Depends(get_current_user),
):
    """Get specific order details"""

    query = select(Order).where(
        and_(
            Order.id == order_id,
            Order.tenant_id == tenant_id,
            Order.user_id == current_user.id,
        )
    )

    result = await db.execute(query)
    order = result.scalar_first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return OrderResponse(
        id=order.id,
        customer_email=order.customer_email,
        total_amount=order.total_amount,
        tax_amount=order.tax_amount,
        status=order.status,
        items=order.items,
        billing_address=order.billing_address,
        created_at=order.created_at,
    )
