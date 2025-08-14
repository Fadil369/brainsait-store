#!/usr/bin/env python3
"""
BrainSAIT GitHub Repository Scanner
Automatically discovers and categorizes your GitHub repositories for store integration
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

class BrainSAITRepoScanner:
    def __init__(self, github_token: str, username: str = "fadil369"):
        self.github_token = github_token
        self.username = username
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.base_url = "https://api.github.com"
        
    def get_repositories(self) -> List[Dict]:
        """Fetch all public repositories for the user"""
        repos = []
        page = 1
        
        while True:
            url = f"{self.base_url}/users/{self.username}/repos"
            params = {
                "type": "owner",
                "sort": "updated", 
                "per_page": 100,
                "page": page
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                print(f"Error fetching repositories: {response.status_code}")
                break
                
            batch = response.json()
            if not batch:
                break
                
            repos.extend(batch)
            page += 1
            
        print(f"Found {len(repos)} repositories")
        return repos
    
    def get_repository_details(self, repo_name: str) -> Dict:
        """Get detailed information about a specific repository"""
        url = f"{self.base_url}/repos/{self.username}/{repo_name}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        return {}
    
    def get_repository_readme(self, repo_name: str) -> str:
        """Get repository README content"""
        url = f"{self.base_url}/repos/{self.username}/{repo_name}/readme"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            readme_data = response.json()
            if readme_data.get('encoding') == 'base64':
                import base64
                return base64.b64decode(readme_data['content']).decode('utf-8')
        return ""
    
    def categorize_repository(self, repo: Dict) -> str:
        """Categorize repository based on language and description"""
        language = (repo.get('language') or '').lower()
        description = (repo.get('description') or '').lower()
        name = repo.get('name', '').lower()
        
        # AI/ML projects
        ai_keywords = ['ai', 'ml', 'machine learning', 'neural', 'tensorflow', 'pytorch', 
                      'openai', 'llm', 'chatbot', 'nlp', 'computer vision']
        if any(keyword in description or keyword in name for keyword in ai_keywords):
            return 'ai'
        
        # Web applications
        web_keywords = ['website', 'web', 'frontend', 'backend', 'api', 'server']
        web_languages = ['javascript', 'typescript', 'html', 'css', 'php', 'ruby']
        if (language in web_languages or 
            any(keyword in description or keyword in name for keyword in web_keywords)):
            return 'websites'
        
        # Mobile apps
        mobile_keywords = ['mobile', 'ios', 'android', 'app', 'flutter', 'react native']
        mobile_languages = ['swift', 'kotlin', 'dart', 'objective-c']
        if (language in mobile_languages or 
            any(keyword in description or keyword in name for keyword in mobile_keywords)):
            return 'apps'
        
        # Educational content
        edu_keywords = ['tutorial', 'guide', 'course', 'learning', 'documentation', 
                       'book', 'cookbook', 'examples']
        if any(keyword in description or keyword in name for keyword in edu_keywords):
            return 'ebooks'
        
        # Templates
        template_keywords = ['template', 'boilerplate', 'starter', 'scaffold']
        if any(keyword in description or keyword in name for keyword in template_keywords):
            return 'templates'
        
        # Default to tools
        return 'tools'
    
    def calculate_pricing(self, repo: Dict, category: str) -> int:
        """Calculate pricing based on repository metrics and category"""
        base_prices = {
            'ai': 1499,
            'apps': 2999,
            'websites': 1999,
            'courses': 2499,
            'ebooks': 199,
            'templates': 899,
            'tools': 599
        }
        
        base_price = base_prices.get(category, 599)
        
        # Adjust based on stars (popularity)
        stars = repo.get('stargazers_count', 0)
        if stars > 100:
            base_price += 500
        elif stars > 50:
            base_price += 200
        elif stars > 10:
            base_price += 100
        
        # Adjust based on recent activity
        updated_at = repo.get('updated_at', '')
        if updated_at:
            try:
                update_date = datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%SZ")
                days_since_update = (datetime.now() - update_date).days
                if days_since_update < 30:
                    base_price += 200  # Recently maintained
                elif days_since_update < 90:
                    base_price += 100
            except:
                pass
        
        return base_price
    
    def generate_arabic_title(self, title: str, category: str) -> str:
        """Generate Arabic title based on category"""
        category_translations = {
            'ai': 'ذكي',
            'apps': 'تطبيق',
            'websites': 'موقع',
            'courses': 'دورة',
            'ebooks': 'كتاب',
            'templates': 'قالب',
            'tools': 'أداة'
        }
        
        prefix = category_translations.get(category, 'منتج')
        return f"{prefix} {title}"
    
    def get_features_from_readme(self, readme_content: str) -> List[str]:
        """Extract features from README content"""
        features = []
        
        if not readme_content:
            return ["📖 Open Source", "⭐ Community Driven", "🔧 Customizable", "📱 Production Ready"]
        
        # Look for common feature indicators
        lines = readme_content.lower().split('\n')
        feature_indicators = ['features', 'capabilities', 'what it does', 'includes']
        
        in_features_section = False
        for line in lines:
            if any(indicator in line for indicator in feature_indicators):
                in_features_section = True
                continue
                
            if in_features_section:
                if line.strip().startswith(('- ', '* ', '+ ')):
                    feature = line.strip()[2:].strip()
                    if len(feature) > 10 and len(feature) < 80:
                        features.append(feature.capitalize())
                        if len(features) >= 6:
                            break
                elif line.strip() == '' or line.startswith('#'):
                    break
        
        # Default features if none found
        if not features:
            features = [
                "📖 Well Documented",
                "⭐ Production Ready", 
                "🔧 Easy to Setup",
                "🚀 High Performance"
            ]
        
        return features[:4]  # Limit to 4 features
    
    def analyze_repository(self, repo: Dict) -> Dict[str, Any]:
        """Analyze repository and prepare store entry data"""
        category = self.categorize_repository(repo)
        price = self.calculate_pricing(repo, category)
        
        # Get README for features
        readme = self.get_repository_readme(repo['name'])
        features = self.get_features_from_readme(readme)
        
        # Determine badge
        badge = "OPEN SOURCE"
        badge_type = "new"
        
        if repo.get('stargazers_count', 0) > 50:
            badge = "POPULAR"
            badge_type = "hot"
        elif self.is_recently_updated(repo.get('updated_at', '')):
            badge = "UPDATED"
            badge_type = "new"
        
        # Category icons
        icons = {
            'ai': '🤖',
            'apps': '📱', 
            'websites': '🌐',
            'courses': '🎓',
            'ebooks': '📚',
            'templates': '📄',
            'tools': '🛠️'
        }
        
        title = repo['name'].replace('-', ' ').replace('_', ' ').title()
        
        return {
            'id': f"gh_{repo['id']}",
            'category': category,
            'title': title,
            'arabicTitle': self.generate_arabic_title(title, category),
            'description': repo.get('description', 'Open source solution from BrainSAIT'),
            'price': price,
            'badge': badge,
            'badgeType': badge_type,
            'icon': icons.get(category, '🛠️'),
            'features': features,
            'github_url': repo['html_url'],
            'clone_url': repo['clone_url'],
            'stars': repo.get('stargazers_count', 0),
            'forks': repo.get('forks_count', 0),
            'language': repo.get('language', 'Multiple'),
            'created_at': repo.get('created_at', ''),
            'updated_at': repo.get('updated_at', ''),
            'demo': self.generate_demo_content(repo, category)
        }
    
    def is_recently_updated(self, updated_at: str) -> bool:
        """Check if repository was updated in last 3 months"""
        if not updated_at:
            return False
            
        try:
            update_date = datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%SZ")
            three_months_ago = datetime.now() - timedelta(days=90)
            return update_date > three_months_ago
        except:
            return False
    
    def generate_demo_content(self, repo: Dict, category: str) -> Dict:
        """Generate demo content for the repository"""
        title = repo['name'].replace('-', ' ').replace('_', ' ').title()
        
        category_descriptions = {
            'ai': 'AI-powered solution with machine learning capabilities',
            'apps': 'Mobile application with native performance',
            'websites': 'Modern web application with responsive design',
            'courses': 'Educational content with hands-on examples',
            'ebooks': 'Comprehensive guide with practical insights',
            'templates': 'Ready-to-use template for rapid development',
            'tools': 'Utility tool for enhanced productivity'
        }
        
        return {
            'title': f"{title} - Live Demo",
            'arabicTitle': f"عرض مباشر - {title}",
            'preview': f"🚀 Explore {title} - {category_descriptions.get(category, 'Open source solution')}. Built with {repo.get('language', 'modern technologies')} and designed for production use.",
            'features': [
                {
                    'icon': '📂',
                    'title': 'Source Code',
                    'desc': 'Full access to well-documented, production-ready code'
                },
                {
                    'icon': '📖', 
                    'title': 'Documentation',
                    'desc': 'Comprehensive setup guides and API documentation'
                },
                {
                    'icon': '🔧',
                    'title': 'Customizable',
                    'desc': 'Easy to modify and extend for your specific needs'
                },
                {
                    'icon': '🚀',
                    'title': 'Deploy Ready',
                    'desc': 'Optimized for production deployment and scaling'
                }
            ]
        }
    
    def should_include_in_store(self, repo: Dict) -> bool:
        """Determine if repository should be included in store"""
        # Skip forks, archived repos, and repos without descriptions
        if (repo.get('fork', False) or 
            repo.get('archived', False) or 
            not repo.get('description')):
            return False
        
        # Skip very old repositories (over 2 years without updates)
        updated_at = repo.get('updated_at', '')
        if updated_at:
            try:
                update_date = datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%SZ")
                two_years_ago = datetime.now() - timedelta(days=730)
                if update_date < two_years_ago:
                    return False
            except:
                pass
        
        return True
    
    def scan_and_generate_store_entries(self) -> List[Dict]:
        """Main method to scan repositories and generate store entries"""
        print("🔍 Scanning GitHub repositories...")
        
        repositories = self.get_repositories()
        store_entries = []
        
        for repo in repositories:
            if self.should_include_in_store(repo):
                print(f"✅ Processing: {repo['name']}")
                store_entry = self.analyze_repository(repo)
                store_entries.append(store_entry)
            else:
                print(f"⏭️  Skipping: {repo['name']} (fork/archived/no description)")
        
        print(f"\n🎉 Generated {len(store_entries)} store entries")
        return store_entries
    
    def save_to_file(self, store_entries: List[Dict], filename: str = "brainsait_github_products.json"):
        """Save store entries to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(store_entries, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved to {filename}")

def main():
    """Main execution function"""
    # Get GitHub token from environment variable
    github_token = os.environ.get('GITHUB_TOKEN')
    
    if not github_token:
        print("❌ Error: GITHUB_TOKEN environment variable not set")
        print("Please set your GitHub personal access token:")
        print("export GITHUB_TOKEN='your_token_here'")
        return
    
    # Initialize scanner
    scanner = BrainSAITRepoScanner(github_token)
    
    # Scan repositories and generate store entries
    store_entries = scanner.scan_and_generate_store_entries()
    
    # Save to file
    scanner.save_to_file(store_entries)
    
    # Print summary
    print("\n📊 Summary:")
    categories = {}
    for entry in store_entries:
        cat = entry['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    for category, count in categories.items():
        print(f"  {category}: {count} products")
    
    print(f"\n🚀 Ready to integrate {len(store_entries)} products into BrainSAIT store!")

if __name__ == "__main__":
    main()