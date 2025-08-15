import React from 'react';
import { render, screen } from '@testing-library/react';
import { Badge } from '@/components/ui/Badge';
import '@testing-library/jest-dom';

describe('Badge', () => {
  it('should render children content', () => {
    render(<Badge>Test Badge</Badge>);
    
    expect(screen.getByText('Test Badge')).toBeInTheDocument();
  });

  it('should apply default variant and size classes', () => {
    render(<Badge>Default Badge</Badge>);
    
    const badge = screen.getByText('Default Badge');
    expect(badge).toHaveClass('bg-gray/20', 'text-text-secondary', 'text-xs', 'px-2.5', 'py-1');
  });

  describe('Variants', () => {
    it('should apply new variant classes', () => {
      render(<Badge variant="new">New Badge</Badge>);
      
      const badge = screen.getByText('New Badge');
      expect(badge).toHaveClass('bg-vision-green', 'text-dark');
    });

    it('should apply hot variant classes', () => {
      render(<Badge variant="hot">Hot Badge</Badge>);
      
      const badge = screen.getByText('Hot Badge');
      expect(badge).toHaveClass('bg-gradient-accent', 'text-white', 'animate-pulse-glow');
    });

    it('should apply pro variant classes', () => {
      render(<Badge variant="pro">Pro Badge</Badge>);
      
      const badge = screen.getByText('Pro Badge');
      expect(badge).toHaveClass('bg-vision-purple', 'text-white');
    });

    it('should apply vision2030 variant classes', () => {
      render(<Badge variant="vision2030">Vision2030 Badge</Badge>);
      
      const badge = screen.getByText('Vision2030 Badge');
      expect(badge).toHaveClass('bg-gradient-primary', 'text-white');
    });

    it('should apply secondary variant classes', () => {
      render(<Badge variant="secondary">Secondary Badge</Badge>);
      
      const badge = screen.getByText('Secondary Badge');
      expect(badge).toHaveClass('bg-secondary', 'text-secondary-foreground', 'hover:bg-secondary/80');
    });

    it('should apply success variant classes', () => {
      render(<Badge variant="success">Success Badge</Badge>);
      
      const badge = screen.getByText('Success Badge');
      expect(badge).toHaveClass('bg-success', 'text-white');
    });

    it('should apply warning variant classes', () => {
      render(<Badge variant="warning">Warning Badge</Badge>);
      
      const badge = screen.getByText('Warning Badge');
      expect(badge).toHaveClass('bg-warning', 'text-white');
    });

    it('should apply error variant classes', () => {
      render(<Badge variant="error">Error Badge</Badge>);
      
      const badge = screen.getByText('Error Badge');
      expect(badge).toHaveClass('bg-red-500', 'text-white');
    });

    it('should apply outline variant classes', () => {
      render(<Badge variant="outline">Outline Badge</Badge>);
      
      const badge = screen.getByText('Outline Badge');
      expect(badge).toHaveClass('border', 'border-input', 'bg-background', 'hover:bg-accent', 'hover:text-accent-foreground');
    });
  });

  describe('Sizes', () => {
    it('should apply sm size classes', () => {
      render(<Badge size="sm">Small Badge</Badge>);
      
      const badge = screen.getByText('Small Badge');
      expect(badge).toHaveClass('text-xs', 'px-2', 'py-0.5');
    });

    it('should apply md size classes (default)', () => {
      render(<Badge size="md">Medium Badge</Badge>);
      
      const badge = screen.getByText('Medium Badge');
      expect(badge).toHaveClass('text-xs', 'px-2.5', 'py-1');
    });

    it('should apply lg size classes', () => {
      render(<Badge size="lg">Large Badge</Badge>);
      
      const badge = screen.getByText('Large Badge');
      expect(badge).toHaveClass('text-sm', 'px-3', 'py-1.5');
    });
  });

  describe('Variant and Size Combinations', () => {
    it('should apply both variant and size classes correctly', () => {
      render(<Badge variant="new" size="lg">Large New Badge</Badge>);
      
      const badge = screen.getByText('Large New Badge');
      expect(badge).toHaveClass('bg-vision-green', 'text-dark', 'text-sm', 'px-3', 'py-1.5');
    });

    it('should apply hot variant with small size', () => {
      render(<Badge variant="hot" size="sm">Small Hot Badge</Badge>);
      
      const badge = screen.getByText('Small Hot Badge');
      expect(badge).toHaveClass('bg-gradient-accent', 'text-white', 'animate-pulse-glow', 'text-xs', 'px-2', 'py-0.5');
    });
  });

  describe('Custom Styling', () => {
    it('should apply custom className', () => {
      render(<Badge className="custom-badge-class">Custom Badge</Badge>);
      
      const badge = screen.getByText('Custom Badge');
      expect(badge).toHaveClass('custom-badge-class');
    });

    it('should combine custom className with default classes', () => {
      render(<Badge className="custom-class" variant="success">Custom Success Badge</Badge>);
      
      const badge = screen.getByText('Custom Success Badge');
      expect(badge).toHaveClass('custom-class', 'bg-success', 'text-white', 'inline-flex', 'items-center');
    });
  });

  describe('HTML Attributes', () => {
    it('should pass through HTML attributes', () => {
      render(<Badge data-testid="test-badge" id="badge-id">Badge with Attributes</Badge>);
      
      const badge = screen.getByTestId('test-badge');
      expect(badge).toHaveAttribute('id', 'badge-id');
    });

    it('should handle onClick event', () => {
      const handleClick = jest.fn();
      render(<Badge onClick={handleClick}>Clickable Badge</Badge>);
      
      const badge = screen.getByText('Clickable Badge');
      badge.click();
      
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('should handle onMouseOver event', () => {
      const handleMouseOver = jest.fn();
      render(<Badge onMouseOver={handleMouseOver}>Hoverable Badge</Badge>);
      
      const badge = screen.getByText('Hoverable Badge');
      badge.dispatchEvent(new MouseEvent('mouseover', { bubbles: true }));
      
      expect(handleMouseOver).toHaveBeenCalledTimes(1);
    });
  });

  describe('Ref Forwarding', () => {
    it('should forward ref to the div element', () => {
      const ref = React.createRef<HTMLDivElement>();
      render(<Badge ref={ref}>Ref Badge</Badge>);
      
      expect(ref.current).toBeInstanceOf(HTMLDivElement);
      expect(ref.current).toHaveTextContent('Ref Badge');
    });
  });

  describe('Content Types', () => {
    it('should render text content', () => {
      render(<Badge>Simple Text</Badge>);
      
      expect(screen.getByText('Simple Text')).toBeInTheDocument();
    });

    it('should render numeric content', () => {
      render(<Badge>123</Badge>);
      
      expect(screen.getByText('123')).toBeInTheDocument();
    });

    it('should render multiple children', () => {
      render(
        <Badge>
          <span>Multi</span>
          <span>Content</span>
        </Badge>
      );
      
      expect(screen.getByText('Multi')).toBeInTheDocument();
      expect(screen.getByText('Content')).toBeInTheDocument();
    });

    it('should render with JSX elements', () => {
      render(
        <Badge>
          <span data-testid="icon">★</span>
          Featured
        </Badge>
      );
      
      expect(screen.getByTestId('icon')).toBeInTheDocument();
      expect(screen.getByText('Featured')).toBeInTheDocument();
    });

    it('should handle empty children', () => {
      const { container } = render(<Badge></Badge>);
      
      const badge = container.firstChild as HTMLElement;
      expect(badge).toBeInTheDocument();
      expect(badge).toBeEmptyDOMElement();
    });
  });

  describe('Base Classes', () => {
    it('should always include base classes', () => {
      render(<Badge>Base Classes Test</Badge>);
      
      const badge = screen.getByText('Base Classes Test');
      expect(badge).toHaveClass(
        'inline-flex',
        'items-center',
        'rounded-lg',
        'font-bold',
        'uppercase',
        'tracking-wide',
        'transition-all',
        'duration-300'
      );
    });

    it('should maintain base classes with different variants', () => {
      render(<Badge variant="pro">Pro Base Classes</Badge>);
      
      const badge = screen.getByText('Pro Base Classes');
      expect(badge).toHaveClass(
        'inline-flex',
        'items-center',
        'rounded-lg',
        'font-bold',
        'uppercase',
        'tracking-wide',
        'transition-all',
        'duration-300'
      );
    });
  });

  describe('Accessibility', () => {
    it('should have div role by default', () => {
      render(<Badge>Accessible Badge</Badge>);
      
      const badge = screen.getByText('Accessible Badge');
      expect(badge.tagName.toLowerCase()).toBe('div');
    });

    it('should support ARIA attributes', () => {
      render(
        <Badge aria-label="Status indicator" aria-describedby="badge-help">
          Status
        </Badge>
      );
      
      const badge = screen.getByLabelText('Status indicator');
      expect(badge).toHaveAttribute('aria-describedby', 'badge-help');
    });

    it('should support role attribute', () => {
      render(<Badge role="status">Status Badge</Badge>);
      
      const badge = screen.getByRole('status');
      expect(badge).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle null variant gracefully', () => {
      render(<Badge variant={null as any}>Null Variant</Badge>);
      
      const badge = screen.getByText('Null Variant');
      expect(badge).toBeInTheDocument();
    });

    it('should handle undefined size gracefully', () => {
      render(<Badge size={undefined}>Undefined Size</Badge>);
      
      const badge = screen.getByText('Undefined Size');
      expect(badge).toBeInTheDocument();
    });

    it('should handle very long text content', () => {
      const longText = 'This is a very long badge text that might overflow or cause layout issues';
      render(<Badge>{longText}</Badge>);
      
      expect(screen.getByText(longText)).toBeInTheDocument();
    });
  });
});