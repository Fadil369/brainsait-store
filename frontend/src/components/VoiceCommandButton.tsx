'use client';

import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { voiceCommandHandler, parseVoiceIntent, type VoiceCommandResult } from '@/lib/voice-commands';
import { useAppStore } from '@/stores';
import { useRouter } from 'next/navigation';

export function VoiceCommandButton() {
  const { t } = useTranslation('common');
  const { language } = useAppStore();
  const router = useRouter();
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isSupported, setIsSupported] = useState(false);

  useEffect(() => {
    // Check if voice recognition is supported
    setIsSupported(voiceCommandHandler.isSupported());

    // Update voice handler language when app language changes
    voiceCommandHandler.setLanguage(language);
  }, [language]);

  useEffect(() => {
    // Subscribe to voice command results
    const unsubscribe = voiceCommandHandler.subscribe(handleVoiceResult);
    return unsubscribe;
  }, [language]);

  const handleVoiceResult = (result: VoiceCommandResult) => {
    setTranscript(result.transcript);

    if (result.isFinal) {
      // Parse the voice intent
      const intent = parseVoiceIntent(result.transcript, language);
      
      // Execute the intent
      executeIntent(intent);

      // Clear transcript after 2 seconds
      setTimeout(() => {
        setTranscript('');
      }, 2000);
    }
  };

  const executeIntent = (intent: { intent: string; params: Record<string, any> }) => {
    switch (intent.intent) {
      case 'search':
        if (intent.params.query) {
          // Navigate to search with query
          router.push(`/?search=${encodeURIComponent(intent.params.query)}`);
        }
        break;

      case 'navigate':
        // Navigate to page
        const page = intent.params.page;
        if (page === 'cart') {
          router.push('/cart');
        } else if (page === 'products') {
          router.push('/products');
        } else if (page === 'home') {
          router.push('/');
        }
        break;

      case 'add_to_cart':
        // This would need access to current product context
        console.log('Add to cart intent detected');
        break;

      default:
        console.log('Unknown intent:', intent);
    }
  };

  const toggleListening = () => {
    if (isListening) {
      voiceCommandHandler.stop();
      setIsListening(false);
    } else {
      voiceCommandHandler.start();
      setIsListening(true);
    }
  };

  if (!isSupported) {
    return null; // Don't show button if not supported
  }

  return (
    <div className="relative">
      <button
        onClick={toggleListening}
        className={`group relative flex items-center gap-2 px-4 py-2 rounded-lg border transition-all duration-300 ${
          isListening
            ? 'bg-red-500/20 border-red-500/50 text-red-400'
            : 'bg-white/5 hover:bg-white/10 border-white/10 hover:border-white/20 text-gray-300'
        }`}
        aria-label={isListening ? 'Stop voice command' : 'Start voice command'}
        title={t('voice.tooltip', { defaultValue: 'Voice command' })}
      >
        {/* Microphone Icon */}
        <svg
          className={`w-5 h-5 transition-colors ${
            isListening ? 'text-red-400 animate-pulse' : 'text-gray-300 group-hover:text-primary'
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
          />
        </svg>

        {/* Status text */}
        <span className="text-sm font-medium">
          {isListening
            ? (language === 'ar' ? 'استمع...' : 'Listening...')
            : (language === 'ar' ? 'صوتي' : 'Voice')}
        </span>

        {/* Animated indicator */}
        {isListening && (
          <span className="absolute inset-0 rounded-lg bg-red-500/20 animate-ping" />
        )}
      </button>

      {/* Transcript Display */}
      {transcript && (
        <div className="absolute top-full mt-2 left-0 right-0 min-w-[200px] px-4 py-2 bg-black/90 border border-white/20 rounded-lg text-sm text-white z-50 shadow-xl">
          <div className="flex items-start gap-2">
            <svg className="w-4 h-4 mt-0.5 text-primary flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd" />
            </svg>
            <p className="flex-1">{transcript}</p>
          </div>
        </div>
      )}

      {/* Instructions tooltip (show on hover when not listening) */}
      {!isListening && (
        <div className="absolute top-full mt-2 left-0 right-0 min-w-[250px] px-4 py-3 bg-black/90 border border-white/20 rounded-lg text-xs text-gray-300 z-50 shadow-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
          <p className="font-semibold text-white mb-2">
            {language === 'ar' ? 'أوامر صوتية:' : 'Voice commands:'}
          </p>
          <ul className="space-y-1">
            {language === 'ar' ? (
              <>
                <li>• "ابحث عن [منتج]"</li>
                <li>• "اذهب إلى السلة"</li>
                <li>• "أضف للسلة"</li>
              </>
            ) : (
              <>
                <li>• "search for [product]"</li>
                <li>• "go to cart"</li>
                <li>• "add to cart"</li>
              </>
            )}
          </ul>
        </div>
      )}
    </div>
  );
}

export default VoiceCommandButton;
