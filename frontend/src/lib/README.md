# Frontend Library Utilities

This directory contains core utilities for the BrainSAIT Store bilingual platform.

## Overview

| Utility | Purpose | Language Support |
|---------|---------|------------------|
| `i18n.ts` | Internationalization configuration | AR, EN |
| `ttlinc.ts` | Translation & localization agent | AR ↔ EN |
| `voice-commands.ts` | Voice recognition handler | ar-SA, en-US |
| `arabic-ocr.ts` | Optical character recognition | AR, EN, Mixed |
| `hijri-calendar.ts` | Islamic/Gregorian calendar | AR, EN |

## Quick Start

### Language Management

```typescript
import { useTranslation } from 'react-i18next';
import { useAppStore } from '@/stores';

function MyComponent() {
  const { t } = useTranslation('common');
  const { language, setLanguage } = useAppStore();
  
  return (
    <div>
      <h1>{t('hero.title')}</h1>
      <button onClick={() => setLanguage(language === 'en' ? 'ar' : 'en')}>
        {language === 'en' ? 'العربية' : 'English'}
      </button>
    </div>
  );
}
```

### TTLINC Translation

```typescript
import { translateWithTTLINC } from '@/lib/ttlinc';

// Simple translation
const arabicText = await translateWithTTLINC('Hello', 'en', 'ar');

// With context
const productName = await translateWithTTLINC(
  'Premium Laptop',
  'en',
  'ar',
  'product_name'
);
```

### Voice Commands

```typescript
import { VoiceCommandHandler } from '@/lib/voice-commands';

const voiceHandler = new VoiceCommandHandler({ language: 'ar' });

voiceHandler.subscribe((result) => {
  console.log(result.transcript); // What user said
  console.log(result.confidence); // Accuracy (0-1)
});

voiceHandler.start(); // Begin listening
voiceHandler.stop();  // Stop listening
```

### OCR Processing

```typescript
import { processInvoice } from '@/lib/arabic-ocr';

const invoiceData = await processInvoice(imageFile);
console.log(invoiceData.invoiceNumber);
console.log(invoiceData.total);
console.log(invoiceData.vat);
```

### Calendar Display

```typescript
import { formatDate, isRamadan } from '@/lib/hijri-calendar';

// Format as Hijri
const hijriDate = formatDate(new Date(), 'hijri', 'ar');
// "15 رمضان 1446 هـ"

// Check Islamic holidays
if (isRamadan()) {
  console.log('رمضان كريم');
}
```

## File Descriptions

### i18n.ts

Core i18next configuration with:
- React integration
- Language detection (localStorage, navigator, HTML tag)
- Resource loading from `/public/locales`
- Namespace management

**Namespaces:**
- `common` - General UI strings
- `products` - Product-related text
- `cart` - Shopping cart
- `navigation` - Menu and navigation

### ttlinc.ts

Translation & Localization Intelligence agent:
- Translation caching for performance
- Batch translation support
- Context-aware translations
- Quality validation
- Auto-detect source language

**Key Classes:**
- `TTLINCAgent` - Main translation handler
- `TranslationRequest` - Request type
- `TranslationResponse` - Response type

### voice-commands.ts

Web Speech API integration:
- Real-time speech recognition
- Intent parsing (search, navigate, add_to_cart)
- Arabic and English command support
- Continuous and one-shot modes

**Key Classes:**
- `VoiceCommandHandler` - Main handler
- `VoiceCommandResult` - Result type

**Supported Intents:**
- Search: "ابحث عن", "search for"
- Navigate: "اذهب إلى", "go to"
- Add to cart: "أضف للسلة", "add to cart"

### arabic-ocr.ts

Optical Character Recognition for Arabic documents:
- Invoice data extraction
- Batch label processing
- Pattern-based field detection
- Confidence scoring

**Key Classes:**
- `ArabicOCRHandler` - Main OCR processor
- `OCRResult` - Result type
- `InvoiceData` - Structured invoice data

**Extractable Fields:**
- Invoice number
- Date
- Total amount
- VAT
- Line items
- Batch numbers
- Expiry dates

### hijri-calendar.ts

Islamic calendar utilities:
- Gregorian ↔ Hijri conversion
- Cultural date formatting
- Islamic holiday detection
- Month name localization

**Key Functions:**
- `getCalendarDate()` - Get both calendars
- `formatDate()` - Format by calendar type
- `isRamadan()` - Check if Ramadan
- `getIslamicHolidays()` - Get holiday dates

## Integration Examples

### Complete Bilingual Product Card

