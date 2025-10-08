import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '@/components/ui/Button';

describe('Button Component', () => {
  it('should render with default props', () => {
    render(<Button>Click me</Button>);
    const button = screen.getByRole('button', { name: 'Click me' });
    expect(button).toBeInTheDocument();
  });

  it('should handle onClick events', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('should be disabled when disabled prop is true', () => {
    const handleClick = jest.fn();
    render(<Button disabled onClick={handleClick}>Disabled</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
    
    fireEvent.click(button);
    expect(handleClick).not.toHaveBeenCalled();
  });

  it('should apply variant classes correctly', () => {
    const { rerender } = render(<Button variant="primary">Primary</Button>);
    expect(screen.getByRole('button')).toHaveClass('bg-vision-green');

    rerender(<Button variant="secondary">Secondary</Button>);
    expect(screen.getByRole('button')).toHaveClass('glass');

    rerender(<Button variant="outline">Outline</Button>);
    expect(screen.getByRole('button')).toHaveClass('border-vision-green');

    rerender(<Button variant="ghost">Ghost</Button>);
    expect(screen.getByRole('button')).toHaveClass('hover:bg-white/10');

    rerender(<Button variant="gradient">Gradient</Button>);
    expect(screen.getByRole('button')).toHaveClass('bg-gradient-primary');
  });

  it('should apply size classes correctly', () => {
    const { rerender } = render(<Button size="sm">Small</Button>);
    expect(screen.getByRole('button')).toHaveClass('h-9');

    rerender(<Button size="md">Medium</Button>);
    expect(screen.getByRole('button')).toHaveClass('h-11');

    rerender(<Button size="lg">Large</Button>);
    expect(screen.getByRole('button')).toHaveClass('h-12');

    rerender(<Button size="xl">Extra Large</Button>);
    expect(screen.getByRole('button')).toHaveClass('h-14');
  });

  it('should show loading state correctly', () => {
    render(<Button loading>Loading</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
    expect(screen.getByText('Loading')).toBeInTheDocument();
  });

  it('should apply custom className', () => {
    render(<Button className="custom-class">Custom</Button>);
    expect(screen.getByRole('button')).toHaveClass('custom-class');
  });

  it('should handle different button types', () => {
    const { rerender } = render(<Button type="submit">Submit</Button>);
    expect(screen.getByRole('button')).toHaveAttribute('type', 'submit');

    rerender(<Button type="reset">Reset</Button>);
    expect(screen.getByRole('button')).toHaveAttribute('type', 'reset');
  });

  it('should render with leftIcon when provided', () => {
    const Icon = () => <span data-testid="icon">🚀</span>;
    render(<Button leftIcon={<Icon />}>With Icon</Button>);
    
    expect(screen.getByTestId('icon')).toBeInTheDocument();
    expect(screen.getByText('With Icon')).toBeInTheDocument();
  });

  it('should handle full width with className', () => {
    render(<Button className="w-full">Full Width</Button>);
    expect(screen.getByRole('button')).toHaveClass('w-full');
  });

  it('should apply loading variant styling', () => {
    render(<Button loading variant="primary">Loading Primary</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('bg-vision-green');
    expect(button).toBeDisabled();
  });

  it('should prevent click when loading', () => {
    const handleClick = jest.fn();
    render(<Button loading onClick={handleClick}>Loading</Button>);
    
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).not.toHaveBeenCalled();
  });

  it('should handle keyboard navigation', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Keyboard</Button>);
    
    const button = screen.getByRole('button');
    button.focus();
    expect(button).toHaveFocus();
  });

  it('should accept aria-label attribute', () => {
    render(<Button aria-label="Custom label">ARIA Button</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-label', 'Custom label');
  });

  it('should handle disabled state with aria attributes', () => {
    render(<Button aria-label="Custom label" disabled>ARIA Button</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-label', 'Custom label');
    expect(button).toBeDisabled();
  });

  it('should handle ref forwarding', () => {
    const ref = React.createRef<HTMLButtonElement>();
    render(<Button ref={ref}>Ref Button</Button>);
    expect(ref.current).toBeInstanceOf(HTMLButtonElement);
  });

  it('should combine multiple classes correctly', () => {
    render(
      <Button 
        variant="primary" 
        size="lg" 
        className="custom-class"
      >
        Multiple Classes
      </Button>
    );
    
    const button = screen.getByRole('button');
    expect(button).toHaveClass('bg-vision-green');
    expect(button).toHaveClass('h-12');
    expect(button).toHaveClass('custom-class');
  });
});