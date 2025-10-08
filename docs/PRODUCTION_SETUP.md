# Production Setup Guide for Bilingual Platform

## Overview

This guide covers the steps needed to prepare the bilingual platform for production deployment.

## Required Dependencies

### Backend Python Packages

Install these additional packages for production use:

```bash
# Accurate Hijri calendar conversion
pip install hijri-converter

# Google Cloud Translation API (recommended)
pip install google-cloud-translate

# Azure Translator (alternative)
pip install azure-ai-translation-text

# Tesseract OCR for Arabic text
pip install pytesseract
sudo apt-get install tesseract-ocr tesseract-ocr-ara
```

### Frontend npm Packages

The current implementation uses existing packages. For production enhancements:

```bash
# Optional: Enhanced voice recognition
npm install @tensorflow-models/speech-commands

# Optional: Advanced OCR
npm install tesseract.js
```

## Configuration

### 1. Hijri Calendar Setup

Replace the placeholder implementation:

**Before (Development):**
```python
# backend/app/utils/calendar.py
def gregorian_to_hijri(gregorian_date):
    # Simplified conversion
    hijri_year = int(year - 621.5643)
    # ...
```

**After (Production):**
```python
# backend/app/utils/calendar.py
from hijri_converter import Gregorian

def gregorian_to_hijri(gregorian_date):
    """Convert Gregorian date to Hijri date using accurate library"""
    if isinstance(gregorian_date, datetime):
        gregorian_date = gregorian_date.date()
    
    hijri = Gregorian(
        gregorian_date.year,
        gregorian_date.month,
        gregorian_date.day
    ).to_hijri()
    
    return (hijri.year, hijri.month, hijri.day)
```

### 2. TTLINC Translation API

Update the TTLINC agent to use a real translation API:

**Google Cloud Translation:**
```typescript
// frontend/src/lib/ttlinc.ts
import { Translate } from '@google-cloud/translate/build/src/v2';

class GoogleTranslationAdapter {
  private translate: Translate;
  
  constructor(apiKey: string) {
    this.translate = new Translate({ key: apiKey });
  }
  
  async translate(text: string, to: string): Promise<string> {
    const [translation] = await this.translate.translate(text, to);
    return translation;
  }
}

// Update TTLINCAgent to use the adapter
export class TTLINCAgent {
  private adapter: GoogleTranslationAdapter;
  
  async translate(request: TranslationRequest): Promise<TranslationResponse> {
    const cacheKey = `${request.from}_${request.to}_${request.text}`;
    
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey)!;
    }
    
    try {
      const translatedText = await this.adapter.translate(
        request.text,
        request.to
      );
      
      const response: TranslationResponse = {
        translatedText,
        confidence: 1.0,
        alternatives: [],
      };
      
      this.cache.set(cacheKey, response);
      return response;
    } catch (error) {
      console.error('Translation error:', error);
      return {
        translatedText: request.text,
        confidence: 0,
        alternatives: [],
      };
    }
  }
}
```

**Backend Translation Service:**
```python
# backend/app/services/translation_service.py
from google.cloud import translate_v2 as translate
from app.core.config import settings

class TranslationService:
    def __init__(self):
        self.client = translate.Client()
    
    async def translate(
        self,
        text: str,
        target_language: str,
        source_language: str = None
    ) -> dict:
        """Translate text using Google Cloud Translation"""
        result = self.client.translate(
            text,
            target_language=target_language,
            source_language=source_language
        )
        
        return {
            "translated_text": result["translatedText"],
            "detected_source_language": result.get("detectedSourceLanguage"),
            "confidence": 1.0
        }
```

### 3. OCR Setup

**Backend with Tesseract:**
```python
# backend/app/services/ocr_service.py
import pytesseract
from PIL import Image
import io

class OCRService:
    def extract_text(self, image_data: bytes, language: str = "ara") -> dict:
        """Extract text from image using Tesseract OCR"""
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            
            # Configure for Arabic (ara) or English (eng)
            custom_config = r'--oem 3 --psm 6'
            
            # Extract text
            text = pytesseract.image_to_string(
                image,
                lang=language,
                config=custom_config
            )
            
            # Get confidence data
            data = pytesseract.image_to_data(
                image,
                lang=language,
                output_type=pytesseract.Output.DICT
            )
            
            # Calculate average confidence
            confidences = [c for c in data['conf'] if c != -1]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                "text": text,
                "confidence": avg_confidence / 100,
                "language": language
            }
        except Exception as e:
            raise Exception(f"OCR extraction failed: {str(e)}")
```

**Frontend with Tesseract.js:**
```typescript
// frontend/src/lib/arabic-ocr.ts
import Tesseract from 'tesseract.js';

export class ArabicOCRHandler {
  async extractText(
    imageFile: File | string,
    language: 'ar' | 'en' | 'auto' = 'auto'
  ): Promise<OCRResult> {
    try {
      const lang = language === 'ar' ? 'ara' : 'eng';
      
      const { data } = await Tesseract.recognize(imageFile, lang, {
        logger: (m) => console.log(m),
      });
      
      return {
        text: data.text,
        confidence: data.confidence / 100,
        language: language,
        blocks: data.words.map(word => ({
          text: word.text,
          confidence: word.confidence / 100,
          boundingBox: {
            x: word.bbox.x0,
            y: word.bbox.y0,
            width: word.bbox.x1 - word.bbox.x0,
            height: word.bbox.y1 - word.bbox.y0,
          },
        })),
      };
    } catch (error) {
      console.error('OCR extraction failed:', error);
      throw new Error('Failed to extract text from image');
    }
  }
}
```

