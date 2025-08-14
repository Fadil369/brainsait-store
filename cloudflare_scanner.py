#!/usr/bin/env python3
"""
BrainSAIT Cloudflare Scanner
Automatically discovers and categorizes your Cloudflare Workers and Pages for store integration
"""

import requests
import json
import os
from datetime import datetime
from typing import List, Dict, Any

class BrainSAITCloudflareScanner:
    def __init__(self, api_token: str, account_id: str = "519d80ce438f427d096a3e3bdd98a7e0"):
        self.api_token = api_token
        self.account_id = account_id
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        self.base_url = "https://api.cloudflare.com/client/v4"
        
    def get_workers(self) -> List[Dict]:
        """Fetch all Cloudflare Workers"""
        url = f"{self.base_url}/accounts/{self.account_id}/workers/scripts"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            if data.get('success'):
                workers = data.get('result', [])
                print(f"Found {len(workers)} Cloudflare Workers")
                return workers
            else:
                print(f"Error fetching workers: {data.get('errors', 'Unknown error')}")
                return []
        except Exception as e:
            print(f"Error fetching workers: {e}")
            return []
    
    def get_pages(self) -> List[Dict]:
        """Fetch all Cloudflare Pages projects"""
        url = f"{self.base_url}/accounts/{self.account_id}/pages/projects"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            if data.get('success'):
                pages = data.get('result', [])
                print(f"Found {len(pages)} Cloudflare Pages")
                return pages
            else:
                print(f"Error fetching pages: {data.get('errors', 'Unknown error')}")
                return []
        except Exception as e:
            print(f"Error fetching pages: {e}")
            return []
    
    def get_worker_routes(self, script_name: str) -> List[Dict]:
        """Get routes for a specific worker"""
        url = f"{self.base_url}/accounts/{self.account_id}/workers/scripts/{script_name}/routes"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            if data.get('success'):
                return data.get('result', [])
        except Exception as e:
            print(f"Error fetching routes for {script_name}: {e}")
        
        return []
    
    def categorize_cloudflare_asset(self, asset: Dict, asset_type: str) -> str:
        """Categorize Cloudflare asset based on name and type"""
        name = asset.get('id' if asset_type == 'worker' else 'name', '').lower()
        
        # AI/ML related
        ai_keywords = ['ai', 'ml', 'chat', 'gpt', 'openai', 'llm', 'neural', 'intelligence']
        if any(keyword in name for keyword in ai_keywords):
            return 'ai'
        
        # API/Backend services
        api_keywords = ['api', 'backend', 'server', 'gateway', 'webhook', 'service']
        if any(keyword in name for keyword in api_keywords) or asset_type == 'worker':
            return 'tools'
        
        # Web applications (Pages are typically websites)
        if asset_type == 'page':
            return 'websites'
        
        return 'tools'
    
    def calculate_cloudflare_pricing(self, asset: Dict, category: str, asset_type: str) -> int:
        """Calculate pricing for Cloudflare assets"""
        base_prices = {
            'ai': 2999,      # AI services command premium
            'websites': 1999, # Static sites/web apps
            'tools': 1499,   # Workers/APIs
            'apps': 2499     # Mobile/complex apps
        }
        
        base_price = base_prices.get(category, 1499)
        
        # Workers get higher pricing due to serverless nature
        if asset_type == 'worker':
            base_price += 500
        
        # Pages with custom domains get premium pricing
        if asset_type == 'page':
            domains = asset.get('domains', [])
            custom_domains = [d for d in domains if not d.endswith('.pages.dev')]
            if custom_domains:
                base_price += 300
        
        return base_price
    
    def generate_arabic_title(self, title: str, category: str, asset_type: str) -> str:
        """Generate Arabic title"""
        if asset_type == 'worker':
            prefix = "خدمة"  # Service
        else:
            prefix = "موقع"  # Website
            
        return f"{prefix} {title}"
    
    def get_live_url(self, asset: Dict, asset_type: str) -> str:
        """Get live URL for the asset"""
        if asset_type == 'worker':
            # Try to get custom domain from routes, fallback to worker subdomain
            script_name = asset.get('id', '')
            routes = self.get_worker_routes(script_name)
            
            for route in routes:
                pattern = route.get('pattern', '')
                if pattern and not pattern.startswith('*'):
                    # Clean up the pattern to get a proper URL
                    if not pattern.startswith('http'):
                        return f"https://{pattern.rstrip('/*')}"
                    return pattern.rstrip('/*')
            
            # Fallback to worker subdomain
            return f"https://{script_name}.fadil.workers.dev"
        
        elif asset_type == 'page':
            # Get the canonical URL for Pages
            canonical_url = asset.get('canonical_deployment', {}).get('url')
            if canonical_url:
                return canonical_url
            
            # Fallback to subdomain
            subdomain = asset.get('subdomain', asset.get('name', ''))
            return f"https://{subdomain}.pages.dev"
        
        return ""
    
    def analyze_cloudflare_asset(self, asset: Dict, asset_type: str) -> Dict[str, Any]:
        """Analyze Cloudflare asset and prepare store entry"""
        category = self.categorize_cloudflare_asset(asset, asset_type)
        price = self.calculate_cloudflare_pricing(asset, category, asset_type)
        
        # Get asset name
        name = asset.get('id' if asset_type == 'worker' else 'name', '')
        title = name.replace('-', ' ').replace('_', ' ').title()
        
        # Determine badge based on asset type and status
        badge = "DEPLOYED"
        badge_type = "hot"
        
        if asset_type == 'worker':
            badge = "LIVE API"
            badge_type = "hot"
        elif asset_type == 'page':
            badge = "LIVE SITE"
            badge_type = "new"
        
        # Category icons
        icons = {
            'ai': '🤖',
            'websites': '🌐',
            'tools': '⚡',
            'apps': '📱'
        }
        
        # Get live URL
        live_url = self.get_live_url(asset, asset_type)
        
        # Generate features based on asset type
        features = self.generate_features(asset_type, category)
        
        return {
            'id': f"cf_{asset_type}_{asset.get('id' if asset_type == 'worker' else 'name', '')}",
            'category': category,
            'title': title,
            'arabicTitle': self.generate_arabic_title(title, category, asset_type),
            'description': f"{'Serverless API' if asset_type == 'worker' else 'Static Web Application'} deployed on Cloudflare {'Workers' if asset_type == 'worker' else 'Pages'}",
            'price': price,
            'badge': badge,
            'badgeType': badge_type,
            'icon': icons.get(category, '⚡'),
            'features': features,
            'live_url': live_url,
            'cloudflare_type': asset_type,
            'created_at': asset.get('created_at', ''),
            'modified_at': asset.get('modified_on' if asset_type == 'worker' else 'modified_at', ''),
            'demo': self.generate_demo_content(title, category, asset_type, live_url)
        }
    
    def generate_features(self, asset_type: str, category: str) -> List[str]:
        """Generate features based on asset type and category"""
        base_features = []
        
        if asset_type == 'worker':
            base_features = [
                "⚡ Global Edge Deployment",
                "🚀 Sub-millisecond Response",
                "📈 Auto-scaling Infrastructure", 
                "🔒 Enterprise Security"
            ]
        else:  # Pages
            base_features = [
                "🌐 Global CDN Distribution",
                "🔒 Automatic HTTPS/SSL",
                "📱 Mobile Optimized",
                "⚡ Lightning Fast Loading"
            ]
        
        # Add category-specific features
        if category == 'ai':
            base_features[0] = "🤖 AI-Powered Processing"
        
        return base_features
    
    def generate_demo_content(self, title: str, category: str, asset_type: str, live_url: str) -> Dict:
        """Generate demo content for Cloudflare asset"""
        asset_descriptions = {
            'ai': 'AI-powered serverless solution with global edge processing',
            'websites': 'Modern web application with global CDN delivery',
            'tools': 'Serverless API with enterprise-grade performance',
            'apps': 'Progressive web application with mobile optimization'
        }
        
        return {
            'title': f"{title} - Live Demo",
            'arabicTitle': f"عرض مباشر - {title}",
            'preview': f"🔗 Access {title} live at {live_url}. {asset_descriptions.get(category, 'High-performance solution')} deployed on Cloudflare's global network.",
            'liveUrl': live_url,
            'features': [
                {
                    'icon': '🔗',
                    'title': 'Live Access',
                    'desc': 'Access the live application directly in your browser'
                },
                {
                    'icon': '⚡',
                    'title': 'Global Performance',
                    'desc': 'Served from 200+ locations worldwide for optimal speed'
                },
                {
                    'icon': '🔒',
                    'title': 'Enterprise Security',
                    'desc': 'Protected by Cloudflare\'s enterprise security suite'
                },
                {
                    'icon': '📊',
                    'title': 'Real-time Analytics',
                    'desc': 'Monitor performance and usage with detailed analytics'
                }
            ]
        }
    
    def should_include_asset(self, asset: Dict, asset_type: str) -> bool:
        """Determine if asset should be included in store"""
        # Get asset name
        name = asset.get('id' if asset_type == 'worker' else 'name', '')
        
        # Skip test/development assets
        test_keywords = ['test', 'dev', 'debug', 'temp', 'example', 'hello-world']
        if any(keyword in name.lower() for keyword in test_keywords):
            return False
        
        # Include all other assets
        return True
    
    def scan_and_generate_store_entries(self) -> List[Dict]:
        """Main method to scan Cloudflare assets and generate store entries"""
        print("☁️  Scanning Cloudflare deployments...")
        
        # Get Workers and Pages
        workers = self.get_workers()
        pages = self.get_pages()
        
        store_entries = []
        
        # Process Workers
        for worker in workers:
            if self.should_include_asset(worker, 'worker'):
                print(f"⚡ Processing Worker: {worker.get('id', 'Unknown')}")
                store_entry = self.analyze_cloudflare_asset(worker, 'worker')
                store_entries.append(store_entry)
            else:
                print(f"⏭️  Skipping Worker: {worker.get('id', 'Unknown')} (test/dev)")
        
        # Process Pages
        for page in pages:
            if self.should_include_asset(page, 'page'):
                print(f"🌐 Processing Page: {page.get('name', 'Unknown')}")
                store_entry = self.analyze_cloudflare_asset(page, 'page')
                store_entries.append(store_entry)
            else:
                print(f"⏭️  Skipping Page: {page.get('name', 'Unknown')} (test/dev)")
        
        print(f"\n🎉 Generated {len(store_entries)} Cloudflare store entries")
        return store_entries
    
    def save_to_file(self, store_entries: List[Dict], filename: str = "brainsait_cloudflare_products.json"):
        """Save store entries to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(store_entries, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved to {filename}")

def main():
    """Main execution function"""
    # Try to get Cloudflare API token from environment or wrangler
    api_token = os.environ.get('CLOUDFLARE_API_TOKEN')
    
    if not api_token:
        print("❌ Error: CLOUDFLARE_API_TOKEN environment variable not set")
        print("Please set your Cloudflare API token:")
        print("export CLOUDFLARE_API_TOKEN='your_token_here'")
        print("\nOr run: wrangler whoami to check your authentication")
        return
    
    # Initialize scanner
    scanner = BrainSAITCloudflareScanner(api_token)
    
    # Scan Cloudflare assets and generate store entries
    store_entries = scanner.scan_and_generate_store_entries()
    
    # Save to file
    scanner.save_to_file(store_entries)
    
    # Print summary
    print("\n📊 Summary:")
    categories = {}
    asset_types = {}
    
    for entry in store_entries:
        cat = entry['category']
        asset_type = entry['cloudflare_type']
        
        categories[cat] = categories.get(cat, 0) + 1
        asset_types[asset_type] = asset_types.get(asset_type, 0) + 1
    
    print("By Category:")
    for category, count in categories.items():
        print(f"  {category}: {count} products")
    
    print("By Type:")
    for asset_type, count in asset_types.items():
        print(f"  {asset_type}: {count} assets")
    
    print(f"\n🚀 Ready to integrate {len(store_entries)} Cloudflare products into BrainSAIT store!")

if __name__ == "__main__":
    main()