```typescript
import { useTranslation } from 'react-i18next';
import { useAppStore } from '@/stores';
import { formatDate } from '@/lib/hijri-calendar';

function ProductCard({ product }) {
  const { t } = useTranslation('products');
  const { language } = useAppStore();
  
  const name = language === 'ar' 
    ? product.arabicTitle || product.title
    : product.title;
  
  const releaseDate = formatDate(
    new Date(product.releaseDate),
    'gregorian',
    language
  );
  
  return (
    <div dir={language === 'ar' ? 'rtl' : 'ltr'}>
      <h3>{name}</h3>
      <p>{product.description}</p>
      <span>{releaseDate}</span>
      <button>{t('addToCart')}</button>
    </div>
  );
}
```

### Voice-Enabled Search

```typescript
import { useState, useEffect } from 'react';
import { voiceCommandHandler, parseVoiceIntent } from '@/lib/voice-commands';
import { useAppStore } from '@/stores';

function VoiceSearch() {
  const [isListening, setIsListening] = useState(false);
  const [query, setQuery] = useState('');
  const { language } = useAppStore();
  
  useEffect(() => {
    voiceCommandHandler.setLanguage(language);
    
    const unsubscribe = voiceCommandHandler.subscribe((result) => {
      if (result.isFinal) {
        const intent = parseVoiceIntent(result.transcript, language);
        if (intent.intent === 'search') {
          setQuery(intent.params.query);
          performSearch(intent.params.query);
        }
      }
    });
    
    return unsubscribe;
  }, [language]);
  
  const toggleListening = () => {
    if (isListening) {
      voiceCommandHandler.stop();
    } else {
      voiceCommandHandler.start();
    }
    setIsListening(!isListening);
  };
  
  return (
    <div>
      <input value={query} onChange={(e) => setQuery(e.target.value)} />
      <button onClick={toggleListening}>
        {isListening ? '🔴 Stop' : '🎤 Voice'}
      </button>
    </div>
  );
}
```

### Invoice Upload with OCR

```typescript
import { useState } from 'react';
import { processInvoice } from '@/lib/arabic-ocr';

function InvoiceUploader() {
  const [invoice, setInvoice] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const handleUpload = async (file: File) => {
    setLoading(true);
    try {
      const data = await processInvoice(file);
      setInvoice(data);
    } catch (error) {
      console.error('OCR failed:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div>
      <input 
        type="file" 
        accept="image/*"
        onChange={(e) => e.target.files?.[0] && handleUpload(e.target.files[0])}
      />
      
      {loading && <p>Processing...</p>}
      
      {invoice && (
        <div>
          <p>Invoice #: {invoice.invoiceNumber}</p>
          <p>Total: {invoice.total}</p>
          <p>VAT: {invoice.vat}</p>
        </div>
      )}
    </div>
  );
}
```

## Best Practices

### Translation Keys

✅ **Good:**
```typescript
t('product.card.addToCart')
t('cart.items.count', { count: 5 })
```

❌ **Bad:**
```typescript
'Add to Cart' // Hardcoded string
t('addToCart') // Too generic
```

### RTL Layouts

✅ **Good:**
```typescript
<div dir={language === 'ar' ? 'rtl' : 'ltr'}>
<span className="text-start"> {/* Logical property */}
```

❌ **Bad:**
```typescript
<div> {/* Missing dir */}
<span className="text-left"> {/* Directional property */}
```

### Voice Commands

✅ **Good:**
```typescript
// Clear error handling
try {
  voiceHandler.start();
} catch (error) {
  showNotification('Microphone not available');
}
```

❌ **Bad:**
```typescript
voiceHandler.start(); // No error handling
```

### OCR Processing

✅ **Good:**
```typescript
// Show loading state
setLoading(true);
const data = await processInvoice(file);
setLoading(false);
```

❌ **Bad:**
```typescript
// Blocking without feedback
const data = await processInvoice(file);
```

## Performance Tips

1. **Translation Caching**: TTLINC automatically caches translations
2. **Lazy Loading**: Load voice/OCR only when needed
3. **Image Optimization**: Compress images before OCR
4. **Debounce Voice**: Add delay before processing commands

## Browser Compatibility

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| i18n | ✅ | ✅ | ✅ | ✅ |
| TTLINC | ✅ | ✅ | ✅ | ✅ |
| Voice | ✅ | ❌ | ✅* | ✅ |
| OCR | ✅ | ✅ | ✅ | ✅ |
| Calendar | ✅ | ✅ | ✅ | ✅ |

*Safari: Limited voice recognition support

## Testing

Run tests:
```bash
npm test -- --testPathPattern=lib
```

Run specific utility tests:
```bash
npm test -- i18n
npm test -- ttlinc
npm test -- voice-commands
```

## Documentation

- [Bilingual Architecture Guide](../../../docs/BILINGUAL_ARCHITECTURE.md)
- [TTLINC Integration Guide](../../../docs/TTLINC_INTEGRATION.md)
- [Testing Guide](../../../docs/TESTING_BILINGUAL.md)

## Support

For issues or questions:
- GitHub Issues: Tag with `i18n`, `translation`, or specific utility
- Documentation: `/docs` directory
- Technical Lead: Dr. Fadil
