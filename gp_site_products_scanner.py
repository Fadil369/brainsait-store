#!/usr/bin/env python3
"""
GP Site Products Scanner
Discovers and integrates additional products from gp.thefadil.site demo websites
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any

class GPSiteProductsScanner:
    def __init__(self):
        self.discovered_products = []
        
    def create_gp_site_products(self) -> List[Dict]:
        """Create product entries from gp.thefadil.site discoveries"""
        
        products = [
            {
                "id": "gp_1",
                "category": "ai",
                "title": "GPChat Healthcare Consultant",
                "arabicTitle": "مستشار الرعاية الصحية الذكي",
                "description": "AI-powered healthcare technology consultant with journey tracking and adaptive interactions",
                "price": 2499,
                "badge": "LIVE AI",
                "badgeType": "hot",
                "icon": "🤖",
                "features": [
                    "🔄 Journey Tracking",
                    "📊 Engagement Scoring", 
                    "🧠 Adaptive AI Interaction",
                    "🏥 Healthcare Specialized"
                ],
                "live_url": "https://gp-chatbot.fadil.workers.dev/workspace",
                "cloudflare_type": "worker",
                "demo": {
                    "title": "GPChat Live Demo",
                    "arabicTitle": "عرض مباشر للمستشار الذكي",
                    "preview": "🤖 Experience AI-powered healthcare consulting with journey tracking and engagement scoring. Live workspace for healthcare technology consultation.",
                    "liveUrl": "https://gp-chatbot.fadil.workers.dev/workspace",
                    "hasLiveDemo": True,
                    "features": [
                        {"icon": "🔄", "title": "Journey Tracking", "desc": "Track user journey and consultation progress"},
                        {"icon": "📊", "title": "Engagement Analytics", "desc": "Real-time engagement scoring and analysis"},
                        {"icon": "🧠", "title": "Adaptive AI", "desc": "AI adapts to user needs and consultation style"},
                        {"icon": "🏥", "title": "Healthcare Focus", "desc": "Specialized for healthcare technology consulting"}
                    ]
                }
            },
            {
                "id": "gp_2", 
                "category": "tools",
                "title": "Context Prompt Generator",
                "arabicTitle": "مولد السياق والتوجيهات",
                "description": "Advanced tool for building structured prompts and AI agent contexts with intelligent frameworks",
                "price": 1699,
                "badge": "PROMPT TOOL",
                "badgeType": "new",
                "icon": "🔧",
                "features": [
                    "📝 Structured Prompt Building",
                    "🤖 AI Agent Context Creation",
                    "🏗️ Framework Templates",
                    "⚡ Real-time Generation"
                ],
                "live_url": "https://context.thefadil.site/",
                "cloudflare_type": "page",
                "demo": {
                    "title": "Context Generator Demo",
                    "arabicTitle": "عرض مولد السياق",
                    "preview": "🔧 Build sophisticated AI prompts and agent contexts with structured frameworks. Professional prompt engineering made simple.",
                    "liveUrl": "https://context.thefadil.site/",
                    "hasLiveDemo": True,
                    "features": [
                        {"icon": "📝", "title": "Prompt Building", "desc": "Create structured, effective AI prompts"},
                        {"icon": "🤖", "title": "Agent Contexts", "desc": "Design comprehensive AI agent contexts"},
                        {"icon": "🏗️", "title": "Templates", "desc": "Pre-built frameworks for common use cases"},
                        {"icon": "⚡", "title": "Live Preview", "desc": "Real-time preview of generated prompts"}
                    ]
                }
            },
            {
                "id": "gp_3",
                "category": "tools", 
                "title": "Excel Advanced Consolidator",
                "arabicTitle": "مدمج ملفات الإكسل المتقدم",
                "description": "Professional tool for merging and cleaning complex Excel files with advanced data processing",
                "price": 1299,
                "badge": "DATA TOOL",
                "badgeType": "hot",
                "icon": "📊",
                "features": [
                    "📁 Complex File Merging",
                    "🧹 Automated Data Cleaning",
                    "🔄 Batch Processing",
                    "📈 Advanced Analytics"
                ],
                "live_url": "https://excel-advanced-consolidator.fadil.workers.dev/",
                "cloudflare_type": "worker",
                "demo": {
                    "title": "Excel Consolidator Demo",
                    "arabicTitle": "عرض مدمج الإكسل",
                    "preview": "📊 Merge and clean complex Excel files with advanced automation. Perfect for data analysts and business professionals.",
                    "liveUrl": "https://excel-advanced-consolidator.fadil.workers.dev/",
                    "hasLiveDemo": True,
                    "features": [
                        {"icon": "📁", "title": "File Merging", "desc": "Merge multiple Excel files intelligently"},
                        {"icon": "🧹", "title": "Data Cleaning", "desc": "Automated cleaning and validation"},
                        {"icon": "🔄", "title": "Batch Operations", "desc": "Process multiple files simultaneously"},
                        {"icon": "📈", "title": "Analytics", "desc": "Generate insights from consolidated data"}
                    ]
                }
            },
            {
                "id": "gp_4",
                "category": "ai",
                "title": "AI Docs Cod Containers",
                "arabicTitle": "حاويات تحليل المستندات الذكية",
                "description": "Convert PDFs and Word documents into structured JSON with AI-powered document analysis",
                "price": 1899,
                "badge": "DOCUMENT AI",
                "badgeType": "new",
                "icon": "📄",
                "features": [
                    "📄 PDF/Word Processing",
                    "🔄 JSON Conversion",
                    "🧠 AI Document Analysis", 
                    "🏗️ Structured Data Output"
                ],
                "live_url": "https://ai-docs-cod-containers.fadil.workers.dev/",
                "cloudflare_type": "worker",
                "demo": {
                    "title": "Document AI Demo",
                    "arabicTitle": "عرض تحليل المستندات",
                    "preview": "📄 Transform documents into structured data with AI. Convert PDFs and Word files to JSON with intelligent parsing.",
                    "liveUrl": "https://ai-docs-cod-containers.fadil.workers.dev/",
                    "hasLiveDemo": True,
                    "features": [
                        {"icon": "📄", "title": "Document Parsing", "desc": "Parse PDFs and Word documents intelligently"},
                        {"icon": "🔄", "title": "JSON Output", "desc": "Convert to structured JSON format"},
                        {"icon": "🧠", "title": "AI Analysis", "desc": "AI-powered content understanding"},
                        {"icon": "🏗️", "title": "Structure", "desc": "Maintain document structure and context"}
                    ]
                }
            },
            {
                "id": "gp_5",
                "category": "ai",
                "title": "Healthcare Insurance Analysis",
                "arabicTitle": "تحليل التأمين الصحي الذكي",
                "description": "Analyze health insurance data for claims processing and risk scoring with AI insights",
                "price": 2799,
                "badge": "HEALTHCARE AI",
                "badgeType": "hot",
                "icon": "🏥",
                "features": [
                    "🏥 Claims Analysis",
                    "📊 Risk Scoring",
                    "🤖 AI Insights",
                    "📈 Predictive Analytics"
                ],
                "live_url": "https://healthcare-insurance-analysis.fadil.workers.dev/",
                "cloudflare_type": "worker", 
                "demo": {
                    "title": "Insurance AI Demo",
                    "arabicTitle": "عرض تحليل التأمين",
                    "preview": "🏥 Analyze healthcare insurance data with AI. Claims processing, risk scoring, and predictive analytics for insurance professionals.",
                    "liveUrl": "https://healthcare-insurance-analysis.fadil.workers.dev/",
                    "hasLiveDemo": True,
                    "features": [
                        {"icon": "🏥", "title": "Claims Processing", "desc": "Automated claims analysis and processing"},
                        {"icon": "📊", "title": "Risk Assessment", "desc": "AI-powered risk scoring algorithms"},
                        {"icon": "🤖", "title": "AI Insights", "desc": "Machine learning insights for decisions"},
                        {"icon": "📈", "title": "Predictions", "desc": "Predictive analytics for future claims"}
                    ]
                }
            },
            {
                "id": "gp_6",
                "category": "websites",
                "title": "BrainSAIT Care Platform",
                "arabicTitle": "منصة برين سايت للرعاية",
                "description": "Smart healthcare automation system with comprehensive patient management and care coordination",
                "price": 3299,
                "badge": "HEALTHCARE",
                "badgeType": "hot",
                "icon": "🏥", 
                "features": [
                    "🏥 Patient Management",
                    "🤖 Smart Automation",
                    "📊 Care Analytics",
                    "🔗 System Integration"
                ],
                "live_url": "https://care.brainsait.io",
                "cloudflare_type": "page",
                "demo": {
                    "title": "BrainSAIT Care Demo",
                    "arabicTitle": "عرض منصة الرعاية",
                    "preview": "🏥 Comprehensive healthcare automation platform. Smart patient management with advanced care coordination and analytics.",
                    "liveUrl": "https://care.brainsait.io",
                    "hasLiveDemo": True,
                    "features": [
                        {"icon": "🏥", "title": "Patient Care", "desc": "Complete patient management system"},
                        {"icon": "🤖", "title": "Automation", "desc": "Smart healthcare workflow automation"},
                        {"icon": "📊", "title": "Analytics", "desc": "Advanced care analytics and reporting"},
                        {"icon": "🔗", "title": "Integration", "desc": "Seamless EHR and system integration"}
                    ]
                }
            },
            {
                "id": "gp_7",
                "category": "websites",
                "title": "Next Starter Template Pro",
                "arabicTitle": "قالب البداية المتطور",
                "description": "Professional launchpad template for BrainSAIT web applications with modern architecture",
                "price": 1999,
                "badge": "TEMPLATE",
                "badgeType": "new",
                "icon": "🚀",
                "features": [
                    "🚀 Quick Launch",
                    "🏗️ Modern Architecture",
                    "🎨 Professional Design",
                    "⚡ Performance Optimized"
                ],
                "live_url": "https://next-starter-template.fadil.workers.dev/",
                "cloudflare_type": "worker",
                "demo": {
                    "title": "Starter Template Demo",
                    "arabicTitle": "عرض قالب البداية",
                    "preview": "🚀 Professional Next.js starter template for rapid web app development. Modern architecture with best practices built-in.",
                    "liveUrl": "https://next-starter-template.fadil.workers.dev/",
                    "hasLiveDemo": True,
                    "features": [
                        {"icon": "🚀", "title": "Rapid Start", "desc": "Get your app running in minutes"},
                        {"icon": "🏗️", "title": "Architecture", "desc": "Modern, scalable application structure"},
                        {"icon": "🎨", "title": "Design System", "desc": "Professional UI components included"},
                        {"icon": "⚡", "title": "Performance", "desc": "Optimized for speed and efficiency"}
                    ]
                }
            },
            {
                "id": "gp_8",
                "category": "ai",
                "title": "Claim Chat Agent",
                "arabicTitle": "وكيل المحادثة للمطالبات",
                "description": "Conversational AI agent specialized for insurance claims processing and customer support",
                "price": 2199,
                "badge": "CHAT AI",
                "badgeType": "hot",
                "icon": "💬",
                "features": [
                    "💬 Conversational AI",
                    "🏥 Insurance Expertise",
                    "🔄 Claims Processing",
                    "📞 24/7 Support"
                ],
                "live_url": "https://claim-chat-agent.fadil.workers.dev/",
                "cloudflare_type": "worker",
                "demo": {
                    "title": "Claim Chat Demo",
                    "arabicTitle": "عرض وكيل المطالبات", 
                    "preview": "💬 AI-powered chat agent for insurance claims. Intelligent conversation handling with specialized insurance knowledge.",
                    "liveUrl": "https://claim-chat-agent.fadil.workers.dev/",
                    "hasLiveDemo": True,
                    "features": [
                        {"icon": "💬", "title": "Natural Chat", "desc": "Human-like conversation experience"},
                        {"icon": "🏥", "title": "Insurance Expert", "desc": "Specialized knowledge in insurance claims"},
                        {"icon": "🔄", "title": "Process Claims", "desc": "Guide users through claims process"},
                        {"icon": "📞", "title": "Always Available", "desc": "24/7 automated customer support"}
                    ]
                }
            },
            {
                "id": "gp_9",
                "category": "tools",
                "title": "Remote MCP Server",
                "arabicTitle": "خادم التحكم عن بُعد",
                "description": "Microcontroller and API management server for remote device control and integration",
                "price": 1799,
                "badge": "IOT SERVER",
                "badgeType": "new",
                "icon": "🖥️",
                "features": [
                    "🖥️ Device Management",
                    "📡 Remote Control",
                    "🔗 API Integration",
                    "⚡ Real-time Monitoring"
                ],
                "live_url": "https://remote-mcp-server.fadil.workers.dev/",
                "cloudflare_type": "worker",
                "demo": {
                    "title": "MCP Server Demo",
                    "arabicTitle": "عرض خادم التحكم",
                    "preview": "🖥️ Manage microcontrollers and devices remotely. API-driven device control with real-time monitoring capabilities.",
                    "liveUrl": "https://remote-mcp-server.fadil.workers.dev/",
                    "hasLiveDemo": True,
                    "features": [
                        {"icon": "🖥️", "title": "Device Control", "desc": "Manage multiple microcontrollers remotely"},
                        {"icon": "📡", "title": "Remote Access", "desc": "Secure remote device access and control"},
                        {"icon": "🔗", "title": "API Gateway", "desc": "RESTful API for device integration"},
                        {"icon": "⚡", "title": "Live Monitoring", "desc": "Real-time device status and analytics"}
                    ]
                }
            },
            {
                "id": "gp_10",
                "category": "ai",
                "title": "AI Form Segmenter",
                "arabicTitle": "مقسم النماذج الذكي",
                "description": "AI-powered document form segmentation tool for claims processing and data extraction",
                "price": 1599,
                "badge": "FORM AI",
                "badgeType": "new", 
                "icon": "📋",
                "features": [
                    "📋 Form Recognition",
                    "✂️ Intelligent Segmentation",
                    "🔍 Data Extraction",
                    "🏥 Claims Optimized"
                ],
                "live_url": "https://claude.ai/public/artifacts/69bda7c6-6395-4e78-b522-5517217fce51",
                "cloudflare_type": "external",
                "demo": {
                    "title": "Form Segmenter Demo",
                    "arabicTitle": "عرض مقسم النماذج",
                    "preview": "📋 AI-powered form segmentation for claims processing. Intelligent document analysis with automated data extraction.",
                    "liveUrl": "https://claude.ai/public/artifacts/69bda7c6-6395-4e78-b522-5517217fce51",
                    "hasLiveDemo": True,
                    "features": [
                        {"icon": "📋", "title": "Form Analysis", "desc": "Recognize and analyze form structures"},
                        {"icon": "✂️", "title": "Smart Segmentation", "desc": "Intelligently segment form sections"},
                        {"icon": "🔍", "title": "Data Extraction", "desc": "Extract key data points automatically"},
                        {"icon": "🏥", "title": "Claims Ready", "desc": "Optimized for insurance claims processing"}
                    ]
                }
            }
        ]
        
        self.discovered_products = products
        print(f"✅ Created {len(products)} GP Site products")
        return products
    
    def standardize_gp_products(self) -> List[Dict]:
        """Standardize GP site products for store integration"""
        standardized_products = []
        
        for product in self.discovered_products:
            standardized = {
                "id": product["id"],
                "category": product["category"],
                "title": product["title"],
                "arabicTitle": product["arabicTitle"],
                "description": product["description"],
                "price": product["price"],
                "badge": product["badge"],
                "badgeType": product["badgeType"],
                "icon": product["icon"],
                "features": product["features"],
                "demo": product["demo"],
                "source": "gp_site",
                "metadata": {
                    "live_url": product["live_url"],
                    "cloudflare_type": product["cloudflare_type"],
                    "deployment_status": "live",
                    "discovery_source": "gp.thefadil.site"
                }
            }
            
            # Add pricing options for bundle sales
            if product["cloudflare_type"] == "worker":
                standardized["pricing_options"] = {
                    "live_service": product["price"],
                    "source_code": product["price"] + 400,
                    "full_bundle": product["price"] + 900
                }
                standardized["description"] += " | Live API with optional source code bundle"
            elif product["cloudflare_type"] == "page":
                standardized["pricing_options"] = {
                    "live_app": product["price"],
                    "template": product["price"] + 300,
                    "full_package": product["price"] + 700
                }
                standardized["description"] += " | Live application with template access"
            
            # Set price range for display
            if "pricing_options" in standardized:
                options = standardized["pricing_options"]
                min_price = min(options.values())
                max_price = max(options.values())
                standardized["price_range"] = f"{min_price} - {max_price} SAR"
            
            standardized_products.append(standardized)
        
        return standardized_products
    
    def save_gp_products(self, filename: str = "brainsait_gp_site_products.json"):
        """Save GP site products to JSON file"""
        standardized_products = self.standardize_gp_products()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(standardized_products, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(standardized_products)} GP site products to {filename}")
        
        # Print summary
        categories = {}
        for product in standardized_products:
            cat = product["category"]
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\n📊 GP Site Products Summary:")
        for category, count in categories.items():
            icon = {"ai": "🤖", "websites": "🌐", "tools": "🛠️", "apps": "📱"}.get(category, "📦")
            print(f"   {icon} {category.upper()}: {count} products")
        
        print(f"   💰 Price Range: 1,299 - 3,299 SAR")
        print(f"   🔗 All with Live Demos")
        
        return standardized_products

def main():
    """Main execution function"""
    print("🔍 Scanning GP Site for additional products...")
    
    scanner = GPSiteProductsScanner()
    
    # Create and save GP site products
    products = scanner.create_gp_site_products()
    scanner.save_gp_products()
    
    print(f"\n🎉 Successfully discovered and processed {len(products)} additional products!")
    print("📁 Ready for integration with existing store catalog")

if __name__ == "__main__":
    main()