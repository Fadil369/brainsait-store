# Bilingual Platform Testing Guide

## Overview

This guide provides comprehensive testing procedures for the bilingual-first architecture, covering frontend, backend, and integration scenarios.

## Test Categories

1. [UI/UX Testing](#uiux-testing)
2. [Translation Testing](#translation-testing)
3. [RTL/LTR Layout Testing](#rtlltr-layout-testing)
4. [Voice Command Testing](#voice-command-testing)
5. [OCR Testing](#ocr-testing)
6. [Calendar Testing](#calendar-testing)
7. [Integration Testing](#integration-testing)
8. [Performance Testing](#performance-testing)

## UI/UX Testing

### Language Switcher

**Test Case 1: Basic Language Switching**
```
Steps:
1. Open the application
2. Click the language switcher button
3. Observe language change

Expected Results:
- All UI text changes to selected language
- Layout direction changes (RTL for Arabic, LTR for English)
- Language preference saved to localStorage
- No page reload required
```

**Test Case 2: Language Persistence**
```
Steps:
1. Switch to Arabic
2. Refresh the page
3. Navigate to different pages

Expected Results:
- Arabic language persists after refresh
- All pages display in Arabic
- Direction remains RTL
```

### Mobile Responsiveness

**Test Case 3: Mobile Language Switching**
```
Devices: iPhone 12, Samsung Galaxy S21, iPad
Steps:
1. Access on mobile device
2. Switch language
3. Test all major features

Expected Results:
- Language switcher accessible on mobile
- RTL layout works correctly on mobile
- Touch interactions work in both directions
```

## Translation Testing

### Completeness Check

**Test Case 4: Translation Coverage**
```
Steps:
1. Navigate through all pages in English
2. Switch to Arabic
3. Check for untranslated text

Expected Results:
- No English text appears in Arabic mode
- No missing translation keys
- All dynamic content translates correctly
```

### Quality Assurance

**Test Case 5: Translation Accuracy**
```
Focus Areas:
- Product names and descriptions
- Error messages
- Form labels
- Button text
- Navigation items

Validation:
- Correct Arabic terminology
- Culturally appropriate phrases
- Proper grammar and spelling
```

### Context Appropriateness

**Test Case 6: Contextual Translation**
```
Examples to verify:
- "Order" → "طلب" (in shopping context) not "أمر" (command)
- "Add" → "أضف" (action) vs "إضافة" (noun)
- "Save" → "حفظ" (keep) vs "توفير" (economize)

Expected Results:
- Translations match context
- No literal/incorrect translations
```

## RTL/LTR Layout Testing

### Visual Alignment

**Test Case 7: Text Alignment**
```
Components to test:
- Headers and paragraphs
- Forms and inputs
- Cards and lists
- Navigation menus
- Footer sections

English (LTR):
- Text aligned left
- Icons on left side
- Menus open from left

Arabic (RTL):
- Text aligned right
- Icons on right side
- Menus open from right
```

### Layout Mirroring

**Test Case 8: Component Mirroring**
```
Elements to verify:
✓ Navigation arrows (← becomes →)
✓ Breadcrumbs (reverse order)
✓ Carousels (swipe direction)
✓ Dropdowns (open direction)
✓ Sidebars (position flip)

Testing:
1. Take screenshots in English
2. Switch to Arabic
3. Compare layouts
4. Verify proper mirroring
```

### CSS Direction Support

**Test Case 9: RTL CSS Classes**
```
Verify these work correctly:
- .ml-auto → .mr-auto in RTL
- .pl-4 → .pr-4 in RTL
- .text-left → .text-right in RTL
- .rounded-l-lg → .rounded-r-lg in RTL

Test Method:
Inspect elements in dev tools and verify CSS properties
```

## Voice Command Testing

### English Voice Commands

**Test Case 10: English Speech Recognition**
```
Commands to test:
1. "search for laptop"
2. "find AI tools"
3. "add to cart"
4. "go to cart"
5. "show products"

Setup:
- Chrome or Edge browser
- Allow microphone access
- Quiet environment
- Clear pronunciation

Expected Results:
- Accurate transcription (>90% confidence)
- Correct intent detection
- Appropriate action execution
```

### Arabic Voice Commands

**Test Case 11: Arabic Speech Recognition**
```
Commands to test:
1. "ابحث عن منتج"
2. "أضف للسلة"
3. "اذهب إلى السلة"
4. "اعرض المنتجات"
5. "أريد منتجات الذكاء الاصطناعي"

Expected Results:
- Accurate Arabic transcription
- Correct intent parsing
- Proper action execution
- Handles dialectal variations
```

### Voice Command Edge Cases

**Test Case 12: Error Handling**
```
Scenarios:
1. Background noise
2. Unclear speech
3. Unsupported commands
4. Mixed language input

Expected Behavior:
- Show error message
- Request clarification
- Fallback to text input
- Log failed attempts
```

## OCR Testing

### Invoice Processing

**Test Case 13: Arabic Invoice OCR**
```
Test Data:
- Arabic invoice samples
- Mixed Arabic/English invoices
- Various formats (PDF, JPEG, PNG)

Fields to extract:
✓ Invoice number
✓ Date
✓ Vendor name
✓ Total amount
✓ VAT amount
✓ Line items

Success Criteria:
- >85% extraction accuracy
- Correct field identification
- Proper number parsing
```

**Test Case 14: English Invoice OCR**
```
Similar to TC13 but with English invoices

Verify:
- Currency formatting
- Date format recognition
- Decimal separator handling
```

### Batch Label Processing

**Test Case 15: Batch Information Extraction**
```
Test Data:
- Product batch labels
- Expiry date labels
- Manufacturing labels

Fields to extract:
✓ Batch number
✓ Product code
✓ Manufacturing date
✓ Expiry date
✓ Lot number

Validation:
- Date format parsing
- Code pattern recognition
- Arabic/English text handling
```

### OCR Edge Cases

**Test Case 16: Low Quality Images**
```
Scenarios:
- Low resolution (< 150 DPI)
- Poor lighting
- Skewed/rotated text
- Partially obscured text

Expected Behavior:
- Attempt extraction
- Report confidence score
- Request better image quality
- Provide manual entry option
```

## Calendar Testing

### Hijri Calendar

**Test Case 17: Hijri Date Conversion**
```
Test Cases:
1. Current date conversion
2. Historical dates
3. Future dates
4. Edge cases (month boundaries)

Validation Method:
Compare with IslamicFinder.org or similar tool

Expected Accuracy: ±1-2 days (placeholder implementation)

IMPORTANT NOTE:
The current Hijri conversion uses a simplified algorithm for demonstration.
For production use, integrate the 'hijri-converter' Python package:
  pip install hijri-converter
  
This will provide accurate lunar calendar calculations.
```

**Test Case 18: Islamic Holidays**
```
Verify correct dates for:
- Ramadan start
- Eid al-Fitr
- Eid al-Adha
- Islamic New Year
- Day of Arafat

Cross-reference:
Saudi Ministry of Islamic Affairs calendar
```

### Date Formatting

**Test Case 19: Cultural Date Display**
```
English (Gregorian):
- March 15, 2025
- 03/15/2025

Arabic (Hijri):
- 15 رمضان 1446 هـ
- 15/09/1446

Arabic (Gregorian):
- 15 مارس 2025
- 15/03/2025

Verify:
- Correct format per language
- Month names in correct language
- Proper calendar indicator (هـ for Hijri)
```

## Integration Testing

### End-to-End Workflows

**Test Case 20: Complete Shopping Flow (Arabic)**
```
Workflow:
1. Switch to Arabic
2. Search for product (voice)
3. View product details
4. Add to cart
5. Proceed to checkout
6. Complete purchase

Verify at each step:
- Correct RTL layout
- Proper translations
- Currency formatting
- Date formatting
- Invoice generation in Arabic
```

**Test Case 21: Admin Operations (Bilingual)**
```
Workflow:
1. Login as admin
2. Create product (English)
3. Verify auto-translation to Arabic
4. Edit product in Arabic
5. View analytics in both languages

Verify:
- TTLINC translation quality
- Data consistency
- Report formatting
```

## Performance Testing

### Translation Performance

**Test Case 22: Translation Load Time**
```
Measure:
- Initial page load with translations
- Language switch time
- Translation cache effectiveness

Benchmarks:
- Initial load: < 2 seconds
- Language switch: < 500ms
- Cache hit rate: > 80%
```

### Voice Recognition Performance

**Test Case 23: Voice Command Latency**
```
Measure:
- Time from speech end to transcription
- Intent parsing time
- Action execution time

Benchmarks:
- Transcription: < 1 second
- Total latency: < 2 seconds
```

### OCR Performance

**Test Case 24: OCR Processing Time**
```
Test with various image sizes:
- Small (< 500KB): < 3 seconds
- Medium (500KB - 2MB): < 5 seconds
- Large (> 2MB): < 10 seconds

Verify:
- Processing time scales linearly
- Memory usage stays reasonable
- No memory leaks
```

## Automated Testing

### Unit Tests

```typescript
// Example: Translation loading test
describe('i18n', () => {
  it('should load English translations', () => {
    const t = i18n.getFixedT('en');
    expect(t('common:hero.title')).toBe('Digital Innovation Marketplace');
  });
  
  it('should load Arabic translations', () => {
    const t = i18n.getFixedT('ar');
    expect(t('common:hero.title')).toBe('سوق الابتكار الرقمي');
  });
});
```

### Integration Tests

```typescript
// Example: Language switching test
describe('Language Switcher', () => {
  it('should change language and update UI', async () => {
    render(<App />);
    
    const switcher = screen.getByRole('button', { name: /language/i });
    fireEvent.click(switcher);
    
    await waitFor(() => {
      expect(document.documentElement.dir).toBe('rtl');
      expect(screen.getByText('المنتجات')).toBeInTheDocument();
    });
  });
});
```

### E2E Tests

```typescript
// Example: Playwright test
test('complete bilingual shopping flow', async ({ page }) => {
  await page.goto('/');
  
  // Switch to Arabic
  await page.click('[data-testid="language-switcher"]');
  await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
  
  // Search for product
  await page.fill('[data-testid="search-input"]', 'منتج');
  await page.press('[data-testid="search-input"]', 'Enter');
  
  // Add to cart
  await page.click('[data-testid="add-to-cart"]');
  await expect(page.locator('[data-testid="cart-count"]')).toHaveText('1');
  
  // Verify cart in Arabic
  await page.click('[data-testid="cart-button"]');
  await expect(page.locator('h2')).toHaveText('سلة التسوق');
});
```

## Test Data

### Sample Products

```json
{
  "products": [
    {
      "id": 1,
      "title": "AI Assistant",
      "arabicTitle": "مساعد ذكي",
      "description": "Advanced AI tool",
      "arabicDescription": "أداة ذكاء اصطناعي متقدمة"
    }
  ]
}
```

### Sample Invoices

Create test invoice images:
- `test-invoice-arabic.jpg`
- `test-invoice-english.jpg`
- `test-invoice-mixed.jpg`

### Sample Voice Commands

Audio files for testing:
- `voice-search-en.wav`
- `voice-search-ar.wav`
- `voice-add-to-cart-en.wav`
- `voice-add-to-cart-ar.wav`

## Bug Reporting Template

```markdown
**Language:** Arabic / English
**Component:** [Navigation/Cart/Voice/OCR/Calendar]
**Severity:** [Critical/High/Medium/Low]

**Description:**
Clear description of the issue

**Steps to Reproduce:**
1. 
2. 
3. 

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Screenshots:**
[Attach screenshots]

**Environment:**
- Browser: 
- OS: 
- Device: 
- Screen Size: 
```

## Acceptance Criteria

Before marking bilingual support as complete, verify:

- [ ] All user-facing text translates correctly
- [ ] RTL/LTR layouts work on all pages
- [ ] Voice commands work in both languages
- [ ] OCR accurately extracts Arabic text
- [ ] Hijri calendar displays correctly
- [ ] Performance benchmarks met
- [ ] No console errors or warnings
- [ ] Accessibility standards met
- [ ] Mobile devices fully supported
- [ ] All tests passing

## Continuous Monitoring

Set up monitoring for:
- Translation API failures
- Voice recognition errors
- OCR processing failures
- Performance regressions
- User language preferences
- Error rates by language

## Resources

- [W3C Internationalization](https://www.w3.org/International/)
- [RTL Styling Best Practices](https://rtlstyling.com/)
- [Arabic Typography Guide](https://arabictypography.com/)
- [Islamic Calendar Resources](https://www.islamicfinder.org/)

## Support

For testing support or to report issues:
- GitHub Issues: Tag with `testing` and `bilingual`
- Documentation: `/docs/BILINGUAL_ARCHITECTURE.md`
- QA Team: qa@brainsait.com
