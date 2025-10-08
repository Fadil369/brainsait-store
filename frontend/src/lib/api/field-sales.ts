/**
 * Field Sales API Client
 */

import axios from 'axios';
import type {
  SalesRep,
  SalesRepDashboard,
  OutletCheckIn,
  VoiceOrder,
  CreditRequest,
  Achievement,
  LeaderboardEntry,
  CheckInFormData,
  VoiceOrderFormData,
  CreditRequestFormData,
  OfflineSyncData,
  ARProduct,
} from '@/types/field-sales';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const fieldSalesApi = {
  // Sales Rep
  getSalesRep: async (repId: string): Promise<SalesRep> => {
    const response = await axios.get(`${API_BASE_URL}/api/v1/field-sales/reps/${repId}`);
    return response.data;
  },

  getSalesRepByUser: async (userId: string): Promise<SalesRep> => {
    const response = await axios.get(`${API_BASE_URL}/api/v1/field-sales/reps/user/${userId}`);
    return response.data;
  },

  getDashboard: async (repId: string): Promise<SalesRepDashboard> => {
    const response = await axios.get(`${API_BASE_URL}/api/v1/field-sales/dashboard/${repId}`);
    return response.data;
  },

  // Check-ins
  createCheckIn: async (repId: string, data: CheckInFormData): Promise<OutletCheckIn> => {
    const response = await axios.post(
      `${API_BASE_URL}/api/v1/field-sales/check-ins?rep_id=${repId}`,
      data
    );
    return response.data;
  },

  updateCheckIn: async (checkInId: string, data: Partial<OutletCheckIn>): Promise<OutletCheckIn> => {
    const response = await axios.patch(
      `${API_BASE_URL}/api/v1/field-sales/check-ins/${checkInId}`,
      data
    );
    return response.data;
  },

  getCheckIns: async (
    repId: string,
    params?: { start_date?: string; end_date?: string; limit?: number }
  ): Promise<OutletCheckIn[]> => {
    const response = await axios.get(`${API_BASE_URL}/api/v1/field-sales/check-ins`, {
      params: { rep_id: repId, ...params },
    });
    return response.data;
  },

  // Voice Orders
  createVoiceOrder: async (repId: string, data: VoiceOrderFormData): Promise<VoiceOrder> => {
    const response = await axios.post(
      `${API_BASE_URL}/api/v1/field-sales/voice-orders?rep_id=${repId}`,
      data
    );
    return response.data;
  },

  getVoiceOrder: async (orderId: string): Promise<VoiceOrder> => {
    const response = await axios.get(`${API_BASE_URL}/api/v1/field-sales/voice-orders/${orderId}`);
    return response.data;
  },

  // Credit Requests
  createCreditRequest: async (repId: string, data: CreditRequestFormData): Promise<CreditRequest> => {
    const response = await axios.post(
      `${API_BASE_URL}/api/v1/field-sales/credit-requests?rep_id=${repId}`,
      data
    );
    return response.data;
  },

  getCreditRequests: async (
    repId: string,
    params?: { status?: string; limit?: number }
  ): Promise<CreditRequest[]> => {
    const response = await axios.get(`${API_BASE_URL}/api/v1/field-sales/credit-requests`, {
      params: { rep_id: repId, ...params },
    });
    return response.data;
  },

  // Gamification
  getLeaderboard: async (period: 'daily' | 'weekly' | 'monthly' = 'monthly'): Promise<{
    period_type: string;
    period_start: string;
    period_end: string;
    entries: LeaderboardEntry[];
    my_position?: LeaderboardEntry;
  }> => {
    const response = await axios.get(`${API_BASE_URL}/api/v1/field-sales/leaderboard`, {
      params: { period },
    });
    return response.data;
  },

  getAchievements: async (repId?: string): Promise<Achievement[]> => {
    const response = await axios.get(`${API_BASE_URL}/api/v1/field-sales/achievements`, {
      params: repId ? { rep_id: repId } : {},
    });
    return response.data;
  },

  // Offline Sync
  syncOfflineData: async (repId: string, data: OfflineSyncData): Promise<{
    synced_check_ins: number;
    synced_voice_orders: number;
    synced_credit_requests: number;
    failed_items: any[];
    sync_completed_at: string;
  }> => {
    const response = await axios.post(
      `${API_BASE_URL}/api/v1/field-sales/sync?rep_id=${repId}`,
      data
    );
    return response.data;
  },

  // AR Catalog
  getARProducts: async (params?: { category?: string; limit?: number }): Promise<{
    products: ARProduct[];
    total: number;
  }> => {
    const response = await axios.get(`${API_BASE_URL}/api/v1/field-sales/ar-catalog/products`, {
      params,
    });
    return response.data;
  },
};

// Geolocation utilities
export const geolocationUtils = {
  getCurrentPosition: (): Promise<GeolocationPosition> => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation is not supported'));
        return;
      }

      navigator.geolocation.getCurrentPosition(resolve, reject, {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      });
    });
  },

  calculateDistance: (lat1: number, lon1: number, lat2: number, lon2: number): number => {
    // Haversine formula for distance calculation in meters
    const R = 6371e3; // Earth's radius in meters
    const φ1 = (lat1 * Math.PI) / 180;
    const φ2 = (lat2 * Math.PI) / 180;
    const Δφ = ((lat2 - lat1) * Math.PI) / 180;
    const Δλ = ((lon2 - lon1) * Math.PI) / 180;

    const a =
      Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
      Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return R * c; // Distance in meters
  },
};

// Camera utilities
export const cameraUtils = {
  capturePhoto: (videoElement: HTMLVideoElement): Promise<string> => {
    return new Promise((resolve, reject) => {
      try {
        const canvas = document.createElement('canvas');
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;
        const ctx = canvas.getContext('2d');
        
        if (!ctx) {
          reject(new Error('Could not get canvas context'));
          return;
        }

        ctx.drawImage(videoElement, 0, 0);
        const base64 = canvas.toDataURL('image/jpeg', 0.8);
        resolve(base64.split(',')[1]); // Return only base64 data
      } catch (error) {
        reject(error);
      }
    });
  },

  startCamera: async (videoElement: HTMLVideoElement): Promise<MediaStream> => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' }, // Use rear camera on mobile
        audio: false,
      });
      videoElement.srcObject = stream;
      await videoElement.play();
      return stream;
    } catch (error) {
      throw new Error(`Camera access denied: ${error}`);
    }
  },

  stopCamera: (stream: MediaStream): void => {
    stream.getTracks().forEach(track => track.stop());
  },
};

// Voice recording utilities
export const voiceUtils = {
  startRecording: async (): Promise<{
    recorder: MediaRecorder;
    stream: MediaStream;
  }> => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      return { recorder, stream };
    } catch (error) {
      throw new Error(`Microphone access denied: ${error}`);
    }
  },

  stopRecording: (recorder: MediaRecorder, stream: MediaStream): Promise<Blob> => {
    return new Promise((resolve, reject) => {
      const chunks: Blob[] = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.push(e.data);
        }
      };

      recorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        stream.getTracks().forEach(track => track.stop());
        resolve(blob);
      };

      recorder.onerror = (error) => {
        stream.getTracks().forEach(track => track.stop());
        reject(error);
      };

      recorder.stop();
    });
  },

  blobToBase64: (blob: Blob): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = reader.result as string;
        resolve(base64.split(',')[1]); // Return only base64 data
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  },
};
