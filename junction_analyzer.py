#!/usr/bin/env python3
"""
Script to analyze reads at junction sites created by region removal.

This script identifies reads at junction sites (Shifted Start positions from
removed_regions_report.txt) and extracts their soft-clipping information.
"""

import sys
import argparse
from typing import Dict, List, Tuple
from pathlib import Path


def parse_removed_regions_log(log_file: str) -> Dict[str, List[int]]:
    """
    Parse removed_regions_report.txt to extract junction sites (Shifted Start values).
    
    Args:
        log_file: Path to the removed regions report file
        
    Returns:
        Dictionary mapping chromosome IDs to list of junction positions (1-based)
    """
    junctions = {}
    current_chrom = None
    
    with open(log_file, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines and separator lines
            if not line or line.startswith('=') or line.startswith('-'):
                continue
            
            # Check for chromosome line
            if line.startswith('Chromosome:'):
                current_chrom = line.split(':')[1].strip()
                junctions[current_chrom] = []
            # Check for data lines (skip header line)
            elif current_chrom and not line.startswith('Region Name') and not line.startswith('Total regions'):
                parts = line.split()
                if len(parts) >= 5:
                    try:
                        # Extract Shifted Start (5th column, 0-indexed position 4)
                        shifted_start = int(parts[4])
                        junctions[current_chrom].append(shifted_start)
                    except (ValueError, IndexError):
                        # Skip lines that don't match expected format
                        continue
    
    return junctions


def parse_cigar(cigar_string: str) -> Tuple[int, int]:
    """
    Parse CIGAR string to extract left and right soft-clip lengths.
    
    Args:
        cigar_string: CIGAR string from SAM/BAM file
        
    Returns:
        Tuple of (left_softclip, right_softclip) lengths
    """
    if not cigar_string or cigar_string == '*':
        return 0, 0
    
    left_clip = 0
    right_clip = 0
    
    # Parse CIGAR operations
    i = 0
    operations = []
    while i < len(cigar_string):
        # Read number
        num_str = ''
        while i < len(cigar_string) and cigar_string[i].isdigit():
            num_str += cigar_string[i]
            i += 1
        
        if i < len(cigar_string):
            op = cigar_string[i]
            if num_str:
                operations.append((int(num_str), op))
            i += 1
    
    # Check first operation for left soft-clip
    if operations and operations[0][1] == 'S':
        left_clip = operations[0][0]
    
    # Check last operation for right soft-clip
    if operations and operations[-1][1] == 'S':
        right_clip = operations[-1][0]
    
    return left_clip, right_clip


def reverse_complement(seq: str) -> str:
    """
    Return the reverse complement of a DNA sequence.
    
    Args:
        seq: DNA sequence
        
    Returns:
        Reverse complement of the sequence
    """
    complement = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', 'N': 'N',
                  'a': 't', 't': 'a', 'g': 'c', 'c': 'g', 'n': 'n'}
    return ''.join(complement.get(base, base) for base in reversed(seq))


def extract_soft_clipped_sequences(seq: str, cigar_string: str, is_reverse: bool) -> Tuple[str, str]:
    """
    Extract soft-clipped sequences from a read.
    
    Args:
        seq: Read sequence
        cigar_string: CIGAR string
        is_reverse: Whether the read is reverse-strand
        
    Returns:
        Tuple of (left_clip_seq, right_clip_seq) - empty strings if no clips
    """
    left_clip, right_clip = parse_cigar(cigar_string)
    
    # If reverse strand, reverse-complement the sequence first
    if is_reverse:
        seq = reverse_complement(seq)
    
    left_seq = ''
    right_seq = ''
    
    if left_clip > 0:
        left_seq = seq[:left_clip]
    
    if right_clip > 0:
        right_seq = seq[-right_clip:]
    
    return left_seq, right_seq


