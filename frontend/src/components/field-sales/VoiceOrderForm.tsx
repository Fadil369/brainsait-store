'use client';

import React, { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { MicrophoneIcon, StopIcon } from '@heroicons/react/24/outline';
import { fieldSalesApi, voiceUtils } from '@/lib/api/field-sales';
import { offlineStorage } from '@/lib/offline-storage';

interface VoiceOrderFormProps {
  repId: string;
  onSuccess?: () => void;
}

export default function VoiceOrderForm({ repId, onSuccess }: VoiceOrderFormProps) {
  const { t, i18n } = useTranslation();
  const [recording, setRecording] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [language, setLanguage] = useState<'ar' | 'en'>(i18n.language === 'ar' ? 'ar' : 'en');
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [error, setError] = useState<string | null>(null);
  
  const recorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const startTimeRef = useRef<number>(0);

  const isRTL = i18n.language === 'ar';

  const startRecording = async () => {
    try {
      setError(null);
      const { recorder, stream } = await voiceUtils.startRecording();
      
      recorderRef.current = recorder;
      streamRef.current = stream;
      startTimeRef.current = Date.now();
      
      recorder.start();
      setRecording(true);
    } catch (err) {
      setError(t('field_sales.microphone_error', 'Failed to access microphone. Please enable microphone permissions.'));
      console.error(err);
    }
  };

  const stopRecording = async () => {
    if (!recorderRef.current || !streamRef.current) return;

    setRecording(false);
    setProcessing(true);

    try {
      const duration = Math.floor((Date.now() - startTimeRef.current) / 1000);
      const audioBlob = await voiceUtils.stopRecording(recorderRef.current, streamRef.current);
      const base64 = await voiceUtils.blobToBase64(audioBlob);

      const voiceData = {
        audio_base64: base64,
        language,
        audio_duration_seconds: duration,
      };

      if (isOnline) {
        // Submit online
        await fieldSalesApi.createVoiceOrder(repId, voiceData);
        alert(t('field_sales.voice_order_submitted', 'Voice order submitted for processing'));
        if (onSuccess) onSuccess();
      } else {
        // Save offline
        await offlineStorage.saveVoiceOrder(voiceData);
        alert(t('field_sales.voice_saved_offline', 'Voice order saved offline. Will sync when online.'));
        if (onSuccess) onSuccess();
      }
    } catch (err) {
      setError(t('field_sales.voice_order_error', 'Failed to process voice order'));
      console.error(err);
    } finally {
      setProcessing(false);
      recorderRef.current = null;
      streamRef.current = null;
    }
  };

  return (
    <div className={`max-w-2xl mx-auto p-4 ${isRTL ? 'rtl' : 'ltr'}`}>
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          {t('field_sales.voice_to_order', 'Voice to Order')}
        </h2>

        {!isOnline && (
          <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-yellow-800 text-sm">
              📱 {t('field_sales.offline_mode', 'Offline Mode - Data will be synced when online')}
            </p>
          </div>
        )}

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        {/* Language Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('field_sales.select_language', 'Select Language')}
          </label>
          <div className="flex space-x-4">
            <button
              onClick={() => setLanguage('ar')}
              disabled={recording || processing}
              className={`flex-1 px-4 py-3 rounded-lg font-medium ${
                language === 'ar'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              } disabled:opacity-50`}
            >
              🇸🇦 العربية
            </button>
            <button
              onClick={() => setLanguage('en')}
              disabled={recording || processing}
              className={`flex-1 px-4 py-3 rounded-lg font-medium ${
                language === 'en'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              } disabled:opacity-50`}
            >
              🇬🇧 English
            </button>
          </div>
        </div>

        {/* Instructions */}
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-blue-900 text-sm">
            {language === 'ar' 
              ? 'اضغط على الزر وابدأ في قول طلبك. تحدث بوضوح واذكر اسم المنتج والكمية.'
              : 'Press the button and start speaking your order. Speak clearly and mention product name and quantity.'}
          </p>
        </div>

        {/* Recording Controls */}
        <div className="flex flex-col items-center space-y-6">
          {!recording && !processing && (
            <button
              onClick={startRecording}
              className="w-32 h-32 bg-gradient-to-br from-purple-600 to-purple-400 rounded-full flex items-center justify-center hover:from-purple-700 hover:to-purple-500 shadow-lg transition-all transform hover:scale-105"
            >
              <MicrophoneIcon className="w-16 h-16 text-white" />
            </button>
          )}

          {recording && (
            <>
              <div className="w-32 h-32 bg-red-600 rounded-full flex items-center justify-center animate-pulse shadow-lg">
                <MicrophoneIcon className="w-16 h-16 text-white" />
              </div>
              <p className="text-lg font-medium text-gray-900">
                {t('field_sales.recording', 'Recording...')}
              </p>
              <button
                onClick={stopRecording}
                className="px-8 py-3 bg-gray-800 text-white rounded-lg hover:bg-gray-900 flex items-center font-medium"
              >
                <StopIcon className="w-6 h-6 mr-2" />
                {t('field_sales.stop_recording', 'Stop Recording')}
              </button>
            </>
          )}

          {processing && (
            <div className="flex flex-col items-center">
              <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-purple-600"></div>
              <p className="mt-4 text-lg font-medium text-gray-900">
                {t('field_sales.processing', 'Processing...')}
              </p>
            </div>
          )}
        </div>

        {/* Example Orders */}
        <div className="mt-8 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-medium text-gray-900 mb-2">
            {t('field_sales.example_orders', 'Example Orders')}:
          </h3>
          <ul className="text-sm text-gray-700 space-y-1">
            {language === 'ar' ? (
              <>
                <li>• "عشرة علب من المنتج A و خمسة من المنتج B"</li>
                <li>• "احتاج ثلاثين قطعة من المنتج رقم 123"</li>
              </>
            ) : (
              <>
                <li>• "Ten boxes of Product A and five of Product B"</li>
                <li>• "I need thirty pieces of product number 123"</li>
              </>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
}
