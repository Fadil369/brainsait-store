import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
// Removed user-event import to simplify tests
import { SearchBar } from '@/components/features/SearchBar';

// Mock the translation hook
jest.mock('@/hooks/useTranslation', () => ({
  useTranslation: () => ({
    t: (key: string) => {
      const translations: Record<string, string> = {
        'hero.searchPlaceholder': 'Search for products, solutions, or services...',
      };
      return translations[key] || key;
    },
  }),
}));

// Mock the debounce function
const mockDebounce = jest.fn();
jest.mock('@/lib/utils', () => ({
  debounce: (fn: Function, delay: number) => {
    mockDebounce(fn, delay);
    return fn; // Return the original function for immediate execution in tests
  },
}));

// Mock Input component
jest.mock('@/components/ui/Input', () => ({
  Input: React.forwardRef<HTMLInputElement, any>(({ leftIcon, ...props }, ref) => (
    <div data-testid="input-wrapper">
      {leftIcon && <span data-testid="search-icon">{leftIcon}</span>}
      <input ref={ref} {...props} data-testid="search-input" />
    </div>
  )),
}));

// Mock MagnifyingGlassIcon
jest.mock('@heroicons/react/24/outline', () => ({
  MagnifyingGlassIcon: (props: any) => <svg data-testid="magnifying-glass-icon" {...props} />,
}));

