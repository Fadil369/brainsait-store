import React from 'react';
import { render, screen } from '@testing-library/react';
import { CustomerPortalDashboard } from '@/components/customer-portal/CustomerPortalDashboard';
import { useAppStore } from '@/stores';
import '@testing-library/jest-dom';

describe('CustomerPortalDashboard Component', () => {
  beforeEach(() => {
    // Reset app store to clean state
    useAppStore.getState().setLanguage('en');
  });

  it('should render customer portal dashboard with all tabs', () => {
    render(<CustomerPortalDashboard />);
    
    // Check if main title is rendered
    expect(screen.getByText('Customer Portal')).toBeInTheDocument();
    
    // Check if all tabs are present
    expect(screen.getByText('Overview')).toBeInTheDocument();
    expect(screen.getByText('Ordering')).toBeInTheDocument();
    expect(screen.getByText('Inventory')).toBeInTheDocument();
    expect(screen.getByText('Payments')).toBeInTheDocument();
    expect(screen.getByText('Promotions')).toBeInTheDocument();
    expect(screen.getByText('AI Recommendations')).toBeInTheDocument();
    expect(screen.getByText('Complaints')).toBeInTheDocument();
  });

  it('should render in Arabic when language is set to ar', () => {
    // Set language to Arabic
    useAppStore.getState().setLanguage('ar');
    
    render(<CustomerPortalDashboard />);
    
    // Check if Arabic title is rendered
    expect(screen.getByText('بوابة العملاء')).toBeInTheDocument();
  });

  it('should render dashboard overview by default', () => {
    render(<CustomerPortalDashboard />);
    
    // Dashboard stats should be visible
    expect(screen.getByText(/Total Orders/i)).toBeInTheDocument();
    expect(screen.getByText(/Available Products/i)).toBeInTheDocument();
  });
});
