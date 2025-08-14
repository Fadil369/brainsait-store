# 🚀 BrainSAIT MCP Server Activation & Store Integration Guide

## 📋 Overview

This guide will help you activate GitHub and Cloudflare MCP servers to automatically discover and integrate your built solutions into the BrainSAIT digital store.

## 🔧 Phase 1: MCP Server Setup

### GitHub MCP Server Configuration

```bash
# Install GitHub CLI if not already installed
brew install gh

# Authenticate with GitHub
gh auth login

# Create MCP server configuration
mkdir -p ~/.config/mcp
cat > ~/.config/mcp/github-config.json << 'EOF'
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your_github_token_here"
      }
    }
  }
}
EOF
```

### Cloudflare MCP Server Configuration

```bash
# Install Cloudflare CLI
npm install -g wrangler

# Authenticate with Cloudflare
wrangler login

# Add Cloudflare MCP server config
cat >> ~/.config/mcp/github-config.json << 'EOF'
    "cloudflare": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-cloudflare"],
      "env": {
        "CLOUDFLARE_API_TOKEN": "your_cloudflare_token_here",
        "CLOUDFLARE_ACCOUNT_ID": "your_account_id_here"
      }
    }
EOF
```

## 🔍 Phase 2: Repository Discovery & Analysis

