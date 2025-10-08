/**
 * Voice Command Support for Arabic/English
 * Enables voice-based navigation and product search
 */

export interface VoiceCommandConfig {
  language: 'ar' | 'en';
  continuous: boolean;
  interimResults: boolean;
}

export interface VoiceCommandResult {
  transcript: string;
  confidence: number;
  isFinal: boolean;
  language: string;
}

export type VoiceCommandCallback = (result: VoiceCommandResult) => void;

/**
 * Voice Command Handler
 */
export class VoiceCommandHandler {
  private recognition: any = null;
  private isListening: boolean = false;
  private config: VoiceCommandConfig;
  private callbacks: Set<VoiceCommandCallback> = new Set();

  constructor(config: Partial<VoiceCommandConfig> = {}) {
    this.config = {
      language: config.language || 'en',
      continuous: config.continuous !== undefined ? config.continuous : false,
      interimResults: config.interimResults !== undefined ? config.interimResults : true,
    };
    this.initialize();
  }

  /**
   * Initialize Web Speech API
   */
  private initialize(): void {
    if (typeof window === 'undefined') return;

    const SpeechRecognition = 
      (window as any).SpeechRecognition || 
      (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      console.warn('Speech recognition not supported in this browser');
      return;
    }

    this.recognition = new SpeechRecognition();
    this.recognition.continuous = this.config.continuous;
    this.recognition.interimResults = this.config.interimResults;
    this.recognition.lang = this.config.language === 'ar' ? 'ar-SA' : 'en-US';

    this.recognition.onresult = (event: any) => {
      const result = event.results[event.results.length - 1];
      const transcript = result[0].transcript;
      const confidence = result[0].confidence;

      this.notifyCallbacks({
        transcript,
        confidence,
        isFinal: result.isFinal,
        language: this.config.language,
      });
    };

    this.recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      this.isListening = false;
    };

    this.recognition.onend = () => {
      this.isListening = false;
    };
  }

  /**
   * Start listening for voice commands
   */
  start(): void {
    if (!this.recognition) {
      console.warn('Speech recognition not available');
      return;
    }

    if (this.isListening) {
      console.warn('Already listening');
      return;
    }

    try {
      this.recognition.start();
      this.isListening = true;
    } catch (error) {
      console.error('Failed to start speech recognition:', error);
    }
  }

  /**
   * Stop listening for voice commands
   */
  stop(): void {
    if (!this.recognition || !this.isListening) return;

    try {
      this.recognition.stop();
      this.isListening = false;
    } catch (error) {
      console.error('Failed to stop speech recognition:', error);
    }
  }

  /**
   * Change language
   */
  setLanguage(language: 'ar' | 'en'): void {
    this.config.language = language;
    if (this.recognition) {
      this.recognition.lang = language === 'ar' ? 'ar-SA' : 'en-US';
    }
  }

  /**
   * Subscribe to voice command results
   */
  subscribe(callback: VoiceCommandCallback): () => void {
    this.callbacks.add(callback);
    return () => this.callbacks.delete(callback);
  }

  /**
   * Notify all subscribers
   */
  private notifyCallbacks(result: VoiceCommandResult): void {
    this.callbacks.forEach((callback) => callback(result));
  }

  /**
   * Check if speech recognition is supported
   */
  isSupported(): boolean {
    return this.recognition !== null;
  }

  /**
   * Get current listening status
   */
  getIsListening(): boolean {
    return this.isListening;
  }
}

/**
 * Parse voice command intents
 */
export function parseVoiceIntent(
  transcript: string,
  language: 'ar' | 'en'
): { intent: string; params: Record<string, any> } {
  const lowerTranscript = transcript.toLowerCase();

  // Search intents
  const searchKeywords = language === 'ar' 
    ? ['ابحث عن', 'أريد', 'أبحث', 'ابحث']
    : ['search for', 'find', 'look for', 'show me'];

  for (const keyword of searchKeywords) {
    if (lowerTranscript.includes(keyword)) {
      const query = lowerTranscript.split(keyword)[1]?.trim();
      return {
        intent: 'search',
        params: { query },
      };
    }
  }

  // Navigation intents
  const navigationKeywords = language === 'ar'
    ? { 'السلة': 'cart', 'المنتجات': 'products', 'الرئيسية': 'home' }
    : { 'cart': 'cart', 'products': 'products', 'home': 'home' };

  for (const [keyword, page] of Object.entries(navigationKeywords)) {
    if (lowerTranscript.includes(keyword)) {
      return {
        intent: 'navigate',
        params: { page },
      };
    }
  }

  // Add to cart intents
  const addToCartKeywords = language === 'ar'
    ? ['أضف إلى السلة', 'أضف للسلة', 'اشتر']
    : ['add to cart', 'buy', 'purchase'];

  for (const keyword of addToCartKeywords) {
    if (lowerTranscript.includes(keyword)) {
      return {
        intent: 'add_to_cart',
        params: {},
      };
    }
  }

  // Default: unknown intent
  return {
    intent: 'unknown',
    params: { transcript },
  };
}

/**
 * Singleton instance
 */
export const voiceCommandHandler = new VoiceCommandHandler();

export default VoiceCommandHandler;
