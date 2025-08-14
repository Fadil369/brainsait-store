#!/usr/bin/env python3
"""
GP Site B2B Pricing Update
Updates all products with B2B complete solution pricing
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any

class B2BPricingUpdater:
    def __init__(self):
        self.b2b_multiplier = 5  # 5x increase for B2B complete solutions
        
    def calculate_b2b_pricing(self, category: str, current_price: int) -> Dict[str, int]:
        """Calculate B2B pricing for complete solutions"""
        
        # Base B2B pricing for complete solutions
        b2b_base_prices = {
            'ai': 19999,        # AI solutions - enterprise premium
            'websites': 14999,  # Complete websites/platforms  
            'tools': 9999,      # Professional tools/APIs
            'apps': 17999,      # Mobile/complex applications
            'courses': 12999    # Professional training
        }
        
        base_price = b2b_base_prices.get(category, 9999)
        
        # Pricing tiers for B2B
        pricing_options = {
            "app_only": base_price,                    # Complete application only
            "app_with_source": base_price + 7000,     # App + source code
            "enterprise_package": base_price + 15000  # App + source + support + customization
        }
        
        return pricing_options
    
    def update_gp_site_products(self) -> List[Dict]:
        """Update GP site products with B2B pricing"""
        
        # Load existing GP site products
        try:
            with open('brainsait_gp_site_products.json', 'r', encoding='utf-8') as f:
                products = json.load(f)
        except FileNotFoundError:
            print("❌ GP site products file not found")
            return []
        
        updated_products = []
        
        for product in products:
            # Calculate new B2B pricing
            category = product['category']
            pricing_options = self.calculate_b2b_pricing(category, product['price'])
            
            # Update product with B2B pricing
            product['price'] = pricing_options['app_only']
            product['pricing_options'] = pricing_options
            product['price_range'] = f"{pricing_options['app_only']:,} - {pricing_options['enterprise_package']:,} SAR"
            
            # Update description for B2B
            product['description'] = product['description'].replace(
                " | Live service with optional source code access", 
                " | Complete B2B solution with enterprise support options"
            ).replace(
                " | Live application with template access",
                " | Professional B2B platform with full customization"
            )
            
            # Add B2B features
            if 'features' in product:
                product['features'].extend([
                    "🏢 Enterprise Ready",
                    "🤝 Professional Support",
                    "🎯 Custom Branding",
                    "📞 Implementation Assistance"
                ])
            
            # Update badges for B2B
            if product.get('badge') in ['LIVE API', 'LIVE SITE', 'DEPLOYED']:
                product['badge'] = 'B2B SOLUTION'
                product['badgeType'] = 'premium'
            
            updated_products.append(product)
        
        print(f"✅ Updated {len(updated_products)} products with B2B pricing")
        return updated_products
    
    def update_all_store_products(self):
        """Update all store products with B2B pricing"""
        
        # Load complete store catalog
        try:
            with open('brainsait_store_complete.json', 'r', encoding='utf-8') as f:
                all_products = json.load(f)
        except FileNotFoundError:
            print("❌ Complete store catalog not found")
            return
        
        updated_products = []
        
        for product in all_products:
            category = product.get('category', 'tools')
            current_price = product.get('price', 999)
            source = product.get('source', 'existing')
            
            # Calculate B2B pricing based on source and category
            pricing_options = self.calculate_b2b_pricing(category, current_price)
            
            # Update pricing
            product['price'] = pricing_options['app_only']
            product['pricing_options'] = pricing_options
            product['price_range'] = f"{pricing_options['app_only']:,} - {pricing_options['enterprise_package']:,} SAR"
            
            # Update description for B2B focus
            if '|' in product['description']:
                base_desc = product['description'].split('|')[0].strip()
            else:
                base_desc = product['description']
            
            if source == 'github':
                product['description'] = f"{base_desc} | Complete B2B solution with source code and enterprise support"
            elif source == 'cloudflare':
                product['description'] = f"{base_desc} | Live B2B platform with professional deployment and customization"
            elif source == 'gp_site':
                product['description'] = f"{base_desc} | Professional B2B solution with full enterprise features"
            else:
                product['description'] = f"{base_desc} | Premium B2B package with professional support and customization"
            
            # Ensure all products have enterprise features
            features = product.get('features', [])
            b2b_features = ["🏢 Enterprise License", "🤝 Professional Support", "🎯 Custom Deployment"]
            
            # Add B2B features if not already present
            for feature in b2b_features:
                if feature not in features:
                    features.append(feature)
            
            product['features'] = features
            
            updated_products.append(product)
        
        # Save updated catalog
        with open('brainsait_store_complete.json', 'w', encoding='utf-8') as f:
            json.dump(updated_products, f, indent=2, ensure_ascii=False)
        
        # Update GP site products separately
        gp_products = self.update_gp_site_products()
        with open('brainsait_gp_site_products.json', 'w', encoding='utf-8') as f:
            json.dump(gp_products, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Updated {len(updated_products)} products with B2B pricing")
        
        # Print pricing summary
        self.print_pricing_summary(updated_products)
    
    def print_pricing_summary(self, products: List[Dict]):
        """Print summary of B2B pricing"""
        print("\n" + "="*60)
        print("💰 B2B PRICING SUMMARY")
        print("="*60)
        
        categories = {}
        price_ranges = {}
        
        for product in products:
            category = product['category']
            price = product['price']
            
            if category not in categories:
                categories[category] = []
                price_ranges[category] = {'min': price, 'max': price}
            
            categories[category].append(price)
            price_ranges[category]['min'] = min(price_ranges[category]['min'], price)
            price_ranges[category]['max'] = max(price_ranges[category]['max'], price)
        
        print(f"\n🏷️ BY CATEGORY:")
        for category, prices in categories.items():
            icon = {"ai": "🤖", "websites": "🌐", "tools": "🛠️", "apps": "📱", "courses": "🎓"}.get(category, "📦")
            avg_price = sum(prices) / len(prices)
            print(f"   {icon} {category.upper()}: {len(prices)} products (Avg: {avg_price:,.0f} SAR)")
        
        print(f"\n💰 PRICE RANGES:")
        for category, ranges in price_ranges.items():
            print(f"   {category}: {ranges['min']:,} - {ranges['max']:,} SAR")
        
        print(f"\n🎯 B2B PACKAGE OPTIONS:")
        print(f"   📱 App Only: Base price")
        print(f"   📂 App + Source: Base + 7,000 SAR")
        print(f"   🏢 Enterprise: Base + 15,000 SAR")
        
        total_value = sum(p['price'] for p in products)
        print(f"\n💎 TOTAL CATALOG VALUE: {total_value:,} SAR")
        print("="*60)

def main():
    """Main execution function"""
    print("💰 Updating pricing for B2B complete solutions...")
    
    updater = B2BPricingUpdater()
    updater.update_all_store_products()
    
    print("\n🎉 B2B pricing update complete!")
    print("📈 All products now priced for enterprise B2B sales")

if __name__ == "__main__":
    main()