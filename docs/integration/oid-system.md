# OID System Integration Specification

## Overview

This document specifies the integration between BrainsAIT Store and the unified OID (Object Identifier) system portal, enabling product synchronization, B2B solution mapping, and healthcare-specific node structures.

**Integration Type**: Unified Platform Integration  
**OID Portal Path**: `/Users/fadil369/02_BRAINSAIT_ECOSYSTEM/Unified_Platform/UNIFICATION_SYSTEM/brainSAIT-oid-system/oid-portal/`  
**Status**: 🔄 In Progress  
**Last Updated**: October 2024

---

## 🎯 OID System Purpose

The OID system provides:
- Hierarchical organization of products and services
- Unique identification for all platform resources
- Cross-platform product synchronization
- B2B solution catalog management
- Healthcare-specific node structures

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    BrainsAIT Store                          │
│                  (Product Catalog)                          │
├─────────────────────────────────────────────────────────────┤
│  • Products                                                 │
│  • Pricing Tiers                                           │
│  • Features                                                │
│  • Metadata                                                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Synchronization
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    OID System Portal                        │
│              (Unified Platform Registry)                    │
├─────────────────────────────────────────────────────────────┤
│  OID Hierarchy:                                            │
│  ├── 1.3.6.1.4.1.XXXX.1              (BrainsAIT)          │
│  │   ├── .1                          (Products)           │
│  │   │   ├── .1                      (Websites)           │
│  │   │   ├── .2                      (Applications)       │
│  │   │   ├── .3                      (APIs)               │
│  │   │   └── .4                      (Healthcare)         │
│  │   ├── .2                          (Services)           │
│  │   └── .3                          (Integrations)       │
│  └── 1.3.6.1.4.1.XXXX.2              (GIVC)              │
│      ├── .1                          (Healthcare Platform) │
│      ├── .2                          (NPHIES Integration)  │
│      └── .3                          (Medical AI)         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔗 Integration Points

### 1. Product Synchronization

**Purpose**: Sync product catalog with OID registry

**Data Flow**:
```typescript
// Frontend: frontend/src/lib/oid-integration.ts
export class OIDSystemService {
  private baseUrl = process.env.NEXT_PUBLIC_OID_API_URL || 
                    'https://oid.brainsait.io/api/v1';
  
  async queryOID(params: OIDQueryParams): Promise<OIDResponse> {
    // Query OID system for products
    const response = await fetch(`${this.baseUrl}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`
      },
      body: JSON.stringify(params)
    });
    
    return await response.json();
  }
  
  async getB2BSolutions(): Promise<OIDNode[]> {
    // Get B2B solutions from OID system
    return await this.queryOID({
      category: 'solution',
      is_b2b: true,
      status: 'active'
    });
  }
}
```

**Sync Schedule**:
- Real-time: On product create/update/delete
- Batch: Every 6 hours for full catalog sync
- Fallback: Manual sync via admin interface

### 2. B2B Solution Mapping

**Purpose**: Map BrainsAIT products to OID B2B solution nodes

**Product Categories**:
```typescript
// Product to OID Node Mapping
const oidMapping = {
  // Healthcare Solutions
  'givc-healthcare': {
    oid: '1.3.6.1.4.1.XXXX.2.1',
    category: 'healthcare',
    is_b2b: true,
    compliance: ['HIPAA', 'NPHIES', 'ZATCA']
  },
  
  // API Solutions
  'givc-healthcare-api': {
    oid: '1.3.6.1.4.1.XXXX.1.3.1',
    category: 'api',
    is_b2b: true,
    target_market: 'Healthcare Providers'
  },
  
  // Web Applications
  'givc-website': {
    oid: '1.3.6.1.4.1.XXXX.1.1.5',
    category: 'website',
    is_b2b: true,
    features: ['multi-tenant', 'bilingual', 'healthcare']
  }
};
```

