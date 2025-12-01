#!/usr/bin/env python3
"""
Quick script to check how many data points each variable has in Causal Affect database.
"""

import requests
import json
from collections import defaultdict

BASE_URL = "https://businessventures-production.up.railway.app"

def check_data_points():
    # Get all variables
    response = requests.get(f"{BASE_URL}/api/variables")
    variables = response.json()
    
    print(f"Total variables: {len(variables)}")
    print("\n" + "="*80)
    
    # Group by category
    by_category = defaultdict(list)
    
    for var in variables:
        var_id = var['id']
        var_name = var['name']
        is_active = var['is_active']
        category = var['category']
        
        # Get data points for this variable
        data_response = requests.get(f"{BASE_URL}/api/variables/{var_id}/data")
        data_points = data_response.json() if data_response.status_code == 200 else []
        
        by_category[category].append({
            'id': var_id,
            'name': var_name,
            'active': is_active,
            'data_points': len(data_points)
        })
    
    # Print summary by category
    for category, vars_list in sorted(by_category.items()):
        print(f"\n{category.upper()}:")
        print("-" * 80)
        for var in vars_list:
            status = "✓" if var['active'] else "✗"
            print(f"  {status} {var['name']}: {var['data_points']} data points")
        
        total_points = sum(v['data_points'] for v in vars_list)
        active_count = sum(1 for v in vars_list if v['active'])
        print(f"  Total: {len(vars_list)} variables ({active_count} active), {total_points} data points")
    
    # Find variables with < 10 data points
    print("\n" + "="*80)
    print("\nVARIABLES WITH < 10 DATA POINTS:")
    print("-" * 80)
    
    low_data_vars = []
    for category, vars_list in by_category.items():
        for var in vars_list:
            if var['active'] and var['data_points'] < 10:
                low_data_vars.append((category, var['name'], var['data_points']))
    
    if low_data_vars:
        for cat, name, points in sorted(low_data_vars, key=lambda x: x[2]):
            print(f"  {cat}/{name}: {points} points")
        print(f"\nTotal: {len(low_data_vars)} variables with insufficient data")
    else:
        print("  None! All active variables have >= 10 data points")

if __name__ == "__main__":
    try:
        check_data_points()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
