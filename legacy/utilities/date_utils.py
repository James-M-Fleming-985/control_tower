#!/usr/bin/env python3
"""
Date utilities for Control Tower
Flexible date parsing and formatting
"""

from datetime import datetime, timedelta

def parse_date_flexible(date_str):
    """Parse date string with multiple format support"""
    if not date_str or not isinstance(date_str, str):
        return None
    
    date_str = date_str.strip()
    
    # Skip formula references
    if any(ref in date_str for ref in ['FS', 'SF', '%]']):
        return None
    
    formats = [
        "%a %d/%m/%y",  # Mon 14/04/25
        "%d/%m/%y",     # 14/04/25
        "%Y-%m-%d",     # 2025-04-14
        "%m/%d/%Y",     # 04/14/2025
        "%d/%m/%Y",     # 14/04/2025
        "%Y-%m-%d %H:%M:%S",  # 2025-04-14 10:30:00
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None

def format_date(date_obj, format_str="%Y-%m-%d"):
    """Format datetime object to string"""
    if not date_obj:
        return ""
    
    try:
        return date_obj.strftime(format_str)
    except:
        return str(date_obj)