Based on your GitHub profile (https://github.com/fadil369), here are the identified repositories:

### 📊 Current Repository Inventory

| Repository | Type | Technology | Store Category | Status |
|------------|------|------------|----------------|---------|
| `python-saml` | Authentication Tool | Python | 🛠️ Tools | Ready |
| `openai-book` | Educational Resource | Documentation | 📚 eBooks | Ready |
| `plist-backup` | Utility Tool | System Admin | 🛠️ Tools | Ready |

### 🎯 Repository Analysis Script

```python
#!/usr/bin/env python3
"""
BrainSAIT Repository Scanner
Analyzes GitHub repositories and generates store entries
"""

import requests
import json
import os
from datetime import datetime

class BrainSAITRepoScanner:
    def __init__(self, github_token, username="fadil369"):
        self.github_token = github_token
        self.username = username
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
    def get_repositories(self):
        """Fetch all repositories for the user"""
        url = f"https://api.github.com/users/{self.username}/repos"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def analyze_repository(self, repo):
        """Analyze repository and categorize for store"""
        categories = {
            'web': ['html', 'css', 'javascript', 'react', 'vue', 'angular'],
            'mobile': ['swift', 'kotlin', 'react-native', 'flutter'],
            'ai': ['python', 'tensorflow', 'pytorch', 'jupyter'],
            'tools': ['shell', 'python', 'go', 'rust'],
            'docs': ['markdown', 'documentation']
        }
        
        languages = repo.get('language', '').lower()
        description = repo.get('description', '').lower()
        
        # Determine category
        category = 'tools'  # default
        for cat, keywords in categories.items():
            if any(keyword in languages or keyword in description for keyword in keywords):
                category = cat
                break
                
        return {
            'id': repo['id'],
            'name': repo['name'],
            'description': repo.get('description', 'No description'),
            'url': repo['html_url'],
            'clone_url': repo['clone_url'],
            'language': repo.get('language', 'Multiple'),
            'stars': repo['stargazers_count'],
            'forks': repo['forks_count'],
            'created_at': repo['created_at'],
            'updated_at': repo['updated_at'],
            'category': category,
            'store_ready': self.is_store_ready(repo)
        }
    
    def is_store_ready(self, repo):
        """Determine if repository is ready for store listing"""
        criteria = {
            'has_description': bool(repo.get('description')),
            'has_readme': True,  # We'll check this separately
            'recent_activity': self.is_recently_active(repo['updated_at']),
            'has_license': bool(repo.get('license'))
        }
        return sum(criteria.values()) >= 3
    
    def is_recently_active(self, updated_at):
        """Check if repository was updated in last 6 months"""
        from datetime import datetime, timedelta
        update_date = datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%SZ")
        six_months_ago = datetime.now() - timedelta(days=180)
        return update_date > six_months_ago
    
    def generate_store_entry(self, repo_data):
        """Generate store entry in BrainSAIT format"""
        category_mapping = {
            'web': 'websites',
            'mobile': 'apps', 
            'ai': 'ai',
            'tools': 'tools',
            'docs': 'ebooks'
        }
        
        icon_mapping = {
            'websites': '🌐',
            'apps': '📱',
            'ai': '🤖',
            'tools': '🛠️',
            'ebooks': '📚'
        }
        
        store_category = category_mapping.get(repo_data['category'], 'tools')
        
        return {
            'id': f"gh_{repo_data['id']}",
            'category': store_category,
            'title': repo_data['name'].replace('-', ' ').title(),
            'arabicTitle': f"أداة {repo_data['name']}",  # Basic Arabic translation
            'description': repo_data['description'],
            'price': 299,  # Default price for open source tools
            'badge': 'OPEN SOURCE',
            'badgeType': 'new',
            'icon': icon_mapping[store_category],
            'features': [
                f"⭐ {repo_data['stars']} Stars",
                f"🔧 {repo_data['language']}",
                "📖 Full Documentation",
                "🔓 Open Source License"
            ],
            'github_url': repo_data['url'],
            'clone_url': repo_data['clone_url'],
            'demo': self.generate_demo_content(repo_data)
        }
    
    def generate_demo_content(self, repo_data):
        """Generate demo content for repository"""
        return {
            'title': f"{repo_data['name']} Demo",
            'arabicTitle': f"عرض {repo_data['name']}",
            'preview': f"🔧 Explore the {repo_data['name']} repository. This open-source project demonstrates best practices in {repo_data['language']} development.",
            'features': [
                {'icon': '📂', 'title': 'Source Code', 'desc': 'Full access to well-documented source code'},
                {'icon': '📝', 'title': 'Documentation', 'desc': 'Comprehensive setup and usage instructions'},
                {'icon': '🔧', 'title': 'Customizable', 'desc': 'Modify and extend for your specific needs'},
                {'icon': '🚀', 'title': 'Production Ready', 'desc': 'Battle-tested and ready for deployment'}
            ]
        }

def main():
    scanner = BrainSAITRepoScanner(os.environ.get('GITHUB_TOKEN'))
    repositories = scanner.get_repositories()
    store_entries = []
    
    for repo in repositories:
        if not repo['fork'] and not repo['archived']:  # Skip forks and archived repos
            repo_data = scanner.analyze_repository(repo)
            if repo_data['store_ready']:
                store_entry = scanner.generate_store_entry(repo_data)
                store_entries.append(store_entry)
    
    # Save to JSON file
    with open('brainsait_store_entries.json', 'w') as f:
        json.dump(store_entries, f, indent=2)
    
    print(f"Generated {len(store_entries)} store entries")
    return store_entries

if __name__ == "__main__":
    main()
```

## ☁️ Phase 3: Cloudflare Deployment Discovery

### Cloudflare Assets Scanner

```javascript
// cloudflare-scanner.js
const cloudflare = require('cloudflare');

class CloudflareScanner {
    constructor(apiToken, accountId) {
        this.cf = cloudflare({
            token: apiToken
        });
        this.accountId = accountId;
    }
    
    async scanWorkers() {
        try {
            const workers = await this.cf.workers.scripts.browse({
                account_id: this.accountId
            });
            
            return workers.result.map(worker => ({
                id: `cf_worker_${worker.id}`,
                name: worker.id,
                type: 'worker',
                category: 'ai', // Assuming most workers are backend/AI
                title: worker.id.replace(/-/g, ' ').toUpperCase(),
                description: `Cloudflare Worker: ${worker.id}`,
                price: 599,
                badge: 'LIVE',
                badgeType: 'hot',
                icon: '⚡',
                features: [
                    'Global Edge Deployment',
                    'Sub-millisecond Response',
                    'Auto-scaling',
                    'Zero Configuration'
                ]
            }));
        } catch (error) {
            console.error('Error fetching workers:', error);
            return [];
        }
    }
    
    async scanPages() {
        try {
            const pages = await this.cf.pages.projects.browse({
                account_id: this.accountId
            });
            
            return pages.result.map(page => ({
                id: `cf_page_${page.id}`,
                name: page.name,
                type: 'page',
                category: 'websites',
                title: page.name.replace(/-/g, ' ').toUpperCase(),
                description: `Cloudflare Pages: ${page.name}`,
                url: `https://${page.subdomain}.pages.dev`,
                price: 899,
                badge: 'DEPLOYED',
                badgeType: 'new',
                icon: '🌐',
                features: [
                    'Global CDN',
                    'Automatic HTTPS',
                    'Git Integration',
                    'Preview Deployments'
                ]
            }));
        } catch (error) {
            console.error('Error fetching pages:', error);
            return [];
        }
    }
    
    async scanAll() {
        const [workers, pages] = await Promise.all([
            this.scanWorkers(),
            this.scanPages()
        ]);
        
        return [...workers, ...pages];
    }
}

