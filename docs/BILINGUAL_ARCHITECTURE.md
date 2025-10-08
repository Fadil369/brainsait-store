# Bilingual-First Architecture Guide

## Overview

This document describes the bilingual-first architecture implemented for the BrainSAIT Store platform, providing comprehensive support for Arabic and English languages across all user-facing applications.

## Table of Contents

1. [Core Features](#core-features)
2. [Translation System](#translation-system)
3. [RTL/LTR Support](#rtlltr-support)
4. [TTLINC Integration](#ttlinc-integration)
5. [Voice Commands](#voice-commands)
6. [Arabic OCR](#arabic-ocr)
7. [Hijri Calendar](#hijri-calendar)
8. [Usage Examples](#usage-examples)
9. [Testing Guidelines](#testing-guidelines)

## Core Features

### Supported Languages
- **English (en)**: Default language, LTR layout
- **Arabic (ar)**: Fully supported, RTL layout

### Key Capabilities
- Dynamic language switching without page reload
- Automatic RTL/LTR layout adjustment
- Voice commands in both languages
- Arabic OCR for documents
- Hijri/Gregorian calendar integration
- Cultural-aware date formatting
- Currency formatting per locale

## Translation System

### Frontend Translation Files

Translation files are located in `/frontend/public/locales/{language}/{namespace}.json`

#### Available Namespaces
- `common.json` - General UI strings
- `products.json` - Product-related strings
- `cart.json` - Shopping cart strings
- `navigation.json` - Navigation menu strings

#### Example Usage

```typescript
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { t } = useTranslation('common');
  
  return (
    <div>
      <h1>{t('hero.title')}</h1>
      <p>{t('hero.subtitle')}</p>
    </div>
  );
}
```

### Backend Translation Files

Translation files are located in `/backend/app/translations/{language}.json`

#### Example Usage

```python
from app.core.localization import get_localized_message

message = get_localized_message(
    key="product.created",
    language=request.state.language,
    default_en="Product created successfully",
    default_ar="تم إنشاء المنتج بنجاح"
)
```

## RTL/LTR Support

### Automatic Layout Direction

The layout direction is automatically set based on the selected language:

```typescript
// In layout.tsx
const dir = language === 'ar' ? 'rtl' : 'ltr';
document.documentElement.dir = dir;
```

### RTL-Specific CSS

Custom CSS utilities are provided for RTL layouts:

```css
/* RTL margin adjustments */
[dir="rtl"] .ml-auto {
  margin-left: 0;
  margin-right: auto;
}

/* RTL flexbox */
[dir="rtl"] .flex-row {
  flex-direction: row-reverse;
}

/* RTL text alignment */
[dir="rtl"] .text-left {
  text-align: right;
}
```

### Arabic Font Optimization

Arabic text uses optimized fonts with proper rendering:

```css
[dir="rtl"] body {
  font-family: 'Noto Sans Arabic', 'Noto Sans', sans-serif;
  font-feature-settings: 'ss01', 'ss05';
  -webkit-font-smoothing: antialiased;
}
```

## TTLINC Integration

TTLINC (Translation & Localization Intelligence) provides continuous translation capabilities.

### Basic Usage

```typescript
import { ttlincAgent, translateWithTTLINC } from '@/lib/ttlinc';

// Simple translation
const translated = await translateWithTTLINC(
  'Hello World',
  'en',
  'ar',
  'greeting'
);

// Batch translation
const texts = ['Product 1', 'Product 2', 'Product 3'];
const results = await ttlincAgent.batchTranslate(texts, 'en', 'ar');

// Auto-translate product names
import { autoTranslateProductName } from '@/lib/ttlinc';
const arabicName = await autoTranslateProductName('Product Name', 'ar');
```

### Configuration

```typescript
import { TTLINCAgent } from '@/lib/ttlinc';

const agent = new TTLINCAgent({
  sourceLanguage: 'en',
  targetLanguage: 'ar',
  domain: 'ecommerce',
  contextual: true,
});
```

## Voice Commands

### Setup Voice Recognition

```typescript
import { VoiceCommandHandler } from '@/lib/voice-commands';

const voiceHandler = new VoiceCommandHandler({
  language: 'ar', // or 'en'
  continuous: false,
  interimResults: true,
});

// Start listening
voiceHandler.start();

// Subscribe to results
voiceHandler.subscribe((result) => {
  console.log('Transcript:', result.transcript);
  console.log('Confidence:', result.confidence);
});

// Stop listening
voiceHandler.stop();
```

### Voice Intent Parsing

```typescript
import { parseVoiceIntent } from '@/lib/voice-commands';

// Parse Arabic command
const intent = parseVoiceIntent('ابحث عن منتج', 'ar');
// { intent: 'search', params: { query: 'منتج' } }

// Parse English command
const intent2 = parseVoiceIntent('search for product', 'en');
// { intent: 'search', params: { query: 'product' } }
```

### Supported Intents

- **search**: Search for products
  - Arabic: "ابحث عن", "أريد", "أبحث"
  - English: "search for", "find", "look for"

- **navigate**: Navigate to pages
  - Arabic: "السلة", "المنتجات", "الرئيسية"
  - English: "cart", "products", "home"

- **add_to_cart**: Add items to cart
  - Arabic: "أضف إلى السلة", "أضف للسلة"
  - English: "add to cart", "buy"

## Arabic OCR

### Extract Text from Images

```typescript
import { arabicOCR } from '@/lib/arabic-ocr';

// Extract text from invoice
const result = await arabicOCR.extractText(imageFile, 'ar');
console.log('Text:', result.text);
console.log('Confidence:', result.confidence);
```

### Extract Invoice Data

```typescript
import { processInvoice } from '@/lib/arabic-ocr';

const invoiceData = await processInvoice(imageFile);
console.log('Invoice Number:', invoiceData.invoiceNumber);
console.log('Total:', invoiceData.total);
console.log('VAT:', invoiceData.vat);
```

### Extract Batch Information

```typescript
import { processBatchLabel } from '@/lib/arabic-ocr';

const batchInfo = await processBatchLabel(imageFile);
console.log('Batch Number:', batchInfo.batchNumber);
console.log('Expiry Date:', batchInfo.expiryDate);
```

## Hijri Calendar

### Convert Dates

```typescript
import { getCalendarDate, formatDate } from '@/lib/hijri-calendar';

// Get both calendars
const calendarDate = getCalendarDate(new Date());
console.log('Gregorian:', calendarDate.gregorian);
console.log('Hijri:', calendarDate.hijri);

// Format date
const hijriDate = formatDate(new Date(), 'hijri', 'ar');
// Output: "15 رمضان 1446 هـ"

const gregorianDate = formatDate(new Date(), 'gregorian', 'en');
// Output: "March 15, 2025"
```

### Islamic Holidays

```typescript
import { getIslamicHolidays, isRamadan } from '@/lib/hijri-calendar';

// Check if current date is in Ramadan
if (isRamadan()) {
  console.log('Happy Ramadan!');
}

// Get Islamic holidays for the year
const holidays = getIslamicHolidays(1446);
holidays.forEach(holiday => {
  console.log(holiday.nameAr, '-', holiday.name);
});
```

## Usage Examples

### Complete Language Switcher Implementation

```typescript
import { LanguageSwitcher } from '@/components/LanguageSwitcher';

function Header() {
  return (
    <header>
      <nav>
        {/* Your navigation items */}
        <LanguageSwitcher />
      </nav>
    </header>
  );
}
```

### Bilingual Product Display

```typescript
import { useTranslation } from 'react-i18next';
import { useAppStore } from '@/stores';

function ProductCard({ product }) {
  const { t } = useTranslation('products');
  const { language } = useAppStore();
  
  const productName = language === 'ar' 
    ? product.arabicTitle || product.title
    : product.title;
  
  return (
    <div className="product-card">
      <h3>{productName}</h3>
      <p>{product.description}</p>
      <button>{t('addToCart')}</button>
    </div>
  );
}
```

### Cultural Date Display

```typescript
import { formatDate } from '@/lib/hijri-calendar';
import { useAppStore } from '@/stores';

function OrderDate({ date }) {
  const { language } = useAppStore();
  const calendarPref = localStorage.getItem('calendar-preference') || 'gregorian';
  
  return (
    <span>
      {formatDate(date, calendarPref, language)}
    </span>
  );
}
```

## Testing Guidelines

### Testing RTL/LTR Layouts

1. Switch language to Arabic
2. Verify:
   - Text is aligned to the right
   - Menus open from the right side
   - Navigation flows right-to-left
   - Icons and buttons are mirrored appropriately

### Testing Voice Commands

1. Enable microphone permissions
2. Test in Arabic:
   ```
   "ابحث عن منتج"
   "أضف للسلة"
   "الذهاب إلى السلة"
   ```
3. Test in English:
   ```
   "search for product"
   "add to cart"
   "go to cart"
   ```

### Testing OCR

1. Prepare test invoices in Arabic and English
2. Upload images through OCR interface
3. Verify extracted data accuracy:
   - Invoice numbers
   - Dates
   - Amounts
   - VAT calculations

### Testing Hijri Calendar

1. Compare Hijri dates with known conversion tools
2. Verify Islamic holiday dates
3. Test date formatting in both languages
4. Verify Ramadan and Hajj season detection

## Best Practices

### Translation Keys

- Use descriptive, hierarchical keys: `product.card.addToCart`
- Keep keys consistent across languages
- Avoid hardcoded strings in components

### RTL Design

- Use logical properties (`margin-inline-start` instead of `margin-left`)
- Test with real Arabic content (not Lorem Ipsum)
- Consider text expansion (Arabic can be 20-30% longer)

### Performance

- Lazy load translation files
- Cache TTLINC translations
- Preload voice recognition models
- Optimize OCR processing with image compression

### Accessibility

- Provide language labels in both languages
- Use `lang` attribute correctly
- Ensure voice commands have visual feedback
- Add keyboard shortcuts for language switching

## Troubleshooting

### Language Not Switching

Check:
1. localStorage has correct language value
2. i18n is properly initialized
3. Translation files are loaded
4. Component is using correct hook

### RTL Layout Issues

Check:
1. `dir` attribute is set on `<html>`
2. RTL CSS is loaded
3. Tailwind RTL utilities are used
4. Custom CSS respects direction

### Voice Commands Not Working

Check:
1. Browser supports Web Speech API
2. Microphone permissions granted
3. Correct language code is set
4. HTTPS is used (required for speech API)

### OCR Accuracy Issues

Tips:
1. Use high-quality images (300+ DPI)
2. Ensure good lighting and contrast
3. Align text horizontally
4. Use supported image formats (JPEG, PNG)

## Future Enhancements

- Integration with professional translation APIs (Google Translate, DeepL)
- Real-time voice translation
- Advanced OCR with machine learning models
- Automatic language detection
- Regional dialect support
- Multi-script support (Arabic variations)

## Support

For questions or issues related to bilingual support, please contact:
- Technical Lead: Dr. Fadil
- Documentation: `/docs` directory
- GitHub Issues: [brainsait-store/issues](https://github.com/Fadil369/brainsait-store/issues)
