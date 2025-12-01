#!/usr/bin/env python3
"""
Check data point counts for each variable in Causal Affect database
"""
import requests
import json
from collections import defaultdict

BASE_URL = "https://businessventures-production.up.railway.app"

# Get correlations to see sample sizes
print("Fetching correlations from Causal Affect...")
response = requests.get(f"{BASE_URL}/api/dashboard/correlations?limit=2000")
if response.status_code != 200:
    print(f"Error: {response.status_code} - {response.text}")
    exit(1)

correlations = response.json()
print(f"Total correlations: {len(correlations)}")

# Analyze sample sizes
sample_sizes = defaultdict(int)
variable_min_samples = defaultdict(lambda: float('inf'))

for corr in correlations:
    n = corr.get('n', 0)
    sample_sizes[n] += 1
    
    var1 = corr.get('variable1_name', '')
    var2 = corr.get('variable2_name', '')
    
    variable_min_samples[var1] = min(variable_min_samples[var1], n)
    variable_min_samples[var2] = min(variable_min_samples[var2], n)

print("\n=== Sample Size Distribution ===")
for size in sorted(sample_sizes.keys()):
    print(f"n={size}: {sample_sizes[size]} correlations")

print("\n=== Variables with Low Sample Sizes ===")
low_sample_vars = [(var, n) for var, n in variable_min_samples.items() if n < 10]
low_sample_vars.sort(key=lambda x: x[1])

for var, n in low_sample_vars[:30]:
    print(f"{var}: minimum n={n}")

print(f"\n=== Summary ===")
print(f"Total variables: {len(variable_min_samples)}")
print(f"Variables with n<10 in any correlation: {len(low_sample_vars)}")
print(f"Correlations with n<10: {sum(sample_sizes[n] for n in sample_sizes if n < 10)}")
