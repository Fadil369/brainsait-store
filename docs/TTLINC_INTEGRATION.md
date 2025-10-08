# TTLINC Integration Guide

## Overview

TTLINC (Translation & Localization Intelligence) is an AI-powered agent for continuous translation and localization management in the BrainSAIT platform.

## Architecture

```
┌─────────────────────────────────────────────────┐
│              TTLINC Agent                        │
├─────────────────────────────────────────────────┤
│  Translation Cache  │  Context Analysis          │
│  Quality Validation │  Batch Processing          │
│  Domain Adaptation  │  Cultural Localization     │
└─────────────────────────────────────────────────┘
         │                  │                │
         ▼                  ▼                ▼
    Frontend           Backend          External APIs
```

## Core Components

### 1. Translation Cache

The TTLINC agent includes an intelligent caching system:

```typescript
class TTLINCAgent {
  private cache: Map<string, TranslationResponse>;
  
  // Cache key format: {from}_{to}_{text}
  cacheKey = `${request.from}_${request.to}_${request.text}`;
}
```

**Benefits:**
- Reduces API calls
- Improves response time
- Maintains consistency

### 2. Context Awareness

TTLINC uses contextual information for better translations:

```typescript
await ttlincAgent.translate({
  text: 'Order',
  from: 'en',
  to: 'ar',
  context: 'ecommerce',
  domain: 'product_name'
});
// Better: "طلب" (order/purchase) vs "أمر" (command)
```

### 3. Quality Validation

Built-in validation ensures translation quality:

```typescript
const isValid = ttlincAgent.validateTranslation(
  original: 'Hello',
  translated: 'مرحبا',
  language: 'ar'
);
// Checks: Not empty, different from original, contains Arabic chars
```

## Integration Scenarios

### Scenario 1: Product Name Translation

```typescript
import { autoTranslateProductName } from '@/lib/ttlinc';

async function createProduct(productData) {
  // Auto-detect source language and translate
  const arabicName = await autoTranslateProductName(
    productData.name,
    'ar'
  );
  
  return {
    ...productData,
    name: productData.name,
    arabicTitle: arabicName
  };
}
```

### Scenario 2: Batch Product Translation

```typescript
import { ttlincAgent } from '@/lib/ttlinc';

async function translateProductCatalog(products) {
  const names = products.map(p => p.name);
  const descriptions = products.map(p => p.description);
  
  // Batch translate for efficiency
  const [translatedNames, translatedDescriptions] = await Promise.all([
    ttlincAgent.batchTranslate(names, 'en', 'ar'),
    ttlincAgent.batchTranslate(descriptions, 'en', 'ar')
  ]);
  
  return products.map((product, index) => ({
    ...product,
    arabicTitle: translatedNames[index].translatedText,
    arabicDescription: translatedDescriptions[index].translatedText
  }));
}
```

### Scenario 3: User-Generated Content Translation

```typescript
import { translateWithTTLINC } from '@/lib/ttlinc';

async function translateReview(review, targetLanguage) {
  const translatedTitle = await translateWithTTLINC(
    review.title,
    review.language,
    targetLanguage,
    'product_review_title'
  );
  
  const translatedContent = await translateWithTTLINC(
    review.content,
    review.language,
    targetLanguage,
    'product_review_content'
  );
  
  return {
    ...review,
    translatedTitle,
    translatedContent,
    targetLanguage
  };
}
```

## Backend Integration

### Python TTLINC Service

Create a TTLINC service in the backend:

```python
# backend/app/services/ttlinc_service.py

from typing import Dict, List, Optional
import httpx
from app.core.config import settings

class TTLINCService:
    def __init__(self):
        self.cache: Dict[str, str] = {}
        self.api_key = settings.TRANSLATION_API_KEY
    
    async def translate(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "ar",
        context: Optional[str] = None
    ) -> Dict[str, any]:
        """Translate text using TTLINC agent"""
        
        cache_key = f"{source_lang}_{target_lang}_{text}"
        
        if cache_key in self.cache:
            return {
                "translated_text": self.cache[cache_key],
                "confidence": 1.0,
                "cached": True
            }
        
        # In production, call actual translation API
        # For now, return original as fallback
        translated = text  # TODO: Implement API call
        
        self.cache[cache_key] = translated
        
        return {
            "translated_text": translated,
            "confidence": 0.95,
            "cached": False
        }
    
    async def batch_translate(
        self,
        texts: List[str],
        source_lang: str = "en",
        target_lang: str = "ar"
    ) -> List[Dict[str, any]]:
        """Batch translate multiple texts"""
        return [
            await self.translate(text, source_lang, target_lang)
            for text in texts
        ]

ttlinc_service = TTLINCService()
```