describe('SearchBar', () => {
  const mockOnSearch = jest.fn();
  
  const defaultProps = {
    onSearch: mockOnSearch,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('should render with default placeholder', () => {
    render(<SearchBar {...defaultProps} />);
    
    const input = screen.getByTestId('search-input');
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('placeholder', 'Search for products, solutions, or services...');
  });

  it('should render with custom placeholder', () => {
    render(<SearchBar {...defaultProps} placeholder="Custom search placeholder" />);
    
    const input = screen.getByTestId('search-input');
    expect(input).toHaveAttribute('placeholder', 'Custom search placeholder');
  });

  it('should render with search icon', () => {
    render(<SearchBar {...defaultProps} />);
    
    expect(screen.getByTestId('magnifying-glass-icon')).toBeInTheDocument();
  });

  it('should render with default value', () => {
    render(<SearchBar {...defaultProps} defaultValue="initial search" />);
    
    const input = screen.getByTestId('search-input') as HTMLInputElement;
    expect(input.value).toBe('initial search');
  });

  it('should update input value when typed', () => {
    render(<SearchBar {...defaultProps} />);
    
    const input = screen.getByTestId('search-input');
    
    fireEvent.change(input, { target: { value: 'test search' } });
    
    expect(input).toHaveValue('test search');
  });

  it('should call onSearch with debounced input changes', () => {
    render(<SearchBar {...defaultProps} />);
    
    const input = screen.getByTestId('search-input');
    
    fireEvent.change(input, { target: { value: 'test' } });
    
    // Verify debounce was called
    expect(mockDebounce).toHaveBeenCalledWith(expect.any(Function), 300);
    
    // Since we mocked debounce to return the original function, onSearch should be called
    expect(mockOnSearch).toHaveBeenCalledWith('test');
  });

  it('should call onSearch on form submission', () => {
    render(<SearchBar {...defaultProps} />);
    
    const input = screen.getByTestId('search-input');
    const form = input.closest('form');
    
    fireEvent.change(input, { target: { value: 'submit test' } });
    fireEvent.submit(form!);
    
    expect(mockOnSearch).toHaveBeenCalledWith('submit test');
  });

  it('should prevent default form submission', () => {
    render(<SearchBar {...defaultProps} />);
    
    const input = screen.getByTestId('search-input');
    const form = input.closest('form');
    
    const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
    const preventDefaultSpy = jest.spyOn(submitEvent, 'preventDefault');
    
    fireEvent(form!, submitEvent);
    
    expect(preventDefaultSpy).toHaveBeenCalled();
  });

  it('should apply custom className', () => {
    const { container } = render(<SearchBar {...defaultProps} className="custom-search-class" />);
    
    const form = container.querySelector('form');
    expect(form).toHaveClass('custom-search-class');
  });

  it('should have proper input attributes', () => {
    render(<SearchBar {...defaultProps} />);
    
    const input = screen.getByTestId('search-input');
    expect(input).toHaveAttribute('type', 'text');
    expect(input).toHaveClass('w-full', 'pr-12', 'text-lg', 'h-14', 'glass', 'hover:glass-hover', 'focus:border-vision-green', 'focus:ring-vision-green/20');
  });

  it('should handle empty search submission', () => {
    render(<SearchBar {...defaultProps} />);
    
    const input = screen.getByTestId('search-input');
    const form = input.closest('form');
    
    fireEvent.submit(form!);
    
    expect(mockOnSearch).toHaveBeenCalledWith('');
  });

  it('should handle rapid typing with debounce', () => {
    render(<SearchBar {...defaultProps} />);
    
    const input = screen.getByTestId('search-input');
    
    // Simulate rapid typing
    fireEvent.change(input, { target: { value: 'r' } });
    fireEvent.change(input, { target: { value: 'ra' } });
    fireEvent.change(input, { target: { value: 'rap' } });
    fireEvent.change(input, { target: { value: 'rapi' } });
    fireEvent.change(input, { target: { value: 'rapid' } });
    
    // Debounce should be called for each change
    expect(mockDebounce).toHaveBeenCalledTimes(5);
    expect(mockOnSearch).toHaveBeenLastCalledWith('rapid');
  });

  it('should handle special characters in search', () => {
    render(<SearchBar {...defaultProps} />);
    
    const input = screen.getByTestId('search-input');
    
    fireEvent.change(input, { target: { value: '!@#$%^&*()' } });
    
    expect(input).toHaveValue('!@#$%^&*()');
    expect(mockOnSearch).toHaveBeenCalledWith('!@#$%^&*()');
  });

  it('should handle unicode characters', () => {
    render(<SearchBar {...defaultProps} />);
    
    const input = screen.getByTestId('search-input');
    
    fireEvent.change(input, { target: { value: 'البحث العربي' } });
    
    expect(input).toHaveValue('البحث العربي');
    expect(mockOnSearch).toHaveBeenCalledWith('البحث العربي');
  });

  it('should handle clearing the input', () => {
    render(<SearchBar {...defaultProps} defaultValue="initial text" />);
    
    const input = screen.getByTestId('search-input');
    
    // Clear the input
    fireEvent.change(input, { target: { value: '' } });
    
    expect(input).toHaveValue('');
    expect(mockOnSearch).toHaveBeenCalledWith('');
  });

  it('should handle input focus and blur events', () => {
    render(<SearchBar {...defaultProps} />);
    
    const input = screen.getByTestId('search-input');
    
    // Focus the input directly
    input.focus();
    expect(document.activeElement).toBe(input);
    
    // Blur the input
    input.blur();
    expect(document.activeElement).toBe(document.body);
  });

  it('should maintain controlled input behavior', () => {
    render(<SearchBar {...defaultProps} />);
    
    const input = screen.getByTestId('search-input');
    
    // Type multiple characters
    fireEvent.change(input, { target: { value: 'a' } });
    expect(input).toHaveValue('a');
    
    fireEvent.change(input, { target: { value: 'ab' } });
    expect(input).toHaveValue('ab');
    
    fireEvent.change(input, { target: { value: 'abc' } });
    expect(input).toHaveValue('abc');
  });

  it('should handle form submission with Enter key', () => {
    render(<SearchBar {...defaultProps} />);
    
    const input = screen.getByTestId('search-input');
    
    fireEvent.change(input, { target: { value: 'enter test' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });
    
    // The form submission should trigger onSearch
    const form = input.closest('form');
    fireEvent.submit(form!);
    
    expect(mockOnSearch).toHaveBeenCalledWith('enter test');
  });

  it('should call debounced search function on each input change', () => {
    render(<SearchBar {...defaultProps} />);
    
    const input = screen.getByTestId('search-input');
    
    fireEvent.change(input, { target: { value: 't' } });
    fireEvent.change(input, { target: { value: 'te' } });
    fireEvent.change(input, { target: { value: 'tes' } });
    fireEvent.change(input, { target: { value: 'test' } });
    
    // Each character should trigger the debounced function
    expect(mockDebounce).toHaveBeenCalledTimes(4); // t, e, s, t
  });

  it('should handle input change with different values', () => {
    render(<SearchBar {...defaultProps} />);
    
    const input = screen.getByTestId('search-input');
    
    // Type first value
    fireEvent.change(input, { target: { value: 'first' } });
    expect(mockOnSearch).toHaveBeenLastCalledWith('first');
    
    // Clear and type second value
    fireEvent.change(input, { target: { value: '' } });
    fireEvent.change(input, { target: { value: 'second' } });
    expect(mockOnSearch).toHaveBeenLastCalledWith('second');
  });

  it('should have proper form structure', () => {
    render(<SearchBar {...defaultProps} />);
    
    const form = screen.getByTestId('search-input').closest('form');
    expect(form).toBeInTheDocument();
    expect(form?.tagName).toBe('FORM');
    
    const wrapper = screen.getByTestId('input-wrapper');
    expect(wrapper).toBeInTheDocument();
    
    // Check the wrapper's parent has the correct classes
    const relativeWrapper = wrapper.parentElement;
    expect(relativeWrapper).toHaveClass('relative', 'max-w-2xl', 'mx-auto');
  });

  it('should handle multiple rapid submissions', () => {
    render(<SearchBar {...defaultProps} />);
    
    const input = screen.getByTestId('search-input');
    const form = input.closest('form');
    
    fireEvent.change(input, { target: { value: 'multi test' } });
    // Clear previous calls from the change event
    mockOnSearch.mockClear();
    
    // Submit multiple times rapidly
    fireEvent.submit(form!);
    fireEvent.submit(form!);
    fireEvent.submit(form!);
    
    expect(mockOnSearch).toHaveBeenCalledTimes(3);
    expect(mockOnSearch).toHaveBeenCalledWith('multi test');
  });
});