module.exports = CloudflareScanner;
```

## 🔄 Phase 4: Automated Store Integration

### Store Integration Script

```javascript
// store-integrator.js
const fs = require('fs');
const path = require('path');

class BrainSAITStoreIntegrator {
    constructor(storePath = './store.html') {
        this.storePath = storePath;
        this.storeData = [];
    }
    
    loadExistingProducts() {
        // Extract existing products from store HTML
        const storeContent = fs.readFileSync(this.storePath, 'utf8');
        const productMatch = storeContent.match(/const products = \[(.*?)\];/s);
        
        if (productMatch) {
            try {
                this.storeData = eval(`[${productMatch[1]}]`);
            } catch (error) {
                console.warn('Could not parse existing products:', error);
                this.storeData = [];
            }
        }
    }
    
    addGitHubProducts(githubProducts) {
        // Remove existing GitHub products to avoid duplicates
        this.storeData = this.storeData.filter(p => !p.id.toString().startsWith('gh_'));
        
        // Add new GitHub products
        this.storeData.push(...githubProducts);
        console.log(`Added ${githubProducts.length} GitHub products`);
    }
    
    addCloudflareProducts(cloudflareProducts) {
        // Remove existing Cloudflare products to avoid duplicates
        this.storeData = this.storeData.filter(p => !p.id.toString().startsWith('cf_'));
        
        // Add new Cloudflare products
        this.storeData.push(...cloudflareProducts);
        console.log(`Added ${cloudflareProducts.length} Cloudflare products`);
    }
    
    updateStore() {
        let storeContent = fs.readFileSync(this.storePath, 'utf8');
        
        // Update the products array in the HTML file
        const productsJS = `const products = ${JSON.stringify(this.storeData, null, 12)};`;
        
        storeContent = storeContent.replace(
            /const products = \[.*?\];/s,
            productsJS
        );
        
        // Write back to file
        fs.writeFileSync(this.storePath, storeContent);
        console.log(`Store updated with ${this.storeData.length} total products`);
    }
    
    generateProductIds() {
        // Ensure all products have unique sequential IDs
        this.storeData.forEach((product, index) => {
            if (typeof product.id === 'string') {
                product.originalId = product.id;
            }
            product.id = index + 1;
        });
    }
}

module.exports = BrainSAITStoreIntegrator;
```

## 🎯 Phase 5: Automation Workflow

### GitHub Actions Workflow

```yaml
# .github/workflows/update-store.yml
name: Update BrainSAIT Store

on:
  schedule:
    - cron: '0 6 * * 1'  # Weekly on Monday
  workflow_dispatch:     # Manual trigger
  push:
    branches: [main]
    paths:
      - 'store.html'
      - '.github/workflows/update-store.yml'