**B2B Solution Tiers**:
```typescript
interface B2BSolutionTier {
  tier: 'starter' | 'professional' | 'enterprise';
  pricing_model: 'one-time' | 'subscription' | 'custom';
  features: string[];
  support_level: 'basic' | 'standard' | 'premium';
  includes_source_code: boolean;
  customization_hours: number;
  sla: {
    uptime: string;
    response_time: string;
    support_hours: string;
  };
}

// Example: GIVC Healthcare Enterprise Tier
{
  tier: 'enterprise',
  pricing_model: 'custom',
  features: [
    'Complete B2B platform',
    'AI-powered processing',
    'NPHIES integration',
    'Multi-tenant architecture',
    'Custom branding',
    'Dedicated support',
    'SLA guarantee'
  ],
  support_level: 'premium',
  includes_source_code: true,
  customization_hours: 100,
  sla: {
    uptime: '99.9%',
    response_time: '< 1 hour',
    support_hours: '24/7'
  }
}
```

### 3. Healthcare-Specific Nodes

**Purpose**: Organize healthcare products in OID hierarchy

**Node Structure**:
```
1.3.6.1.4.1.XXXX.2                  (GIVC Healthcare Root)
├── .1                              (Healthcare Platform)
│   ├── .1                          (Web Application)
│   ├── .2                          (Mobile App)
│   └── .3                          (Admin Portal)
├── .2                              (Healthcare APIs)
│   ├── .1                          (Medical Data Processing)
│   ├── .2                          (NPHIES Integration)
│   ├── .3                          (Provider Management)
│   └── .4                          (Claims Processing)
├── .3                              (Medical AI)
│   ├── .1                          (Diagnosis Support)
│   ├── .2                          (Drug Interaction)
│   └── .3                          (Medical Coding)
└── .4                              (Compliance & Reporting)
    ├── .1                          (HIPAA Compliance)
    ├── .2                          (ZATCA Integration)
    └── .3                          (Audit Logging)
```

**Node Metadata**:
```json
{
  "oid": "1.3.6.1.4.1.XXXX.2.1",
  "name": "GIVC Healthcare Platform",
  "type": "product",
  "category": "healthcare",
  "status": "active",
  "metadata": {
    "description": "Complete B2B healthcare platform",
    "version": "1.0.0",
    "license": "Enterprise",
    "compliance": ["HIPAA", "NPHIES", "ZATCA"],
    "target_market": "Healthcare Providers (Saudi Arabia)",
    "deployment": "Cloud (Cloudflare Workers)",
    "database": "PostgreSQL",
    "features": [
      "Multi-tenant architecture",
      "Arabic/English bilingual",
      "Real-time analytics",
      "Payment processing",
      "NPHIES integration"
    ],
    "pricing": {
      "currency": "SAR",
      "tiers": [
        {"name": "Starter", "price": 9999},
        {"name": "Professional", "price": 14999},
        {"name": "Enterprise", "price": 24999}
      ]
    },
    "support": {
      "documentation": "https://docs.brainsait.io/givc",
      "api_docs": "https://givc-healthcare-api.fadil.workers.dev/docs",
      "support_email": "support@brainsait.io",
      "support_level": "24/7 Enterprise"
    }
  },
  "relationships": {
    "depends_on": [
      "1.3.6.1.4.1.XXXX.2.2.2",  // NPHIES Integration
      "1.3.6.1.4.1.XXXX.1.3.1"   // Healthcare API
    ],
    "integrates_with": [
      "1.3.6.1.4.1.XXXX.1.2.1",  // BrainsAIT Gateway
      "1.3.6.1.4.1.XXXX.1.2.2"   // Payment Processing
    ]
  }
}
```

### 4. Product Lifecycle Management

**Status Workflow**:
```
draft → review → active → deprecated → archived
```

**Status Transitions**:
- **draft**: New product, not yet published
- **review**: Under review by product team
- **active**: Live and available for purchase
- **deprecated**: Still available but no longer recommended
- **archived**: Historical record, not available

