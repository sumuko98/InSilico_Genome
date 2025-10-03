#!/usr/bin/env python3
"""
Script to remove specified regions from a multi-chromosome FASTA file.

This script reads a multi-FASTA file containing multiple chromosomes and
removes specified regions from each chromosome based on a regions file.
"""

import sys
import argparse
from typing import Dict, List, Tuple
from pathlib import Path


def parse_fasta(fasta_file: str) -> Dict[str, Tuple[str, str]]:
    """
    Parse a multi-FASTA file and return a dictionary of sequences.
    
    Args:
        fasta_file: Path to the FASTA file
        
    Returns:
        Dictionary mapping chromosome IDs to (full_header, sequence) tuples
    """
    sequences = {}
    current_id = None
    current_header = None
    current_seq = []
    
    with open(fasta_file, 'r') as f:
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('>'):
                # Save previous sequence if exists
                if current_id is not None:
                    sequences[current_id] = (current_header, ''.join(current_seq))
                
                # Start new sequence
                current_header = line
                # Extract chromosome ID (first word after >)
                current_id = line.split()[0][1:]  # Remove '>'
                current_seq = []
            else:
                current_seq.append(line)
        
        # Save last sequence
        if current_id is not None:
            sequences[current_id] = (current_header, ''.join(current_seq))
    
    return sequences


