#!/usr/bin/env python3
"""
Update Frontend Products
Updates the Next.js frontend with the integrated product catalog
"""

import json
import os

def update_frontend_products():
    """Update the frontend products data file"""
    
    # Load the integrated products
    try:
        with open('brainsait_store_complete.json', 'r', encoding='utf-8') as f:
            integrated_products = json.load(f)
        print(f"✅ Loaded {len(integrated_products)} integrated products")
    except FileNotFoundError:
        print("❌ brainsait_store_complete.json not found. Run store_integrator.py first.")
        return
    
    # Convert to frontend format (TypeScript-compatible)
    frontend_products = []
    
    for product in integrated_products:
        frontend_product = {
            "id": product["id"],
            "category": product["category"],
            "title": product["title"],
            "arabicTitle": product["arabicTitle"],
            "description": product["description"],
            "price": product["price"],
            "originalPrice": product.get("originalPrice"),
            "badge": product["badge"],
            "badgeType": product["badgeType"],
            "icon": product["icon"],
            "features": product["features"],
            "demo": product["demo"],
            "metadata": product.get("metadata", {}),
            "source": product.get("source", "existing")
        }
        
        # Add pricing options if available
        if "pricing_options" in product:
            frontend_product["pricingOptions"] = product["pricing_options"]
            frontend_product["priceRange"] = product.get("price_range", "")
        
        frontend_products.append(frontend_product)
    
    # Create TypeScript products file
    frontend_dir = "frontend/src/data"
    os.makedirs(frontend_dir, exist_ok=True)
    
    from datetime import datetime
    current_time = datetime.now().isoformat()
    
    ts_content = f'''// BrainSAIT Store Products
// Auto-generated from GitHub and Cloudflare integrations
// Last updated: {current_time}

export interface Product {{
  id: number;
  category: string;
  title: string;
  arabicTitle: string;
  description: string;
  price: number;
  originalPrice?: number;
  badge: string;
  badgeType: string;
  icon: string;
  features: string[];
  demo: {{
    title: string;
    arabicTitle: string;
    preview: string;
    liveUrl?: string;
    githubUrl?: string;
    hasLiveDemo?: boolean;
    hasSourceCode?: boolean;
    features: Array<{{
      icon: string;
      title: string;
      desc: string;
    }}>;
  }};
  metadata?: {{
    github_url?: string;
    clone_url?: string;
    live_url?: string;
    stars?: number;
    language?: string;
    cloudflare_type?: string;
    deployment_status?: string;
  }};
  source: 'existing' | 'github' | 'cloudflare';
  pricingOptions?: {{
    [key: string]: number;
  }};
  priceRange?: string;
}}

export const products: Product[] = {json.dumps(frontend_products, indent=2, ensure_ascii=False)};

export const productCategories = [
  {{ id: 'all', name: 'All Products', nameAr: 'جميع المنتجات', icon: '🌟' }},
  {{ id: 'ai', name: 'AI Solutions', nameAr: 'حلول الذكاء الاصطناعي', icon: '🤖' }},
  {{ id: 'websites', name: 'Websites', nameAr: 'المواقع الإلكترونية', icon: '🌐' }},
  {{ id: 'apps', name: 'Applications', nameAr: 'التطبيقات', icon: '📱' }},
  {{ id: 'tools', name: 'Tools', nameAr: 'الأدوات', icon: '🛠️' }},
  {{ id: 'courses', name: 'Courses', nameAr: 'الدورات', icon: '🎓' }},
];

export const productSources = [
  {{ id: 'all', name: 'All Sources', nameAr: 'جميع المصادر', icon: '🌟' }},
  {{ id: 'existing', name: 'Store Originals', nameAr: 'منتجات المتجر الأصلية', icon: '⭐' }},
  {{ id: 'github', name: 'GitHub Projects', nameAr: 'مشاريع GitHub', icon: '🐙' }},
  {{ id: 'cloudflare', name: 'Live Services', nameAr: 'الخدمات المباشرة', icon: '☁️' }},
];

// Statistics
export const storeStats = {{
  totalProducts: {len(frontend_products)},
  byCategory: {{
    ai: {len([p for p in frontend_products if p['category'] == 'ai'])},
    websites: {len([p for p in frontend_products if p['category'] == 'websites'])},
    apps: {len([p for p in frontend_products if p['category'] == 'apps'])},
    tools: {len([p for p in frontend_products if p['category'] == 'tools'])},
    courses: {len([p for p in frontend_products if p['category'] == 'courses'])},
  }},
  bySource: {{
    existing: {len([p for p in frontend_products if p['source'] == 'existing'])},
    github: {len([p for p in frontend_products if p['source'] == 'github'])},
    cloudflare: {len([p for p in frontend_products if p['source'] == 'cloudflare'])},
  }},
  liveDemos: {len([p for p in frontend_products if p.get('metadata', {}).get('live_url')])},
  sourceCode: {len([p for p in frontend_products if p.get('metadata', {}).get('github_url')])},
}};'''
    
    # Write the TypeScript file
    products_file = f"{frontend_dir}/products.ts"
    with open(products_file, 'w', encoding='utf-8') as f:
        f.write(ts_content)
    
    print(f"✅ Updated {products_file}")
    
    # Also create a JSON version for API use
    json_file = f"{frontend_dir}/products.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(frontend_products, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created {json_file}")
    
    print(f"\n📊 Frontend Integration Summary:")
    print(f"   📦 Total Products: {len(frontend_products)}")
    print(f"   🤖 AI Solutions: {len([p for p in frontend_products if p['category'] == 'ai'])}")
    print(f"   🌐 Websites: {len([p for p in frontend_products if p['category'] == 'websites'])}")
    print(f"   📱 Apps: {len([p for p in frontend_products if p['category'] == 'apps'])}")
    print(f"   🛠️ Tools: {len([p for p in frontend_products if p['category'] == 'tools'])}")
    print(f"   🎓 Courses: {len([p for p in frontend_products if p['category'] == 'courses'])}")
    print(f"   🔗 Live Demos: {len([p for p in frontend_products if p.get('metadata', {}).get('live_url')])}")
    print(f"   📂 Source Code: {len([p for p in frontend_products if p.get('metadata', {}).get('github_url')])}")

if __name__ == "__main__":
    from datetime import datetime
    print("🔄 Updating frontend products...")
    update_frontend_products()
    print("🎉 Frontend products updated successfully!")