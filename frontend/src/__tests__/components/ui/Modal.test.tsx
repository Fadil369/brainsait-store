import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Modal } from '@/components/ui/Modal';
import '@testing-library/jest-dom';

// Mock createPortal to render in the same container
jest.mock('react-dom', () => ({
  ...jest.requireActual('react-dom'),
  createPortal: (node: React.ReactNode) => node,
}));

// Mock the XMarkIcon from Heroicons
jest.mock('@heroicons/react/24/outline', () => ({
  XMarkIcon: () => <div data-testid="close-icon">X</div>
}));

describe('Modal', () => {
  const defaultProps = {
    isOpen: true,
    onClose: jest.fn(),
    children: <div data-testid="modal-content">Modal Content</div>
  };

  beforeEach(() => {
    jest.clearAllMocks();
    // Reset document.body overflow style
    document.body.style.overflow = '';
  });

  it('should render when isOpen is true', () => {
    render(<Modal {...defaultProps} />);
    
    expect(screen.getByTestId('modal-content')).toBeInTheDocument();
  });

  it('should not render when isOpen is false', () => {
    render(<Modal {...defaultProps} isOpen={false} />);
    
    expect(screen.queryByTestId('modal-content')).not.toBeInTheDocument();
  });

  it('should display title when provided', () => {
    render(<Modal {...defaultProps} title="Test Modal Title" />);
    
    expect(screen.getByText('Test Modal Title')).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent('Test Modal Title');
  });

  it('should not display header when no title and showCloseButton is false', () => {
    render(<Modal {...defaultProps} showCloseButton={false} />);
    
    expect(screen.queryByRole('heading')).not.toBeInTheDocument();
    expect(screen.queryByLabelText('Close modal')).not.toBeInTheDocument();
  });

  describe('Close Button', () => {
    it('should show close button by default', () => {
      render(<Modal {...defaultProps} />);
      
      expect(screen.getByLabelText('Close modal')).toBeInTheDocument();
      expect(screen.getByTestId('close-icon')).toBeInTheDocument();
    });

    it('should hide close button when showCloseButton is false', () => {
      render(<Modal {...defaultProps} showCloseButton={false} />);
      
      expect(screen.queryByLabelText('Close modal')).not.toBeInTheDocument();
    });

    it('should call onClose when close button is clicked', () => {
      const onCloseMock = jest.fn();
      render(<Modal {...defaultProps} onClose={onCloseMock} />);
      
      fireEvent.click(screen.getByLabelText('Close modal'));
      
      expect(onCloseMock).toHaveBeenCalledTimes(1);
    });
  });

  describe('Size Variants', () => {
    it('should apply default lg size class', () => {
      render(<Modal {...defaultProps} />);
      
      const modalContent = screen.getByTestId('modal-content').closest('.max-w-2xl');
      expect(modalContent).toBeInTheDocument();
    });

    it('should apply sm size class', () => {
      render(<Modal {...defaultProps} size="sm" />);
      
      const modalContent = screen.getByTestId('modal-content').closest('.max-w-md');
      expect(modalContent).toBeInTheDocument();
    });

    it('should apply md size class', () => {
      render(<Modal {...defaultProps} size="md" />);
      
      const modalContent = screen.getByTestId('modal-content').closest('.max-w-lg');
      expect(modalContent).toBeInTheDocument();
    });

    it('should apply xl size class', () => {
      render(<Modal {...defaultProps} size="xl" />);
      
      const modalContent = screen.getByTestId('modal-content').closest('.max-w-4xl');
      expect(modalContent).toBeInTheDocument();
    });

    it('should apply full size class', () => {
      render(<Modal {...defaultProps} size="full" />);
      
      const modalContent = screen.getByTestId('modal-content').closest('.max-w-\\[95vw\\]');
      expect(modalContent).toBeInTheDocument();
    });
  });

  describe('Custom Styling', () => {
    it('should apply custom className', () => {
      render(<Modal {...defaultProps} className="custom-modal-class" />);
      
      const modalDialog = screen.getByTestId('modal-content').closest('.custom-modal-class');
      expect(modalDialog).toBeInTheDocument();
    });

    it('should combine custom className with default classes', () => {
      render(<Modal {...defaultProps} className="custom-class" />);
      
      const modalDialog = screen.getByTestId('modal-content').closest('.custom-class');
      expect(modalDialog).toBeInTheDocument();
      expect(modalDialog).toHaveClass('relative', 'glass', 'border');
    });
  });

  describe('Overlay Click Behavior', () => {
    it('should close modal when overlay is clicked and closeOnOverlayClick is true', () => {
      const onCloseMock = jest.fn();
      render(<Modal {...defaultProps} onClose={onCloseMock} closeOnOverlayClick={true} />);
      
      // Find the backdrop/overlay element
      const backdrop = screen.getByTestId('modal-content').closest('.fixed')?.querySelector('.absolute.inset-0');
      expect(backdrop).toBeInTheDocument();
      
      if (backdrop) {
        fireEvent.click(backdrop);
        expect(onCloseMock).toHaveBeenCalledTimes(1);
      }
    });

    it('should not close modal when overlay is clicked and closeOnOverlayClick is false', () => {
      const onCloseMock = jest.fn();
      render(<Modal {...defaultProps} onClose={onCloseMock} closeOnOverlayClick={false} />);
      
      const backdrop = screen.getByTestId('modal-content').closest('.fixed')?.querySelector('.absolute.inset-0');
      
      if (backdrop) {
        fireEvent.click(backdrop);
        expect(onCloseMock).not.toHaveBeenCalled();
      }
    });

    it('should not close modal when modal content is clicked', () => {
      const onCloseMock = jest.fn();
      render(<Modal {...defaultProps} onClose={onCloseMock} />);
      
      fireEvent.click(screen.getByTestId('modal-content'));
      
      expect(onCloseMock).not.toHaveBeenCalled();
    });
  });

  describe('Keyboard Interactions', () => {
    it('should close modal when Escape key is pressed', () => {
      const onCloseMock = jest.fn();
      render(<Modal {...defaultProps} onClose={onCloseMock} />);
      
      fireEvent.keyDown(document, { key: 'Escape', code: 'Escape' });
      
      expect(onCloseMock).toHaveBeenCalledTimes(1);
    });

    it('should not close modal when other keys are pressed', () => {
      const onCloseMock = jest.fn();
      render(<Modal {...defaultProps} onClose={onCloseMock} />);
      
      fireEvent.keyDown(document, { key: 'Enter', code: 'Enter' });
      fireEvent.keyDown(document, { key: 'Space', code: 'Space' });
      fireEvent.keyDown(document, { key: 'Tab', code: 'Tab' });
      
      expect(onCloseMock).not.toHaveBeenCalled();
    });

    it('should not respond to Escape key when modal is closed', () => {
      const onCloseMock = jest.fn();
      render(<Modal {...defaultProps} isOpen={false} onClose={onCloseMock} />);
      
      fireEvent.keyDown(document, { key: 'Escape', code: 'Escape' });
      
      expect(onCloseMock).not.toHaveBeenCalled();
    });
  });

  describe('Body Scroll Prevention', () => {
    it('should set body overflow to hidden when modal is open', () => {
      render(<Modal {...defaultProps} isOpen={true} />);
      
      expect(document.body.style.overflow).toBe('hidden');
    });

    it('should reset body overflow when modal is closed', async () => {
      const { rerender } = render(<Modal {...defaultProps} isOpen={true} />);
      
      expect(document.body.style.overflow).toBe('hidden');
      
      rerender(<Modal {...defaultProps} isOpen={false} />);
      
      await waitFor(() => {
        expect(document.body.style.overflow).toBe('unset');
      });
    });

    it('should reset body overflow when component unmounts', () => {
      const { unmount } = render(<Modal {...defaultProps} isOpen={true} />);
      
      expect(document.body.style.overflow).toBe('hidden');
      
      unmount();
      
      expect(document.body.style.overflow).toBe('unset');
    });
  });

  describe('Event Listeners Management', () => {
    it('should add event listener when modal opens', () => {
      const addEventListenerSpy = jest.spyOn(document, 'addEventListener');
      
      render(<Modal {...defaultProps} isOpen={true} />);
      
      expect(addEventListenerSpy).toHaveBeenCalledWith('keydown', expect.any(Function));
      
      addEventListenerSpy.mockRestore();
    });

    it('should remove event listener when modal closes', () => {
      const removeEventListenerSpy = jest.spyOn(document, 'removeEventListener');
      const { rerender } = render(<Modal {...defaultProps} isOpen={true} />);
      
      rerender(<Modal {...defaultProps} isOpen={false} />);
      
      expect(removeEventListenerSpy).toHaveBeenCalledWith('keydown', expect.any(Function));
      
      removeEventListenerSpy.mockRestore();
    });

    it('should clean up event listener on unmount', () => {
      const removeEventListenerSpy = jest.spyOn(document, 'removeEventListener');
      const { unmount } = render(<Modal {...defaultProps} isOpen={true} />);
      
      unmount();
      
      expect(removeEventListenerSpy).toHaveBeenCalledWith('keydown', expect.any(Function));
      
      removeEventListenerSpy.mockRestore();
    });
  });

  describe('Content Rendering', () => {
    it('should render children content', () => {
      render(
        <Modal {...defaultProps}>
          <div data-testid="custom-content">Custom Modal Content</div>
        </Modal>
      );
      
      expect(screen.getByTestId('custom-content')).toBeInTheDocument();
      expect(screen.getByText('Custom Modal Content')).toBeInTheDocument();
    });

    it('should render complex children content', () => {
      render(
        <Modal {...defaultProps}>
          <div>
            <h3 data-testid="content-title">Form Title</h3>
            <input data-testid="content-input" placeholder="Enter text" />
            <button data-testid="content-button">Submit</button>
          </div>
        </Modal>
      );
      
      expect(screen.getByTestId('content-title')).toBeInTheDocument();
      expect(screen.getByTestId('content-input')).toBeInTheDocument();
      expect(screen.getByTestId('content-button')).toBeInTheDocument();
    });
  });

  describe('Modal Structure', () => {
    it('should have proper ARIA attributes', () => {
      render(<Modal {...defaultProps} />);
      
      const closeButton = screen.getByLabelText('Close modal');
      expect(closeButton).toHaveAttribute('aria-label', 'Close modal');
    });

    it('should have proper z-index class for modal overlay', () => {
      render(<Modal {...defaultProps} />);
      
      const modalContainer = screen.getByTestId('modal-content').closest('.z-modal');
      expect(modalContainer).toBeInTheDocument();
    });

    it('should have backdrop blur effect', () => {
      render(<Modal {...defaultProps} />);
      
      const backdrop = screen.getByTestId('modal-content').closest('.fixed')?.querySelector('.backdrop-blur-xl');
      expect(backdrop).toBeInTheDocument();
    });

    it('should have glass effect styling', () => {
      render(<Modal {...defaultProps} />);
      
      const modalContent = screen.getByTestId('modal-content').closest('.glass');
      expect(modalContent).toBeInTheDocument();
    });

    it('should have border styling', () => {
      render(<Modal {...defaultProps} />);
      
      const modalContent = screen.getByTestId('modal-content').closest('.border-glass-border');
      expect(modalContent).toBeInTheDocument();
    });
  });

  describe('Header Conditional Rendering', () => {
    it('should render header with both title and close button', () => {
      render(<Modal {...defaultProps} title="Test Title" showCloseButton={true} />);
      
      expect(screen.getByText('Test Title')).toBeInTheDocument();
      expect(screen.getByLabelText('Close modal')).toBeInTheDocument();
    });

    it('should render header with only title', () => {
      render(<Modal {...defaultProps} title="Test Title" showCloseButton={false} />);
      
      expect(screen.getByText('Test Title')).toBeInTheDocument();
      expect(screen.queryByLabelText('Close modal')).not.toBeInTheDocument();
    });

    it('should render header with only close button', () => {
      render(<Modal {...defaultProps} showCloseButton={true} />);
      
      expect(screen.queryByRole('heading')).not.toBeInTheDocument();
      expect(screen.getByLabelText('Close modal')).toBeInTheDocument();
    });

    it('should not render header when no title and no close button', () => {
      render(<Modal {...defaultProps} showCloseButton={false} />);
      
      expect(screen.queryByRole('heading')).not.toBeInTheDocument();
      expect(screen.queryByLabelText('Close modal')).not.toBeInTheDocument();
      
      // Check that header container is not rendered
      const headerContainer = screen.getByTestId('modal-content').closest('.relative')?.querySelector('.border-b');
      expect(headerContainer).not.toBeInTheDocument();
    });
  });

  describe('Content Scrolling', () => {
    it('should have scrollable content area', () => {
      render(
        <Modal {...defaultProps}>
          <div style={{ height: '2000px' }} data-testid="tall-content">
            Very tall content
          </div>
        </Modal>
      );
      
      const contentArea = screen.getByTestId('tall-content').closest('.overflow-y-auto');
      expect(contentArea).toBeInTheDocument();
      expect(contentArea).toHaveClass('max-h-[calc(95vh-8rem)]');
    });
  });

  describe('Multiple Modal Interactions', () => {
    it('should handle multiple modals with different props', () => {
      render(
        <div>
          <Modal isOpen={true} onClose={jest.fn()} title="Modal 1">
            <div data-testid="modal-1">First Modal</div>
          </Modal>
          <Modal isOpen={false} onClose={jest.fn()} title="Modal 2">
            <div data-testid="modal-2">Second Modal</div>
          </Modal>
        </div>
      );
      
      expect(screen.getByTestId('modal-1')).toBeInTheDocument();
      expect(screen.getByText('Modal 1')).toBeInTheDocument();
      expect(screen.queryByTestId('modal-2')).not.toBeInTheDocument();
      expect(screen.queryByText('Modal 2')).not.toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle onClose being called multiple times', () => {
      const onCloseMock = jest.fn();
      render(<Modal {...defaultProps} onClose={onCloseMock} />);
      
      const closeButton = screen.getByLabelText('Close modal');
      fireEvent.click(closeButton);
      fireEvent.click(closeButton);
      fireEvent.keyDown(document, { key: 'Escape' });
      
      expect(onCloseMock).toHaveBeenCalledTimes(3);
    });

    it('should handle empty children', () => {
      render(<Modal {...defaultProps}>{null}</Modal>);
      
      // Modal should still render with empty content - check for content area
      const contentArea = document.querySelector('.p-6.overflow-y-auto');
      expect(contentArea).toBeInTheDocument();
      // Content area should be empty
      expect(contentArea).toBeEmptyDOMElement();
    });

    it('should handle undefined onClose callback gracefully', () => {
      // This shouldn't throw an error
      expect(() => {
        render(<Modal {...defaultProps} onClose={undefined as any} />);
      }).not.toThrow();
    });
  });
});