**OID Node Lifecycle**:
```typescript
interface OIDNodeLifecycle {
  created_at: string;
  updated_at: string;
  published_at?: string;
  deprecated_at?: string;
  archived_at?: string;
  status_history: Array<{
    status: string;
    timestamp: string;
    user: string;
    reason: string;
  }>;
}
```

---

## 🔄 Synchronization Protocol

### Real-Time Sync

**Webhook Events**:
```typescript
// BrainsAIT Store → OID System
interface WebhookEvent {
  event_type: 'product.created' | 'product.updated' | 'product.deleted';
  timestamp: string;
  data: {
    product_id: string;
    oid: string;
    changes: object;
  };
}

// Example: Product Updated
{
  "event_type": "product.updated",
  "timestamp": "2024-10-08T10:30:00Z",
  "data": {
    "product_id": "5",
    "oid": "1.3.6.1.4.1.XXXX.2.1",
    "changes": {
      "price": 14999,
      "features": ["New feature added"]
    }
  }
}
```

**OID System Response**:
```json
{
  "status": "success",
  "oid": "1.3.6.1.4.1.XXXX.2.1",
  "version": "1.0.1",
  "sync_timestamp": "2024-10-08T10:30:05Z"
}
```

### Batch Sync

**Schedule**: Every 6 hours

**Process**:
1. Query all active products from BrainsAIT Store
2. Compare with OID system registry
3. Identify differences (new, updated, deleted)
4. Sync changes to OID system
5. Update sync status in database
6. Generate sync report

**Implementation**:
```python
# Backend: Batch sync service
async def batch_sync_with_oid():
    """Sync product catalog with OID system"""
    
    # Get all active products
    products = await db.get_all_products(status='active')
    
    # Get OID nodes
    oid_nodes = await oid_api.get_all_nodes(
        category='product',
        owner='brainsait'
    )
    
    # Compare and sync
    sync_results = {
        'created': [],
        'updated': [],
        'deleted': [],
        'errors': []
    }
    
    for product in products:
        try:
            oid_node = find_oid_node(product.id, oid_nodes)
            
            if not oid_node:
                # Create new OID node
                result = await oid_api.create_node(
                    map_product_to_oid(product)
                )
                sync_results['created'].append(result)
            
            elif product_has_changes(product, oid_node):
                # Update existing OID node
                result = await oid_api.update_node(
                    oid_node.oid,
                    map_product_to_oid(product)
                )
                sync_results['updated'].append(result)
        
        except Exception as e:
            sync_results['errors'].append({
                'product_id': product.id,
                'error': str(e)
            })
    
    # Log sync results
    await analytics.track_sync_event('oid_batch_sync', sync_results)
    
    return sync_results
```

### Fallback Mechanism

**OID System Unavailable**:
```typescript
// Frontend fallback
export class OIDSystemService {
  private getFallbackB2BSolutions(): any[] {
    // Return cached B2B solutions
    return [
      {
        id: 'oid-b2b-enterprise',
        name: 'Enterprise B2B Solution',
        description: 'Complete B2B platform',
        price: 24999,
        category: 'solution',
        status: 'active',
        is_b2b: true
      },
      // More fallback solutions...
    ];
  }
  
  async getB2BSolutions(): Promise<OIDNode[]> {
    try {
      // Try to fetch from OID system
      return await this.queryOID({
        category: 'solution',
        is_b2b: true
      });
    } catch (error) {
      console.warn('OID system unavailable, using fallback');
      // Return cached/fallback data
      return this.getFallbackB2BSolutions();
    }
  }
}
```

---

## 🔐 Security

### Authentication

**API Key Authentication**:
```typescript
const oidApiKey = process.env.NEXT_PUBLIC_OID_API_KEY;

const response = await fetch(oidApiUrl, {
  headers: {
    'Authorization': `Bearer ${oidApiKey}`,
    'X-API-Version': '1.0'
  }
});
```

**JWT Token for User Context**:
```typescript
const token = await getAuthToken();

const response = await fetch(oidApiUrl, {
  headers: {
    'Authorization': `Bearer ${token}`,
    'X-Tenant-ID': tenantId
  }
});
```

