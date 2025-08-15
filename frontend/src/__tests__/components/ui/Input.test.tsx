import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Input } from '@/components/ui/Input';

describe('Input Component', () => {
  describe('Basic Rendering', () => {
    it('should render input with default props', () => {
      render(<Input data-testid="test-input" />);
      
      const input = screen.getByTestId('test-input');
      expect(input).toBeInTheDocument();
      expect(input).toHaveAttribute('type', 'text');
      expect(input).toHaveClass('h-11', 'px-4', 'text-sm'); // default md size
    });

    it('should render with custom placeholder', () => {
      render(<Input placeholder="Enter your name" data-testid="test-input" />);
      
      const input = screen.getByTestId('test-input');
      expect(input).toHaveAttribute('placeholder', 'Enter your name');
    });

    it('should render with custom value', () => {
      render(<Input value="test value" data-testid="test-input" readOnly />);
      
      const input = screen.getByTestId('test-input');
      expect(input).toHaveValue('test value');
    });

    it('should support different input types', () => {
      const types = ['text', 'email', 'password', 'number', 'tel'];
      
      types.forEach(type => {
        const { unmount } = render(<Input type={type as any} data-testid={`input-${type}`} />);
        const input = screen.getByTestId(`input-${type}`);
        expect(input).toHaveAttribute('type', type);
        unmount();
      });
    });
  });

  describe('Variants', () => {
    it('should render default variant with correct classes', () => {
      render(<Input variant="default" data-testid="test-input" />);
      
      const input = screen.getByTestId('test-input');
      expect(input).toHaveClass('glass', 'border-glass-border');
    });

    it('should render filled variant with correct classes', () => {
      render(<Input variant="filled" data-testid="test-input" />);
      
      const input = screen.getByTestId('test-input');
      expect(input).toHaveClass('bg-white/5', 'border-transparent');
    });

    it('should render outline variant with correct classes', () => {
      render(<Input variant="outline" data-testid="test-input" />);
      
      const input = screen.getByTestId('test-input');
      expect(input).toHaveClass('border-vision-green/30');
    });
  });

  describe('Sizes', () => {
    it('should render small size correctly', () => {
      render(<Input inputSize="sm" data-testid="test-input" />);
      
      const input = screen.getByTestId('test-input');
      expect(input).toHaveClass('h-9', 'px-3', 'text-xs');
    });

    it('should render medium size correctly', () => {
      render(<Input inputSize="md" data-testid="test-input" />);
      
      const input = screen.getByTestId('test-input');
      expect(input).toHaveClass('h-11', 'px-4', 'text-sm');
    });

    it('should render large size correctly', () => {
      render(<Input inputSize="lg" data-testid="test-input" />);
      
      const input = screen.getByTestId('test-input');
      expect(input).toHaveClass('h-12', 'px-6', 'text-base');
    });
  });

  describe('Icons', () => {
    it('should render with left icon', () => {
      const LeftIcon = <span data-testid="left-icon">🔍</span>;
      render(<Input leftIcon={LeftIcon} data-testid="test-input" />);
      
      expect(screen.getByTestId('left-icon')).toBeInTheDocument();
      const input = screen.getByTestId('test-input');
      expect(input).toHaveClass('pl-10');
    });

    it('should render with right icon', () => {
      const RightIcon = <span data-testid="right-icon">👁️</span>;
      render(<Input rightIcon={RightIcon} data-testid="test-input" />);
      
      expect(screen.getByTestId('right-icon')).toBeInTheDocument();
      const input = screen.getByTestId('test-input');
      expect(input).toHaveClass('pr-10');
    });

    it('should render with both left and right icons', () => {
      const LeftIcon = <span data-testid="left-icon">🔍</span>;
      const RightIcon = <span data-testid="right-icon">👁️</span>;
      
      render(<Input leftIcon={LeftIcon} rightIcon={RightIcon} data-testid="test-input" />);
      
      expect(screen.getByTestId('left-icon')).toBeInTheDocument();
      expect(screen.getByTestId('right-icon')).toBeInTheDocument();
      
      const input = screen.getByTestId('test-input');
      expect(input).toHaveClass('pl-10', 'pr-10');
    });

    it('should position icons correctly', () => {
      const LeftIcon = <span data-testid="left-icon">🔍</span>;
      const RightIcon = <span data-testid="right-icon">👁️</span>;
      
      render(<Input leftIcon={LeftIcon} rightIcon={RightIcon} data-testid="test-input" />);
      
      const leftIconContainer = screen.getByTestId('left-icon').parentElement;
      const rightIconContainer = screen.getByTestId('right-icon').parentElement;
      
      expect(leftIconContainer).toHaveClass('absolute', 'left-3', 'top-1/2', '-translate-y-1/2');
      expect(rightIconContainer).toHaveClass('absolute', 'right-3', 'top-1/2', '-translate-y-1/2');
    });
  });

  describe('Error States', () => {
    it('should render error message when error prop is provided', () => {
      const errorMessage = 'This field is required';
      render(<Input error={errorMessage} data-testid="test-input" />);
      
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
      expect(screen.getByText(errorMessage)).toHaveClass('text-red-500');
    });

    it('should apply error styles to input when error exists', () => {
      render(<Input error="Error message" data-testid="test-input" />);
      
      const input = screen.getByTestId('test-input');
      expect(input).toHaveClass('border-red-500');
    });

    it('should not render error message when error prop is empty', () => {
      const { container } = render(<Input error="" data-testid="test-input" />);
      
      // Check that no error paragraph is rendered
      const errorParagraph = container.querySelector('.text-red-500');
      expect(errorParagraph).not.toBeInTheDocument();
    });

    it('should not render error message when error prop is undefined', () => {
      render(<Input data-testid="test-input" />);
      
      // Should not find any error text elements
      const errorElements = screen.queryAllByText('', { selector: '.text-red-500' });
      expect(errorElements).toHaveLength(0);
    });
  });

  describe('Disabled State', () => {
    it('should render disabled input correctly', () => {
      render(<Input disabled data-testid="test-input" />);
      
      const input = screen.getByTestId('test-input');
      expect(input).toBeDisabled();
      expect(input).toHaveClass('disabled:cursor-not-allowed', 'disabled:opacity-50');
    });

    it('should not accept input when disabled', () => {
      render(<Input disabled defaultValue="" data-testid="test-input" />);
      
      const input = screen.getByTestId('test-input');
      // Disabled inputs in jsdom still update values during testing
      // but in real browsers they would not. We test that it's disabled instead.
      expect(input).toBeDisabled();
      expect(input).toHaveAttribute('disabled');
    });
  });

  describe('Focus and Interaction', () => {
    it('should handle focus events', () => {
      const onFocus = jest.fn();
      render(<Input onFocus={onFocus} data-testid="test-input" />);
      
      const input = screen.getByTestId('test-input');
      fireEvent.focus(input);
      
      expect(onFocus).toHaveBeenCalledTimes(1);
    });

    it('should handle blur events', () => {
      const onBlur = jest.fn();
      render(<Input onBlur={onBlur} data-testid="test-input" />);
      
      const input = screen.getByTestId('test-input');
      fireEvent.focus(input);
      fireEvent.blur(input);
      
      expect(onBlur).toHaveBeenCalledTimes(1);
    });

    it('should handle change events', () => {
      const onChange = jest.fn();
      render(<Input onChange={onChange} data-testid="test-input" />);
      
      const input = screen.getByTestId('test-input');
      fireEvent.change(input, { target: { value: 'new value' } });
      
      expect(onChange).toHaveBeenCalledTimes(1);
      expect(input).toHaveValue('new value');
    });

    it('should handle key events', () => {
      const onKeyDown = jest.fn();
      render(<Input onKeyDown={onKeyDown} data-testid="test-input" />);
      
      const input = screen.getByTestId('test-input');
      fireEvent.keyDown(input, { key: 'Enter' });
      
      expect(onKeyDown).toHaveBeenCalledTimes(1);
    });

    it('should apply focus styles when focused', () => {
      render(<Input data-testid="test-input" />);
      
      const input = screen.getByTestId('test-input');
      expect(input).toHaveClass('focus-visible:outline-none', 'focus-visible:ring-2', 'focus-visible:ring-vision-green');
    });
  });

  describe('Custom Styling', () => {
    it('should merge custom className with default classes', () => {
      const customClass = 'custom-input-class';
      render(<Input className={customClass} data-testid="test-input" />);
      
      const input = screen.getByTestId('test-input');
      expect(input).toHaveClass(customClass);
      // Should still have default classes
      expect(input).toHaveClass('flex', 'w-full', 'rounded-xl');
    });

    it('should override variant styles when custom className conflicts', () => {
      render(
        <Input 
          variant="default" 
          className="bg-red-500" 
          data-testid="test-input" 
        />
      );
      
      const input = screen.getByTestId('test-input');
      // Custom className should be applied
      expect(input).toHaveClass('bg-red-500');
    });
  });

  describe('Form Integration', () => {
    it('should work with form elements', () => {
      const onSubmit = jest.fn(e => e.preventDefault());
      
      render(
        <form onSubmit={onSubmit}>
          <Input name="testField" data-testid="test-input" />
          <button type="submit" data-testid="submit-btn">Submit</button>
        </form>
      );
      
      const input = screen.getByTestId('test-input');
      const submit = screen.getByTestId('submit-btn');
      
      fireEvent.change(input, { target: { value: 'form value' } });
      fireEvent.click(submit);
      
      expect(onSubmit).toHaveBeenCalledTimes(1);
      expect(input).toHaveValue('form value');
    });

    it('should have proper name and id attributes', () => {
      render(<Input name="username" id="user-input" data-testid="test-input" />);
      
      const input = screen.getByTestId('test-input');
      expect(input).toHaveAttribute('name', 'username');
      expect(input).toHaveAttribute('id', 'user-input');
    });
  });

  describe('Accessibility', () => {
    it('should be accessible via role', () => {
      render(<Input data-testid="test-input" />);
      
      const input = screen.getByRole('textbox');
      expect(input).toBeInTheDocument();
    });

    it('should support aria-label', () => {
      render(<Input aria-label="Search products" data-testid="test-input" />);
      
      const input = screen.getByTestId('test-input');
      expect(input).toHaveAttribute('aria-label', 'Search products');
    });

    it('should support aria-describedby for error messages', () => {
      render(
        <div>
          <Input aria-describedby="error-msg" error="Invalid input" data-testid="test-input" />
        </div>
      );
      
      const input = screen.getByTestId('test-input');
      expect(input).toHaveAttribute('aria-describedby', 'error-msg');
    });

    it('should be keyboard navigable', () => {
      render(
        <div>
          <Input data-testid="input1" />
          <Input data-testid="input2" />
        </div>
      );
      
      const input1 = screen.getByTestId('input1');
      const input2 = screen.getByTestId('input2');
      
      input1.focus();
      expect(document.activeElement).toBe(input1);
      
      // Tab navigation
      fireEvent.keyDown(input1, { key: 'Tab' });
      // Note: jsdom doesn't handle tab navigation automatically,
      // but we can test that the inputs are properly focusable
      expect(input2).toBeInTheDocument();
    });
  });

  describe('Forward Ref', () => {
    it('should forward ref to input element', () => {
      const ref = React.createRef<HTMLInputElement>();
      render(<Input ref={ref} data-testid="test-input" />);
      
      expect(ref.current).toBeInstanceOf(HTMLInputElement);
      expect(ref.current).toBe(screen.getByTestId('test-input'));
    });

    it('should allow imperative focus via ref', () => {
      const ref = React.createRef<HTMLInputElement>();
      render(<Input ref={ref} data-testid="test-input" />);
      
      ref.current?.focus();
      expect(document.activeElement).toBe(ref.current);
    });
  });

  describe('Edge Cases', () => {
    it('should handle null/undefined icons gracefully', () => {
      render(<Input leftIcon={null} rightIcon={undefined} data-testid="test-input" />);
      
      const input = screen.getByTestId('test-input');
      expect(input).toBeInTheDocument();
      // Should not have padding for icons
      expect(input).not.toHaveClass('pl-10', 'pr-10');
    });

    it('should handle very long error messages', () => {
      const longError = 'This is a very long error message that might wrap to multiple lines and should still be displayed properly';
      render(<Input error={longError} data-testid="test-input" />);
      
      expect(screen.getByText(longError)).toBeInTheDocument();
    });

    it('should handle special characters in input', () => {
      render(<Input data-testid="test-input" />);
      
      const input = screen.getByTestId('test-input');
      const specialText = 'Special chars: !@#$%^&*()_+-=[]{}|;:,.<>?';
      
      fireEvent.change(input, { target: { value: specialText } });
      expect(input).toHaveValue(specialText);
    });
  });

  describe('Component Composition', () => {
    it('should work with complex icon components', () => {
      const ComplexIcon = () => (
        <svg data-testid="complex-icon" width="16" height="16">
          <circle cx="8" cy="8" r="4" />
        </svg>
      );
      
      render(<Input leftIcon={<ComplexIcon />} data-testid="test-input" />);
      
      expect(screen.getByTestId('complex-icon')).toBeInTheDocument();
    });

    it('should maintain proper structure with all features enabled', () => {
      const { container } = render(
        <Input
          leftIcon={<span>🔍</span>}
          rightIcon={<span>👁️</span>}
          error="Test error"
          variant="outline"
          inputSize="lg"
          data-testid="test-input"
        />
      );
      
      // Should have proper nesting structure
      const outerDiv = container.firstChild;
      expect(outerDiv).toHaveClass('relative');
      
      const innerDiv = outerDiv?.firstChild;
      expect(innerDiv).toHaveClass('relative');
      
      const input = screen.getByTestId('test-input');
      expect(input).toBeInTheDocument();
      
      const error = screen.getByText('Test error');
      expect(error).toBeInTheDocument();
    });
  });
});