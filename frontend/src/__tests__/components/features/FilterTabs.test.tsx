import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { FilterTabs } from '@/components/features/FilterTabs';
import { ProductCategory } from '@/types';

// Mock the translation hook
jest.mock('@/hooks/useTranslation', () => ({
  useTranslation: () => ({
    t: (key: string) => {
      const translations: Record<string, string> = {
        'categories.all': 'All Products',
        'categories.ai': 'AI Solutions',
        'categories.apps': 'Applications',
        'categories.websites': 'Websites',
        'categories.templates': 'Templates',
        'categories.ebooks': 'E-books',
        'categories.courses': 'Courses',
        'categories.tools': 'Tools',
      };
      return translations[key] || key;
    },
  }),
}));

// Mock utils
jest.mock('@/lib/utils', () => ({
  cn: (...classes: (string | undefined)[]) => classes.filter(Boolean).join(' '),
}));

describe('FilterTabs', () => {
  const mockOnFilterChange = jest.fn();
  
  const defaultProps = {
    activeFilter: 'all' as ProductCategory | 'all',
    onFilterChange: mockOnFilterChange,
  };

  const mockProductCounts = {
    all: 100,
    ai: 25,
    apps: 15,
    websites: 20,
    templates: 10,
    ebooks: 8,
    courses: 12,
    tools: 10,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render all filter tabs', () => {
    render(<FilterTabs {...defaultProps} />);
    
    expect(screen.getByText('All Products')).toBeInTheDocument();
    expect(screen.getByText('AI Solutions')).toBeInTheDocument();
    expect(screen.getByText('Applications')).toBeInTheDocument();
    expect(screen.getByText('Websites')).toBeInTheDocument();
    expect(screen.getByText('Templates')).toBeInTheDocument();
    expect(screen.getByText('E-books')).toBeInTheDocument();
    expect(screen.getByText('Courses')).toBeInTheDocument();
    expect(screen.getByText('Tools')).toBeInTheDocument();
  });

  it('should render filter icons', () => {
    render(<FilterTabs {...defaultProps} />);
    
    // Check that emojis are present
    expect(screen.getByText('📦')).toBeInTheDocument(); // all
    expect(screen.getByText('🤖')).toBeInTheDocument(); // ai
    expect(screen.getByText('📱')).toBeInTheDocument(); // apps
    expect(screen.getByText('🌐')).toBeInTheDocument(); // websites
    expect(screen.getByText('📄')).toBeInTheDocument(); // templates
    expect(screen.getByText('📚')).toBeInTheDocument(); // ebooks
    expect(screen.getByText('🎓')).toBeInTheDocument(); // courses
    expect(screen.getByText('🛠️')).toBeInTheDocument(); // tools
  });

  it('should highlight active filter', () => {
    render(<FilterTabs {...defaultProps} activeFilter="ai" />);
    
    const aiButton = screen.getByRole('button', { name: /🤖 AI Solutions/ });
    const allButton = screen.getByRole('button', { name: /📦 All Products/ });
    
    // AI button should have primary variant (active)
    expect(aiButton).toHaveClass('bg-vision-green');
    // All button should have secondary variant (inactive)  
    expect(allButton).toHaveClass('glass');
  });

  it('should call onFilterChange when tab is clicked', () => {
    render(<FilterTabs {...defaultProps} />);
    
    const aiButton = screen.getByRole('button', { name: /🤖 AI Solutions/ });
    fireEvent.click(aiButton);
    
    expect(mockOnFilterChange).toHaveBeenCalledWith('ai');
  });

  it('should display product counts when provided', () => {
    render(<FilterTabs {...defaultProps} productCounts={mockProductCounts} />);
    
    expect(screen.getByText('100')).toBeInTheDocument(); // all
    expect(screen.getByText('25')).toBeInTheDocument(); // ai
    expect(screen.getByText('15')).toBeInTheDocument(); // apps
    expect(screen.getByText('20')).toBeInTheDocument(); // websites
    expect(screen.getAllByText('10')).toHaveLength(2); // templates and tools both have count of 10
    expect(screen.getByText('8')).toBeInTheDocument(); // ebooks
    expect(screen.getByText('12')).toBeInTheDocument(); // courses
  });

  it('should not display count badges when counts are zero', () => {
    const zeroCounts = {
      all: 0,
      ai: 0,
      apps: 0,
      websites: 0,
      templates: 0,
      ebooks: 0,
      courses: 0,
      tools: 0,
    };
    
    render(<FilterTabs {...defaultProps} productCounts={zeroCounts} />);
    
    // Check that no count badges are rendered
    const buttons = screen.getAllByRole('button');
    buttons.forEach(button => {
      expect(button).not.toHaveTextContent(/^\d+$/);
    });
  });

  it('should not display count badges when counts are not provided', () => {
    render(<FilterTabs {...defaultProps} />);
    
    // Check that no count badges are rendered
    const buttons = screen.getAllByRole('button');
    buttons.forEach(button => {
      const textContent = button.textContent || '';
      // Should not contain any standalone numbers
      expect(textContent).not.toMatch(/\s\d+\s*$/);
    });
  });

  it('should handle each category filter correctly', () => {
    render(<FilterTabs {...defaultProps} />);
    
    const categories: (ProductCategory | 'all')[] = ['all', 'ai', 'apps', 'websites', 'templates', 'ebooks', 'courses', 'tools'];
    
    categories.forEach((category) => {
      const buttonTexts = {
        all: 'All Products',
        ai: 'AI Solutions', 
        apps: 'Applications',
        websites: 'Websites',
        templates: 'Templates',
        ebooks: 'E-books',
        courses: 'Courses',
        tools: 'Tools'
      };
      const button = screen.getByRole('button', { name: new RegExp(buttonTexts[category as keyof typeof buttonTexts], 'i') });
      fireEvent.click(button);
      expect(mockOnFilterChange).toHaveBeenCalledWith(category);
    });
    
    expect(mockOnFilterChange).toHaveBeenCalledTimes(categories.length);
  });

  it('should apply custom className', () => {
    const { container } = render(<FilterTabs {...defaultProps} className="custom-class" />);
    
    expect(container.firstChild).toHaveClass('custom-class');
  });

  it('should have proper accessibility attributes', () => {
    render(<FilterTabs {...defaultProps} />);
    
    const buttons = screen.getAllByRole('button');
    expect(buttons).toHaveLength(8); // 8 filter tabs
    
    buttons.forEach(button => {
      expect(button).toBeVisible();
      expect(button).toBeEnabled();
    });
  });

  it('should handle active filter styling for count badges', () => {
    render(<FilterTabs {...defaultProps} activeFilter="ai" productCounts={mockProductCounts} />);
    
    const aiButton = screen.getByRole('button', { name: /🤖 AI Solutions/ });
    const allButton = screen.getByRole('button', { name: /📦 All Products/ });
    
    // Check that the AI button (active) has different styling than inactive buttons
    expect(aiButton).toHaveClass('bg-vision-green');
    expect(allButton).toHaveClass('glass');
  });

  it('should render mobile filter indicator', () => {
    const { container } = render(<FilterTabs {...defaultProps} />);
    
    // Check for the mobile indicator line
    const indicator = container.querySelector('.h-0\\.5');
    expect(indicator).toBeInTheDocument();
    expect(indicator).toHaveClass('bg-gradient-to-r');
  });

  it('should handle scrollable container for mobile', () => {
    const { container } = render(<FilterTabs {...defaultProps} />);
    
    // Check for scrollable container
    const scrollContainer = container.querySelector('.overflow-x-auto');
    expect(scrollContainer).toBeInTheDocument();
    expect(scrollContainer).toHaveClass('scrollbar-hide');
  });

  it('should display correct count styling for active vs inactive tabs', () => {
    render(<FilterTabs {...defaultProps} activeFilter="ai" productCounts={mockProductCounts} />);
    
    const aiButton = screen.getByRole('button', { name: /🤖 AI Solutions/ });
    const allButton = screen.getByRole('button', { name: /📦 All Products/ });
    
    // Both should contain their respective counts
    expect(aiButton).toHaveTextContent('25');
    expect(allButton).toHaveTextContent('100');
  });

  it('should handle partial product counts', () => {
    const partialCounts = {
      all: 50,
      ai: 10,
      // Missing other categories
    };
    
    render(<FilterTabs {...defaultProps} productCounts={partialCounts} />);
    
    expect(screen.getByText('50')).toBeInTheDocument(); // all
    expect(screen.getByText('10')).toBeInTheDocument(); // ai
    
    // Other categories should not have count badges
    const appsButton = screen.getByRole('button', { name: /📱 Applications/ });
    expect(appsButton).not.toHaveTextContent(/\d+/);
  });

  it('should maintain button structure with icons and text', () => {
    render(<FilterTabs {...defaultProps} productCounts={mockProductCounts} />);
    
    const aiButton = screen.getByRole('button', { name: /🤖 AI Solutions/ });
    
    // Should contain icon, text, and count
    expect(aiButton).toHaveTextContent('🤖');
    expect(aiButton).toHaveTextContent('AI Solutions');
    expect(aiButton).toHaveTextContent('25');
  });

  it('should handle click events for all filter types', () => {
    const { rerender } = render(<FilterTabs {...defaultProps} />);
    
    // Test clicking each filter
    const filterTests = [
      { key: 'ai', label: '🤖 AI Solutions' },
      { key: 'apps', label: '📱 Applications' },
      { key: 'websites', label: '🌐 Websites' },
      { key: 'templates', label: '📄 Templates' },
      { key: 'ebooks', label: '📚 E-books' },
      { key: 'courses', label: '🎓 Courses' },
      { key: 'tools', label: '🛠️ Tools' },
      { key: 'all', label: '📦 All Products' },
    ];
    
    filterTests.forEach(({ key, label }) => {
      const button = screen.getByRole('button', { name: new RegExp(label.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')) });
      fireEvent.click(button);
      expect(mockOnFilterChange).toHaveBeenLastCalledWith(key);
    });
  });
});