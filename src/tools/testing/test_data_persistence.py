#!/usr/bin/env python3
"""
Test Script for Data Persistence System
Tests all aspects of the UserDataManager and data flow between tabs
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Add the modules directory to the path
sys.path.append(str(Path(__file__).parent / "modules"))

# Import the data persistence system
from modules.personal_mode.data_persistence import user_data_manager

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_result(operation, result):
    """Print operation result in a formatted way"""
    status = "✅ SUCCESS" if result.get("success", False) else "❌ FAILED"
    print(f"\n{operation}: {status}")
    
    if result.get("success", False):
        # Print success details
        if "message" in result:
            print(f"  Message: {result['message']}")
        if "file_path" in result:
            print(f"  File: {result['file_path']}")
        if "changes_detected" in result:
            print(f"  Changes: {result['changes_detected']}")
        if "version_id" in result and result["version_id"]:
            print(f"  Version: {result['version_id']}")
    else:
        # Print error details
        if "message" in result:
            print(f"  Error: {result['message']}")
        if "error" in result:
            print(f"  Details: {result['error']}")

def test_directory_structure():
    """Test that all required directories exist"""
    print_section("TESTING DIRECTORY STRUCTURE")
    
    directories = [
        user_data_manager.data_dir,
        user_data_manager.backup_dir,
        user_data_manager.versions_dir
    ]
    
    for directory in directories:
        exists = directory.exists()
        status = "✅" if exists else "❌"
        print(f"{status} {directory}: {'EXISTS' if exists else 'MISSING'}")
        
        if exists:
            contents = list(directory.glob("*"))
            print(f"    Contents: {len(contents)} files")
            for item in contents[:5]:  # Show first 5 items
                print(f"      - {item.name}")
            if len(contents) > 5:
                print(f"      ... and {len(contents) - 5} more")

def test_load_initial_data():
    """Test loading initial data"""
    print_section("TESTING INITIAL DATA LOAD")
    
    result = user_data_manager.load_user_data()
    print_result("Load User Data", result)
    
    if result["success"]:
        data = result["data"]
        print(f"\n📊 DATA SUMMARY:")
        print(f"  Source: {result['source']}")
        print(f"  Last Updated: {result.get('last_updated', 'Never')}")
        print(f"  Income Gross Salary: £{data['income']['gross_salary']:,}")
        print(f"  Housing Mortgage/Rent: £{data['housing']['mortgage_rent']:,}")
        print(f"  Savings Account: £{data['financial']['savings_account']:,}")
        print(f"  Total Debt: £{sum(data['debts'].values()):,}")
    
    return result

def test_save_modified_data():
    """Test saving modified data"""
    print_section("TESTING DATA SAVE WITH MODIFICATIONS")
    
    # Load current data
    load_result = user_data_manager.load_user_data()
    if not load_result["success"]:
        print("❌ Cannot test save - failed to load data")
        return None
    
    # Modify some values
    data = load_result["data"]
    original_salary = data["income"]["gross_salary"]
    original_savings = data["financial"]["savings_account"]
    
    # Make some test changes
    data["income"]["gross_salary"] = 50000  # Increase salary
    data["financial"]["savings_account"] = 20000  # Increase savings
    data["personal_info"]["name"] = "Test User"  # Add name
    
    print(f"📝 MAKING TEST CHANGES:")
    print(f"  Salary: £{original_salary:,} → £{data['income']['gross_salary']:,}")
    print(f"  Savings: £{original_savings:,} → £{data['financial']['savings_account']:,}")
    print(f"  Name: '' → '{data['personal_info']['name']}'")
    
    # Save the modified data
    save_result = user_data_manager.save_user_data(
        data, 
        create_backup=True, 
        change_description="Test script modifications"
    )
    
    print_result("Save Modified Data", save_result)
    return save_result

def test_data_management_features():
    """Test all data management features"""
    print_section("TESTING DATA MANAGEMENT FEATURES")
    
    # Test data summary
    print("\n🔍 TESTING DATA SUMMARY:")
    summary = user_data_manager.get_data_summary()
    print_result("Get Data Summary", summary)
    
    if summary["success"]:
        print(f"  Has Saved Data: {summary['has_saved_data']}")
        print(f"  Last Updated: {summary['last_updated']}")
        print(f"  Backup Count: {summary['backup_count']}")
        print(f"  Data Source: {summary['data_source']}")
    
    # Test backup list
    print("\n💾 TESTING BACKUP LIST:")
    backups = user_data_manager.list_backups()
    print_result("List Backups", backups)
    
    if backups["success"]:
        print(f"  Total Backups: {backups['count']}")
        for backup in backups["backups"][:3]:  # Show first 3
            print(f"    - {backup['filename']} ({backup['formatted_date']}) - {backup['size_kb']} KB")
    
    # Test version history
    print("\n📚 TESTING VERSION HISTORY:")
    versions = user_data_manager.get_version_history()
    print_result("Get Version History", versions)
    
    if versions["success"]:
        print(f"  Total Versions: {versions['total_versions']}")
        for version in versions["versions"][:3]:  # Show first 3
            print(f"    - {version['version_id']}: {version['description']} ({version['change_count']} changes)")
    
    # Test change log
    print("\n📋 TESTING CHANGE LOG:")
    changes = user_data_manager.get_change_log(limit=5)
    print_result("Get Change Log", changes)
    
    if changes["success"]:
        print(f"  Total Changes: {changes['total_changes']}")
        print(f"  Showing: {changes['showing']}")
        for change in changes["changes"]:
            print(f"    - {change['timestamp']}: {change['description']} ({change['change_count']} changes)")

def test_file_existence():
    """Test that all expected files exist"""
    print_section("TESTING FILE EXISTENCE")
    
    files_to_check = [
        ("Current Data", user_data_manager.current_data_file),
        ("Changes Log", user_data_manager.changes_log)
    ]
    
    for name, file_path in files_to_check:
        exists = file_path.exists()
        status = "✅" if exists else "❌"
        print(f"{status} {name}: {file_path}")
        
        if exists:
            size_kb = round(file_path.stat().st_size / 1024, 2)
            modified = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            print(f"    Size: {size_kb} KB, Modified: {modified}")
            
            # For JSON files, try to validate structure
            if file_path.suffix == ".json":
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    print(f"    ✅ Valid JSON with {len(data)} top-level keys")
                except Exception as e:
                    print(f"    ❌ Invalid JSON: {e}")

def test_callback_integration():
    """Test if callback functions would work"""
    print_section("TESTING CALLBACK INTEGRATION READINESS")
    
    # Test that all required methods exist and are callable
    methods_to_test = [
        "get_data_summary",
        "get_version_history", 
        "list_backups",
        "get_change_log",
        "create_backup",
        "reset_to_defaults"
    ]
    
    for method_name in methods_to_test:
        if hasattr(user_data_manager, method_name):
            method = getattr(user_data_manager, method_name)
            if callable(method):
                print(f"✅ {method_name}: Available and callable")
                
                # Test calling with no parameters (for methods that support it)
                if method_name in ["get_data_summary", "get_version_history", "list_backups", "get_change_log"]:
                    try:
                        result = method()
                        status = "✅ WORKS" if result.get("success", False) else "⚠️ RETURNS ERROR"
                        print(f"    Test call: {status}")
                    except Exception as e:
                        print(f"    Test call: ❌ EXCEPTION - {e}")
            else:
                print(f"❌ {method_name}: Not callable")
        else:
            print(f"❌ {method_name}: Not found")

def test_data_persistence_workflow():
    """Test the complete workflow that should happen in the app"""
    print_section("TESTING COMPLETE WORKFLOW")
    
    print("🔄 SIMULATING APP WORKFLOW:")
    
    # Step 1: Load data (app startup)
    print("\n1️⃣ App Startup - Load Data:")
    load_result = user_data_manager.load_user_data()
    print_result("Load on Startup", load_result)
    
    # Step 2: User makes changes (slider updates)
    print("\n2️⃣ User Updates Sliders:")
    if load_result["success"]:
        data = load_result["data"]
        print(f"  Current salary: £{data['income']['gross_salary']:,}")
        
        # Simulate slider change
        data["income"]["gross_salary"] = 55000
        print(f"  Updated salary: £{data['income']['gross_salary']:,}")
        
        # Step 3: Auto-save (what should happen on slider change)
        print("\n3️⃣ Auto-Save on Change:")
        save_result = user_data_manager.save_user_data(
            data, 
            create_backup=True, 
            change_description="Slider update - gross salary"
        )
        print_result("Auto-Save", save_result)
        
        # Step 4: Data Management tab queries (what should show in UI)
        print("\n4️⃣ Data Management Tab Queries:")
        
        # Summary for tab display
        summary = user_data_manager.get_data_summary()
        print(f"  📊 Summary: {summary['success']}")
        
        # Version history for dropdown
        versions = user_data_manager.get_version_history()
        print(f"  📚 Versions: {versions['success']} ({versions.get('total_versions', 0)} versions)")
        
        # Backups for list
        backups = user_data_manager.list_backups()
        print(f"  💾 Backups: {backups['success']} ({backups.get('count', 0)} backups)")
        
        # Changes for log
        changes = user_data_manager.get_change_log()
        print(f"  📋 Changes: {changes['success']} ({changes.get('total_changes', 0)} changes)")

def main():
    """Run all tests"""
    print("🚀 FINANCIAL OPTIMIZER DATA PERSISTENCE TEST SUITE")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run all test functions
        test_directory_structure()
        test_load_initial_data()
        test_save_modified_data()
        test_data_management_features()
        test_file_existence()
        test_callback_integration()
        test_data_persistence_workflow()
        
        print_section("TEST SUMMARY")
        print("✅ All tests completed successfully!")
        print("\n🔍 CHECK RESULTS ABOVE FOR:")
        print("  - Directory structure and file creation")
        print("  - Data loading and saving functionality")
        print("  - Version tracking and change detection")
        print("  - Backup system operation")
        print("  - Data Management tab readiness")
        print("  - Complete workflow simulation")
        
        print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