### 4. Voice Commands Setup

No additional setup needed for Web Speech API. To enhance:

**Backend Voice Recognition Service (optional):**
```python
# backend/app/services/speech_service.py
from google.cloud import speech_v1 as speech

class SpeechRecognitionService:
    def __init__(self):
        self.client = speech.SpeechClient()
    
    async def transcribe_audio(
        self,
        audio_data: bytes,
        language_code: str = "ar-SA"
    ) -> dict:
        """Transcribe audio using Google Cloud Speech-to-Text"""
        audio = speech.RecognitionAudio(content=audio_data)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=language_code,
            alternative_language_codes=["en-US"],
        )
        
        response = self.client.recognize(config=config, audio=audio)
        
        if not response.results:
            return {
                "transcript": "",
                "confidence": 0.0
            }
        
        result = response.results[0]
        alternative = result.alternatives[0]
        
        return {
            "transcript": alternative.transcript,
            "confidence": alternative.confidence
        }
```

## Environment Variables

Add these to your `.env` file:

```bash
# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GOOGLE_CLOUD_PROJECT=your-project-id

# Translation
TRANSLATION_API_KEY=your-translation-api-key

# OCR
TESSERACT_PATH=/usr/bin/tesseract
TESSERACT_DATA=/usr/share/tesseract-ocr/4.00/tessdata/

# Azure (if using Azure Translator)
AZURE_TRANSLATOR_KEY=your-azure-key
AZURE_TRANSLATOR_ENDPOINT=https://api.cognitive.microsofttranslator.com/
AZURE_TRANSLATOR_REGION=your-region
```

## Deployment Checklist

- [ ] Install `hijri-converter` package
- [ ] Set up Google Cloud Translation API credentials
- [ ] Install and configure Tesseract OCR with Arabic language pack
- [ ] Update TTLINC agent to use real translation API
- [ ] Update OCR service to use Tesseract
- [ ] Configure environment variables
- [ ] Test Hijri calendar accuracy
- [ ] Test translation quality with sample content
- [ ] Test OCR with Arabic documents
- [ ] Monitor API usage and costs
- [ ] Set up error logging and monitoring
- [ ] Configure rate limiting for APIs
- [ ] Set up caching strategy
- [ ] Test voice commands on production domain (HTTPS required)

## API Cost Considerations

### Google Cloud Translation
- Free tier: 500,000 characters/month
- Paid: $20 per 1M characters
- **Recommendation**: Cache aggressively, translate only new content

### Google Cloud Speech-to-Text
- Free tier: 60 minutes/month
- Paid: $0.006 per 15 seconds
- **Recommendation**: Use browser Web Speech API when possible

### Google Cloud Vision (OCR)
- Free tier: 1,000 units/month
- Paid: $1.50 per 1,000 units
- **Recommendation**: Use Tesseract for simple documents, Vision for complex

## Performance Optimization

### Translation Caching
```python
# Implement Redis caching for translations
from redis import Redis

class CachedTranslationService:
    def __init__(self):
        self.redis = Redis(host='localhost', port=6379, db=0)
        self.translation_service = TranslationService()
        self.cache_ttl = 86400  # 24 hours
    
    async def translate(self, text: str, target: str) -> dict:
        cache_key = f"translation:{target}:{hash(text)}"
        
        # Check cache
        cached = self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Translate and cache
        result = await self.translation_service.translate(text, target)
        self.redis.setex(cache_key, self.cache_ttl, json.dumps(result))
        
        return result
```

### OCR Preprocessing
```python
def preprocess_image_for_ocr(image: Image) -> Image:
    """Optimize image for better OCR accuracy"""
    # Convert to grayscale
    image = image.convert('L')
    
    # Increase contrast
    from PIL import ImageEnhance
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    
    # Resize if too small
    if image.width < 1000:
        ratio = 1000 / image.width
        new_size = (int(image.width * ratio), int(image.height * ratio))
        image = image.resize(new_size, Image.LANCZOS)
    
    return image
```

## Monitoring

Set up monitoring for:
- Translation API response times
- Translation cache hit rates
- OCR accuracy scores
- Voice command success rates
- Language preference distribution
- Error rates by feature

## Testing in Production

After deployment, verify:
1. Hijri dates match official Islamic calendar
2. Translations are culturally appropriate
3. OCR accuracy meets >85% threshold
4. Voice commands work on HTTPS
5. RTL layouts display correctly
6. Performance meets benchmarks

## Rollback Plan

If issues occur:
1. Keep placeholder implementations as fallback
2. Feature flag each service independently
3. Monitor error rates and revert if > 5%
4. Have manual translation process ready as backup

## Support

For production issues:
- Technical Lead: Dr. Fadil
- Documentation: `/docs` directory
- Emergency contact: DevOps team

## Additional Resources

- [Google Cloud Translation API Docs](https://cloud.google.com/translate/docs)
- [Tesseract OCR Documentation](https://tesseract-ocr.github.io/)
- [hijri-converter Package](https://pypi.org/project/hijri-converter/)
- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
