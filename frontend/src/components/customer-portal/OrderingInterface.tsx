'use client';

import React, { useState } from 'react';
import { useAppStore } from '@/stores';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { 
  MagnifyingGlassIcon, 
  ShoppingCartIcon,
  PlusIcon
} from '@heroicons/react/24/outline';

export function OrderingInterface() {
  const { language } = useAppStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [cart, setCart] = useState<{productId: string; quantity: number}[]>([]);

  // Mock products
  const products = [
    { id: 'P001', name: 'Product A', nameAr: 'منتج أ', price: 150, stock: 45, category: 'Electronics' },
    { id: 'P002', name: 'Product B', nameAr: 'منتج ب', price: 200, stock: 32, category: 'Food' },
    { id: 'P003', name: 'Product C', nameAr: 'منتج ج', price: 85, stock: 120, category: 'Beverages' },
    { id: 'P004', name: 'Product D', nameAr: 'منتج د', price: 320, stock: 18, category: 'Electronics' },
    { id: 'P005', name: 'Product E', nameAr: 'منتج هـ', price: 95, stock: 67, category: 'Food' },
  ];

  const filteredProducts = products.filter(p => 
    p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.nameAr.includes(searchQuery) ||
    p.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const addToCart = (productId: string) => {
    setCart(prev => {
      const existing = prev.find(item => item.productId === productId);
      if (existing) {
        return prev.map(item => 
          item.productId === productId 
            ? { ...item, quantity: item.quantity + 1 } 
            : item
        );
      }
      return [...prev, { productId, quantity: 1 }];
    });
  };

  return (
    <div className="space-y-6">
      <Card className="bg-glass-bg border-white/10">
        <CardHeader>
          <CardTitle className="text-white">
            {language === 'ar' ? 'طلب منتجات جديدة' : 'Order New Products'}
          </CardTitle>
          <CardDescription className="text-gray-300">
            {language === 'ar' 
              ? 'ابحث عن المنتجات وأضفها إلى سلة التسوق' 
              : 'Search for products and add them to your cart'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Search Bar */}
          <div className="mb-6">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <Input
                type="text"
                placeholder={language === 'ar' ? 'ابحث عن المنتجات...' : 'Search products...'}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 bg-white/5 border-white/10 text-white"
              />
            </div>
          </div>

          {/* Products Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
            {filteredProducts.map((product) => (
              <div 
                key={product.id} 
                className="p-4 bg-white/5 border border-white/10 rounded-lg hover:border-vision-green/50 transition-all"
              >
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h3 className="font-semibold text-white">
                      {language === 'ar' ? product.nameAr : product.name}
                    </h3>
                    <p className="text-xs text-gray-400">{product.category}</p>
                  </div>
                  <span className="text-vision-green font-bold">{product.price} SAR</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className={`text-sm ${product.stock < 20 ? 'text-yellow-400' : 'text-gray-400'}`}>
                    {language === 'ar' ? 'المخزون:' : 'Stock:'} {product.stock}
                  </span>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => addToCart(product.id)}
                    className="text-vision-green hover:bg-vision-green/20"
                  >
                    <PlusIcon className="h-4 w-4 mr-1" />
                    {language === 'ar' ? 'أضف' : 'Add'}
                  </Button>
                </div>
              </div>
            ))}
          </div>

          {/* Cart Summary */}
          {cart.length > 0 && (
            <div className="p-4 bg-vision-green/10 border border-vision-green/30 rounded-lg">
              <div className="flex justify-between items-center mb-4">
                <h3 className="font-semibold text-white flex items-center gap-2">
                  <ShoppingCartIcon className="h-5 w-5" />
                  {language === 'ar' ? 'سلة التسوق' : 'Shopping Cart'}
                </h3>
                <span className="text-vision-green font-bold">
                  {cart.reduce((acc, item) => acc + item.quantity, 0)} {language === 'ar' ? 'عنصر' : 'items'}
                </span>
              </div>
              <div className="space-y-2 mb-4">
                {cart.map(item => {
                  const product = products.find(p => p.id === item.productId);
                  return product ? (
                    <div key={item.productId} className="flex justify-between text-sm text-gray-300">
                      <span>{language === 'ar' ? product.nameAr : product.name} x{item.quantity}</span>
                      <span>{product.price * item.quantity} SAR</span>
                    </div>
                  ) : null;
                })}
              </div>
              <div className="flex justify-between items-center pt-4 border-t border-white/10">
                <span className="font-semibold text-white">
                  {language === 'ar' ? 'الإجمالي:' : 'Total:'}
                </span>
                <span className="text-2xl font-bold text-vision-green">
                  {cart.reduce((acc, item) => {
                    const product = products.find(p => p.id === item.productId);
                    return acc + (product ? product.price * item.quantity : 0);
                  }, 0)} SAR
                </span>
              </div>
              <Button variant="gradient" className="w-full mt-4">
                {language === 'ar' ? 'تأكيد الطلب' : 'Confirm Order'}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
