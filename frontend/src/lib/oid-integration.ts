/**
 * BrainSAIT OID System Integration
 * Connects with the unified platform OID system from /Users/fadil369/02_BRAINSAIT_ECOSYSTEM/Unified_Platform/UNIFICATION_SYSTEM/brainSAIT-oid-system/oid-portal/
 */

interface OIDNode {
  id: string;
  name: string;
  type: 'product' | 'service' | 'solution' | 'category';
  parent_id?: string;
  children?: OIDNode[];
  metadata: {
    description: string;
    price?: number;
    currency?: string;
    features?: string[];
    technologies?: string[];
    target_market?: string;
    complexity_level?: 'basic' | 'advanced' | 'enterprise';
  };
  relationships: {
    dependencies?: string[];
    integrates_with?: string[];
    extends?: string[];
  };
  status: 'active' | 'deprecated' | 'coming_soon';
  created_at: string;
  updated_at: string;
}

interface OIDResponse {
  success: boolean;
  data: OIDNode | OIDNode[];
  message?: string;
  total?: number;
  page?: number;
  limit?: number;
}

interface OIDQueryParams {
  type?: string;
  status?: string;
  search?: string;
  parent_id?: string;
  include_children?: boolean;
  page?: number;
  limit?: number;
}

export class OIDSystemService {
  private baseUrl: string;
  private apiKey: string;

  constructor() {
    // In production, this would connect to the actual OID system API
    this.baseUrl = process.env.NEXT_PUBLIC_OID_API_URL || 'https://oid.brainsait.io/api/v1';
    this.apiKey = process.env.NEXT_PUBLIC_OID_API_KEY || '';
  }

