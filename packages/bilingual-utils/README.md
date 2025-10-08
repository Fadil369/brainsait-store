# Bilingual Utils Package

Utilities for Arabic/English bilingual support in BrainSAIT applications.

## Features

- Text direction detection (LTR/RTL)
- Number formatting (Arabic/Western numerals)
- Date formatting (Arabic/Gregorian, Hijri calendar)
- Currency formatting (SAR, USD, EUR)
- Language detection
- Text translation helpers
- RTL CSS utilities

## Usage

### Text Direction

```typescript
import { getTextDirection, isRTL } from '@brainsait/bilingual-utils';

const direction = getTextDirection('ar'); // 'rtl'
const isArabic = isRTL('ar'); // true
```

### Number Formatting

```typescript
import { formatNumber } from '@brainsait/bilingual-utils';

// Arabic (Eastern Arabic numerals)
formatNumber(12345, 'ar'); // '١٢٬٣٤٥'

// English (Western numerals)
formatNumber(12345, 'en'); // '12,345'
```

### Date Formatting

```typescript
import { formatDate } from '@brainsait/bilingual-utils';

const date = new Date('2024-01-01');

// Arabic
formatDate(date, 'ar'); // '١ يناير ٢٠٢٤'

// English
formatDate(date, 'en'); // 'January 1, 2024'
```

### Currency Formatting

```typescript
import { formatCurrency } from '@brainsait/bilingual-utils';

// Arabic (SAR)
formatCurrency(1234.56, 'SAR', 'ar'); // '١٬٢٣٤٫٥٦ ر.س'

// English (SAR)
formatCurrency(1234.56, 'SAR', 'en'); // 'SAR 1,234.56'
```

### Language Detection

```typescript
import { detectLanguage } from '@brainsait/bilingual-utils';

detectLanguage('مرحبا'); // 'ar'
detectLanguage('Hello'); // 'en'
```

### Translation Helper

```typescript
import { translate } from '@brainsait/bilingual-utils';

// With i18next integration
translate('common.welcome', 'ar'); // 'مرحبا'
translate('common.welcome', 'en'); // 'Welcome'
```

## Development

```bash
npm install
npm run dev
```

## Testing

```bash
npm test
```
