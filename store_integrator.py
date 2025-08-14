#!/usr/bin/env python3
"""
BrainSAIT Store Integrator
Combines GitHub and Cloudflare products into the unified store with SAR pricing
"""

import json
import os
from typing import List, Dict, Any
from datetime import datetime

class BrainSAITStoreIntegrator:
    def __init__(self):
        self.github_products = []
        self.cloudflare_products = []
        self.existing_products = []
        self.gp_site_products = []
        self.final_products = []
        
    def load_github_products(self, filename: str = "brainsait_github_products.json") -> List[Dict]:
        """Load GitHub-sourced products"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.github_products = json.load(f)
            print(f"✅ Loaded {len(self.github_products)} GitHub products")
            return self.github_products
        except FileNotFoundError:
            print(f"⚠️  {filename} not found, skipping GitHub products")
            return []
        except Exception as e:
            print(f"❌ Error loading GitHub products: {e}")
            return []
    
    def load_cloudflare_products(self, filename: str = "brainsait_cloudflare_products.json") -> List[Dict]:
        """Load Cloudflare-sourced products"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.cloudflare_products = json.load(f)
            print(f"✅ Loaded {len(self.cloudflare_products)} Cloudflare products")
            return self.cloudflare_products
        except FileNotFoundError:
            print(f"⚠️  {filename} not found, skipping Cloudflare products")
            return []
        except Exception as e:
            print(f"❌ Error loading Cloudflare products: {e}")
            return []
    
    def load_gp_site_products(self, filename: str = "brainsait_gp_site_products.json") -> List[Dict]:
        """Load GP site-sourced products"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.gp_site_products = json.load(f)
            print(f"✅ Loaded {len(self.gp_site_products)} GP site products")
            return self.gp_site_products
        except FileNotFoundError:
            print(f"⚠️  {filename} not found, skipping GP site products")
            return []
        except Exception as e:
            print(f"❌ Error loading GP site products: {e}")
            return []
    
    def load_existing_store_products(self) -> List[Dict]:
        """Load existing store products from the HTML prototype"""
        # Define existing products from the HTML prototype
        existing_products = [
            {
                "id": 1,
                "category": "ai",
                "title": "AI Business Assistant",
                "arabicTitle": "مساعد الأعمال الذكي",
                "description": "Advanced AI-powered business automation and analytics platform with GPT-4 integration",
                "price": 1499,
                "originalPrice": 2499,
                "badge": "BESTSELLER",
                "badgeType": "hot",
                "icon": "🤖",
                "features": [
                    "🧠 GPT-4 Integration", 
                    "🌐 Multi-language Support",
                    "📊 Advanced Analytics", 
                    "🔗 API Access"
                ],
                "demo": {
                    "title": "AI Business Assistant Demo",
                    "arabicTitle": "عرض مساعد الأعمال الذكي",
                    "preview": "🤖 Experience the power of AI-driven business automation. This assistant can handle customer inquiries, generate reports, analyze data, and provide intelligent insights to boost your business efficiency.",
                    "features": [
                        {"icon": "💬", "title": "Smart Chat", "desc": "Natural language processing for customer interactions"},
                        {"icon": "📊", "title": "Data Analysis", "desc": "Automated insights from your business data"},
                        {"icon": "📝", "title": "Report Generation", "desc": "AI-generated business reports and summaries"},
                        {"icon": "🔄", "title": "Workflow Automation", "desc": "Streamline repetitive business processes"}
                    ]
                }
            },
            {
                "id": 2,
                "category": "courses",
                "title": "Digital Marketing Mastery",
                "arabicTitle": "إتقان التسويق الرقمي",
                "description": "Complete digital marketing course with real-world case studies and hands-on projects",
                "price": 2999,
                "badge": "FEATURED",
                "badgeType": "new",
                "icon": "🎓",
                "features": [
                    "⏱️ 60+ Hours Content",
                    "🏆 Certificate Included",
                    "👥 Live Sessions",
                    "🤝 1-on-1 Mentoring"
                ],
                "demo": {
                    "title": "Digital Marketing Course Preview",
                    "arabicTitle": "معاينة دورة التسويق الرقمي",
                    "preview": "🎓 Master digital marketing with our comprehensive course. Learn SEO, social media marketing, content strategy, and analytics through practical projects and real case studies.",
                    "features": [
                        {"icon": "🎥", "title": "Video Lessons", "desc": "High-quality video content with practical examples"},
                        {"icon": "📱", "title": "Mobile Learning", "desc": "Learn on-the-go with mobile-optimized content"},
                        {"icon": "🏆", "title": "Certification", "desc": "Industry-recognized certificate upon completion"},
                        {"icon": "👨‍🏫", "title": "Expert Mentoring", "desc": "Direct access to industry professionals"}
                    ]
                }
            },
            {
                "id": 3,
                "category": "websites",
                "title": "E-commerce Template Pro",
                "arabicTitle": "قالب المتجر الإلكتروني المحترف",
                "description": "Professional e-commerce template with payment integration and inventory management",
                "price": 1999,
                "badge": "POPULAR",
                "badgeType": "hot",
                "icon": "🛒",
                "features": [
                    "💳 Payment Integration",
                    "📦 Inventory Management",
                    "📱 Mobile Responsive",
                    "🎨 Customizable Design"
                ],
                "demo": {
                    "title": "E-commerce Template Preview",
                    "arabicTitle": "معاينة قالب المتجر الإلكتروني",
                    "preview": "🛒 Launch your online store with our professional template. Includes payment processing, inventory management, customer accounts, and a beautiful responsive design.",
                    "features": [
                        {"icon": "🎨", "title": "Modern Design", "desc": "Clean, professional design that converts visitors"},
                        {"icon": "💳", "title": "Payment Ready", "desc": "Integrated with major payment processors"},
                        {"icon": "📊", "title": "Analytics", "desc": "Built-in analytics to track your store performance"},
                        {"icon": "🔧", "title": "Easy Setup", "desc": "Quick installation and configuration process"}
                    ]
                }
            },
            {
                "id": 4,
                "category": "apps",
                "title": "Task Management App",
                "arabicTitle": "تطبيق إدارة المهام",
                "description": "Cross-platform task management application with team collaboration features",
                "price": 3499,
                "badge": "NEW",
                "badgeType": "new",
                "icon": "📋",
                "features": [
                    "👥 Team Collaboration",
                    "📅 Calendar Integration",
                    "🔔 Smart Notifications",
                    "☁️ Cloud Sync"
                ],
                "demo": {
                    "title": "Task Manager App Demo",
                    "arabicTitle": "عرض تطبيق إدارة المهام",
                    "preview": "📋 Boost your productivity with our comprehensive task management app. Organize projects, collaborate with teams, and track progress with intelligent insights.",
                    "features": [
                        {"icon": "✅", "title": "Task Organization", "desc": "Organize tasks with projects, labels, and priorities"},
                        {"icon": "👥", "title": "Team Features", "desc": "Collaborate with team members and assign tasks"},
                        {"icon": "📊", "title": "Progress Tracking", "desc": "Visual progress tracking and productivity insights"},
                        {"icon": "🔄", "title": "Integrations", "desc": "Connect with your favorite tools and services"}
                    ]
                }
            }
        ]
        
        self.existing_products = existing_products
        print(f"✅ Loaded {len(existing_products)} existing store products")
        return existing_products
    
    def standardize_product_format(self, product: Dict, source: str) -> Dict:
        """Standardize product format across all sources"""
        standardized = {
            "id": product.get("id"),
            "category": product.get("category", "tools"),
            "title": product.get("title", ""),
            "arabicTitle": product.get("arabicTitle", product.get("title", "")),
            "description": product.get("description", ""),
            "price": product.get("price", 999),
            "originalPrice": product.get("originalPrice"),
            "badge": product.get("badge", "NEW"),
            "badgeType": product.get("badgeType", "new"),
            "icon": product.get("icon", "🛠️"),
            "features": product.get("features", []),
            "demo": product.get("demo", {}),
            "source": source,
            "metadata": {}
        }
        
        # Add source-specific metadata
        if source == "github":
            standardized["metadata"] = {
                "github_url": product.get("github_url"),
                "clone_url": product.get("clone_url"),
                "stars": product.get("stars", 0),
                "language": product.get("language", "")
            }
        elif source == "cloudflare":
            standardized["metadata"] = {
                "live_url": product.get("live_url"),
                "cloudflare_type": product.get("cloudflare_type"),
                "deployment_status": "live"
            }
        
        return standardized
    
    def adjust_pricing_for_bundles(self, products: List[Dict]) -> List[Dict]:
        """Adjust pricing to offer app + source code bundles"""
        for product in products:
            source = product.get("source", "")
            base_price = product["price"]
            
            if source == "github":
                # Offer source code version
                product["pricing_options"] = {
                    "source_only": base_price,
                    "compiled_app": base_price + 500,
                    "full_bundle": base_price + 1000
                }
                product["description"] += " | Available as source code, compiled app, or full development bundle"
                
            elif source == "cloudflare":
                # Offer live service + source code
                product["pricing_options"] = {
                    "live_service": base_price,
                    "source_code": base_price + 300,
                    "full_access": base_price + 800
                }
                product["description"] += " | Live service with optional source code access"
                
            # Update the display price to show bundle pricing
            if "pricing_options" in product:
                options = product["pricing_options"]
                min_price = min(options.values())
                max_price = max(options.values())
                product["price_range"] = f"{min_price} - {max_price} SAR"
        
        return products
    
    def add_live_demo_links(self, products: List[Dict]) -> List[Dict]:
        """Add live demo links where available"""
        for product in products:
            demo = product.get("demo", {})
            metadata = product.get("metadata", {})
            
            # Add live URLs to demo content
            if metadata.get("live_url"):
                demo["liveUrl"] = metadata["live_url"]
                demo["hasLiveDemo"] = True
            elif metadata.get("github_url"):
                demo["githubUrl"] = metadata["github_url"]
                demo["hasSourceCode"] = True
            
            product["demo"] = demo
        
        return products
    
    def generate_category_summary(self, products: List[Dict]) -> Dict:
        """Generate summary by category and source"""
        summary = {
            "total_products": len(products),
            "by_category": {},
            "by_source": {},
            "price_ranges": {},
            "live_demos": 0,
            "source_code": 0
        }
        
        for product in products:
            category = product["category"]
            source = product.get("source", "existing")
            price = product["price"]
            
            # Count by category
            summary["by_category"][category] = summary["by_category"].get(category, 0) + 1
            
            # Count by source
            summary["by_source"][source] = summary["by_source"].get(source, 0) + 1
            
            # Track price ranges
            if category not in summary["price_ranges"]:
                summary["price_ranges"][category] = {"min": price, "max": price}
            else:
                summary["price_ranges"][category]["min"] = min(summary["price_ranges"][category]["min"], price)
                summary["price_ranges"][category]["max"] = max(summary["price_ranges"][category]["max"], price)
            
            # Count features
            if product.get("metadata", {}).get("live_url"):
                summary["live_demos"] += 1
            if product.get("metadata", {}).get("github_url"):
                summary["source_code"] += 1
        
        return summary
    
    def integrate_all_products(self) -> List[Dict]:
        """Main integration method"""
        print("🔄 Integrating all products...")
        
        # Load all sources
        self.load_existing_store_products()
        self.load_github_products()
        self.load_cloudflare_products()
        self.load_gp_site_products()
        
        # Standardize formats
        all_products = []
        
        # Add existing products
        for product in self.existing_products:
            standardized = self.standardize_product_format(product, "existing")
            all_products.append(standardized)
        
        # Add GitHub products
        for product in self.github_products:
            standardized = self.standardize_product_format(product, "github")
            all_products.append(standardized)
        
        # Add Cloudflare products
        for product in self.cloudflare_products:
            standardized = self.standardize_product_format(product, "cloudflare")
            all_products.append(standardized)
        
        # Add GP site products (already standardized)
        for product in self.gp_site_products:
            all_products.append(product)
        
        # Assign sequential IDs
        for i, product in enumerate(all_products, 1):
            product["id"] = i
        
        # Apply enhancements
        all_products = self.adjust_pricing_for_bundles(all_products)
        all_products = self.add_live_demo_links(all_products)
        
        self.final_products = all_products
        return all_products
    
    def save_integrated_products(self, filename: str = "brainsait_store_complete.json"):
        """Save the complete integrated product catalog"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.final_products, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved complete store catalog to {filename}")
    
    def generate_store_summary(self):
        """Generate and display store summary"""
        summary = self.generate_category_summary(self.final_products)
        
        print("\n" + "="*60)
        print("🏪 BRAINSAIT STORE INTEGRATION COMPLETE")
        print("="*60)
        
        print(f"\n📊 TOTAL PRODUCTS: {summary['total_products']}")
        
        print(f"\n🏷️  BY CATEGORY:")
        for category, count in summary['by_category'].items():
            icon = {"ai": "🤖", "websites": "🌐", "tools": "🛠️", "apps": "📱", "courses": "🎓"}.get(category, "📦")
            print(f"   {icon} {category.upper()}: {count} products")
        
        print(f"\n📡 BY SOURCE:")
        for source, count in summary['by_source'].items():
            icon = {"existing": "⭐", "github": "🐙", "cloudflare": "☁️", "gp_site": "🌟"}.get(source, "📦")
            print(f"   {icon} {source.upper()}: {count} products")
        
        print(f"\n💰 PRICE RANGES (SAR):")
        for category, ranges in summary['price_ranges'].items():
            print(f"   {category}: {ranges['min']} - {ranges['max']} SAR")
        
        print(f"\n🔗 FEATURES:")
        print(f"   🌐 Live Demos: {summary['live_demos']} products")
        print(f"   📂 Source Code: {summary['source_code']} products")
        
        print(f"\n🎯 HIGHLIGHTS:")
        print(f"   ✅ Multi-language support (Arabic/English)")
        print(f"   ✅ SAR pricing for Saudi market")
        print(f"   ✅ Live demos and source code access")
        print(f"   ✅ Bundle pricing (app + source)")
        print(f"   ✅ Real-time Cloudflare deployments")
        
        print("\n" + "="*60)

def main():
    """Main execution function"""
    print("🚀 Starting BrainSAIT Store Integration...")
    
    # Initialize integrator
    integrator = BrainSAITStoreIntegrator()
    
    # Integrate all products
    integrated_products = integrator.integrate_all_products()
    
    # Save complete catalog
    integrator.save_integrated_products()
    
    # Generate summary
    integrator.generate_store_summary()
    
    print(f"\n🎉 Store integration complete! Ready to serve {len(integrated_products)} products.")
    print("📁 Files generated:")
    print("   - brainsait_store_complete.json (Complete product catalog)")
    print("   - Ready for Next.js frontend integration")

if __name__ == "__main__":
    main()