  private async makeRequest(endpoint: string, options?: any): Promise<any> {
    // Check if API key is available
    if (!this.apiKey) {
      throw new Error('OID API key is not configured. Please set NEXT_PUBLIC_OID_API_KEY environment variable.');
    }

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`,
          ...options?.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`OID API Error ${response.status}: ${response.statusText}. Details: ${errorText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('OID System is currently unavailable. Please try again later.');
      }
      throw error;
    }
  }

  /**
   * Get OID tree structure
   */
  async getOIDTree(params?: OIDQueryParams): Promise<OIDNode[]> {
    const queryString = new URLSearchParams(params as any).toString();
    const response: OIDResponse = await this.makeRequest(`/oid/tree?${queryString}`);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch OID tree');
    }

    return Array.isArray(response.data) ? response.data : [response.data as OIDNode];
  }

  /**
   * Get specific OID node by ID
   */
  async getOIDNode(id: string, includeChildren: boolean = false): Promise<OIDNode> {
    const queryString = includeChildren ? '?include_children=true' : '';
    const response: OIDResponse = await this.makeRequest(`/oid/nodes/${id}${queryString}`);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch OID node');
    }

    return response.data as OIDNode;
  }

  /**
   * Search OID nodes
   */
  async searchOIDNodes(query: string, filters?: OIDQueryParams): Promise<OIDNode[]> {
    const params = { search: query, ...filters };
    const queryString = new URLSearchParams(params as any).toString();
    const response: OIDResponse = await this.makeRequest(`/oid/search?${queryString}`);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to search OID nodes');
    }

    return Array.isArray(response.data) ? response.data : [response.data as OIDNode];
  }

  /**
   * Get OID nodes by type
   */
  async getOIDNodesByType(type: string, params?: OIDQueryParams): Promise<OIDNode[]> {
    const queryParams = { type, ...params };
    const queryString = new URLSearchParams(queryParams as any).toString();
    const response: OIDResponse = await this.makeRequest(`/oid/nodes?${queryString}`);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch OID nodes by type');
    }

    return Array.isArray(response.data) ? response.data : [response.data as OIDNode];
  }

  /**
   * Get product recommendations based on OID relationships
   */
  async getRecommendations(nodeId: string): Promise<OIDNode[]> {
    const response: OIDResponse = await this.makeRequest(`/oid/nodes/${nodeId}/recommendations`);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch recommendations');
    }

    return Array.isArray(response.data) ? response.data : [response.data as OIDNode];
  }

  /**
   * Get personalized product recommendations using the new recommendation engine
   */
  async getPersonalizedRecommendations(limit: number = 10): Promise<any[]> {
    try {
      const response = await this.makeRequest(`/recommendations/personalized?limit=${limit}`);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch personalized recommendations');
      }

      return Array.isArray(response.data) ? response.data : [response.data];
    } catch (error) {
      console.error('Error fetching personalized recommendations:', error);
      // Fallback to trending products
      return this.getTrendingRecommendations(limit);
    }
  }

  /**
   * Get trending product recommendations
   */
  async getTrendingRecommendations(limit: number = 10): Promise<any[]> {
    try {
      const response = await this.makeRequest(`/recommendations/trending?limit=${limit}`);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch trending recommendations');
      }

      return Array.isArray(response.data) ? response.data : [response.data];
    } catch (error) {
      console.error('Error fetching trending recommendations:', error);
      return [];
    }
  }

  /**
   * Get seasonal product recommendations
   */
  async getSeasonalRecommendations(season: string, limit: number = 10): Promise<any[]> {
    try {
      const response = await this.makeRequest(`/recommendations/seasonal?season=${season}&limit=${limit}`);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch seasonal recommendations');
      }

      return Array.isArray(response.data) ? response.data : [response.data];
    } catch (error) {
      console.error('Error fetching seasonal recommendations:', error);
      return [];
    }
  }

  /**
   * Get similar products for a specific product
   */
  async getSimilarProducts(productId: string, limit: number = 10): Promise<any[]> {
    try {
      const response = await this.makeRequest(`/recommendations/similar/${productId}?limit=${limit}`);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch similar products');
      }

      return Array.isArray(response.data) ? response.data : [response.data];
    } catch (error) {
      console.error('Error fetching similar products:', error);
      return [];
    }
  }

  /**
   * Track user behavior for improving recommendations
   */
  async trackUserBehavior(action: string, productId: string, metadata?: any): Promise<void> {
    try {
      await this.makeRequest('/recommendations/track-behavior', {
        method: 'POST',
        body: JSON.stringify({
          action,
          product_id: productId,
          metadata
        })
      });
    } catch (error) {
      console.error('Error tracking user behavior:', error);
      // Don't throw error as this is for analytics
    }
  }

  /**
   * Get user recommendation analytics
   */
  async getUserRecommendationAnalytics(): Promise<any> {
    try {
      const response = await this.makeRequest('/recommendations/analytics/user-preferences');
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch user analytics');
      }

      return response.data;
    } catch (error) {
      console.error('Error fetching user recommendation analytics:', error);
      return null;
    }
  }

  /**
   * Map OID nodes to store products
   */
  mapOIDToStoreProducts(oidNodes: OIDNode[]): any[] {
    return oidNodes.map(node => ({
      id: `oid-${node.id}`,
      name: node.name,
      description: node.metadata.description,
      price: node.metadata.price || 0,
      currency: node.metadata.currency || 'USD',
      category: node.type,
      features: node.metadata.features || [],
      technologies: node.metadata.technologies || [],
      target_market: node.metadata.target_market || 'General',
      complexity_level: node.metadata.complexity_level || 'basic',
      status: node.status,
      oid_id: node.id,
      oid_type: node.type,
      relationships: node.relationships,
      created_at: node.created_at,
      updated_at: node.updated_at,
    }));
  }

  /**
   * Get B2B solution packages from OID system
   */
  async getB2BSolutions(): Promise<any[]> {
    try {
      const oidNodes = await this.getOIDNodesByType('solution', {
        status: 'active',
        limit: 50,
      });

      const solutions = this.mapOIDToStoreProducts(oidNodes).map(product => ({
        ...product,
        is_b2b: true,
        pricing_model: 'enterprise',
        includes_source_code: product.complexity_level === 'enterprise',
        support_level: product.complexity_level === 'enterprise' ? 'premium' : 'standard',
      }));

      if (solutions.length === 0) {
        return this.getFallbackB2BSolutions();
      }

      return solutions;
    } catch (error) {
      // Log error but don't expose API details to user
      if (error instanceof Error) {
        if (error.message.includes('API key')) {
          throw error; // Re-throw API key errors as they need user attention
        }
      }
      
      // For other errors, fallback gracefully
      return this.getFallbackB2BSolutions();
    }
  }

  /**
   * Fallback B2B solutions when OID system is unavailable
   */
  private getFallbackB2BSolutions(): any[] {
    return [
      {
        id: 'oid-b2b-complete',
        name: 'Complete B2B Solution',
        description: 'Full-stack B2B platform with all features, source code, and enterprise support',
        price: 19999,
        currency: 'USD',
        category: 'solution',
        features: [
          'Complete source code',
          'Multi-tenant architecture',
          'Payment gateway integration',
          'Analytics dashboard',
          'Enterprise SSO',
          'Mobile app',
          'API documentation',
          '1 year support'
        ],
        technologies: ['React', 'Next.js', 'FastAPI', 'PostgreSQL', 'Redis', 'Cloudflare'],
        target_market: 'Enterprise',
        complexity_level: 'enterprise',
        status: 'active',
        is_b2b: true,
        pricing_model: 'enterprise',
        includes_source_code: true,
        support_level: 'premium',
      },
      {
        id: 'oid-b2b-pro',
        name: 'Professional B2B Solution',
        description: 'Ready-to-deploy B2B platform with core features and standard support',
        price: 9999,
        currency: 'USD',
        category: 'solution',
        features: [
          'Compiled application',
          'Basic customization',
          'Payment integration',
          'Basic analytics',
          'Standard authentication',
          'Documentation',
          '6 months support'
        ],
        technologies: ['React', 'Next.js', 'FastAPI', 'PostgreSQL'],
        target_market: 'SME',
        complexity_level: 'advanced',
        status: 'active',
        is_b2b: true,
        pricing_model: 'professional',
        includes_source_code: false,
        support_level: 'standard',
      },
      {
        id: 'oid-b2b-starter',
        name: 'Starter B2B Solution',
        description: 'Basic B2B platform for small businesses with essential features',
        price: 4999,
        currency: 'USD',
        category: 'solution',
        features: [
          'Basic B2B features',
          'Simple payment integration',
          'User management',
          'Basic reporting',
          'Email support',
          '3 months support'
        ],
        technologies: ['React', 'Next.js', 'SQLite'],
        target_market: 'Small Business',
        complexity_level: 'basic',
        status: 'active',
        is_b2b: true,
        pricing_model: 'starter',
        includes_source_code: false,
        support_level: 'basic',
      }
    ];
  }

  /**
   * Sync OID data with store inventory
   */
  async syncWithStore(): Promise<{success: boolean, count: number, error?: string}> {
    try {
      const b2bSolutions = await this.getB2BSolutions();
      
      // Here you would typically sync with your store's product database
      // For now, we'll just store in localStorage as an example
      if (typeof window !== 'undefined') {
        localStorage.setItem('oid_synced_products', JSON.stringify(b2bSolutions));
        localStorage.setItem('oid_last_sync', new Date().toISOString());
        localStorage.setItem('oid_sync_status', 'success');
      }
      
      return {
        success: true,
        count: b2bSolutions.length
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown sync error';
      
      if (typeof window !== 'undefined') {
        localStorage.setItem('oid_sync_status', 'failed');
        localStorage.setItem('oid_last_error', errorMessage);
      }
      
      return {
        success: false,
        count: 0,
        error: errorMessage
      };
    }
  }

  /**
   * Get synchronized products from local storage
   */
  getSyncedProducts(): any[] {
    if (typeof window === 'undefined') return [];
    
    try {
      const stored = localStorage.getItem('oid_synced_products');
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      // If stored data is corrupted, return empty array and clear storage
      localStorage.removeItem('oid_synced_products');
      localStorage.removeItem('oid_last_sync');
      return [];
    }
  }

  /**
   * Check if sync is needed (older than 1 hour)
   */
  isSyncNeeded(): boolean {
    if (typeof window === 'undefined') return true;
    
    const lastSync = localStorage.getItem('oid_last_sync');
    const syncStatus = localStorage.getItem('oid_sync_status');
    
    // Force sync if previous sync failed
    if (syncStatus === 'failed') return true;
    
    // Force sync if no previous sync
    if (!lastSync) return true;
    
    // Sync every hour for successful syncs
    const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
    return new Date(lastSync) < oneHourAgo;
  }

  /**
   * Auto-sync if needed
   */
  async autoSync(): Promise<{synced: boolean, result?: any}> {
    if (this.isSyncNeeded()) {
      const result = await this.syncWithStore();
      return { synced: true, result };
    }
    return { synced: false };
  }
}

