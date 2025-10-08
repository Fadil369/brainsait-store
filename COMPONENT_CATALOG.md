# BrainSAIT Store - Component Catalog

**Version:** 1.0.0  
**Last Updated:** 2024-01-10  
**Components Documented:** 15+

---

## 📚 Table of Contents

1. [UI Components](#ui-components)
   - [Button](#button)
   - [Badge](#badge)
   - [Modal](#modal)
   - [Input](#input)
2. [Layout Components](#layout-components)
   - [Navigation](#navigation)
   - [Footer](#footer)
3. [Feature Components](#feature-components)
   - [Cart](#cart)
   - [FilterTabs](#filtertabs)
4. [Component Testing](#component-testing)
5. [Accessibility Guidelines](#accessibility-guidelines)

---

## 🧩 UI Components

### Button

**Location:** `src/components/ui/Button.tsx`  
**Test Coverage:** 90%+  
**Accessibility:** ✅ WCAG AA Compliant

#### Variants

```tsx
// Primary Button (Vision Green)
<Button variant="primary">
  Primary Action
</Button>

// Secondary Button
<Button variant="secondary">
  Secondary Action
</Button>

// Outline Button
<Button variant="outline">
  Outline Action
</Button>

// Ghost Button (transparent)
<Button variant="ghost">
  Ghost Action
</Button>

// Destructive Button (for delete actions)
<Button variant="destructive">
  Delete
</Button>
```

#### Sizes

```tsx
<Button size="sm">Small Button</Button>
<Button size="md">Medium Button</Button>   {/* Default */}
<Button size="lg">Large Button</Button>
<Button size="xl">Extra Large Button</Button>
```

#### States

```tsx
// Loading State
<Button loading>
  Processing...
</Button>

// Disabled State
<Button disabled>
  Disabled Button
</Button>

// With Icon
<Button icon={<ShoppingCartIcon />}>
  Add to Cart
</Button>

// Full Width
<Button fullWidth>
  Full Width Button
</Button>
```

#### Accessibility Features

- ✅ Keyboard navigation (Enter, Space)
- ✅ Focus indicators (ring-2 ring-vision-green)
- ✅ Disabled state handling
- ✅ ARIA attributes support
- ✅ Screen reader friendly

#### Usage Example

```tsx
import { Button } from '@/components/ui/Button';
import { ShoppingCartIcon } from '@heroicons/react/24/outline';

function ProductCard() {
  const handleAddToCart = () => {
    // Add to cart logic
  };

  return (
    <Button 
      variant="primary" 
      size="lg"
      icon={<ShoppingCartIcon className="w-5 h-5" />}
      onClick={handleAddToCart}
      aria-label="Add product to cart"
    >
      Add to Cart
    </Button>
  );
}
```

#### Common Patterns

```tsx
// Submit Button
<Button type="submit" variant="primary">
  Submit Form
</Button>

// Cancel Button
<Button type="button" variant="ghost" onClick={onCancel}>
  Cancel
</Button>

// Delete Button
<Button variant="destructive" onClick={onDelete}>
  Delete Item
</Button>
```

---

### Badge

**Location:** `src/components/ui/Badge.tsx`  
**Test Coverage:** 95%+  
**Accessibility:** ✅ WCAG AA Compliant

#### Variants

```tsx
// New Product Badge
<Badge variant="new">New</Badge>

// Hot/Featured Badge
<Badge variant="hot">Hot</Badge>

// Pro/Premium Badge
<Badge variant="pro">Pro</Badge>

// Vision 2030 Badge
<Badge variant="vision2030">Vision 2030</Badge>

// Status Badges
<Badge variant="success">Active</Badge>
<Badge variant="warning">Pending</Badge>
<Badge variant="error">Error</Badge>

// Outline Badge
<Badge variant="outline">Outline</Badge>
```

#### Sizes

```tsx
<Badge size="sm">Small</Badge>
<Badge size="md">Medium</Badge>   {/* Default */}
<Badge size="lg">Large</Badge>
```

#### Accessibility Features

- ✅ ARIA label support
- ✅ Role attribute support
- ✅ Screen reader friendly
- ✅ High contrast colors

#### Usage Example

```tsx
import { Badge } from '@/components/ui/Badge';

function ProductCard({ product }) {
  return (
    <div className="product-card">
      {product.isNew && (
        <Badge variant="new" size="sm">
          New
        </Badge>
      )}
      {product.isFeatured && (
        <Badge variant="hot" size="sm">
          Hot
        </Badge>
      )}
      <h3>{product.name}</h3>
    </div>
  );
}
```

#### Common Patterns

```tsx
// Status Indicator
<Badge 
  variant={status === 'active' ? 'success' : 'error'}
  role="status"
  aria-label={`Status: ${status}`}
>
  {status}
</Badge>

// Count Badge
<Badge variant="outline" size="sm">
  {count} items
</Badge>

// Feature Tag
<Badge variant="pro">Premium Feature</Badge>
```

---

### Modal

**Location:** `src/components/ui/Modal.tsx`  
**Test Coverage:** 90%+  
**Accessibility:** ✅ WCAG AA Compliant

#### Basic Usage

```tsx
<Modal
  isOpen={isOpen}
  onClose={handleClose}
  title="Modal Title"
>
  <p>Modal content goes here</p>
</Modal>
```

#### With Custom Size

```tsx
<Modal
  isOpen={isOpen}
  onClose={handleClose}
  title="Large Modal"
  size="lg"  // sm, md, lg, xl, full
>
  <p>Large modal content</p>
</Modal>
```

#### Accessibility Features

- ✅ Focus trap (keeps focus inside modal)
- ✅ ESC key to close
- ✅ Click outside to close
- ✅ ARIA attributes (role="dialog", aria-modal)
- ✅ Focus returns to trigger element on close
- ✅ Backdrop blur effect

#### Usage Example

```tsx
import { useState } from 'react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';

function ProductDetails() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <Button onClick={() => setIsOpen(true)}>
        View Details
      </Button>

      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="Product Details"
      >
        <div className="space-y-4">
          <p>Product description goes here...</p>
          <Button variant="primary" fullWidth>
            Add to Cart
          </Button>
        </div>
      </Modal>
    </>
  );
}
```

#### Common Patterns

```tsx
// Confirmation Dialog
<Modal
  isOpen={showConfirm}
  onClose={() => setShowConfirm(false)}
  title="Confirm Delete"
>
  <p>Are you sure you want to delete this item?</p>
  <div className="flex gap-4 mt-6">
    <Button variant="destructive" onClick={handleDelete}>
      Delete
    </Button>
    <Button variant="ghost" onClick={() => setShowConfirm(false)}>
      Cancel
    </Button>
  </div>
</Modal>

// Form Modal
<Modal
  isOpen={showForm}
  onClose={() => setShowForm(false)}
  title="Edit Profile"
>
  <form onSubmit={handleSubmit}>
    <Input label="Name" name="name" />
    <Input label="Email" name="email" type="email" />
    <Button type="submit" fullWidth>
      Save Changes
    </Button>
  </form>
</Modal>
```

---

### Input

**Location:** `src/components/ui/Input.tsx`  
**Test Coverage:** 90%+  
**Accessibility:** ✅ WCAG AA Compliant

#### Basic Usage

```tsx
<Input
  label="Email"
  type="email"
  placeholder="Enter your email"
/>
```

#### With Error State

```tsx
<Input
  label="Password"
  type="password"
  error="Password must be at least 8 characters"
  required
/>
```

#### Input Types

```tsx
// Text Input
<Input label="Name" type="text" />

// Email Input
<Input label="Email" type="email" />

// Password Input
<Input label="Password" type="password" />

// Number Input
<Input label="Quantity" type="number" min="1" max="99" />

// Textarea
<Input label="Description" as="textarea" rows={4} />
```

#### Accessibility Features

- ✅ Label association (htmlFor/id)
- ✅ Required field indication
- ✅ Error message announcement (aria-invalid, aria-describedby)
- ✅ Disabled state handling
- ✅ Placeholder text

#### Usage Example

```tsx
import { Input } from '@/components/ui/Input';
import { useState } from 'react';

function ContactForm() {
  const [errors, setErrors] = useState({});

  return (
    <form>
      <Input
        label="Full Name"
        name="name"
        required
        error={errors.name}
      />
      
      <Input
        label="Email Address"
        name="email"
        type="email"
        required
        error={errors.email}
      />
      
      <Input
        label="Message"
        name="message"
        as="textarea"
        rows={4}
        required
        error={errors.message}
      />
    </form>
  );
}
```

#### Common Patterns

```tsx
// Search Input
<Input
  label="Search"
  type="search"
  placeholder="Search products..."
  icon={<MagnifyingGlassIcon />}
/>

// Number Input with Validation
<Input
  label="Quantity"
  type="number"
  min="1"
  max="99"
  defaultValue="1"
  required
/>

// Disabled Input
<Input
  label="Order ID"
  value={orderId}
  disabled
  readOnly
/>
```

---

## 🏗️ Layout Components

### Navigation

**Location:** `src/components/layout/Navigation.tsx`  
**Test Coverage:** 85%+  
**Accessibility:** ✅ WCAG AA Compliant

#### Features

- ✅ Responsive design (mobile menu)
- ✅ RTL support
- ✅ Glass morphism effect
- ✅ Cart badge counter
- ✅ Language toggle
- ✅ Smooth animations

#### Accessibility Features

- ✅ Semantic HTML (`<nav>`)
- ✅ ARIA labels for icon buttons
- ✅ Keyboard navigation
- ✅ Mobile menu toggle
- ✅ Focus management

#### Usage Example

```tsx
import { Navigation } from '@/components/layout/Navigation';

function Layout({ children }) {
  return (
    <>
      <Navigation />
      <main>{children}</main>
    </>
  );
}
```

---

### Footer

**Location:** `src/components/layout/Footer.tsx`  
**Test Coverage:** TBD  
**Accessibility:** ✅ WCAG AA Compliant

#### Features

- ✅ Multi-column layout
- ✅ Social media links
- ✅ Newsletter signup
- ✅ Copyright information
- ✅ RTL support

#### Accessibility Features

- ✅ Semantic HTML (`<footer>`)
- ✅ Proper heading hierarchy
- ✅ Link accessibility
- ✅ Form labels

---

## ⚡ Feature Components

### Cart

**Location:** `src/components/features/Cart.tsx`  
**Test Coverage:** 70%+  
**Accessibility:** ✅ WCAG AA Compliant

#### Features

- ✅ Add/remove items
- ✅ Update quantities
- ✅ Price calculations
- ✅ VAT calculation (15%)
- ✅ Empty state
- ✅ Checkout flow
- ✅ Persistent storage

#### Accessibility Features

- ✅ Modal dialog (role="dialog")
- ✅ Close button accessibility
- ✅ Keyboard navigation
- ✅ Screen reader announcements
- ✅ Focus management

#### Usage Example

```tsx
import { Cart } from '@/components/features/Cart';
import { useCartStore } from '@/stores/useCartStore';

function App() {
  const { isOpen } = useCartStore();

  return (
    <>
      <Navigation />
      {isOpen && <Cart />}
      <main>Content</main>
    </>
  );
}
```

---

### FilterTabs

**Location:** `src/components/features/FilterTabs.tsx`  
**Test Coverage:** 90%+  
**Accessibility:** ✅ WCAG AA Compliant

#### Features

- ✅ Tab navigation
- ✅ Active state indication
- ✅ Smooth transitions
- ✅ Responsive design

#### Accessibility Features

- ✅ ARIA roles (role="tablist", role="tab")
- ✅ Keyboard navigation (arrows)
- ✅ aria-selected attribute
- ✅ Focus indicators

#### Usage Example

```tsx
import { FilterTabs } from '@/components/features/FilterTabs';

function ProductList() {
  const [activeTab, setActiveTab] = useState('all');

  const tabs = [
    { id: 'all', label: 'All Products' },
    { id: 'new', label: 'New' },
    { id: 'featured', label: 'Featured' },
  ];

  return (
    <FilterTabs
      tabs={tabs}
      activeTab={activeTab}
      onTabChange={setActiveTab}
    />
  );
}
```

---

## 🧪 Component Testing

### Test Coverage Summary

| Component | Coverage | Tests | Status |
|-----------|----------|-------|--------|
| Button | 90%+ | 15 tests | ✅ |
| Badge | 95%+ | 20 tests | ✅ |
| Modal | 90%+ | 12 tests | ✅ |
| Input | 90%+ | 15 tests | ✅ |
| Navigation | 85%+ | 10 tests | ✅ |
| Cart | 70%+ | 25 tests | ⚠️ |
| FilterTabs | 90%+ | 8 tests | ✅ |

### Testing Guidelines

1. **Render Tests:** Verify component renders without errors
2. **Props Tests:** Test all prop variations
3. **Event Tests:** Test user interactions
4. **Accessibility Tests:** Test keyboard navigation and ARIA
5. **State Tests:** Test internal state management
6. **Integration Tests:** Test component interactions

### Example Test Structure

```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '@/components/ui/Button';

describe('Button Component', () => {
  it('should render with default props', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('should handle onClick events', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('should be keyboard accessible', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    const button = screen.getByRole('button');
    button.focus();
    fireEvent.keyDown(button, { key: 'Enter' });
    expect(handleClick).toHaveBeenCalled();
  });
});
```

---

## ♿ Accessibility Guidelines

### General Guidelines

1. **Keyboard Navigation**
   - All interactive elements must be keyboard accessible
   - Use `Tab` to navigate, `Enter/Space` to activate
   - Use `Esc` to close modals/menus

2. **Focus Indicators**
   - Always show visible focus indicators
   - Use `focus-visible:ring-2 focus-visible:ring-vision-green`

3. **Color Contrast**
   - Text must meet WCAG AA contrast ratios
   - Vision Green on Dark: 7.8:1 (AAA)
   - Text Primary on Dark: 21:1 (AAA)

4. **ARIA Attributes**
   - Use semantic HTML first
   - Add ARIA attributes when needed
   - Don't overuse ARIA (HTML5 is often sufficient)

5. **Screen Readers**
   - Test with screen readers
   - Use `aria-label` for icon-only buttons
   - Use `aria-live` for dynamic content

### Component-Specific Guidelines

#### Buttons
```tsx
// Icon button needs aria-label
<button aria-label="Close menu">
  <XMarkIcon />
</button>

// Disabled button
<button disabled aria-disabled="true">
  Disabled
</button>
```

#### Forms
```tsx
// Label association
<label htmlFor="email">Email</label>
<input id="email" type="email" />

// Error handling
<input
  aria-invalid={hasError}
  aria-describedby="email-error"
/>
{hasError && (
  <p id="email-error" role="alert">
    Error message
  </p>
)}
```

#### Modals
```tsx
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="modal-title"
>
  <h2 id="modal-title">Modal Title</h2>
</div>
```

---

## 📱 Responsive Design

### Breakpoint Guidelines

```tsx
// Mobile First Approach
<div className="
  text-base      /* Mobile */
  md:text-lg     /* Tablet */
  lg:text-xl     /* Desktop */
">
  Responsive Text
</div>
```

### Component Responsiveness

- **Navigation:** Hamburger menu on mobile
- **Cart:** Full-screen on mobile, sidebar on desktop
- **Cards:** Stack on mobile, grid on desktop
- **Forms:** Single column on mobile, two columns on desktop

---

## 🌍 RTL Support

### RTL-Safe Components

All components support RTL languages (Arabic):

```tsx
// Automatic direction switching
const { isRTL, setLanguage } = useAppStore();

// Switch to Arabic
setLanguage('ar'); // Sets dir="rtl"

// Components automatically adapt
<Button>زر</Button>  // Right-aligned text
```

### RTL Guidelines

1. Use logical properties (`start`/`end` instead of `left`/`right`)
2. Test all components in Arabic
3. Keep icons in logical positions
4. Use flexbox/grid for automatic mirroring

---

## 🎨 Styling Guidelines

### Glassmorphism

```tsx
<div className="glass rounded-2xl p-6">
  Glass Effect Content
</div>
```

### Animations

```tsx
<div className="animate-fade-in">
  Fades in on mount
</div>

<button className="transition-all duration-300 hover:scale-105">
  Hover me
</button>
```

### Color Usage

```tsx
// Primary Actions
className="bg-vision-green text-dark"

// Secondary Actions
className="bg-dark-card border border-glass-border"

// Text
className="text-text-primary"  // White
className="text-text-secondary"  // Gray
```

---

## 📚 Additional Resources

- [Design System Guide](./DESIGN_SYSTEM_GUIDE.md)
- [QA Status](./DESIGN_SYSTEM_QA_STATUS.md)
- [Accessibility Tests](./frontend/src/__tests__/accessibility/)
- [Component Tests](./frontend/src/__tests__/components/)

---

**Maintained by:** BrainSAIT Development Team  
**Last Review:** 2024-01-10  
**Next Review:** On component updates
