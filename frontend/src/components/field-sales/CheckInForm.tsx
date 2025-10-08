'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  MapPinIcon,
  CameraIcon,
  CheckCircleIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';
import { fieldSalesApi, geolocationUtils, cameraUtils } from '@/lib/api/field-sales';
import { offlineStorage } from '@/lib/offline-storage';
import type { CheckInFormData } from '@/types/field-sales';

interface CheckInFormProps {
  repId: string;
  onSuccess?: () => void;
}

export default function CheckInForm({ repId, onSuccess }: CheckInFormProps) {
  const { t, i18n } = useTranslation();
  const videoRef = useRef<HTMLVideoElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  
  const [formData, setFormData] = useState<CheckInFormData>({
    outlet_name: '',
    outlet_id: '',
    latitude: 0,
    longitude: 0,
    address: '',
    photo_base64: '',
    visit_notes: '',
    products_discussed: [],
  });

  const [location, setLocation] = useState<{latitude: number; longitude: number} | null>(null);
  const [photo, setPhoto] = useState<string | null>(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  const isRTL = i18n.language === 'ar';

  useEffect(() => {
    // Get current location
    getCurrentLocation();

    // Monitor online status
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      if (stream) {
        cameraUtils.stopCamera(stream);
      }
    };
  }, []);

  const getCurrentLocation = async () => {
    try {
      const position = await geolocationUtils.getCurrentPosition();
      const coords = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
      };
      setLocation(coords);
      setFormData(prev => ({
        ...prev,
        latitude: coords.latitude,
        longitude: coords.longitude,
      }));
    } catch (err) {
      setError(t('field_sales.location_error', 'Failed to get location. Please enable location services.'));
      console.error(err);
    }
  };

  const startCamera = async () => {
    try {
      if (!videoRef.current) return;
      const mediaStream = await cameraUtils.startCamera(videoRef.current);
      setStream(mediaStream);
      setCameraActive(true);
      setError(null);
    } catch (err) {
      setError(t('field_sales.camera_error', 'Failed to access camera. Please enable camera permissions.'));
      console.error(err);
    }
  };

  const capturePhoto = async () => {
    try {
      if (!videoRef.current) return;
      const base64 = await cameraUtils.capturePhoto(videoRef.current);
      setPhoto(`data:image/jpeg;base64,${base64}`);
      setFormData(prev => ({ ...prev, photo_base64: base64 }));
      
      // Stop camera
      if (stream) {
        cameraUtils.stopCamera(stream);
        setCameraActive(false);
        setStream(null);
      }
    } catch (err) {
      setError(t('field_sales.photo_capture_error', 'Failed to capture photo'));
      console.error(err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!location) {
      setError(t('field_sales.location_required', 'Location is required'));
      return;
    }

    if (!formData.outlet_name) {
      setError(t('field_sales.outlet_name_required', 'Outlet name is required'));
      return;
    }

    setLoading(true);
    setError(null);

    try {
      if (isOnline) {
        // Submit online
        await fieldSalesApi.createCheckIn(repId, formData);
        if (onSuccess) onSuccess();
      } else {
        // Save offline
        await offlineStorage.saveCheckIn(formData);
        alert(t('field_sales.saved_offline', 'Check-in saved offline. Will sync when online.'));
        if (onSuccess) onSuccess();
      }
      
      // Reset form
      setFormData({
        outlet_name: '',
        outlet_id: '',
        latitude: location.latitude,
        longitude: location.longitude,
        address: '',
        photo_base64: '',
        visit_notes: '',
        products_discussed: [],
      });
      setPhoto(null);
    } catch (err) {
      setError(t('field_sales.check_in_error', 'Failed to create check-in'));
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`max-w-2xl mx-auto p-4 ${isRTL ? 'rtl' : 'ltr'}`}>
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          {t('field_sales.outlet_check_in', 'Outlet Check-In')}
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

        {/* Location Status */}
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center">
            <MapPinIcon className="w-6 h-6 text-blue-600 mr-3" />
            <div>
              <div className="font-medium text-blue-900">
                {t('field_sales.location_status', 'Location Status')}
              </div>
              {location ? (
                <div className="text-sm text-blue-700">
                  ✅ {location.latitude.toFixed(6)}, {location.longitude.toFixed(6)}
                </div>
              ) : (
                <div className="text-sm text-blue-700">
                  ⏳ {t('field_sales.getting_location', 'Getting location...')}
                </div>
              )}
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Outlet Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t('field_sales.outlet_name', 'Outlet Name')} *
            </label>
            <input
              type="text"
              value={formData.outlet_name}
              onChange={(e) => setFormData(prev => ({ ...prev, outlet_name: e.target.value }))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          {/* Outlet ID (Optional) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t('field_sales.outlet_id', 'Outlet ID')} ({t('optional', 'Optional')})
            </label>
            <input
              type="text"
              value={formData.outlet_id}
              onChange={(e) => setFormData(prev => ({ ...prev, outlet_id: e.target.value }))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Address */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t('field_sales.address', 'Address')} ({t('optional', 'Optional')})
            </label>
            <input
              type="text"
              value={formData.address}
              onChange={(e) => setFormData(prev => ({ ...prev, address: e.target.value }))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Photo Capture */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t('field_sales.photo', 'Photo')} ({t('optional', 'Optional')})
            </label>
            
            {!cameraActive && !photo && (
              <button
                type="button"
                onClick={startCamera}
                className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center"
              >
                <CameraIcon className="w-6 h-6 mr-2" />
                {t('field_sales.take_photo', 'Take Photo')}
              </button>
            )}

            {cameraActive && (
              <div className="relative">
                <video
                  ref={videoRef}
                  className="w-full rounded-lg"
                  autoPlay
                  playsInline
                  muted
                />
                <div className="mt-4 flex space-x-4">
                  <button
                    type="button"
                    onClick={capturePhoto}
                    className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center justify-center"
                  >
                    <CheckCircleIcon className="w-5 h-5 mr-2" />
                    {t('field_sales.capture', 'Capture')}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      if (stream) cameraUtils.stopCamera(stream);
                      setCameraActive(false);
                      setStream(null);
                    }}
                    className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
                  >
                    <XMarkIcon className="w-5 h-5" />
                  </button>
                </div>
              </div>
            )}

            {photo && (
              <div className="relative">
                <img src={photo} alt="Captured" className="w-full rounded-lg" />
                <button
                  type="button"
                  onClick={() => {
                    setPhoto(null);
                    setFormData(prev => ({ ...prev, photo_base64: '' }));
                  }}
                  className="absolute top-2 right-2 p-2 bg-red-600 text-white rounded-full hover:bg-red-700"
                >
                  <XMarkIcon className="w-5 h-5" />
                </button>
              </div>
            )}
          </div>

          {/* Visit Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t('field_sales.visit_notes', 'Visit Notes')} ({t('optional', 'Optional')})
            </label>
            <textarea
              value={formData.visit_notes}
              onChange={(e) => setFormData(prev => ({ ...prev, visit_notes: e.target.value }))}
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading || !location}
            className="w-full px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium text-lg"
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                </svg>
                {t('field_sales.submitting', 'Submitting...')}
              </span>
            ) : (
              t('field_sales.check_in_now', 'Check In Now')
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
