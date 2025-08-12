#!/usr/bin/env python3
"""
Simple CSV to XML test
"""

import os

def test_files():
    csv_file = "/workspaces/control_tower/cloned_repos/contract_projects/projects/Safran/1_ZnNi_Line_Stabilization_Critical_Documentation_and_Training/SF_OEE_and_OLE/SF_Investment_Strategy_OEE_OLE_Import.csv"
    main_xml = "/workspaces/control_tower/cloned_repos/contract_projects/xml_workspace/ZnNi Line Development Plan-08.xml"
    
    print("Testing file access...")
    print(f"CSV exists: {os.path.exists(csv_file)}")
    print(f"Main XML exists: {os.path.exists(main_xml)}")
    
    if os.path.exists(csv_file):
        print(f"CSV file size: {os.path.getsize(csv_file)} bytes")
    
    if os.path.exists(main_xml):
        print(f"XML file size: {os.path.getsize(main_xml)} bytes")

if __name__ == "__main__":
    test_files()
