#!/usr/bin/env python3
"""
Test script to validate the shifted start site calculation.
Uses the example from the problem statement.
"""

import os
import sys
import tempfile

# Example from problem statement:
# Region A: 100-200 (length 101 bp) → Shifted start: 100
# Region B: 300-350 (length 51 bp) → Shifted start: 300 - 101 = 199
# Region C: 400-420 (length 21 bp) → Shifted start: 400 - (101 + 51) = 248

def create_test_genome(filepath, length=1000):
    """Create a simple test genome."""
    sequence = "ATCG" * (length // 4)
    if len(sequence) < length:
        sequence += "ATCG"[:length - len(sequence)]
    
    with open(filepath, 'w') as f:
        f.write(">TestChromosome\n")
        for i in range(0, len(sequence), 80):
            f.write(sequence[i:i+80] + "\n")
    
    return sequence

def create_test_regions(filepath):
    """Create test regions file matching the problem statement example."""
    with open(filepath, 'w') as f:
        f.write("# Test regions matching problem statement\n")
        f.write("# Region A: 100-200 (length 101), shifted start should be 100\n")
        f.write("# Region B: 300-350 (length 51), shifted start should be 199\n")
        f.write("# Region C: 400-420 (length 21), shifted start should be 248\n")
        f.write("RegionA\t100\t200\n")
        f.write("RegionB\t300\t350\n")
        f.write("RegionC\t400\t420\n")

def test_shifted_start():
    """Test the shifted start site calculation."""
    print("=" * 80)
    print("Testing Shifted Start Site Calculation")
    print("=" * 80)
    
    # Create temporary directory for test files
    test_dir = tempfile.mkdtemp(prefix="shifted_start_test_")
    print(f"\nTest directory: {test_dir}")
    
    try:
        # Create test files
        genome_file = os.path.join(test_dir, "test_genome.fna")
        regions_file = os.path.join(test_dir, "test_regions.txt")
        output_prefix = os.path.join(test_dir, "output")
        
        print("\n1. Creating test genome (1000 bp)...")
        original_seq = create_test_genome(genome_file, 1000)
        print(f"   Created genome with {len(original_seq)} bp")
        
        print("\n2. Creating test regions file (matching problem statement)...")
        create_test_regions(regions_file)
        print("   Expected results:")
        print("   - RegionA (100-200, length 101): Shifted Start = 100")
        print("   - RegionB (300-350, length 51):  Shifted Start = 199")
        print("   - RegionC (400-420, length 21):  Shifted Start = 248")
        
        print("\n3. Running removal script...")
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                   "remove_genomic_regions.py")
        cmd = f"python3 {script_path} {genome_file} {regions_file} {output_prefix}"
        exit_code = os.system(cmd + " 2>&1 | grep -E '(Reading|Parsing|Removing|Writing|Done)'")
        
        if exit_code != 0:
            print(f"\n❌ ERROR: Script may have failed")
            return False
        
        print("\n4. Validating results...")
        
        # Check output report
        output_report = f"{output_prefix}_removed_regions.txt"
        
        if not os.path.exists(output_report):
            print(f"   ❌ ERROR: Output report not created: {output_report}")
            return False
        print(f"   ✓ Output report created")
        
        # Read and validate report content
        with open(output_report, 'r') as f:
            report_content = f.read()
        
        print("\n5. Checking shifted start values in report...")
        
        # Check for the shifted start column header
        if "Shifted Start" not in report_content:
            print("   ❌ ERROR: 'Shifted Start' column not found in report!")
            return False
        print("   ✓ 'Shifted Start' column header found")
        
        # Parse the report to extract shifted start values
        lines = report_content.split('\n')
        region_data = {}
        
        for line in lines:
            # Look for lines that contain region data
            if 'RegionA' in line or 'RegionB' in line or 'RegionC' in line:
                parts = line.split()
                if len(parts) >= 5:
                    region_name = parts[0]
                    # Extract numeric values (removing commas)
                    try:
                        orig_start = int(parts[1].replace(',', ''))
                        orig_end = int(parts[2].replace(',', ''))
                        shifted_start = int(parts[3].replace(',', ''))
                        length = int(parts[4].replace(',', ''))
                        region_data[region_name] = {
                            'orig_start': orig_start,
                            'orig_end': orig_end,
                            'shifted_start': shifted_start,
                            'length': length
                        }
                    except (ValueError, IndexError) as e:
                        print(f"   Warning: Could not parse line: {line}")
                        continue
        
        # Validate the shifted start values
        expected = {
            'RegionA': {'shifted_start': 100, 'length': 101},
            'RegionB': {'shifted_start': 199, 'length': 51},
            'RegionC': {'shifted_start': 248, 'length': 21}
        }
        
        all_correct = True
        for region_name, expected_vals in expected.items():
            if region_name not in region_data:
                print(f"   ❌ ERROR: {region_name} not found in report!")
                all_correct = False
                continue
            
            actual_shifted = region_data[region_name]['shifted_start']
            expected_shifted = expected_vals['shifted_start']
            actual_length = region_data[region_name]['length']
            expected_length = expected_vals['length']
            
            if actual_shifted == expected_shifted and actual_length == expected_length:
                print(f"   ✓ {region_name}: Shifted Start = {actual_shifted} (correct!), Length = {actual_length}")
            else:
                print(f"   ❌ {region_name}: Expected shifted start {expected_shifted}, got {actual_shifted}")
                print(f"      Expected length {expected_length}, got {actual_length}")
                all_correct = False
        
        if not all_correct:
            print("\n❌ TEST FAILED!")
            print("\nFull report content:")
            print("-" * 80)
            print(report_content)
            print("-" * 80)
            return False
        
        print("\n" + "=" * 80)
        print("✓ ALL TESTS PASSED!")
        print("=" * 80)
        
        print("\nSample from report:")
        print("-" * 80)
        for i, line in enumerate(lines):
            if 'Region Name' in line or 'RegionA' in line or 'RegionB' in line or 'RegionC' in line:
                for j in range(max(0, i-2), min(len(lines), i+8)):
                    print(lines[j])
                break
        print("-" * 80)
        
        return True
        
    finally:
        # Cleanup
        print(f"\nCleaning up test directory: {test_dir}")
        import shutil
        shutil.rmtree(test_dir)

if __name__ == "__main__":
    success = test_shifted_start()
    sys.exit(0 if success else 1)
