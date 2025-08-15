'use client';

import React, { memo, useMemo, useCallback } from 'react';
import { useTranslation } from '@/hooks/useTranslation';
import { TrashIcon, ShoppingCartIcon } from '@heroicons/react/24/outline';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { useCartStore, useAppStore } from '@/stores';
import { formatPrice } from '@/lib/utils';

// Memoize the empty cart component
const EmptyCart = memo(() => {
  const { t } = useTranslation('common');
  const { closeCart } = useCartStore();

  return (
    <div className="flex flex-col items-center justify-center py-16">
      <ShoppingCartIcon className="h-20 w-20 text-text-secondary mb-4" />
      <h3 className="text-xl font-semibold text-text-primary mb-2">
        {t('cart.empty')}
      </h3>
      <p className="text-text-secondary text-center mb-6">
        Start adding products to see them here
      </p>
      <Button onClick={closeCart}>
        Continue Shopping
      </Button>
    </div>
  );
});

EmptyCart.displayName = 'EmptyCart';

// Memoize individual cart item to prevent unnecessary re-renders
interface CartItemProps {
  item: {
    id: number;
    productId: number;
    title: string;
    arabicTitle?: string;
    price: number;
    quantity: number;
    icon: string;
  };
  language: string;
  onUpdateQuantity: (productId: number, quantity: number) => void;
  onRemoveItem: (productId: number) => void;
}

const CartItem = memo<CartItemProps>(({ item, language, onUpdateQuantity, onRemoveItem }) => {
  const title = useMemo(() => 
    language === 'ar' && item.arabicTitle 
      ? item.arabicTitle 
      : item.title, [language, item.arabicTitle, item.title]
  );

  const handleDecrease = useCallback(() => {
    onUpdateQuantity(item.productId, item.quantity - 1);
  }, [onUpdateQuantity, item.productId, item.quantity]);

  const handleIncrease = useCallback(() => {
    onUpdateQuantity(item.productId, item.quantity + 1);
  }, [onUpdateQuantity, item.productId, item.quantity]);

  const handleRemove = useCallback(() => {
    onRemoveItem(item.productId);
  }, [onRemoveItem, item.productId]);

  return (
    <div className="glass rounded-xl p-4 flex items-center gap-4 animate-slide-in">
      {/* Product Icon */}
      <div className="w-12 h-12 bg-gradient-glass border border-vision-green/30 rounded-xl flex items-center justify-center text-xl flex-shrink-0">
        {item.icon}
      </div>

      {/* Product Info */}
      <div className="flex-1 min-w-0">
        <h4 className="font-semibold text-text-primary truncate mb-1">
          {title}
        </h4>
        <p className="text-vision-green font-semibold text-sm">
          {formatPrice(item.price, language)}
        </p>
      </div>

      {/* Quantity Controls */}
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          onClick={handleDecrease}
          className="w-8 h-8"
          disabled={item.quantity <= 1}
        >
          -
        </Button>
        
        <span className="w-8 text-center font-semibold text-text-primary">
          {item.quantity}
        </span>
        
        <Button
          variant="ghost"
          size="icon"
          onClick={handleIncrease}
          className="w-8 h-8"
        >
          +
        </Button>
      </div>

      {/* Remove Button */}
      <Button
        variant="ghost"
        size="icon"
        onClick={handleRemove}
        className="text-red-400 hover:text-red-300 hover:bg-red-500/10 w-8 h-8"
        aria-label={`Remove ${title} from cart`}
      >
        <TrashIcon className="h-4 w-4" />
      </Button>
    </div>
  );
});

CartItem.displayName = 'CartItem';

// Memoize cart totals component
interface CartTotalsProps {
  totals: {
    subtotal: number;
    tax: number;
    total: number;
  };
  language: string;
}

const CartTotals = memo<CartTotalsProps>(({ totals, language }) => {
  const { t } = useTranslation('common');

  return (
    <div className="glass rounded-xl p-6 space-y-3">
      <div className="flex justify-between text-text-secondary">
        <span>{t('cart.subtotal')}</span>
        <span>{formatPrice(totals.subtotal, language)}</span>
      </div>
      
      <div className="flex justify-between text-text-secondary">
        <span>{t('cart.vat')}</span>
        <span>{formatPrice(totals.tax, language)}</span>
      </div>
      
      <div className="h-px bg-glass-border" />
      
      <div className="flex justify-between text-lg font-bold text-text-primary">
        <span>{t('cart.total')}</span>
        <span className="text-vision-green">
          {formatPrice(totals.total, language)}
        </span>
      </div>
    </div>
  );
});

CartTotals.displayName = 'CartTotals';

const CartComponent: React.FC = () => {
  const { t } = useTranslation('common');
  const { language } = useAppStore();
  const {
    items,
    totals,
    isOpen,
    closeCart,
    removeItem,
    updateQuantity,
    clearCart,
  } = useCartStore();

  // Memoize cart items to prevent unnecessary re-renders
  const cartItems = useMemo(() => 
    items.map((item) => (
      <CartItem
        key={item.id}
        item={item}
        language={language}
        onUpdateQuantity={updateQuantity}
        onRemoveItem={removeItem}
      />
    )), [items, language, updateQuantity, removeItem]
  );

  const handleCheckout = useCallback(() => {
    // In a real application, this would redirect to a payment processor
    // For now, we'll just show an alert
    alert('This would redirect to the payment gateway in a real application.');
    closeCart();
  }, [closeCart]);

  const isEmpty = items.length === 0;
  const hasMultipleItems = items.length > 1;

  return (
    <Modal
      isOpen={isOpen}
      onClose={closeCart}
      title={t('cart.title')}
      size="lg"
      className="cart-modal"
    >
      {isEmpty ? (
        <EmptyCart />
      ) : (
        <div className="space-y-6">
          {/* Cart Items */}
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {cartItems}
          </div>

          {/* Clear Cart */}
          {hasMultipleItems && (
            <div className="flex justify-end">
              <Button
                variant="ghost"
                size="sm"
                onClick={clearCart}
                className="text-text-secondary hover:text-red-400"
              >
                Clear All Items
              </Button>
            </div>
          )}

          {/* Cart Totals */}
          <CartTotals totals={totals} language={language} />

          {/* Checkout Button */}
          <Button
            variant="gradient"
            size="lg"
            onClick={handleCheckout}
            className="w-full"
          >
            {t('cart.checkout')}
          </Button>

          {/* Payment Methods Info */}
          <div className="text-center text-sm text-text-secondary">
            <p>We accept Mada, Visa, Mastercard, STC Pay, and Apple Pay</p>
            <p className="mt-1">Secure checkout powered by Stripe</p>
          </div>
        </div>
      )}
    </Modal>
  );
};

export const Cart = memo(CartComponent);