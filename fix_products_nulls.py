#!/usr/bin/env python3
"""
Fix null values in products.ts file for TypeScript compatibility
"""

import re

def fix_products_file():
    """Fix null values in products.ts file"""
    file_path = "frontend/src/data/products.ts"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace null values with undefined for optional fields
        content = re.sub(r'"originalPrice": null', '"originalPrice": undefined', content)
        content = re.sub(r'"language": null', '"language": undefined', content)
        content = re.sub(r'"arabicTitle": null', '"arabicTitle": undefined', content)
        content = re.sub(r'"githubUrl": null', '"githubUrl": undefined', content)
        content = re.sub(r'"liveUrl": null', '"liveUrl": undefined', content)
        content = re.sub(r'"clone_url": null', '"clone_url": undefined', content)
        content = re.sub(r'"github_url": null', '"github_url": undefined', content)
        content = re.sub(r'"live_url": null', '"live_url": undefined', content)
        
        # Remove any remaining null values in metadata
        content = re.sub(r':\s*null,?', ': undefined,', content)
        content = re.sub(r':\s*null}', ': undefined}', content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed null values in products.ts")
        
    except Exception as e:
        print(f"❌ Error fixing products file: {e}")

if __name__ == "__main__":
    fix_products_file()