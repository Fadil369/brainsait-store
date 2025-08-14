'use client';

import React from 'react';
import { Navigation } from './Navigation';
import { Footer } from './Footer';
import { Cart } from '@/components/features/Cart';
import { DemoModal } from '@/components/features/DemoModal';
import NotificationContainer from '@/components/ui/NotificationContainer';
import { useProductStore } from '@/stores';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { isDemoOpen, demoProduct, closeDemo } = useProductStore();

  return (
    <div className="min-h-screen bg-dark text-text-primary relative overflow-x-hidden">
      {/* Animated background mesh */}
      <div className="fixed inset-0 z-background">
        <div className="animate-mesh-float" />
      </div>

      {/* Floating geometric shapes */}
      <div className="shape shape-1" />
      <div className="shape shape-2" />
      <div className="shape shape-3" />

      {/* Navigation */}
      <Navigation />

      {/* Main Content */}
      <main className="relative z-10 pt-16">
        {children}
      </main>

      {/* Footer */}
      <Footer />

      {/* Modals and overlays */}
      <Cart />
      <DemoModal 
        isOpen={isDemoOpen}
        onClose={closeDemo}
        product={demoProduct}
      />
      <NotificationContainer />
    </div>
  );
};