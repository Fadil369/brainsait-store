'use client';

import React from 'react';
import Link from 'next/link';
import { useTranslation } from '@/hooks/useTranslation';
import { ShoppingCartIcon } from '@heroicons/react/24/outline';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';
import { useAppStore, useCartStore } from '@/stores';

interface NavigationProps {
  className?: string;
}

export const Navigation: React.FC<NavigationProps> = ({ className }) => {
  const { t } = useTranslation('common');
  const { 
    isMobileMenuOpen, 
    toggleMobileMenu, 
    closeMobileMenu 
  } = useAppStore();
  const { totals, toggleCart } = useCartStore();

  const navItems = [
    { key: 'products', href: '#products' },
    { key: 'solutions', href: '#solutions' },
    { key: 'pricing', href: '#pricing' },
    { key: 'about', href: '#about' },
  ];

  return (
    <nav className={cn(
      'fixed top-0 w-full z-navigation glass border-b border-glass-border animate-slide-down',
      className
    )}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link 
            href="/" 
            className="flex items-center gap-2 group"
          >
            <div className="text-2xl gradient-text-primary transition-transform group-hover:scale-105">
              ◈
            </div>
            <span className="text-xl font-black gradient-text tracking-tight">
              {t('navigation.logo')}
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8 rtl:space-x-reverse">
            {navItems.map((item) => (
              <Link
                key={item.key}
                href={item.href}
                className="relative text-text-secondary hover:text-vision-green transition-colors duration-300 font-medium group"
              >
                {t(`navigation.${item.key}`)}
                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-vision-green transition-all duration-300 group-hover:w-full" />
              </Link>
            ))}
            
            {/* Cart Button */}
            <Button
              variant="gradient"
              size="md"
              onClick={toggleCart}
              className="relative"
              leftIcon={<ShoppingCartIcon className="h-5 w-5" />}
            >
              <span className="hidden sm:inline">
                {t('navigation.cart')}
              </span>
              
              {totals.itemCount > 0 && (
                <span className="absolute -top-2 -right-2 bg-accent text-white rounded-full w-5 h-5 flex items-center justify-center text-xs font-bold border-2 border-dark">
                  {totals.itemCount}
                </span>
              )}
            </Button>
          </div>

          {/* Mobile Menu Button */}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={toggleMobileMenu}
            aria-label={isMobileMenuOpen ? t('accessibility.closeMenu') : t('accessibility.openMenu')}
          >
            <div className={cn('flex flex-col gap-1 transition-transform duration-300', {
              'rotate-45': isMobileMenuOpen
            })}>
              <span className={cn('w-6 h-0.5 bg-text-primary transition-all duration-300', {
                'rotate-90 translate-y-1.5': isMobileMenuOpen
              })} />
              <span className={cn('w-6 h-0.5 bg-text-primary transition-opacity duration-300', {
                'opacity-0': isMobileMenuOpen
              })} />
              <span className={cn('w-6 h-0.5 bg-text-primary transition-all duration-300', {
                'rotate-90 -translate-y-1.5': isMobileMenuOpen
              })} />
            </div>
          </Button>
        </div>
      </div>

      {/* Mobile Menu */}
      <div className={cn(
        'md:hidden fixed top-16 inset-x-0 bg-dark-secondary/98 backdrop-blur-xl border-b border-glass-border transition-all duration-300 z-50',
        {
          'translate-y-0 opacity-100': isMobileMenuOpen,
          '-translate-y-full opacity-0 pointer-events-none': !isMobileMenuOpen
        }
      )}>
        <div className="px-4 py-6 space-y-6">
          {/* Navigation Links */}
          <div className="space-y-4">
            {navItems.map((item) => (
              <Link
                key={item.key}
                href={item.href}
                onClick={closeMobileMenu}
                className="block text-lg font-medium text-text-secondary hover:text-vision-green transition-colors duration-300 py-2"
              >
                {t(`navigation.${item.key}`)}
              </Link>
            ))}
          </div>

          {/* Mobile Cart Button */}
          <div className="pt-4 border-t border-glass-border">
            <Button
              variant="gradient"
              size="lg"
              onClick={() => {
                toggleCart();
                closeMobileMenu();
              }}
              className="w-full relative"
              leftIcon={<ShoppingCartIcon className="h-5 w-5" />}
            >
              {t('navigation.cart')}
              
              {totals.itemCount > 0 && (
                <span className="absolute -top-2 -right-2 bg-accent text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold border-2 border-dark">
                  {totals.itemCount}
                </span>
              )}
            </Button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <div 
          className="md:hidden fixed inset-0 top-16 bg-black/50 backdrop-blur-sm z-40"
          onClick={closeMobileMenu}
        />
      )}
    </nav>
  );
};