### API Endpoint

```python
# backend/app/api/v1/translation.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from app.services.ttlinc_service import ttlinc_service

router = APIRouter(prefix="/translation", tags=["translation"])

class TranslationRequest(BaseModel):
    text: str
    source_lang: str = "en"
    target_lang: str = "ar"
    context: Optional[str] = None

class BatchTranslationRequest(BaseModel):
    texts: List[str]
    source_lang: str = "en"
    target_lang: str = "ar"

@router.post("/translate")
async def translate_text(request: TranslationRequest):
    """Translate single text"""
    result = await ttlinc_service.translate(
        text=request.text,
        source_lang=request.source_lang,
        target_lang=request.target_lang,
        context=request.context
    )
    return result

@router.post("/batch-translate")
async def batch_translate_texts(request: BatchTranslationRequest):
    """Batch translate multiple texts"""
    results = await ttlinc_service.batch_translate(
        texts=request.texts,
        source_lang=request.source_lang,
        target_lang=request.target_lang
    )
    return {"translations": results}
```

## Continuous Translation Workflow

### Automated Translation Pipeline

```typescript
// Workflow: New Product → Auto-Translate → Save

import { ttlincAgent } from '@/lib/ttlinc';

class ProductTranslationWorkflow {
  async process(product: any) {
    try {
      // Step 1: Detect source language
      const hasArabic = /[\u0600-\u06FF]/.test(product.name);
      const sourceLang = hasArabic ? 'ar' : 'en';
      const targetLang = hasArabic ? 'en' : 'ar';
      
      // Step 2: Translate all fields
      const translations = await Promise.all([
        ttlincAgent.translate({
          text: product.name,
          from: sourceLang,
          to: targetLang,
          context: 'product_name'
        }),
        ttlincAgent.translate({
          text: product.description,
          from: sourceLang,
          to: targetLang,
          context: 'product_description'
        })
      ]);
      
      // Step 3: Validate translations
      const isValid = translations.every(t => 
        ttlincAgent.validateTranslation(
          product.name,
          t.translatedText,
          targetLang
        )
      );
      
      if (!isValid) {
        console.warn('Translation validation failed');
      }
      
      // Step 4: Return bilingual product
      return {
        ...product,
        name: sourceLang === 'en' ? product.name : translations[0].translatedText,
        arabicTitle: sourceLang === 'ar' ? product.name : translations[0].translatedText,
        description: sourceLang === 'en' ? product.description : translations[1].translatedText,
        arabicDescription: sourceLang === 'ar' ? product.description : translations[1].translatedText
      };
      
    } catch (error) {
      console.error('Translation workflow failed:', error);
      return product; // Return original on failure
    }
  }
}

export const productTranslationWorkflow = new ProductTranslationWorkflow();
```

## External Translation API Integration

### Google Cloud Translation

```typescript
import { Translate } from '@google-cloud/translate/build/src/v2';

class GoogleTTLINCAdapter {
  private translate: Translate;
  
  constructor(apiKey: string) {
    this.translate = new Translate({ key: apiKey });
  }
  
  async translate(text: string, targetLang: string): Promise<string> {
    const [translation] = await this.translate.translate(text, targetLang);
    return translation;
  }
}
```

### Azure Translator

```typescript
import axios from 'axios';

class AzureTTLINCAdapter {
  private apiKey: string;
  private endpoint: string;
  
  constructor(apiKey: string, endpoint: string) {
    this.apiKey = apiKey;
    this.endpoint = endpoint;
  }
  
  async translate(text: string, from: string, to: string): Promise<string> {
    const response = await axios.post(
      `${this.endpoint}/translate?api-version=3.0&from=${from}&to=${to}`,
      [{ text }],
      {
        headers: {
          'Ocp-Apim-Subscription-Key': this.apiKey,
          'Content-Type': 'application/json'
        }
      }
    );
    
    return response.data[0].translations[0].text;
  }
}
```

