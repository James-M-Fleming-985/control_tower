#!/usr/bin/env python3
"""
Connect to Railway PostgreSQL and check correlation sample sizes
"""

import os
import sys

# Add business_ventures to path
sys.path.insert(0, '/workspaces/control_tower/cloned_repos/business_ventures')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database import get_database_url
from models import CorrelationResult, VariableMetadata
from sqlalchemy.orm import joinedload

def check_sample_sizes():
    """Check which correlations still have small sample sizes"""
    
    # Get database URL
    db_url = get_database_url()
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    
    with SessionLocal() as db:
        # Query correlations with small sample sizes
        print("=" * 100)
        print("CORRELATIONS WITH SAMPLE SIZE < 10:")
        print("=" * 100)
        
        small_sample_corrs = db.query(CorrelationResult).filter(
            CorrelationResult.sample_size < 10
        ).options(
            joinedload(CorrelationResult.variable1),
            joinedload(CorrelationResult.variable2)
        ).order_by(CorrelationResult.sample_size).all()
        
        if not small_sample_corrs:
            print("✅ NO CORRELATIONS WITH < 10 SAMPLE SIZE! Problem solved!")
        else:
            print(f"Found {len(small_sample_corrs)} correlations with < 10 sample size:\n")
            
            for corr in small_sample_corrs[:30]:  # Show first 30
                var1_name = corr.variable1.display_name if corr.variable1 else f"ID{corr.var1_id}"
                var2_name = corr.variable2.display_name if corr.variable2 else f"ID{corr.var2_id}"
                print(f"  {var1_name} ↔ {var2_name}")
                print(f"    r={corr.correlation_value:.3f}, n={corr.sample_size}, p={corr.p_value:.4f if corr.p_value else 'N/A'}")
                print()
        
        # Distribution of sample sizes
        print("\n" + "=" * 100)
        print("SAMPLE SIZE DISTRIBUTION:")
        print("=" * 100)
        
        size_ranges = [
            (0, 5, "0-5"),
            (5, 10, "5-10"),
            (10, 20, "10-20"),
            (20, 50, "20-50"),
            (50, 100, "50-100"),
            (100, 999999, "100+")
        ]
        
        for min_size, max_size, label in size_ranges:
            count = db.query(CorrelationResult).filter(
                CorrelationResult.sample_size >= min_size,
                CorrelationResult.sample_size < max_size
            ).count()
            
            print(f"  {label:10s}: {count:5d} correlations")
        
        # Total correlations
        total = db.query(CorrelationResult).count()
        print(f"\n  {'TOTAL':10s}: {total:5d} correlations")
        
        # Check which variables have the least data
        print("\n" + "=" * 100)
        print("VARIABLES WITH < 20 DATA POINTS:")
        print("=" * 100)
        
        from models import TimeSeriesData
        from sqlalchemy import func
        
        var_counts = db.query(
            VariableMetadata.id,
            VariableMetadata.display_name,
            VariableMetadata.category,
            VariableMetadata.is_active,
            func.count(TimeSeriesData.id).label('data_points')
        ).outerjoin(
            TimeSeriesData, VariableMetadata.id == TimeSeriesData.variable_id
        ).group_by(
            VariableMetadata.id
        ).having(
            func.count(TimeSeriesData.id) < 20
        ).order_by(
            func.count(TimeSeriesData.id)
        ).all()
        
        if not var_counts:
            print("✅ ALL VARIABLES HAVE >= 20 DATA POINTS!")
        else:
            for var_id, name, category, active, count in var_counts:
                status = "✓" if active else "✗"
                print(f"  {status} {name} ({category}): {count} data points")

if __name__ == "__main__":
    try:
        check_sample_sizes()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
