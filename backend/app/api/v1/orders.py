"""
Order and cart management API endpoints
"""

import secrets
import string
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import and_, asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.dependencies import (
    get_current_admin_user,
    get_current_user,
    get_language,
    get_optional_user,
    get_tenant_id,
    verify_rate_limit,
)
from app.core.localization import get_localized_message
from app.models.orders import CartItem, Coupon, Order, OrderItem, OrderStatusHistory
from app.models.products import Product, ProductVariant
from app.models.users import User
from app.schemas.orders import (
    CartItemCreate,
    CartItemResponse,
    CartItemUpdate,
    CartSummary,
    CheckoutRequest,
    CheckoutResponse,
    CouponCreate,
    CouponResponse,
    CouponUpdate,
    CouponValidationRequest,
    CouponValidationResponse,
    OrderCreate,
    OrderListResponse,
    OrderResponse,
    OrderStatusHistoryResponse,
    OrderUpdate,
    PaginatedOrdersResponse,
)

router = APIRouter()


def generate_order_number() -> str:
    """Generate unique order number"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_part = "".join(
        secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6)
    )
    return f"ORD-{timestamp}-{random_part}"


# Cart endpoints
@router.get("/cart", response_model=CartSummary)
async def get_cart(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Get user's shopping cart"""

    # Get cart items with product details
    query = (
        select(CartItem)
        .options(selectinload(CartItem.product), selectinload(CartItem.variant))
        .where(
            and_(CartItem.user_id == current_user.id, CartItem.tenant_id == tenant_id)
        )
        .order_by(CartItem.created_at)
    )

    result = await db.execute(query)
    cart_items = result.scalars().all()

    # Build response
    items = []
    subtotal = 0

    for cart_item in cart_items:
        product = cart_item.product
        variant = cart_item.variant

        # Skip if product is not available
        if not product or not product.is_active:
            continue

        # Use variant price if available, otherwise product price
        unit_price = (
            float(variant.price) if variant and variant.price else float(product.price)
        )
        total_price = unit_price * cart_item.quantity
        subtotal += total_price

        # Get product image
        product_image = None
        if product.images and len(product.images) > 0:
            product_image = product.images[0]
        elif variant and variant.image_url:
            product_image = variant.image_url

        item_response = CartItemResponse(
            id=cart_item.id,
            product_id=cart_item.product_id,
            variant_id=cart_item.variant_id,
            quantity=cart_item.quantity,
            unit_price=unit_price,
            total_price=total_price,
            created_at=cart_item.created_at,
            updated_at=cart_item.updated_at,
            product_name=product.name,
            product_name_ar=product.name_ar,
            product_sku=variant.sku if variant else product.sku,
            product_image=product_image,
            product_slug=product.slug,
            variant_name=variant.name if variant else None,
            variant_options=variant.options if variant else None,
        )
        items.append(item_response)

    # Calculate tax (15% VAT for Saudi Arabia)
    tax_rate = 0.15
    tax_amount = subtotal * tax_rate
    total_amount = subtotal + tax_amount

    return CartSummary(
        items=items,
        subtotal=subtotal,
        tax_amount=tax_amount,
        total_amount=total_amount,
        item_count=len(items),
        currency="SAR",
    )


