#!/bin/bash

# Test script to validate all wrangler configurations
echo "🧪 Testing BrainSAIT Store Wrangler Configurations"
echo "================================================="

# Test root wrangler.toml
echo ""
echo "1️⃣ Testing root wrangler.toml..."
if node scripts/validate-wrangler.js; then
    echo "✅ Root wrangler.toml is valid"
else
    echo "❌ Root wrangler.toml validation failed"
    exit 1
fi

# Test frontend wrangler.toml
echo ""
echo "2️⃣ Testing frontend wrangler.toml..."
cd frontend
if npx wrangler deploy --dry-run 2>&1 | grep -q "ParseError\|Can't redefine"; then
    echo "❌ Frontend wrangler.toml has parsing errors"
    exit 1
else
    echo "✅ Frontend wrangler.toml syntax is valid"
fi

cd ..

# Check for duplicate tables with AWK
echo ""
echo "3️⃣ Checking for duplicate TOML table definitions..."

# Check root wrangler.toml for duplicate single tables (not arrays)
if awk '/^\[env\..*\]/ && !/^\[\[.*\]\]/ { if (seen[$0]++) { print "ERROR: Duplicate table definition: " $0; exit 1 } }' wrangler.toml; then
    echo "✅ No duplicate tables in root wrangler.toml"
else
    echo "❌ Found duplicate tables in root wrangler.toml"
    exit 1
fi

# Check frontend wrangler.toml for duplicate single tables (not arrays)
if awk '/^\[env\..*\]/ && !/^\[\[.*\]\]/ { if (seen[$0]++) { print "ERROR: Duplicate table definition: " $0; exit 1 } }' frontend/wrangler.toml; then
    echo "✅ No duplicate tables in frontend/wrangler.toml"
else
    echo "❌ Found duplicate tables in frontend/wrangler.toml"
    exit 1
fi

echo ""
echo "🎉 All wrangler configurations are valid!"
echo "Ready for Cloudflare deployment!"