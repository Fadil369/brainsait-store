import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { OrderingInterface } from '@/components/customer-portal/OrderingInterface';
import { useAppStore } from '@/stores';
import '@testing-library/jest-dom';

describe('OrderingInterface Component', () => {
  beforeEach(() => {
    useAppStore.getState().setLanguage('en');
  });

  it('should render ordering interface with search', () => {
    render(<OrderingInterface />);
    
    expect(screen.getByPlaceholderText(/Search products/i)).toBeInTheDocument();
  });

  it('should display products', () => {
    render(<OrderingInterface />);
    
    // Check if at least one product is displayed
    expect(screen.getByText(/Product A/i)).toBeInTheDocument();
  });

  it('should filter products when searching', () => {
    render(<OrderingInterface />);
    
    const searchInput = screen.getByPlaceholderText(/Search products/i);
    fireEvent.change(searchInput, { target: { value: 'Product A' } });
    
    // Product A should be visible
    expect(screen.getByText(/Product A/i)).toBeInTheDocument();
  });

  it('should add product to cart when Add button is clicked', () => {
    render(<OrderingInterface />);
    
    // Find and click the first Add button
    const addButtons = screen.getAllByText(/Add/i);
    fireEvent.click(addButtons[0]);
    
    // Cart summary should appear
    expect(screen.getByText(/Shopping Cart/i)).toBeInTheDocument();
  });
});
