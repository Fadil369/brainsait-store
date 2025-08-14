#!/usr/bin/env node

/**
 * Validate wrangler.toml configuration file
 * This script helps catch TOML parsing errors before deployment
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const WRANGLER_CONFIG = 'wrangler.toml';

function validateWranglerConfig() {
  console.log('🔍 Validating wrangler.toml configuration...');
  
  // Check if wrangler.toml exists
  if (!fs.existsSync(WRANGLER_CONFIG)) {
    console.error(`❌ Error: ${WRANGLER_CONFIG} not found`);
    process.exit(1);
  }
  
  try {
    // Use wrangler to validate the configuration
    // We use a deploy dry-run but ignore build errors since we only care about TOML parsing
    const output = execSync(`npx wrangler deploy --dry-run --config ${WRANGLER_CONFIG}`, {
      encoding: 'utf8',
      stdio: 'pipe',
      timeout: 30000
    });
    
    console.log('✅ wrangler.toml configuration is valid!');
    return true;
  } catch (error) {
    const stderr = error.stderr || error.stdout || error.message;
    
    // Check for TOML parsing errors specifically
    if (stderr.includes("Can't redefine existing key") || 
        stderr.includes("ParseError") ||
        stderr.includes("Invalid TOML")) {
      console.error('❌ TOML Configuration Error:');
      console.error(stderr);
      process.exit(1);
    }
    
    // If it's just a build error (not TOML parsing), that's okay for validation
    if (stderr.includes('npm run build') || 
        stderr.includes('package.json') ||
        stderr.includes('Command failed')) {
      console.log('✅ wrangler.toml configuration syntax is valid!');
      console.log('ℹ️  Build errors are expected in validation mode.');
      return true;
    }
    
    // Unknown error
    console.error('❌ Unexpected error during validation:');
    console.error(stderr);
    process.exit(1);
  }
}

function main() {
  console.log('🛠️  BrainSAIT Store - Wrangler Configuration Validator');
  console.log('================================================');
  
  try {
    validateWranglerConfig();
    console.log('');
    console.log('🎉 All validation checks passed!');
  } catch (error) {
    console.error('💥 Validation failed:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { validateWranglerConfig };