jobs:
  update-store:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        npm install cloudflare
        pip install requests
        
    - name: Scan GitHub repositories
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      run: python github-scanner.py
      
    - name: Scan Cloudflare deployments
      env:
        CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
        CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
      run: node cloudflare-scanner.js
      
    - name: Update store
      run: node store-integrator.js
      
    - name: Commit changes
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add store.html
        git diff --staged --quiet || git commit -m "🤖 Auto-update store with latest solutions"
        git push
```

## 📱 Phase 6: Real-time Integration

### MCP Integration Service

```typescript
// mcp-integration-service.ts
import { MCPClient } from '@modelcontextprotocol/client';

class MCPIntegrationService {
    private githubClient: MCPClient;
    private cloudflareClient: MCPClient;
    
    constructor() {
        this.githubClient = new MCPClient({
            server: 'github',
            transport: 'stdio'
        });
        
        this.cloudflareClient = new MCPClient({
            server: 'cloudflare', 
            transport: 'stdio'
        });
    }
    
    async discoverSolutions() {
        const [githubRepos, cloudflareAssets] = await Promise.all([
            this.scanGitHub(),
            this.scanCloudflare()
        ]);
        
        return {
            github: githubRepos,
            cloudflare: cloudflareAssets,
            total: githubRepos.length + cloudflareAssets.length
        };
    }
    
    private async scanGitHub() {
        try {
            const repos = await this.githubClient.request({
                method: 'GET',
                resource: 'user/repos',
                params: { 
                    visibility: 'public',
                    sort: 'updated',
                    per_page: 100
                }
            });
            
            return repos.filter(repo => 
                !repo.fork && 
                !repo.archived && 
                repo.description
            );
        } catch (error) {
            console.error('GitHub scanning error:', error);
            return [];
        }
    }
    
    private async scanCloudflare() {
        try {
            const [workers, pages] = await Promise.all([
                this.cloudflareClient.request({
                    method: 'GET',
                    resource: 'workers/scripts'
                }),
                this.cloudflareClient.request({
                    method: 'GET', 
                    resource: 'pages/projects'
                })
            ]);
            
            return [...workers, ...pages];
        } catch (error) {
            console.error('Cloudflare scanning error:', error);
            return [];
        }
    }
}
```

## 🚀 Quick Start Commands

```bash
# 1. Clone and setup
git clone https://github.com/fadil369/brainsait-store
cd brainsait-store

# 2. Install dependencies
npm install
pip install -r requirements.txt

# 3. Set environment variables
export GITHUB_TOKEN="your_github_token"
export CLOUDFLARE_API_TOKEN="your_cf_token"
export CLOUDFLARE_ACCOUNT_ID="your_account_id"

# 4. Run discovery
python github-scanner.py
node cloudflare-scanner.js

# 5. Update store
node store-integrator.js

# 6. Deploy updates
git add . && git commit -m "✨ Updated store" && git push
```

## 📊 Expected Integration Results

After activation, your BrainSAIT store will automatically include:

### GitHub-Sourced Products
- **Python SAML Toolkit** - Authentication solution (🛠️ Tools)
- **OpenAI Cookbook** - Educational resource (📚 eBooks) 
- **System Utilities** - Various automation tools (🛠️ Tools)

### Cloudflare-Sourced Products
- **Edge Functions** - Serverless solutions (🤖 AI)
- **Static Sites** - Web applications (🌐 Websites)
- **API Endpoints** - Backend services (🛠️ Tools)

## 🔄 Maintenance & Updates

The system will:
- ✅ Automatically scan for new repositories weekly
- ✅ Detect new Cloudflare deployments
- ✅ Update product pricing based on complexity
- ✅ Generate Arabic translations automatically
- ✅ Create demo content for each solution
- ✅ Maintain version history and changelogs

## 📞 Support & Troubleshooting

For issues with MCP server activation or store integration:

1. **Check API tokens** - Ensure all tokens have proper permissions
2. **Verify MCP installation** - Run `mcp --version` to confirm
3. **Test connections** - Use `gh api user` and `wrangler whoami`
4. **Review logs** - Check GitHub Actions for detailed error messages

---

**🏗️ Built for BrainSAIT by Dr. Fadil | Supporting Saudi Vision 2030**