@router.post("/cart/items", response_model=CartItemResponse)
async def add_to_cart(
    item_data: CartItemCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Add item to shopping cart"""

    # Verify product exists and is available
    product_query = select(Product).where(
        and_(
            Product.id == item_data.product_id,
            Product.tenant_id == tenant_id,
            Product.is_active == True,
        )
    )
    product_result = await db.execute(product_query)
    product = product_result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or not available",
        )

    # Verify variant if specified
    variant = None
    if item_data.variant_id:
        variant_query = select(ProductVariant).where(
            and_(
                ProductVariant.id == item_data.variant_id,
                ProductVariant.product_id == item_data.product_id,
                ProductVariant.is_active == True,
            )
        )
        variant_result = await db.execute(variant_query)
        variant = variant_result.scalar_one_or_none()

        if not variant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product variant not found or not available",
            )

    # Check stock availability
    available_stock = variant.stock_quantity if variant else product.stock_quantity
    if product.track_inventory and available_stock < item_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient stock available",
        )

    # Check if item already exists in cart
    existing_query = select(CartItem).where(
        and_(
            CartItem.user_id == current_user.id,
            CartItem.product_id == item_data.product_id,
            CartItem.variant_id == item_data.variant_id,
            CartItem.tenant_id == tenant_id,
        )
    )
    existing_result = await db.execute(existing_query)
    existing_item = existing_result.scalar_one_or_none()

    if existing_item:
        # Update quantity
        new_quantity = existing_item.quantity + item_data.quantity

        # Check stock again
        if product.track_inventory and available_stock < new_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient stock available",
            )

        existing_item.quantity = new_quantity
        existing_item.updated_at = datetime.utcnow()
        cart_item = existing_item
    else:
        # Create new cart item
        unit_price = (
            float(variant.price) if variant and variant.price else float(product.price)
        )

        cart_item = CartItem(
            user_id=current_user.id,
            product_id=item_data.product_id,
            variant_id=item_data.variant_id,
            tenant_id=tenant_id,
            quantity=item_data.quantity,
            unit_price=unit_price,
        )
        db.add(cart_item)

    await db.commit()
    await db.refresh(cart_item)

    # Build response
    unit_price = float(cart_item.unit_price)
    total_price = unit_price * cart_item.quantity

    product_image = None
    if product.images and len(product.images) > 0:
        product_image = product.images[0]
    elif variant and variant.image_url:
        product_image = variant.image_url

    return CartItemResponse(
        id=cart_item.id,
        product_id=cart_item.product_id,
        variant_id=cart_item.variant_id,
        quantity=cart_item.quantity,
        unit_price=unit_price,
        total_price=total_price,
        created_at=cart_item.created_at,
        updated_at=cart_item.updated_at,
        product_name=product.name,
        product_name_ar=product.name_ar,
        product_sku=variant.sku if variant else product.sku,
        product_image=product_image,
        product_slug=product.slug,
        variant_name=variant.name if variant else None,
        variant_options=variant.options if variant else None,
    )


@router.put("/cart/items/{item_id}", response_model=CartItemResponse)
async def update_cart_item(
    item_id: UUID,
    item_data: CartItemUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Update cart item quantity"""

    # Get cart item
    query = (
        select(CartItem)
        .options(selectinload(CartItem.product), selectinload(CartItem.variant))
        .where(
            and_(
                CartItem.id == item_id,
                CartItem.user_id == current_user.id,
                CartItem.tenant_id == tenant_id,
            )
        )
    )
    result = await db.execute(query)
    cart_item = result.scalar_one_or_none()

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found"
        )

    product = cart_item.product
    variant = cart_item.variant

    # Check stock availability
    if product.track_inventory:
        available_stock = variant.stock_quantity if variant else product.stock_quantity
        if available_stock < item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient stock available",
            )

    # Update quantity
    cart_item.quantity = item_data.quantity
    cart_item.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(cart_item)

    # Build response
    unit_price = float(cart_item.unit_price)
    total_price = unit_price * cart_item.quantity

    product_image = None
    if product.images and len(product.images) > 0:
        product_image = product.images[0]
    elif variant and variant.image_url:
        product_image = variant.image_url

    return CartItemResponse(
        id=cart_item.id,
        product_id=cart_item.product_id,
        variant_id=cart_item.variant_id,
        quantity=cart_item.quantity,
        unit_price=unit_price,
        total_price=total_price,
        created_at=cart_item.created_at,
        updated_at=cart_item.updated_at,
        product_name=product.name,
        product_name_ar=product.name_ar,
        product_sku=variant.sku if variant else product.sku,
        product_image=product_image,
        product_slug=product.slug,
        variant_name=variant.name if variant else None,
        variant_options=variant.options if variant else None,
    )


