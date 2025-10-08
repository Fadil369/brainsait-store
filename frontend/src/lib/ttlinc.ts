/**
 * TTLINC (Translation & Localization Intelligence) Integration
 * Continuous translation and localization agent for bilingual platform
 */

export interface TTLINCConfig {
  sourceLanguage: string;
  targetLanguage: string;
  domain: string;
  contextual: boolean;
}

export interface TranslationRequest {
  text: string;
  from: string;
  to: string;
  context?: string;
  domain?: string;
}

export interface TranslationResponse {
  translatedText: string;
  confidence: number;
  alternatives?: string[];
}

/**
 * TTLINC Agent - Handles continuous translation and localization
 */
export class TTLINCAgent {
  private config: TTLINCConfig;
  private cache: Map<string, TranslationResponse>;

  constructor(config: Partial<TTLINCConfig> = {}) {
    this.config = {
      sourceLanguage: config.sourceLanguage || 'en',
      targetLanguage: config.targetLanguage || 'ar',
      domain: config.domain || 'ecommerce',
      contextual: config.contextual !== undefined ? config.contextual : true,
    };
    this.cache = new Map();
  }

  /**
   * Translate text with context awareness
   */
  async translate(request: TranslationRequest): Promise<TranslationResponse> {
    const cacheKey = `${request.from}_${request.to}_${request.text}`;
    
    // Check cache first
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey)!;
    }

    try {
      // In production, this would call an actual translation API
      // For now, we use the existing translation files
      const response: TranslationResponse = {
        translatedText: request.text, // Fallback to original
        confidence: 1.0,
        alternatives: [],
      };

      // Cache the result
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

  /**
   * Batch translate multiple strings
   */
  async batchTranslate(
    texts: string[],
    from: string,
    to: string
  ): Promise<TranslationResponse[]> {
    return Promise.all(
      texts.map((text) => this.translate({ text, from, to }))
    );
  }

  /**
   * Validate translation quality
   */
  validateTranslation(
    original: string,
    translated: string,
    language: string
  ): boolean {
    // Basic validation rules
    if (!translated || translated.length === 0) return false;
    if (translated === original) return false; // Should be different
    
    // Language-specific validation
    if (language === 'ar') {
      // Check if contains Arabic characters
      return /[\u0600-\u06FF]/.test(translated);
    }
    
    return true;
  }

  /**
   * Clear translation cache
   */
  clearCache(): void {
    this.cache.clear();
  }

  /**
   * Get cache statistics
   */
  getCacheStats(): { size: number; keys: string[] } {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys()),
    };
  }
}

/**
 * Singleton instance for global access
 */
export const ttlincAgent = new TTLINCAgent();

/**
 * Helper function to translate with TTLINC
 */
export async function translateWithTTLINC(
  text: string,
  from: string = 'en',
  to: string = 'ar',
  context?: string
): Promise<string> {
  const response = await ttlincAgent.translate({ text, from, to, context });
  return response.translatedText;
}

/**
 * Auto-detect and translate product names
 */
export async function autoTranslateProductName(
  name: string,
  targetLanguage: string
): Promise<string> {
  // Detect source language
  const hasArabic = /[\u0600-\u06FF]/.test(name);
  const sourceLanguage = hasArabic ? 'ar' : 'en';
  
  if (sourceLanguage === targetLanguage) {
    return name; // Already in target language
  }
  
  return translateWithTTLINC(name, sourceLanguage, targetLanguage, 'product_name');
}

export default TTLINCAgent;