### Data Validation

**OID Format Validation**:
```typescript
function validateOID(oid: string): boolean {
  // OID format: 1.3.6.1.4.1.XXXX.Y.Z...
  const oidPattern = /^[0-9]+(\.[0-9]+)+$/;
  return oidPattern.test(oid);
}
```

**Node Data Validation**:
```typescript
const oidNodeSchema = z.object({
  oid: z.string().regex(/^[0-9]+(\.[0-9]+)+$/),
  name: z.string().min(1).max(255),
  type: z.enum(['product', 'service', 'integration']),
  status: z.enum(['draft', 'review', 'active', 'deprecated', 'archived']),
  metadata: z.object({
    description: z.string(),
    price: z.number().optional(),
    category: z.string(),
    features: z.array(z.string())
  })
});
```

---

## 📊 Monitoring

### Sync Metrics

**Key Metrics**:
- Sync success rate (target: >99%)
- Average sync duration (target: <5 seconds)
- Failed syncs (target: <1%)
- OID API response time (target: <200ms)

**Dashboard**:
```
OID Integration Dashboard:
├── Sync Status
│   ├── Last sync: 2024-10-08 10:00:00
│   ├── Success rate: 99.5%
│   └── Next sync: 2024-10-08 16:00:00
├── Product Synchronization
│   ├── Total products: 50
│   ├── Synced: 49
│   └── Pending: 1
└── API Health
    ├── OID API status: Operational
    ├── Response time: 150ms (avg)
    └── Error rate: 0.1%
```

### Alerting

**Critical Alerts**:
- OID system unavailable > 5 minutes
- Sync failure rate > 5%
- OID API response time > 2 seconds
- Data inconsistency detected

**Warning Alerts**:
- Sync delay > 15 minutes
- OID API response time > 500ms
- Fallback mode activated

---

## 🧪 Testing

### Integration Tests

**Test Cases**:
```typescript
describe('OID System Integration', () => {
  test('should sync new product to OID system', async () => {
    const product = createTestProduct();
    const oidNode = await oidService.syncProduct(product);
    
    expect(oidNode.oid).toMatch(/^1\.3\.6\.1\.4\.1\.XXXX\./);
    expect(oidNode.name).toBe(product.title);
    expect(oidNode.status).toBe('active');
  });
  
  test('should update existing OID node', async () => {
    const product = await getTestProduct();
    product.price = 19999;
    
    const oidNode = await oidService.syncProduct(product);
    
    expect(oidNode.metadata.price).toBe(19999);
  });
  
  test('should handle OID system unavailable', async () => {
    mockOIDApiDown();
    
    const solutions = await oidService.getB2BSolutions();
    
    expect(solutions.length).toBeGreaterThan(0);
    expect(solutions[0]).toHaveProperty('name');
  });
});
```

### Performance Tests

**Load Testing**:
- 100 concurrent product syncs
- 1000 OID queries per minute
- Batch sync of 50+ products
- Fallback mode under load

---

## 📚 References

### Internal Documentation
- [OID Integration Code](../../frontend/src/lib/oid-integration.ts)
- [Product Data](../../frontend/src/data/products.ts)
- [System Architecture](../architecture/README.md)

### External Resources
- OID Portal: `/Users/fadil369/02_BRAINSAIT_ECOSYSTEM/Unified_Platform/UNIFICATION_SYSTEM/brainSAIT-oid-system/oid-portal/`
- OID API Documentation: `https://oid.brainsait.io/api/docs`
- ISO OID Standard: [ISO/IEC 9834-1](https://www.iso.org/standard/67193.html)

### API Endpoints
- **OID System API**: `https://oid.brainsait.io/api/v1`
- **Query Endpoint**: `/query`
- **Node Management**: `/nodes`
- **Health Check**: `/health`

---

**Document Owner**: Platform/Infra Team  
**Last Updated**: October 2024  
**Status**: 🔄 In Progress  
**Next Review**: Weekly