## Performance Optimization

### 1. Translation Preloading

Preload common translations on app startup:

```typescript
async function preloadCommonTranslations() {
  const commonPhrases = [
    'Add to Cart',
    'View Cart',
    'Checkout',
    'Product',
    'Price',
    'Total'
  ];
  
  await ttlincAgent.batchTranslate(commonPhrases, 'en', 'ar');
}
```

### 2. Lazy Translation

Translate content only when needed:

```typescript
const LazyTranslatedText = ({ text, from, to }) => {
  const [translated, setTranslated] = useState(text);
  
  useEffect(() => {
    translateWithTTLINC(text, from, to).then(setTranslated);
  }, [text, from, to]);
  
  return <span>{translated}</span>;
};
```

### 3. Cache Management

Implement cache size limits and TTL:

```typescript
class TTLINCAgent {
  private maxCacheSize = 1000;
  private cacheTTL = 3600000; // 1 hour
  
  private pruneCache() {
    if (this.cache.size > this.maxCacheSize) {
      const oldestKeys = Array.from(this.cache.keys()).slice(0, 100);
      oldestKeys.forEach(key => this.cache.delete(key));
    }
  }
}
```

## Monitoring and Analytics

### Translation Metrics

```typescript
class TTLINCAnalytics {
  private metrics = {
    totalTranslations: 0,
    cacheHits: 0,
    cacheMisses: 0,
    averageConfidence: 0,
    failedTranslations: 0
  };
  
  recordTranslation(result: TranslationResponse, cached: boolean) {
    this.metrics.totalTranslations++;
    if (cached) {
      this.metrics.cacheHits++;
    } else {
      this.metrics.cacheMisses++;
    }
    this.metrics.averageConfidence = 
      (this.metrics.averageConfidence + result.confidence) / 2;
  }
  
  getStats() {
    return {
      ...this.metrics,
      cacheHitRate: this.metrics.cacheHits / this.metrics.totalTranslations
    };
  }
}
```

## Best Practices

### 1. Domain-Specific Context

Always provide context for better translations:

```typescript
// ❌ Poor
await translate('Order', 'en', 'ar');

// ✅ Good
await translate('Order', 'en', 'ar', 'ecommerce_noun');
```

### 2. Fallback Strategy

Always have a fallback for translation failures:

```typescript
async function safeTranslate(text, from, to) {
  try {
    return await translateWithTTLINC(text, from, to);
  } catch (error) {
    console.error('Translation failed:', error);
    return text; // Return original
  }
}
```

### 3. Validation Before Save

Validate translations before persisting:

```typescript
async function saveTranslatedProduct(product) {
  const arabicTitle = await translate(product.title, 'en', 'ar');
  
  if (ttlincAgent.validateTranslation(product.title, arabicTitle, 'ar')) {
    await saveProduct({ ...product, arabicTitle });
  } else {
    throw new Error('Translation validation failed');
  }
}
```

## Troubleshooting

### Common Issues

**Issue: Translations not caching**
- Check cache size limits
- Verify cache key format
- Clear cache if corrupted

**Issue: Low confidence scores**
- Provide more context
- Use domain-specific terminology
- Check source text quality

**Issue: Incorrect translations**
- Verify language codes (ar-SA vs ar)
- Check context parameter
- Review domain configuration

## Future Roadmap

- [ ] Machine learning-based context detection
- [ ] Real-time collaborative translation
- [ ] Translation quality scoring with human feedback
- [ ] Dialect-specific translations (Egyptian, Gulf, Levantine)
- [ ] Integration with professional translation services
- [ ] Translation memory and term bases
- [ ] Automatic content update on translation changes

## Support

For TTLINC integration support:
- Technical documentation: This file
- API Reference: `/docs/API.md`
- GitHub Issues: Tag with `translation` or `ttlinc`
