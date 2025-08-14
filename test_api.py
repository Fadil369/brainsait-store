#!/usr/bin/env python3
"""
Simple test API server to verify Cloudflare Worker integration
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
import os

app = FastAPI(
    title="BrainSAIT Store Backend",
    version="1.0.0",
    description="Test API for BrainSAIT Store integration"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Backend health check"""
    return {
        "status": "healthy",
        "service": "brainsait-store-backend",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/")
async def root(request: Request):
    """Root endpoint"""
    tenant_id = request.headers.get("X-Tenant-ID", "default")
    
    return {
        "message": "BrainSAIT Store Backend API",
        "version": "1.0.0",
        "tenant_id": tenant_id,
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "health": "/health",
            "store": "/api/v1/store",
            "payments": "/api/v1/payments",
            "oid": "/api/v1/oid",
            "docs": "/docs"
        }
    }

@app.get("/api/v1/info")
async def api_info(request: Request):
    """API information"""
    tenant_id = request.headers.get("X-Tenant-ID")
    
    return {
        "api_version": "v1",
        "tenant_id": tenant_id,
        "features": {
            "multi_tenant": True,
            "bilingual": True,
            "languages": ["en", "ar"],
            "payment_methods": ["stripe", "mada", "stc_pay"],
            "zatca_compliant": True,
            "oid_integration": True
        },
        "status": "operational"
    }

@app.get("/api/v1/store/products")
async def get_products(request: Request):
    """Mock store products endpoint"""
    tenant_id = request.headers.get("X-Tenant-ID")
    
    # Sample products from our HTML prototype
    products = [
        {
            "id": "1",
            "name": "AI Business Assistant",
            "name_ar": "مساعد الأعمال الذكي",
            "description": "Advanced AI-powered business automation and analytics platform",
            "price_sar": 1499,
            "category": "ai",
            "status": "active",
            "features": ["GPT-4 Integration", "Multi-language Support", "Custom Training", "API Access"]
        },
        {
            "id": "2", 
            "name": "Digital Marketing Mastery",
            "name_ar": "إتقان التسويق الرقمي",
            "description": "Complete digital marketing course with real-world case studies",
            "price_sar": 2999,
            "category": "courses",
            "status": "active",
            "features": ["60+ Hours Content", "Certificate", "Live Sessions", "1-on-1 Mentoring"]
        }
    ]
    
    return {
        "products": products,
        "total": len(products),
        "tenant_id": tenant_id
    }

@app.get("/api/v1/payments/methods")
async def get_payment_methods():
    """Payment methods endpoint"""
    return {
        "methods": {
            "stripe": {
                "name": "Credit/Debit Cards",
                "name_ar": "البطاقات الائتمانية/المدينة",
                "enabled": True,
                "currencies": ["SAR", "USD"]
            },
            "mada": {
                "name": "Mada Cards", 
                "name_ar": "بطاقات مدى",
                "enabled": True,
                "currencies": ["SAR"]
            },
            "stc_pay": {
                "name": "STC Pay",
                "name_ar": "STC Pay", 
                "enabled": True,
                "currencies": ["SAR"]
            }
        }
    }

@app.get("/api/v1/oid/tree")
async def get_oid_tree():
    """OID tree endpoint"""
    return {
        "nodes": [
            {
                "id": "1",
                "oid_path": "1.3.6.1.4.1.61026.1.2.1",
                "name": "NPHIES Integration",
                "name_ar": "تكامل نظام نفيس",
                "node_type": "healthcare_system",
                "status": "active"
            }
        ],
        "total_nodes": 1,
        "active_nodes": 1
    }

if __name__ == "__main__":
    uvicorn.run(
        "test_api:app",
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )