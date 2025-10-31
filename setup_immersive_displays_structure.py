#!/usr/bin/env python3
"""
Setup complete directory structure for Immersive Displays project
Based on the system requirements already defined
"""

import os
from pathlib import Path

def create_directory_structure():
    """Create the complete directory structure for all systems, features, and layers."""
    
    base_path = Path("/workspaces/control_tower/cloned_repos/business_ventures/immersive_displays/systems")
    
    # System definitions with their features and layers
    systems = {
        "SYSTEM-IMMERSIVE-01_hardware_integration": {
            "features": {
                "FEATURE-IMMERSIVE-01-001_device_communication": [
                    "LAYER_IMMERSIVE_01_001_001_MQTT_Device_Controller",
                    "LAYER_IMMERSIVE_01_001_002_Device_Registration_Service", 
                    "LAYER_IMMERSIVE_01_001_003_Health_Monitor_Service"
                ],
                "FEATURE-IMMERSIVE-01-002_lighting_control": [
                    "LAYER_IMMERSIVE_01_002_001_LED_Strip_Controller",
                    "LAYER_IMMERSIVE_01_002_002_Effect_Sequencer",
                    "LAYER_IMMERSIVE_01_002_003_Performance_Optimizer"
                ],
                "FEATURE-IMMERSIVE-01-003_hardware_management": [
                    "LAYER_IMMERSIVE_01_003_001_Device_Inventory_Manager",
                    "LAYER_IMMERSIVE_01_003_002_Configuration_Interface",
                    "LAYER_IMMERSIVE_01_003_003_Analytics_Dashboard"
                ]
            }
        },
        "SYSTEM-IMMERSIVE-02_mobile_application": {
            "features": {
                "FEATURE-IMMERSIVE-02-001_device_control_interface": [
                    "LAYER_IMMERSIVE_02_001_001_Device_Discovery_Manager",
                    "LAYER_IMMERSIVE_02_001_002_Real_Time_Control_Interface",
                    "LAYER_IMMERSIVE_02_001_003_Camera_Overlay_Preview"
                ],
                "FEATURE-IMMERSIVE-02-002_content_library_management": [
                    "LAYER_IMMERSIVE_02_002_001_Content_Browser",
                    "LAYER_IMMERSIVE_02_002_002_Download_Manager", 
                    "LAYER_IMMERSIVE_02_002_003_Local_Storage_Manager"
                ],
                "FEATURE-IMMERSIVE-02-003_user_account_system": [
                    "LAYER_IMMERSIVE_02_003_001_Authentication_Manager",
                    "LAYER_IMMERSIVE_02_003_002_Profile_Management",
                    "LAYER_IMMERSIVE_02_003_003_Subscription_Interface"
                ]
            }
        },
        "SYSTEM-IMMERSIVE-03_content_management": {
            "features": {
                "FEATURE-IMMERSIVE-03-001_ai_content_generation": [
                    "LAYER_IMMERSIVE_03_001_001_Theme_Generator",
                    "LAYER_IMMERSIVE_03_001_002_Quality_Validator",
                    "LAYER_IMMERSIVE_03_001_003_Content_Optimizer"
                ],
                "FEATURE-IMMERSIVE-03-002_content_storage_delivery": [
                    "LAYER_IMMERSIVE_03_002_001_Asset_Storage_Manager",
                    "LAYER_IMMERSIVE_03_002_002_CDN_Distribution", 
                    "LAYER_IMMERSIVE_03_002_003_Version_Control_System"
                ],
                "FEATURE-IMMERSIVE-03-003_content_personalization": [
                    "LAYER_IMMERSIVE_03_003_001_User_Preference_Engine",
                    "LAYER_IMMERSIVE_03_003_002_Recommendation_System",
                    "LAYER_IMMERSIVE_03_003_003_Custom_Content_Builder"
                ]
            }
        },
        "SYSTEM-IMMERSIVE-04_ecommerce_platform": {
            "features": {
                "FEATURE-IMMERSIVE-04-001_product_catalog_management": [
                    "LAYER_IMMERSIVE_04_001_001_Product_Configuration_Builder",
                    "LAYER_IMMERSIVE_04_001_002_Pricing_Calculator",
                    "LAYER_IMMERSIVE_04_001_003_Inventory_Manager"
                ],
                "FEATURE-IMMERSIVE-04-002_order_processing_system": [
                    "LAYER_IMMERSIVE_04_002_001_Shopping_Cart_Manager",
                    "LAYER_IMMERSIVE_04_002_002_Payment_Processor", 
                    "LAYER_IMMERSIVE_04_002_003_Order_Fulfillment_System"
                ],
                "FEATURE-IMMERSIVE-04-003_subscription_management": [
                    "LAYER_IMMERSIVE_04_003_001_Subscription_Billing_Engine",
                    "LAYER_IMMERSIVE_04_003_002_Usage_Tracking_System",
                    "LAYER_IMMERSIVE_04_003_003_Customer_Portal"
                ]
            }
        },
        "SYSTEM-IMMERSIVE-05_audio_synchronization": {
            "features": {
                "FEATURE-IMMERSIVE-05-001_beat_detection_engine": [
                    "LAYER_IMMERSIVE_05_001_001_Audio_Analyzer",
                    "LAYER_IMMERSIVE_05_001_002_Beat_Detection_Algorithm",
                    "LAYER_IMMERSIVE_05_001_003_Tempo_Tracker"
                ],
                "FEATURE-IMMERSIVE-05-002_lighting_synchronization": [
                    "LAYER_IMMERSIVE_05_002_001_Sync_Signal_Generator",
                    "LAYER_IMMERSIVE_05_002_002_Latency_Compensator", 
                    "LAYER_IMMERSIVE_05_002_003_Effect_Coordinator"
                ],
                "FEATURE-IMMERSIVE-05-003_audio_format_support": [
                    "LAYER_IMMERSIVE_05_003_001_Format_Decoder",
                    "LAYER_IMMERSIVE_05_003_002_Streaming_Handler",
                    "LAYER_IMMERSIVE_05_003_003_Audio_Buffer_Manager"
                ]
            }
        },
        "SYSTEM-IMMERSIVE-06_effect_integration": {
            "features": {
                "FEATURE-IMMERSIVE-06-001_modular_hardware_support": [
                    "LAYER_IMMERSIVE_06_001_001_Device_Driver_Manager",
                    "LAYER_IMMERSIVE_06_001_002_Hardware_Abstraction_Layer",
                    "LAYER_IMMERSIVE_06_001_003_Plugin_System"
                ],
                "FEATURE-IMMERSIVE-06-002_environmental_integration": [
                    "LAYER_IMMERSIVE_06_002_001_Weather_Sensor_Interface",
                    "LAYER_IMMERSIVE_06_002_002_Environmental_Response_Engine", 
                    "LAYER_IMMERSIVE_06_002_003_Safety_Monitor_System"
                ],
                "FEATURE-IMMERSIVE-06-003_advanced_effects_coordination": [
                    "LAYER_IMMERSIVE_06_003_001_Multi_Device_Sequencer",
                    "LAYER_IMMERSIVE_06_003_002_Timing_Synchronization_Manager",
                    "LAYER_IMMERSIVE_06_003_003_Effect_Blend_Engine"
                ]
            }
        }
    }
    
    print("🏗️ Creating complete directory structure for Immersive Displays project...")
    
    total_created = 0
    
    for system_name, system_data in systems.items():
        system_path = base_path / system_name
        system_path.mkdir(exist_ok=True)
        print(f"\n📂 System: {system_name}")
        
        for feature_name, layers in system_data["features"].items():
            feature_path = system_path / feature_name
            feature_path.mkdir(exist_ok=True)
            print(f"  📁 Feature: {feature_name}")
            
            for layer_name in layers:
                layer_path = feature_path / layer_name
                layer_path.mkdir(exist_ok=True)
                
                # Create src and tests directories
                (layer_path / "src").mkdir(exist_ok=True)
                (layer_path / "tests").mkdir(exist_ok=True)
                
                print(f"    📄 Layer: {layer_name}")
                print(f"      ✓ {layer_name}/src/")
                print(f"      ✓ {layer_name}/tests/")
                total_created += 1
    
    print(f"\n✅ Directory structure created successfully!")
    print(f"📊 Total layers created: {total_created}")
    print(f"📊 Total systems: {len(systems)}")
    print(f"📊 Total features: {sum(len(s['features']) for s in systems.values())}")
    
    return True

if __name__ == "__main__":
    success = create_directory_structure()
    if success:
        print("\n🚀 Ready for YAML requirements creation!")
        print("Next steps:")
        print("1. Create SYSTEM requirements YAML files")  
        print("2. Create FEATURE requirements YAML files")
        print("3. Create LAYER requirements YAML files") 
        print("4. Run build_feature.py with --skip-layer-generation flag")
    else:
        print("\n❌ Directory structure creation failed!")