def analyze_junctions_pysam(bam_file: str, chrom: str, junctions: List[int],
                            out_tsv: str, out_fasta: str = None):
    """
    Analyze reads at junction sites using pysam.
    
    Args:
        bam_file: Path to BAM file
        chrom: Chromosome to analyze
        junctions: List of junction positions (1-based)
        out_tsv: Output TSV file path
        out_fasta: Optional output FASTA file path
    """
    try:
        import pysam
    except ImportError:
        print("Error: pysam is required. Install it with: pip install pysam", file=sys.stderr)
        sys.exit(1)
    
    # Open BAM file
    bamfile = pysam.AlignmentFile(bam_file, "rb")
    
    # Collect reads at junctions
    junction_reads = []
    
    for junction_pos in junctions:
        # Fetch reads overlapping the junction region
        # Check a small window around the junction
        start_pos = max(0, junction_pos - 2)  # Convert to 0-based
        end_pos = junction_pos + 2
        
        for read in bamfile.fetch(chrom, start_pos, end_pos):
            # Get read position (1-based for output)
            read_start = read.reference_start + 1  # pysam is 0-based
            read_end = read.reference_end  # Already exclusive, so this is the last aligned position + 1
            
            # Check if read is at junction:
            # - Ends immediately before junction (read_end == junction_pos - 1, but read_end is exclusive so read_end == junction_pos)
            # - Starts exactly at junction (read_start == junction_pos)
            at_junction = False
            if read_end == junction_pos:  # Ends immediately before junction
                at_junction = True
            elif read_start == junction_pos:  # Starts at junction
                at_junction = True
            
            if at_junction:
                # Get strand
                strand = '-' if read.is_reverse else '+'
                
                # Get CIGAR string
                cigar = read.cigarstring if read.cigarstring else '*'
                
                # Parse soft-clips
                left_clip, right_clip = parse_cigar(cigar)
                
                # Store read info
                junction_reads.append({
                    'qname': read.query_name,
                    'chrom': chrom,
                    'ref_start': read_start,
                    'junction': junction_pos,
                    'strand': strand,
                    'cigar': cigar,
                    'left_clip': left_clip,
                    'right_clip': right_clip,
                    'sequence': read.query_sequence,
                    'is_reverse': read.is_reverse
                })
    
    bamfile.close()
    
    # Write TSV output
    with open(out_tsv, 'w') as f:
        # Write header
        f.write("qname\tchrom\tref_start\tJ_MOD\tstrand\tcigar\tleft_clip\tright_clip\n")
        
        # Write read data
        for read_info in junction_reads:
            f.write(f"{read_info['qname']}\t{read_info['chrom']}\t{read_info['ref_start']}\t"
                   f"{read_info['junction']}\t{read_info['strand']}\t{read_info['cigar']}\t"
                   f"{read_info['left_clip']}\t{read_info['right_clip']}\n")
        
        # Write summary line
        total_overlapping = len(junction_reads)
        with_any_softclip = sum(1 for r in junction_reads if r['left_clip'] > 0 or r['right_clip'] > 0)
        f.write(f"# Summary: total_overlapping={total_overlapping}, with_any_softclip={with_any_softclip}\n")
    
    # Write FASTA output if requested
    if out_fasta:
        with open(out_fasta, 'w') as f:
            for read_info in junction_reads:
                # Extract soft-clipped sequences
                left_seq, right_seq = extract_soft_clipped_sequences(
                    read_info['sequence'], 
                    read_info['cigar'], 
                    read_info['is_reverse']
                )
                
                # Write left clip if present
                if left_seq:
                    f.write(f">{read_info['qname']}|side=left|strand={read_info['strand']}|cigar={read_info['cigar']}\n")
                    f.write(f"{left_seq}\n")
                
                # Write right clip if present
                if right_seq:
                    f.write(f">{read_info['qname']}|side=right|strand={read_info['strand']}|cigar={read_info['cigar']}\n")
                    f.write(f"{right_seq}\n")


def main():
    """Main function to analyze junction reads."""
    parser = argparse.ArgumentParser(
        description='Analyze reads at junction sites created by region removal'
    )
    parser.add_argument(
        '--bam',
        required=True,
        help='Input BAM file'
    )
    parser.add_argument(
        '--chrom',
        required=True,
        help='Chromosome to analyze'
    )
    parser.add_argument(
        '--log',
        required=True,
        help='removed_regions_report.txt file'
    )
    parser.add_argument(
        '--out-tsv',
        required=True,
        help='Output TSV file'
    )
    parser.add_argument(
        '--out-fasta',
        help='Optional output FASTA file for soft-clipped sequences'
    )
    
    args = parser.parse_args()
    
    # Validate input files exist
    if not Path(args.bam).exists():
        print(f"Error: BAM file '{args.bam}' not found", file=sys.stderr)
        sys.exit(1)
    
    if not Path(args.log).exists():
        print(f"Error: Log file '{args.log}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Parse junction sites from log file
    print(f"Reading junction sites from {args.log}...")
    junctions_by_chrom = parse_removed_regions_log(args.log)
    
    if args.chrom not in junctions_by_chrom:
        print(f"Error: No junctions found for chromosome '{args.chrom}' in log file", file=sys.stderr)
        sys.exit(1)
    
    junctions = junctions_by_chrom[args.chrom]
    print(f"Found {len(junctions)} junction(s) for chromosome {args.chrom}: {junctions}")
    
    # Analyze reads at junctions
    print(f"Analyzing reads at junctions...")
    analyze_junctions_pysam(args.bam, args.chrom, junctions, args.out_tsv, args.out_fasta)
    
    print(f"TSV output written to: {args.out_tsv}")
    if args.out_fasta:
        print(f"FASTA output written to: {args.out_fasta}")
    
    print("Analysis complete!")


if __name__ == '__main__':
    main()
