# BrainSAIT Store - Design System Guide

**Version:** 1.0.0  
**Last Updated:** 2024-01-10  
**Status:** Active ✅

---

## 📚 Table of Contents

1. [Introduction](#introduction)
2. [Brand Colors](#brand-colors)
3. [Typography](#typography)
4. [Spacing System](#spacing-system)
5. [Glassmorphism](#glassmorphism)
6. [Motion Design](#motion-design)
7. [Component Patterns](#component-patterns)
8. [Accessibility Guidelines](#accessibility-guidelines)
9. [RTL Support](#rtl-support)
10. [Best Practices](#best-practices)

---

## 🎨 Introduction

The BrainSAIT Store design system is built on modern web standards with a focus on:
- **Vision 2030 Compliance:** Saudi Arabia's digital transformation initiative
- **Glassmorphism:** Modern, translucent UI elements
- **Bilingual Support:** Full Arabic/English with RTL
- **Accessibility:** WCAG 2.1 Level AA compliance
- **Performance:** Optimized animations and responsive design

---

## 🌈 Brand Colors

### Primary Colors

```css
/* Vision Green - Primary Brand Color */
--primary: #00d4aa;
--vision-green: #00d4aa;
/* Usage: Primary buttons, links, highlights */
/* Contrast Ratio on Dark: 7.8:1 (AAA) */

/* Secondary - Hover States */
--secondary: #00a886;
/* Usage: Hover states, secondary actions */

/* Vision Purple - Accent Color */
--vision-purple: #7c3aed;
/* Usage: Gradients, special highlights */

/* Accent - Call-to-Action */
--accent: #ff6b35;
/* Usage: Important CTAs, warnings */
/* Contrast Ratio on Dark: 6.2:1 (AA Large) */
```

### Dark Theme Colors

```css
/* Background Colors */
--dark: #000000;              /* Main background */
--dark-secondary: #0a0a0a;    /* Secondary background */
--dark-card: #111111;         /* Card backgrounds */
--dark-elevated: #1a1a1a;     /* Elevated surfaces */
```

### Text Colors

```css
/* Text Hierarchy */
--text-primary: #ffffff;      /* Primary text */
--text-secondary: #94a3b8;    /* Secondary text */
--text-muted: #64748b;        /* Muted text */

/* Contrast Ratios (on Dark Background) */
/* text-primary: 21:1 (AAA) */
/* text-secondary: 8.5:1 (AAA) */
```

### Status Colors

```css
--success: #10b981;  /* Success states */
--warning: #f59e0b;  /* Warning states */
--error: #ef4444;    /* Error states */
--info: #3b82f6;     /* Informational states */
```

### Glass Effects

```css
--glass-bg: rgba(255, 255, 255, 0.05);
--glass-border: rgba(255, 255, 255, 0.1);
--glass-hover: rgba(255, 255, 255, 0.08);
```

### Usage Examples

```tsx
// Primary Button
<button className="bg-vision-green text-dark hover:bg-secondary">
  Primary Action
</button>

// Glass Card
<div className="glass">
  Card Content
</div>

// Status Badge
<span className="bg-success text-white">
  Success
</span>
```

---

## ✍️ Typography

### Font Families

```css
/* Default (LTR) */
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 
             'SF Pro Display', 'Noto Sans Arabic', Roboto, 
             Oxygen, Ubuntu, sans-serif;

/* Arabic (RTL) */
font-family: 'Noto Sans Arabic', -apple-system, 
             BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

### Responsive Typography Scale

Using `clamp()` for fluid typography:

```css
/* Font Sizes */
--text-xs:     clamp(0.75rem, 2vw, 0.875rem);    /* 12-14px */
--text-sm:     clamp(0.875rem, 2.5vw, 1rem);     /* 14-16px */
--text-base:   clamp(1rem, 3vw, 1.125rem);       /* 16-18px */
--text-lg:     clamp(1.125rem, 3.5vw, 1.25rem);  /* 18-20px */
--text-xl:     clamp(1.25rem, 4vw, 1.5rem);      /* 20-24px */
--text-2xl:    clamp(1.5rem, 5vw, 2rem);         /* 24-32px */
--text-3xl:    clamp(1.875rem, 6vw, 2.5rem);     /* 30-40px */
--text-4xl:    clamp(2.25rem, 7vw, 3rem);        /* 36-48px */
--text-5xl:    clamp(3rem, 8vw, 4rem);           /* 48-64px */
```

### Tailwind Classes

```tsx
// Headings
<h1 className="text-clamp-4xl font-bold">Hero Title</h1>
<h2 className="text-clamp-3xl font-semibold">Section Title</h2>
<h3 className="text-clamp-2xl font-semibold">Subsection</h3>

// Body Text
<p className="text-clamp-base text-text-secondary">
  Body content with responsive sizing
</p>

// Small Text
<span className="text-clamp-sm text-text-muted">
  Small descriptive text
</span>
```

### Font Weights

```css
font-weight: 300;  /* Light */
font-weight: 400;  /* Regular */
font-weight: 500;  /* Medium */
font-weight: 600;  /* Semibold */
font-weight: 700;  /* Bold */
font-weight: 800;  /* Extrabold */
font-weight: 900;  /* Black */
```

---

## 📏 Spacing System

### Static Spacing

```css
/* Tailwind Custom Spacing */
xs:   0.25rem  (4px)
sm:   0.5rem   (8px)
md:   1rem     (16px)
lg:   1.5rem   (24px)
xl:   2rem     (32px)
2xl:  3rem     (48px)
3xl:  4rem     (64px)
```

### Responsive Spacing

```css
/* Fluid Spacing with clamp() */
--space-xs:   clamp(0.25rem, 1vw, 0.5rem);
--space-sm:   clamp(0.5rem, 2vw, 0.75rem);
--space-md:   clamp(1rem, 3vw, 1.25rem);
--space-lg:   clamp(1.5rem, 4vw, 2rem);
--space-xl:   clamp(2rem, 5vw, 3rem);
--space-2xl:  clamp(3rem, 6vw, 4rem);
--space-3xl:  clamp(4rem, 8vw, 6rem);
```

### Usage Examples

```tsx
// Static Spacing
<div className="p-md mb-lg">Content</div>

// Responsive Spacing (using CSS vars)
<section style={{ padding: 'var(--space-xl)' }}>
  Section Content
</section>
```

---

## 💎 Glassmorphism

### Core Principles

Glassmorphism creates depth and hierarchy through:
1. Semi-transparent backgrounds
2. Backdrop blur effects
3. Subtle borders
4. Layered shadows

### Glass Utilities

```css
/* Base Glass Effect */
.glass {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Glass Hover State */
.glass-hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: var(--vision-green);
}

/* Enhanced Card */
.enhanced-card {
  background: var(--glass-bg);
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  padding: var(--space-lg);
  transition: all var(--transition-normal);
}
```

### Usage Examples

```tsx
// Glass Card
<div className="glass rounded-2xl p-6 hover:glass-hover transition-all">
  <h3 className="text-xl font-bold text-text-primary">Title</h3>
  <p className="text-text-secondary">Description</p>
</div>

// Glass Navigation
<nav className="glass border-b border-glass-border">
  Navigation items
</nav>

// Glass Modal
<div className="fixed inset-0 bg-black/95 backdrop-blur-xl">
  <div className="glass rounded-3xl p-8">
    Modal content
  </div>
</div>
```

### Browser Support

- ✅ Chrome/Edge: Full support
- ✅ Safari: Full support
- ✅ Firefox: Supported with -webkit- prefix
- ⚠️ IE11: Fallback to solid background

---

## 🎬 Motion Design

### Animation Principles

1. **Purposeful:** Every animation serves a function
2. **Smooth:** Use easing functions for natural motion
3. **Fast:** Keep animations under 300ms for UI elements
4. **Accessible:** Respect `prefers-reduced-motion`

### Transition Speeds

```css
--transition-fast:   150ms ease-in-out;
--transition-normal: 250ms ease-in-out;
--transition-slow:   350ms ease-in-out;
```

### Predefined Animations

```css
/* Fade Effects */
animate-fade-in        /* 0.5s ease-in-out */
animate-fade-in-up     /* 1s ease */

/* Slide Effects */
animate-slide-down     /* 0.5s ease-out */
animate-slide-in       /* 0.3s ease */

/* Special Effects */
animate-float          /* 15s infinite - decorative */
animate-mesh-float     /* 20s infinite - backgrounds */
animate-pulse-glow     /* 2s infinite - highlights */
```

### Usage Examples

```tsx
// Button Hover
<button className="transition-all duration-300 hover:scale-105 hover:shadow-glow">
  Hover Me
</button>

// Modal Entry
<div className="animate-fade-in">
  <div className="animate-fade-in-up">
    Modal Content
  </div>
</div>

// Loading State
<div className="animate-pulse-glow">
  Loading...
</div>

// Decorative Float
<div className="animate-float opacity-30">
  Background Element
</div>
```

### Reduced Motion Support

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 🧩 Component Patterns

### Buttons

```tsx
// Primary Button
<button className="bg-vision-green text-dark hover:bg-secondary 
                   font-semibold px-6 py-3 rounded-xl 
                   transition-all duration-300 
                   focus-visible:ring-2 focus-visible:ring-vision-green">
  Primary Action
</button>

// Secondary Button
<button className="bg-dark-card text-text-primary hover:bg-dark-elevated 
                   border border-glass-border 
                   font-semibold px-6 py-3 rounded-xl">
  Secondary Action
</button>

// Ghost Button
<button className="text-vision-green hover:bg-vision-green/10 
                   font-semibold px-6 py-3 rounded-xl">
  Ghost Action
</button>
```

### Cards

```tsx
// Glass Card
<div className="glass rounded-2xl p-6 
                hover:border-vision-green 
                transition-all duration-300">
  Card Content
</div>

// Enhanced Card with Gradient Top
<div className="enhanced-card">
  Card Content
</div>
```

### Badges

```tsx
// Status Badges
<span className="bg-success text-white text-xs font-bold 
                uppercase tracking-wide px-2.5 py-1 rounded-lg">
  New
</span>

<span className="bg-vision-purple text-white text-xs font-bold 
                uppercase px-2.5 py-1 rounded-lg">
  Pro
</span>

<span className="bg-gradient-primary text-white text-xs font-bold 
                uppercase px-2.5 py-1 rounded-lg animate-pulse-glow">
  Hot
</span>
```

### Inputs

```tsx
// Text Input
<input 
  type="text"
  className="w-full bg-dark-card border border-glass-border 
             rounded-xl px-4 py-3 text-text-primary
             focus:border-vision-green focus:ring-2 
             focus:ring-vision-green/20 
             transition-all"
  placeholder="Enter text..."
/>

// Input with Error
<input 
  className="border-error focus:border-error focus:ring-error/20"
  aria-invalid="true"
  aria-describedby="error-message"
/>
<p id="error-message" className="text-error text-sm mt-1">
  Error message
</p>
```

---

## ♿ Accessibility Guidelines

### WCAG 2.1 Level AA Compliance

#### Color Contrast

✅ **Vision Green on Dark:** 7.8:1 (AAA)  
✅ **Text Primary on Dark:** 21:1 (AAA)  
✅ **Text Secondary on Dark:** 8.5:1 (AAA)  
✅ **Accent on Dark:** 6.2:1 (AA Large)

#### Keyboard Navigation

All interactive elements must be keyboard accessible:

```tsx
// Focus Indicators
<button className="focus-visible:outline-none 
                   focus-visible:ring-2 
                   focus-visible:ring-vision-green 
                   focus-visible:ring-offset-2">
  Accessible Button
</button>
```

#### ARIA Attributes

```tsx
// Icon-only buttons
<button aria-label="Close menu">
  <XMarkIcon />
</button>

// Form inputs
<label htmlFor="email">Email</label>
<input 
  id="email" 
  type="email"
  aria-required="true"
  aria-invalid={hasError}
  aria-describedby="email-error"
/>

// Modal dialogs
<div role="dialog" aria-labelledby="modal-title" aria-modal="true">
  <h2 id="modal-title">Modal Title</h2>
</div>
```

#### Screen Reader Support

```tsx
// Hidden text for screen readers
<span className="sr-only">Loading...</span>

// Aria-live regions for dynamic content
<div aria-live="polite" aria-atomic="true">
  Status update
</div>
```

### Accessibility Checklist

- [ ] All interactive elements keyboard accessible
- [ ] Focus indicators visible and clear
- [ ] Color contrast meets WCAG AA standards
- [ ] All images have alt text
- [ ] Forms have associated labels
- [ ] Error messages are announced
- [ ] Modals trap focus properly
- [ ] Skip links for navigation
- [ ] Semantic HTML used throughout
- [ ] ARIA attributes used correctly

---

## 🌍 RTL Support

### Language Switching

```typescript
// Using useAppStore
const { language, isRTL, setLanguage } = useAppStore();

// Switch to Arabic
setLanguage('ar'); // Sets dir="rtl" and lang="ar"

// Switch to English
setLanguage('en'); // Sets dir="ltr" and lang="en"
```

### RTL Utilities

```tsx
// Direction classes
<div className="rtl">RTL Content</div>
<div className="ltr">LTR Content</div>

// Conditional rendering based on direction
{isRTL ? (
  <div className="text-right">Arabic Text</div>
) : (
  <div className="text-left">English Text</div>
)}
```

### RTL-Safe Spacing

```tsx
// Use logical properties instead of left/right
<div className="ps-4">  {/* padding-inline-start */}
<div className="pe-4">  {/* padding-inline-end */}
<div className="ms-4">  {/* margin-inline-start */}
<div className="me-4">  {/* margin-inline-end */}
```

### Font Handling

```css
/* English (LTR) */
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI';

/* Arabic (RTL) */
font-family: 'Noto Sans Arabic', -apple-system, BlinkMacSystemFont;
```

### RTL Guidelines

1. **Text Alignment:** Use `text-start` and `text-end` instead of `text-left`/`text-right`
2. **Icons:** Keep directional icons (arrows) in their logical position
3. **Layouts:** Use flexbox/grid which automatically mirror
4. **Fixed Elements:** Position fixed elements using logical properties
5. **Animations:** Test all animations in RTL mode

---

## 💡 Best Practices

### Performance

1. **Use CSS Variables:** Faster than recalculating colors
2. **Limit Backdrop Blur:** Can be expensive on low-end devices
3. **Optimize Animations:** Use `transform` and `opacity` for GPU acceleration
4. **Lazy Load:** Load heavy components on demand

### Maintainability

1. **Follow Naming Conventions:** Use BEM or semantic class names
2. **Component Composition:** Build complex UIs from simple components
3. **Design Tokens:** Use CSS variables for consistent theming
4. **Documentation:** Comment complex interactions

### Responsive Design

```tsx
// Mobile-first approach
<div className="
  text-base      /* Mobile: 16px */
  md:text-lg     /* Tablet: 18px */
  lg:text-xl     /* Desktop: 20px */
  p-4            /* Mobile: 16px */
  md:p-6         /* Tablet: 24px */
  lg:p-8         /* Desktop: 32px */
">
  Responsive Content
</div>
```

### Testing

1. **Visual Regression:** Test component appearance
2. **Accessibility:** Use axe-core for automated testing
3. **RTL Testing:** Test all components in Arabic
4. **Browser Testing:** Test on Chrome, Safari, Firefox
5. **Device Testing:** Test on mobile devices

---

## 📱 Responsive Breakpoints

```css
/* Custom Breakpoints */
xs:   475px    /* Small phones */
sm:   640px    /* Large phones */
md:   768px    /* Tablets */
lg:   1024px   /* Small laptops */
xl:   1280px   /* Desktop */
2xl:  1536px   /* Large desktop */
3xl:  1600px   /* Ultra-wide */
```

---

## 🎯 Z-Index Layers

```css
--z-background:    -1
--z-navigation:    1000
--z-modal:         2000
--z-cart:          2000
--z-demo:          3000
--z-notification:  4000
```

---

## 📚 Resources

- [Tailwind CSS Documentation](https://tailwindcss.com)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [MDN Web Docs](https://developer.mozilla.org)
- [Noto Sans Arabic Font](https://fonts.google.com/noto/specimen/Noto+Sans+Arabic)

---

**Maintained by:** BrainSAIT Development Team  
**Questions?** Create an issue in the repository
