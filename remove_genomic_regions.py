#!/usr/bin/env python3
"""
Script to remove specified genomic regions from a FASTA file while tracking
the original coordinates of removed regions.

Usage:
    python remove_genomic_regions.py <genome_file> <regions_file> <output_prefix>

Regions file format (tab-separated):
    region_name    start_position    end_position
    
Example:
    Region1    100    200
    Region2    500    600
"""

import sys
import os
from typing import List, Tuple, Dict
from datetime import datetime


class GenomicRegion:
    """Class to represent a genomic region to be removed."""
    
    def __init__(self, name: str, start: int, end: int, original_start: int, original_end: int):
        self.name = name
        self.start = start  # Current position (adjusted)
        self.end = end      # Current position (adjusted)
        self.original_start = original_start  # Original position
        self.original_end = original_end      # Original position
        self.length = end - start + 1
        
    def __repr__(self):
        return (f"GenomicRegion(name={self.name}, original=[{self.original_start},{self.original_end}], "
                f"adjusted=[{self.start},{self.end}], length={self.length})")


def read_fasta(fasta_file: str) -> Tuple[str, str]:
    """
    Read a FASTA file and return the header and sequence.
    
    Args:
        fasta_file: Path to FASTA file
        
    Returns:
        Tuple of (header, sequence)
    """
    header = ""
    sequence = []
    
    with open(fasta_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                header = line
            else:
                sequence.append(line)
    
    return header, ''.join(sequence)


def write_fasta(output_file: str, header: str, sequence: str):
    """
    Write a FASTA file.
    
    Args:
        output_file: Output file path
        header: FASTA header line
        sequence: Sequence to write
    """
    with open(output_file, 'w') as f:
        f.write(header + '\n')
        # Write sequence in 80-character lines
        for i in range(0, len(sequence), 80):
            f.write(sequence[i:i+80] + '\n')


def parse_regions_file(regions_file: str) -> List[Tuple[str, int, int]]:
    """
    Parse regions file and return list of regions.
    
    Args:
        regions_file: Path to regions file
        
    Returns:
        List of tuples (region_name, start, end)
    """
    regions = []
    
    with open(regions_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
                
            parts = line.split('\t')
            if len(parts) < 3:
                # Try splitting by spaces if tabs don't work
                parts = line.split()
                
            if len(parts) < 3:
                print(f"Warning: Skipping invalid line {line_num}: {line}", file=sys.stderr)
                continue
                
            try:
                region_name = parts[0]
                start = int(parts[1])
                end = int(parts[2])
                
                if start > end:
                    print(f"Warning: Invalid region on line {line_num}: start > end. Swapping values.", 
                          file=sys.stderr)
                    start, end = end, start
                    
                regions.append((region_name, start, end))
            except ValueError as e:
                print(f"Warning: Error parsing line {line_num}: {e}", file=sys.stderr)
                continue
    
    return regions


def remove_regions(sequence: str, regions_list: List[Tuple[str, int, int]]) -> Tuple[str, List[GenomicRegion]]:
    """
    Remove specified regions from sequence, tracking original coordinates.
    
    Args:
        sequence: Original DNA sequence
        regions_list: List of (name, start, end) tuples (1-based coordinates)
        
    Returns:
        Tuple of (modified_sequence, list_of_removed_regions)
    """
    # Sort regions by start position
    sorted_regions = sorted(regions_list, key=lambda x: x[1])
    
    # Validate regions
    seq_length = len(sequence)
    valid_regions = []
    
    for name, start, end in sorted_regions:
        if start < 1:
            print(f"Warning: Region {name} start position {start} < 1. Adjusting to 1.", file=sys.stderr)
            start = 1
        if end > seq_length:
            print(f"Warning: Region {name} end position {end} > sequence length {seq_length}. "
                  f"Adjusting to {seq_length}.", file=sys.stderr)
            end = seq_length
        if start > seq_length:
            print(f"Warning: Region {name} start position {start} > sequence length {seq_length}. "
                  f"Skipping this region.", file=sys.stderr)
            continue
            
        valid_regions.append((name, start, end))
    
    # Check for overlapping regions
    for i in range(len(valid_regions) - 1):
        if valid_regions[i][2] >= valid_regions[i+1][1]:
            print(f"Warning: Regions {valid_regions[i][0]} and {valid_regions[i+1][0]} overlap!", 
                  file=sys.stderr)
    
    # Remove regions from end to beginning to maintain coordinate validity
    removed_regions = []
    modified_seq = sequence
    cumulative_offset = 0
    
    for name, orig_start, orig_end in valid_regions:
        # Convert to 0-based indexing for Python
        start_idx = orig_start - 1
        end_idx = orig_end  # end is inclusive in 1-based, becomes exclusive in 0-based
        
        # Calculate adjusted coordinates (accounting for previous removals)
        adjusted_start = orig_start - cumulative_offset
        adjusted_end = orig_end - cumulative_offset
        
        # Store region information
        region = GenomicRegion(name, adjusted_start, adjusted_end, orig_start, orig_end)
        removed_regions.append(region)
        
        # Remove the region
        modified_seq = modified_seq[:start_idx - cumulative_offset] + modified_seq[end_idx - cumulative_offset:]
        
        # Update cumulative offset for next iteration
        cumulative_offset += (orig_end - orig_start + 1)
    
    return modified_seq, removed_regions


def write_removal_report(output_file: str, regions: List[GenomicRegion], 
                        original_length: int, final_length: int):
    """
    Write a report of removed regions.
    
    Args:
        output_file: Output file path
        regions: List of removed GenomicRegion objects
        original_length: Original sequence length
        final_length: Final sequence length
    """
    with open(output_file, 'w') as f:
        f.write("Genomic Regions Removal Report\n")
        f.write("=" * 80 + "\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Original sequence length: {original_length:,} bp\n")
        f.write(f"Final sequence length: {final_length:,} bp\n")
        f.write(f"Total bases removed: {original_length - final_length:,} bp\n")
        f.write(f"Number of regions removed: {len(regions)}\n")
        f.write("\n")
        
        f.write("Removed Regions (coordinates are 1-based, inclusive):\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'Region Name':<20} {'Original Start':<15} {'Original End':<15} {'Length (bp)':<12}\n")
        f.write("-" * 80 + "\n")
        
        for region in regions:
            f.write(f"{region.name:<20} {region.original_start:<15,} {region.original_end:<15,} "
                   f"{region.length:<12,}\n")
        
        f.write("\n")
        f.write("Note: All coordinates refer to positions in the ORIGINAL sequence.\n")
        f.write("      Regions are removed in order from start to end of the genome.\n")


def main():
    """Main function."""
    if len(sys.argv) != 4:
        print("Usage: python remove_genomic_regions.py <genome_file> <regions_file> <output_prefix>")
        print("\nRegions file format (tab or space separated):")
        print("  region_name    start_position    end_position")
        print("\nExample:")
        print("  Region1    100    200")
        print("  Region2    500    600")
        sys.exit(1)
    
    genome_file = sys.argv[1]
    regions_file = sys.argv[2]
    output_prefix = sys.argv[3]
    
    # Check if input files exist
    if not os.path.exists(genome_file):
        print(f"Error: Genome file '{genome_file}' not found!", file=sys.stderr)
        sys.exit(1)
    
    if not os.path.exists(regions_file):
        print(f"Error: Regions file '{regions_file}' not found!", file=sys.stderr)
        sys.exit(1)
    
    print("Reading genome file...")
    header, sequence = read_fasta(genome_file)
    original_length = len(sequence)
    print(f"Original sequence length: {original_length:,} bp")
    
    print("\nParsing regions to remove...")
    regions_list = parse_regions_file(regions_file)
    print(f"Found {len(regions_list)} regions to remove")
    
    if not regions_list:
        print("No valid regions to remove. Exiting.")
        sys.exit(0)
    
    print("\nRemoving regions...")
    modified_sequence, removed_regions = remove_regions(sequence, regions_list)
    final_length = len(modified_sequence)
    
    print(f"Final sequence length: {final_length:,} bp")
    print(f"Total bases removed: {original_length - final_length:,} bp")
    
    # Write output files
    output_fasta = f"{output_prefix}_modified.fna"
    output_report = f"{output_prefix}_removed_regions.txt"
    
    print(f"\nWriting modified genome to: {output_fasta}")
    write_fasta(output_fasta, header, modified_sequence)
    
    print(f"Writing removal report to: {output_report}")
    write_removal_report(output_report, removed_regions, original_length, final_length)
    
    print("\nDone!")


if __name__ == "__main__":
    main()