@router.delete("/cart/items/{item_id}")
async def remove_cart_item(
    item_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Remove item from cart"""

    query = select(CartItem).where(
        and_(
            CartItem.id == item_id,
            CartItem.user_id == current_user.id,
            CartItem.tenant_id == tenant_id,
        )
    )
    result = await db.execute(query)
    cart_item = result.scalar_one_or_none()

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found"
        )

    await db.delete(cart_item)
    await db.commit()

    return {"message": "Item removed from cart"}


@router.delete("/cart")
async def clear_cart(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Clear all items from cart"""

    query = select(CartItem).where(
        and_(CartItem.user_id == current_user.id, CartItem.tenant_id == tenant_id)
    )
    result = await db.execute(query)
    cart_items = result.scalars().all()

    for item in cart_items:
        await db.delete(item)

    await db.commit()

    return {"message": "Cart cleared"}


# Order endpoints
@router.get("/orders", response_model=PaginatedOrdersResponse)
async def list_orders(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
):
    """List user's orders"""

    # Build query
    query = select(Order).where(
        and_(Order.user_id == current_user.id, Order.tenant_id == tenant_id)
    )

    # Apply status filter
    if status_filter:
        query = query.where(Order.status == status_filter)

    # Order by creation date (newest first)
    query = query.order_by(desc(Order.created_at))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # Apply pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)

    # Execute query
    result = await db.execute(query)
    orders = result.scalars().all()

    # Build response
    items = []
    for order in orders:
        # Get item count
        item_count_query = select(func.count(OrderItem.id)).where(
            OrderItem.order_id == order.id
        )
        item_count_result = await db.execute(item_count_query)
        item_count = item_count_result.scalar() or 0

        items.append(
            OrderListResponse(
                id=order.id,
                order_number=order.order_number,
                status=order.status,
                payment_status=order.payment_status,
                shipping_status=order.shipping_status,
                customer_name=order.customer_name,
                total_amount=float(order.total_amount),
                currency=order.currency,
                item_count=item_count,
                created_at=order.created_at,
            )
        )

    # Calculate pagination info
    pages = (total + per_page - 1) // per_page
    has_next = page < pages
    has_prev = page > 1

    return PaginatedOrdersResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
        has_next=has_next,
        has_prev=has_prev,
    )


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Get order details"""

    # Get order with items
    query = (
        select(Order)
        .options(selectinload(Order.items))
        .where(
            and_(
                Order.id == order_id,
                Order.user_id == current_user.id,
                Order.tenant_id == tenant_id,
            )
        )
    )
    result = await db.execute(query)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    return OrderResponse.from_orm(order)


@router.post("/checkout", response_model=CheckoutResponse)
async def checkout(
    checkout_data: CheckoutRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """Process checkout and create order"""

    # Get cart items
    cart_query = (
        select(CartItem)
        .options(selectinload(CartItem.product), selectinload(CartItem.variant))
        .where(
            and_(CartItem.user_id == current_user.id, CartItem.tenant_id == tenant_id)
        )
    )
    cart_result = await db.execute(cart_query)
    cart_items = cart_result.scalars().all()

    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty"
        )

    # Validate stock and calculate totals
    subtotal = 0
    order_items = []

    for cart_item in cart_items:
        product = cart_item.product
        variant = cart_item.variant

        if not product or not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {product.name if product else 'Unknown'} is no longer available",
            )

        # Check stock
        if product.track_inventory:
            available_stock = (
                variant.stock_quantity if variant else product.stock_quantity
            )
            if available_stock < cart_item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for {product.name}",
                )

        # Calculate pricing
        unit_price = (
            float(variant.price) if variant and variant.price else float(product.price)
        )
        line_total = unit_price * cart_item.quantity
        subtotal += line_total

        # Calculate tax
        tax_rate = float(product.tax_rate) if not product.is_tax_exempt else 0
        tax_amount = line_total * (tax_rate / 100)

        order_items.append(
            {
                "product_id": cart_item.product_id,
                "variant_id": cart_item.variant_id,
                "product_name": product.name,
                "product_name_ar": product.name_ar,
                "product_sku": variant.sku if variant else product.sku,
                "variant_name": variant.name if variant else None,
                "variant_options": variant.options if variant else None,
                "quantity": cart_item.quantity,
                "unit_price": unit_price,
                "total_price": line_total,
                "tax_rate": tax_rate,
                "tax_amount": tax_amount,
                "product_image": (
                    product.images[0]
                    if product.images
                    else (variant.image_url if variant else None)
                ),
            }
        )

    # Calculate totals
    tax_amount = sum(item["tax_amount"] for item in order_items)
    shipping_cost = 0  # TODO: Calculate based on shipping method
    discount_amount = 0  # TODO: Apply coupon if provided
    total_amount = subtotal + tax_amount + shipping_cost - discount_amount

    # Generate order number
    order_number = generate_order_number()

    # Create order
    order = Order(
        order_number=order_number,
        user_id=current_user.id,
        tenant_id=tenant_id,
        status="pending",
        payment_status="pending",
        shipping_status="pending",
        customer_email=checkout_data.billing_address.first_name
        + " "
        + checkout_data.billing_address.last_name,
        customer_phone=checkout_data.billing_address.phone,
        customer_name=checkout_data.billing_address.first_name
        + " "
        + checkout_data.billing_address.last_name,
        billing_address=checkout_data.billing_address.dict(),
        shipping_address=checkout_data.shipping_address.dict(),
        shipping_method=checkout_data.shipping_method,
        shipping_cost=shipping_cost,
        subtotal=subtotal,
        tax_amount=tax_amount,
        discount_amount=discount_amount,
        total_amount=total_amount,
        currency="SAR",
        payment_method=checkout_data.payment_method,
        coupon_code=checkout_data.coupon_code,
        customer_notes=checkout_data.customer_notes,
    )

    db.add(order)
    await db.flush()  # Get order ID

    # Create order items
    for item_data in order_items:
        order_item = OrderItem(order_id=order.id, tenant_id=tenant_id, **item_data)
        db.add(order_item)

    # Create status history
    status_history = OrderStatusHistory(
        order_id=order.id,
        tenant_id=tenant_id,
        from_status=None,
        to_status="pending",
        comment="Order created",
        changed_by_user_id=current_user.id,
    )
    db.add(status_history)

    # Clear cart
    for cart_item in cart_items:
        await db.delete(cart_item)

    await db.commit()
    await db.refresh(order)

    # Prepare response
    payment_required = checkout_data.payment_method not in ["cash_on_delivery"]

    return CheckoutResponse(
        order_id=order.id,
        order_number=order.order_number,
        total_amount=float(total_amount),
        currency="SAR",
        payment_required=payment_required,
    )


# Admin order endpoints
@router.get("/admin/orders", response_model=PaginatedOrdersResponse)
async def list_all_orders(
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_admin_user),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
):
    """List all orders (admin only)"""

    # Build query
    query = select(Order).where(Order.tenant_id == tenant_id)

    # Apply filters
    if status_filter:
        query = query.where(Order.status == status_filter)

    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Order.order_number.ilike(search_term),
                Order.customer_name.ilike(search_term),
                Order.customer_email.ilike(search_term),
            )
        )

    # Order by creation date (newest first)
    query = query.order_by(desc(Order.created_at))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # Apply pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)

    # Execute query
    result = await db.execute(query)
    orders = result.scalars().all()

    # Build response
    items = []
    for order in orders:
        # Get item count
        item_count_query = select(func.count(OrderItem.id)).where(
            OrderItem.order_id == order.id
        )
        item_count_result = await db.execute(item_count_query)
        item_count = item_count_result.scalar() or 0

        items.append(
            OrderListResponse(
                id=order.id,
                order_number=order.order_number,
                status=order.status,
                payment_status=order.payment_status,
                shipping_status=order.shipping_status,
                customer_name=order.customer_name,
                total_amount=float(order.total_amount),
                currency=order.currency,
                item_count=item_count,
                created_at=order.created_at,
            )
        )

    # Calculate pagination info
    pages = (total + per_page - 1) // per_page
    has_next = page < pages
    has_prev = page > 1

    return PaginatedOrdersResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
        has_next=has_next,
        has_prev=has_prev,
    )


@router.put("/admin/orders/{order_id}", response_model=OrderResponse)
async def update_order_status(
    order_id: UUID,
    order_data: OrderUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_admin_user),
):
    """Update order status (admin only)"""

    # Get order
    query = (
        select(Order)
        .options(selectinload(Order.items))
        .where(and_(Order.id == order_id, Order.tenant_id == tenant_id))
    )
    result = await db.execute(query)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    # Track status changes
    original_status = order.status
    update_data = order_data.dict(exclude_unset=True)

    # Update fields
    for field, value in update_data.items():
        setattr(order, field, value)

    # Set timestamps for status changes
    if "status" in update_data:
        if update_data["status"] == "confirmed" and not order.confirmed_at:
            order.confirmed_at = datetime.utcnow()
        elif update_data["status"] == "shipped" and not order.shipped_at:
            order.shipped_at = datetime.utcnow()
        elif update_data["status"] == "delivered" and not order.delivered_at:
            order.delivered_at = datetime.utcnow()
        elif update_data["status"] == "cancelled" and not order.cancelled_at:
            order.cancelled_at = datetime.utcnow()

    # Create status history if status changed
    if "status" in update_data and update_data["status"] != original_status:
        status_history = OrderStatusHistory(
            order_id=order.id,
            tenant_id=tenant_id,
            from_status=original_status,
            to_status=update_data["status"],
            comment=f"Status updated by admin",
            changed_by_user_id=current_user.id,
        )
        db.add(status_history)

    await db.commit()
    await db.refresh(order)

    return OrderResponse.from_orm(order)
