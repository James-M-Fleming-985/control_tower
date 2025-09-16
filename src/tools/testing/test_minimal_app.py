#!/usr/bin/env python3
"""
Minimal App Test - Diagnose callback issues
"""
import sys
sys.path.append('/workspaces/control_tower/cloned_repos/financial_optimizer')

print("🔍 Testing minimal Financial Optimizer setup...")

# Test 1: Basic imports
try:
    from modules.personal_mode.main import app, create_personal_mode_layout
    print("✅ Main imports successful")
except Exception as e:
    print(f"❌ Main import error: {e}")
    exit(1)

# Test 2: Layout creation
try:
    app.layout = create_personal_mode_layout()
    print("✅ Layout created successfully")
except Exception as e:
    print(f"❌ Layout creation error: {e}")
    exit(1)

# Test 3: Callback imports (one by one)
dashboard_callbacks_ok = False
try:
    from modules.personal_mode.callbacks.dashboard_callbacks import register_dashboard_callbacks
    print("✅ Dashboard callbacks import OK")
    dashboard_callbacks_ok = True
except Exception as e:
    print(f"❌ Dashboard callbacks import error: {e}")

data_mgmt_callbacks_ok = False
try:
    from modules.personal_mode.callbacks.data_management_callbacks import register_data_management_callbacks
    print("✅ Data management callbacks import OK")
    data_mgmt_callbacks_ok = True
except Exception as e:
    print(f"❌ Data management callbacks import error: {e}")

# Test 4: Basic callback registration (if imports worked)
if dashboard_callbacks_ok:
    try:
        register_dashboard_callbacks(app)
        print("✅ Dashboard callbacks registered")
    except Exception as e:
        print(f"❌ Dashboard callback registration error: {e}")

if data_mgmt_callbacks_ok:
    try:
        register_data_management_callbacks(app)
        print("✅ Data management callbacks registered")
    except Exception as e:
        print(f"❌ Data management callback registration error: {e}")

print("\n🚀 Starting minimal app on port 8050...")
print("📝 Check http://127.0.0.1:8050 to test functionality")
print("=" * 50)

app.run_server(debug=True, host='0.0.0.0', port=8050)