def parse_regions_file(regions_file: str) -> Dict[str, List[Tuple[str, int, int]]]:
    """
    Parse the regions_to_remove.txt file.
    
    Args:
        regions_file: Path to the regions file
        
    Returns:
        Dictionary mapping chromosome IDs to list of (region_name, start, end) tuples
    """
    regions = {}
    current_chrom = None
    
    with open(regions_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:  # Skip empty lines
                continue
                
            if line.startswith('>'):
                # Extract chromosome ID
                current_chrom = line.split()[0][1:]  # Remove '>'
                regions[current_chrom] = []
            elif current_chrom is not None:
                # Parse region: region_name start end
                parts = line.split()
                if len(parts) >= 3:
                    region_name = parts[0]
                    start = int(parts[1])
                    end = int(parts[2])
                    regions[current_chrom].append((region_name, start, end))
    
    return regions


def remove_regions(sequence: str, regions: List[Tuple[str, int, int]]) -> Tuple[str, List[Tuple[str, int, int, int]]]:
    """
    Remove specified regions from a sequence.
    
    Args:
        sequence: The DNA sequence
        regions: List of (region_name, start, end) tuples (1-based coordinates)
        
    Returns:
        Tuple of (modified_sequence, removed_regions_report)
        where removed_regions_report contains (region_name, original_start, original_end, length)
    """
    # Sort regions by start position
    sorted_regions = sorted(regions, key=lambda x: x[1])
    
    # Build the new sequence by keeping non-removed parts
    result_parts = []
    last_pos = 0  # 0-based index
    removed_report = []
    
    for region_name, start, end in sorted_regions:
        # Convert to 0-based indexing
        start_idx = start - 1
        end_idx = end  # end is inclusive in 1-based, so becomes exclusive in 0-based
        
        # Add sequence before this region
        if start_idx > last_pos:
            result_parts.append(sequence[last_pos:start_idx])
        
        # Record removed region
        region_length = end - start + 1
        removed_report.append((region_name, start, end, region_length))
        
        # Update position
        last_pos = end_idx
    
    # Add remaining sequence after last region
    if last_pos < len(sequence):
        result_parts.append(sequence[last_pos:])
    
    modified_sequence = ''.join(result_parts)
    return modified_sequence, removed_report


def write_fasta(output_file: str, sequences: Dict[str, Tuple[str, str]], line_width: int = 80):
    """
    Write sequences to a FASTA file.
    
    Args:
        output_file: Path to output file
        sequences: Dictionary mapping chromosome IDs to (header, sequence) tuples
        line_width: Number of characters per line in sequence
    """
    with open(output_file, 'w') as f:
        for chrom_id in sorted(sequences.keys()):
            header, sequence = sequences[chrom_id]
            f.write(f"{header}\n")
            
            # Write sequence in lines of specified width
            for i in range(0, len(sequence), line_width):
                f.write(sequence[i:i+line_width] + '\n')


def write_report(report_file: str, removed_regions: Dict[str, List[Tuple[str, int, int, int]]]):
    """
    Write a report of removed regions.
    
    Args:
        report_file: Path to report file
        removed_regions: Dictionary mapping chromosome IDs to list of removed regions
    """
    with open(report_file, 'w') as f:
        f.write("Removed Regions Report\n")
        f.write("=" * 80 + "\n\n")
        
        for chrom_id in sorted(removed_regions.keys()):
            regions = removed_regions[chrom_id]
            if regions:
                f.write(f"Chromosome: {chrom_id}\n")
                f.write("-" * 80 + "\n")
                f.write(f"{'Region Name':<20} {'Start':<10} {'End':<10} {'Length':<10}\n")
                f.write("-" * 80 + "\n")
                
                for region_name, start, end, length in regions:
                    f.write(f"{region_name:<20} {start:<10} {end:<10} {length:<10}\n")
                
                f.write(f"\nTotal regions removed: {len(regions)}\n")
                f.write("\n")


def main():
    """Main function to process multi-chromosome FASTA file."""
    parser = argparse.ArgumentParser(
        description='Remove specified regions from a multi-chromosome FASTA file'
    )
    parser.add_argument(
        'fasta_file',
        help='Input multi-FASTA file'
    )
    parser.add_argument(
        'regions_file',
        help='Regions to remove file (format: >chrom_id followed by region_name start end)'
    )
    parser.add_argument(
        '-o', '--output',
        default='output_modified.fasta',
        help='Output FASTA file (default: output_modified.fasta)'
    )
    parser.add_argument(
        '-r', '--report',
        default='removed_regions_report.txt',
        help='Report file (default: removed_regions_report.txt)'
    )
    
    args = parser.parse_args()
    
    # Validate input files exist
    if not Path(args.fasta_file).exists():
        print(f"Error: FASTA file '{args.fasta_file}' not found", file=sys.stderr)
        sys.exit(1)
    
    if not Path(args.regions_file).exists():
        print(f"Error: Regions file '{args.regions_file}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Parse input files
    print("Reading FASTA file...")
    sequences = parse_fasta(args.fasta_file)
    print(f"Found {len(sequences)} chromosome(s)")
    
    print("Reading regions file...")
    regions_to_remove = parse_regions_file(args.regions_file)
    print(f"Found regions for {len(regions_to_remove)} chromosome(s)")
    
    # Process each chromosome
    modified_sequences = {}
    removed_regions_report = {}
    
    for chrom_id, (header, sequence) in sequences.items():
        print(f"\nProcessing chromosome: {chrom_id}")
        print(f"  Original length: {len(sequence)} bp")
        
        # Get regions for this chromosome
        regions = regions_to_remove.get(chrom_id, [])
        
        if regions:
            print(f"  Removing {len(regions)} region(s)...")
            modified_seq, removed_report = remove_regions(sequence, regions)
            modified_sequences[chrom_id] = (header, modified_seq)
            removed_regions_report[chrom_id] = removed_report
            print(f"  Modified length: {len(modified_seq)} bp")
            print(f"  Removed: {len(sequence) - len(modified_seq)} bp")
        else:
            print(f"  No regions to remove")
            modified_sequences[chrom_id] = (header, sequence)
            removed_regions_report[chrom_id] = []
    
    # Write output files
    print(f"\nWriting modified FASTA to: {args.output}")
    write_fasta(args.output, modified_sequences)
    
    print(f"Writing report to: {args.report}")
    write_report(args.report, removed_regions_report)
    
    print("\nProcessing complete!")


if __name__ == '__main__':
    main()
