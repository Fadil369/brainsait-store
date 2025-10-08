/**
 * Offline Storage using IndexedDB for field sales data
 */

import type {
  CheckInFormData,
  VoiceOrderFormData,
  CreditRequestFormData,
  OfflineSyncData,
} from '@/types/field-sales';

const DB_NAME = 'brainsait_field_sales';
const DB_VERSION = 1;

const STORES = {
  CHECK_INS: 'check_ins',
  VOICE_ORDERS: 'voice_orders',
  CREDIT_REQUESTS: 'credit_requests',
  SYNC_STATUS: 'sync_status',
};

class OfflineStorage {
  private db: IDBDatabase | null = null;

  async init(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        // Create object stores if they don't exist
        if (!db.objectStoreNames.contains(STORES.CHECK_INS)) {
          const checkInStore = db.createObjectStore(STORES.CHECK_INS, {
            keyPath: 'id',
            autoIncrement: true,
          });
          checkInStore.createIndex('timestamp', 'timestamp', { unique: false });
          checkInStore.createIndex('synced', 'synced', { unique: false });
        }

        if (!db.objectStoreNames.contains(STORES.VOICE_ORDERS)) {
          const voiceStore = db.createObjectStore(STORES.VOICE_ORDERS, {
            keyPath: 'id',
            autoIncrement: true,
          });
          voiceStore.createIndex('timestamp', 'timestamp', { unique: false });
          voiceStore.createIndex('synced', 'synced', { unique: false });
        }

        if (!db.objectStoreNames.contains(STORES.CREDIT_REQUESTS)) {
          const creditStore = db.createObjectStore(STORES.CREDIT_REQUESTS, {
            keyPath: 'id',
            autoIncrement: true,
          });
          creditStore.createIndex('timestamp', 'timestamp', { unique: false });
          creditStore.createIndex('synced', 'synced', { unique: false });
        }

        if (!db.objectStoreNames.contains(STORES.SYNC_STATUS)) {
          db.createObjectStore(STORES.SYNC_STATUS, { keyPath: 'key' });
        }
      };
    });
  }

  private async ensureDb(): Promise<IDBDatabase> {
    if (!this.db) {
      await this.init();
    }
    if (!this.db) {
      throw new Error('Database not initialized');
    }
    return this.db;
  }

  // Check-ins
  async saveCheckIn(data: CheckInFormData): Promise<number> {
    const db = await this.ensureDb();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction([STORES.CHECK_INS], 'readwrite');
      const store = transaction.objectStore(STORES.CHECK_INS);
      
      const item = {
        ...data,
        timestamp: new Date().toISOString(),
        synced: false,
      };

      const request = store.add(item);
      request.onsuccess = () => resolve(request.result as number);
      request.onerror = () => reject(request.error);
    });
  }

  async getUnsyncedCheckIns(): Promise<CheckInFormData[]> {
    const db = await this.ensureDb();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction([STORES.CHECK_INS], 'readonly');
      const store = transaction.objectStore(STORES.CHECK_INS);
      const index = store.index('synced');
      const request = index.getAll(false);

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async markCheckInsSynced(ids: number[]): Promise<void> {
    const db = await this.ensureDb();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction([STORES.CHECK_INS], 'readwrite');
      const store = transaction.objectStore(STORES.CHECK_INS);

      let completed = 0;
      ids.forEach((id) => {
        const request = store.get(id);
        request.onsuccess = () => {
          const item = request.result;
          if (item) {
            item.synced = true;
            store.put(item);
          }
          completed++;
          if (completed === ids.length) {
            resolve();
          }
        };
        request.onerror = () => reject(request.error);
      });
    });
  }

  // Voice Orders
  async saveVoiceOrder(data: VoiceOrderFormData): Promise<number> {
    const db = await this.ensureDb();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction([STORES.VOICE_ORDERS], 'readwrite');
      const store = transaction.objectStore(STORES.VOICE_ORDERS);
      
      const item = {
        ...data,
        timestamp: new Date().toISOString(),
        synced: false,
      };

      const request = store.add(item);
      request.onsuccess = () => resolve(request.result as number);
      request.onerror = () => reject(request.error);
    });
  }

  async getUnsyncedVoiceOrders(): Promise<VoiceOrderFormData[]> {
    const db = await this.ensureDb();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction([STORES.VOICE_ORDERS], 'readonly');
      const store = transaction.objectStore(STORES.VOICE_ORDERS);
      const index = store.index('synced');
      const request = index.getAll(false);

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  // Credit Requests
  async saveCreditRequest(data: CreditRequestFormData): Promise<number> {
    const db = await this.ensureDb();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction([STORES.CREDIT_REQUESTS], 'readwrite');
      const store = transaction.objectStore(STORES.CREDIT_REQUESTS);
      
      const item = {
        ...data,
        timestamp: new Date().toISOString(),
        synced: false,
      };

      const request = store.add(item);
      request.onsuccess = () => resolve(request.result as number);
      request.onerror = () => reject(request.error);
    });
  }

  async getUnsyncedCreditRequests(): Promise<CreditRequestFormData[]> {
    const db = await this.ensureDb();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction([STORES.CREDIT_REQUESTS], 'readonly');
      const store = transaction.objectStore(STORES.CREDIT_REQUESTS);
      const index = store.index('synced');
      const request = index.getAll(false);

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  // Sync Status
  async setLastSyncTime(time: string): Promise<void> {
    const db = await this.ensureDb();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction([STORES.SYNC_STATUS], 'readwrite');
      const store = transaction.objectStore(STORES.SYNC_STATUS);
      const request = store.put({ key: 'last_sync', value: time });

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async getLastSyncTime(): Promise<string | null> {
    const db = await this.ensureDb();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction([STORES.SYNC_STATUS], 'readonly');
      const store = transaction.objectStore(STORES.SYNC_STATUS);
      const request = store.get('last_sync');

      request.onsuccess = () => {
        const result = request.result;
        resolve(result ? result.value : null);
      };
      request.onerror = () => reject(request.error);
    });
  }

  // Get all unsynced data
  async getAllUnsyncedData(): Promise<OfflineSyncData> {
    const [checkIns, voiceOrders, creditRequests, lastSyncAt] = await Promise.all([
      this.getUnsyncedCheckIns(),
      this.getUnsyncedVoiceOrders(),
      this.getUnsyncedCreditRequests(),
      this.getLastSyncTime(),
    ]);

    return {
      check_ins: checkIns,
      voice_orders: voiceOrders,
      credit_requests: creditRequests,
      last_sync_at: lastSyncAt || undefined,
    };
  }

  // Clear synced data (optional cleanup)
  async clearSyncedData(): Promise<void> {
    const db = await this.ensureDb();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(
        [STORES.CHECK_INS, STORES.VOICE_ORDERS, STORES.CREDIT_REQUESTS],
        'readwrite'
      );

      const stores = [
        transaction.objectStore(STORES.CHECK_INS),
        transaction.objectStore(STORES.VOICE_ORDERS),
        transaction.objectStore(STORES.CREDIT_REQUESTS),
      ];

      let completed = 0;
      const checkComplete = () => {
        completed++;
        if (completed === stores.length) {
          resolve();
        }
      };

      stores.forEach((store) => {
        const index = store.index('synced');
        const request = index.openCursor(true);
        
        request.onsuccess = () => {
          const cursor = request.result;
          if (cursor) {
            cursor.delete();
            cursor.continue();
          } else {
            checkComplete();
          }
        };
        request.onerror = () => reject(request.error);
      });
    });
  }

  // Get statistics
  async getStats(): Promise<{
    unsynced_check_ins: number;
    unsynced_voice_orders: number;
    unsynced_credit_requests: number;
    last_sync: string | null;
  }> {
    const [checkIns, voiceOrders, creditRequests, lastSync] = await Promise.all([
      this.getUnsyncedCheckIns(),
      this.getUnsyncedVoiceOrders(),
      this.getUnsyncedCreditRequests(),
      this.getLastSyncTime(),
    ]);

    return {
      unsynced_check_ins: checkIns.length,
      unsynced_voice_orders: voiceOrders.length,
      unsynced_credit_requests: creditRequests.length,
      last_sync: lastSync,
    };
  }
}

// Singleton instance
export const offlineStorage = new OfflineStorage();

// Initialize on module load (in browser only)
if (typeof window !== 'undefined') {
  offlineStorage.init().catch(console.error);
}
