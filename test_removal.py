#!/usr/bin/env python3
"""
Test script for remove_genomic_regions.py
Creates a simple test genome and validates the removal functionality.
"""

import os
import sys
import tempfile
import shutil

def create_test_genome(filepath, length=1000):
    """Create a simple test genome."""
    # Create a simple repeating pattern for easy verification
    sequence = "ATCG" * (length // 4)
    if len(sequence) < length:
        sequence += "ATCG"[:length - len(sequence)]
    
    with open(filepath, 'w') as f:
        f.write(">TestChromosome\n")
        for i in range(0, len(sequence), 80):
            f.write(sequence[i:i+80] + "\n")
    
    return sequence

def create_test_regions(filepath):
    """Create test regions file."""
    with open(filepath, 'w') as f:
        f.write("# Test regions\n")
        f.write("Region1\t10\t20\n")  # Remove 11 bp (positions 10-20 inclusive)
        f.write("Region2\t50\t59\n")  # Remove 10 bp (positions 50-59 inclusive)
        f.write("Region3\t100\t109\n")  # Remove 10 bp (positions 100-109 inclusive)

def read_fasta_sequence(filepath):
    """Read sequence from FASTA file."""
    sequence = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line.startswith('>'):
                sequence.append(line)
    return ''.join(sequence)

def test_removal():
    """Test the genomic region removal."""
    print("=" * 80)
    print("Testing Genomic Region Removal Tool")
    print("=" * 80)
    
    # Create temporary directory for test files
    test_dir = tempfile.mkdtemp(prefix="genome_test_")
    print(f"\nTest directory: {test_dir}")
    
    try:
        # Create test files
        genome_file = os.path.join(test_dir, "test_genome.fna")
        regions_file = os.path.join(test_dir, "test_regions.txt")
        output_prefix = os.path.join(test_dir, "output")
        
        print("\n1. Creating test genome (1000 bp)...")
        original_seq = create_test_genome(genome_file, 1000)
        print(f"   Original sequence length: {len(original_seq)}")
        print(f"   First 50 bp: {original_seq[:50]}")
        
        print("\n2. Creating test regions file...")
        create_test_regions(regions_file)
        print("   Regions to remove:")
        print("   - Region1: positions 10-20 (11 bp)")
        print("   - Region2: positions 50-59 (10 bp)")
        print("   - Region3: positions 100-109 (10 bp)")
        print("   Total: 31 bp to be removed")
        
        print("\n3. Running removal script...")
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                   "remove_genomic_regions.py")
        cmd = f"python3 {script_path} {genome_file} {regions_file} {output_prefix}"
        exit_code = os.system(cmd)
        
        if exit_code != 0:
            print(f"\n❌ ERROR: Script failed with exit code {exit_code}")
            return False
        
        print("\n4. Validating results...")
        
        # Check output files exist
        output_fasta = f"{output_prefix}_modified.fna"
        output_report = f"{output_prefix}_removed_regions.txt"
        
        if not os.path.exists(output_fasta):
            print(f"   ❌ ERROR: Output FASTA not created: {output_fasta}")
            return False
        print(f"   ✓ Output FASTA created: {output_fasta}")
        
        if not os.path.exists(output_report):
            print(f"   ❌ ERROR: Output report not created: {output_report}")
            return False
        print(f"   ✓ Output report created: {output_report}")
        
        # Read modified sequence
        modified_seq = read_fasta_sequence(output_fasta)
        print(f"\n   Modified sequence length: {len(modified_seq)}")
        print(f"   Expected length: {1000 - 31} = 969")
        
        if len(modified_seq) != 969:
            print(f"   ❌ ERROR: Length mismatch! Expected 969, got {len(modified_seq)}")
            return False
        print("   ✓ Length is correct")
        
        # Verify the removed regions
        # Region1: positions 10-20 (indices 9-19 in 0-based) should be removed
        # So position 9 should be followed by position 21
        expected_seq = original_seq[:9] + original_seq[20:49] + original_seq[59:99] + original_seq[109:]
        
        if modified_seq == expected_seq:
            print("   ✓ Sequence content is correct")
        else:
            print("   ❌ ERROR: Sequence content mismatch!")
            print(f"   First 50 bp of modified: {modified_seq[:50]}")
            print(f"   First 50 bp of expected: {expected_seq[:50]}")
            return False
        
        # Check report content
        print("\n5. Checking report content...")
        with open(output_report, 'r') as f:
            report_content = f.read()
            
        if "Region1" in report_content and "Region2" in report_content and "Region3" in report_content:
            print("   ✓ All regions listed in report")
        else:
            print("   ❌ ERROR: Not all regions in report")
            return False
            
        if "1,000" in report_content or "1000" in report_content:
            print("   ✓ Original length in report")
        else:
            print("   ❌ ERROR: Original length not in report")
            return False
            
        if "969" in report_content:
            print("   ✓ Final length in report")
        else:
            print("   ❌ ERROR: Final length not in report")
            return False
        
        print("\n" + "=" * 80)
        print("✓ ALL TESTS PASSED!")
        print("=" * 80)
        
        # Show a snippet of the report
        print("\nReport snippet:")
        print("-" * 80)
        lines = report_content.split('\n')
        for i, line in enumerate(lines):
            if i < 15:  # Show first 15 lines
                print(line)
        print("-" * 80)
        
        return True
        
    finally:
        # Cleanup
        print(f"\nCleaning up test directory: {test_dir}")
        shutil.rmtree(test_dir)

if __name__ == "__main__":
    success = test_removal()
    sys.exit(0 if success else 1)