// Export singleton instance
export const oidSystemService = new OIDSystemService();

// Helper functions
export const OIDUtils = {
  /**
   * Format OID node for display
   */
  formatNodeForDisplay: (node: OIDNode) => ({
    title: node.name,
    subtitle: node.metadata.description,
    price: node.metadata.price ? `$${node.metadata.price.toLocaleString()}` : 'Contact for pricing',
    badge: node.type.charAt(0).toUpperCase() + node.type.slice(1),
    status: node.status,
  }),

  /**
   * Build OID hierarchy path
   */
  buildHierarchyPath: (node: OIDNode, allNodes: OIDNode[]): string[] => {
    const path: string[] = [node.name];
    let currentNode = node;
    
    while (currentNode.parent_id) {
      const parent = allNodes.find(n => n.id === currentNode.parent_id);
      if (parent) {
        path.unshift(parent.name);
        currentNode = parent;
      } else {
        break;
      }
    }
    
    return path;
  },

  /**
   * Filter nodes by criteria
   */
  filterNodes: (nodes: OIDNode[], criteria: Partial<OIDNode>) => {
    return nodes.filter(node => {
      return Object.entries(criteria).every(([key, value]) => {
        if (value === undefined) return true;
        return (node as any)[key] === value;
      });
    });
  },
};