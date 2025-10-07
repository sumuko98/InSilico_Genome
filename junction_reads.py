#!/usr/bin/env python3
"""
CLI tool to find reads at junction coordinates and report their soft-clipping.

This tool analyzes BAM files aligned to a modified nuclear genome to find reads
at junction coordinates (Shifted Start values from removed_regions_report.txt)
and reports their soft-clipping information.
"""

import sys
import argparse
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import pysam


def parse_removed_regions_report(report_file: str) -> Dict[str, List[Tuple[str, int, int, int, int]]]:
    """
    Parse the removed_regions_report.txt file.
    
    Args:
        report_file: Path to the removed regions report file
        
    Returns:
        Dictionary mapping chromosome IDs to list of (region_name, start, end, length, shifted_start) tuples
    """
    regions = {}
    current_chrom = None
    
    with open(report_file, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines and separator lines
            if not line or line.startswith('=') or line.startswith('-'):
                continue
            
            # Check for chromosome header
            if line.startswith('Chromosome:'):
                current_chrom = line.split(':', 1)[1].strip()
                regions[current_chrom] = []
                continue
            
            # Skip header row and total lines
            if line.startswith('Region Name') or line.startswith('Total regions'):
                continue
            
            # Skip the main title
            if line == 'Removed Regions Report':
                continue
            
            # Parse region data line
            if current_chrom is not None:
                parts = line.split()
                if len(parts) >= 5:
                    try:
                        region_name = parts[0]
                        start = int(parts[1])
                        end = int(parts[2])
                        length = int(parts[3])
                        shifted_start = int(parts[4])
                        regions[current_chrom].append((region_name, start, end, length, shifted_start))
                    except (ValueError, IndexError):
                        # Skip lines that don't match the expected format
                        pass
    
    return regions


def reverse_complement(seq: str) -> str:
    """
    Return the reverse complement of a DNA sequence.
    
    Args:
        seq: DNA sequence
        
    Returns:
        Reverse complement of the sequence
    """
    complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'N': 'N'}
    return ''.join(complement.get(base.upper(), base) for base in reversed(seq))


def get_soft_clips(read) -> Tuple[int, int, Optional[str], Optional[str]]:
    """
    Extract soft-clip lengths and sequences from a read.
    
    Args:
        read: pysam AlignedSegment
        
    Returns:
        Tuple of (left_clip_len, right_clip_len, left_clip_seq, right_clip_seq)
    """
    left_clip = 0
    right_clip = 0
    left_seq = None
    right_seq = None
    
    if read.cigartuples:
        # Check first operation for left soft clip (operation 4 = soft clip)
        if read.cigartuples[0][0] == 4:
            left_clip = read.cigartuples[0][1]
            if read.query_sequence:
                left_seq = read.query_sequence[:left_clip]
        
        # Check last operation for right soft clip
        if read.cigartuples[-1][0] == 4:
            right_clip = read.cigartuples[-1][1]
            if read.query_sequence:
                right_seq = read.query_sequence[-right_clip:]
    
    return left_clip, right_clip, left_seq, right_seq


def cigar_to_string(cigartuples) -> str:
    """
    Convert CIGAR tuples to string representation.
    
    Args:
        cigartuples: List of (operation, length) tuples
        
    Returns:
        CIGAR string (e.g., "10S50M5S")
    """
    if not cigartuples:
        return "*"
    
    cigar_ops = {
        0: 'M', 1: 'I', 2: 'D', 3: 'N', 4: 'S',
        5: 'H', 6: 'P', 7: '=', 8: 'X'
    }
    
    return ''.join(f"{length}{cigar_ops.get(op, '?')}" for op, length in cigartuples)


def analyze_junction_reads(bam_file: str, chrom: str, j_mod: int, out_fasta: Optional[str] = None):
    """
    Analyze reads at a junction coordinate.
    
    Args:
        bam_file: Path to BAM file (sorted and indexed)
        chrom: Chromosome/contig name
        j_mod: Junction position (1-based)
        out_fasta: Optional path to output FASTA file for soft-clipped sequences
    """
    # Open BAM file
    try:
        bam = pysam.AlignmentFile(bam_file, 'rb')
    except Exception as e:
        print(f"Error opening BAM file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Check if chromosome exists in BAM
    if chrom not in bam.references:
        print(f"Error: Chromosome '{chrom}' not found in BAM file", file=sys.stderr)
        print(f"Available chromosomes: {', '.join(bam.references)}", file=sys.stderr)
        sys.exit(1)
    
    # Fetch reads spanning the junction
    # We fetch reads in the region [J_MOD-1, J_MOD+1] to capture reads at the boundary
    # Convert to 0-based for pysam (J_MOD is 1-based)
    fetch_start = max(0, j_mod - 2)
    fetch_end = j_mod + 1
    
    reads_at_junction = []
    
    for read in bam.fetch(chrom, fetch_start, fetch_end):
        # Skip secondary and supplementary alignments
        if read.is_secondary or read.is_supplementary:
            continue
        
        # Get read boundaries (0-based, half-open interval)
        rstart = read.reference_start  # 0-based
        rend = read.reference_end  # 0-based, exclusive (points to one past the last aligned base)
        
        if rstart is None or rend is None:
            continue
        
        # Convert to 1-based for comparison with J_MOD
        rstart_1based = rstart + 1
        rend_1based = rend  # This is already the 1-based position of the last aligned base + 1
        
        # Check if read is at the junction:
        # - rstart ≤ J_MOD ≤ rend (overlaps the base J_MOD)
        # - rend == J_MOD - 1 (stops immediately before the junction)
        # - rstart == J_MOD (starts at the junction)
        
        # Note: rend is exclusive in 0-based, so rend in 0-based == last_base + 1 in 1-based
        # So rend (0-based) corresponds to position rend (1-based) as the position after the last aligned base
        
        at_junction = False
        
        # Overlaps J_MOD
        if rstart_1based <= j_mod < rend_1based:
            at_junction = True
        # Stops immediately before junction (last aligned base is at J_MOD - 1)
        elif rend_1based == j_mod:
            at_junction = True
        # Starts at the junction
        elif rstart_1based == j_mod:
            at_junction = True
        
        if at_junction:
            reads_at_junction.append(read)
    
    # Output results
    print(f"Found {len(reads_at_junction)} reads at junction {chrom}:{j_mod}")
    print(f"\n{'QNAME':<30} {'CHROM':<15} {'POS':<10} {'J_MOD':<10} {'STRAND':<8} {'CIGAR':<20} {'LEFT_CLIP':<10} {'RIGHT_CLIP':<10}")
    print("-" * 130)
    
    fasta_handle = None
    if out_fasta:
        fasta_handle = open(out_fasta, 'w')
    
    for read in reads_at_junction:
        # Get basic info
        qname = read.query_name
        pos = read.reference_start + 1  # Convert to 1-based
        strand = '-' if read.is_reverse else '+'
        cigar = cigar_to_string(read.cigartuples)
        
        # Get soft clips
        left_clip_len, right_clip_len, left_seq, right_seq = get_soft_clips(read)
        
        # Print read info
        print(f"{qname:<30} {chrom:<15} {pos:<10} {j_mod:<10} {strand:<8} {cigar:<20} {left_clip_len:<10} {right_clip_len:<10}")
        
        # Write to FASTA if requested
        if fasta_handle:
            # For reverse strand reads, reverse complement the sequence
            # so clips are in reference-forward orientation
            if read.is_reverse and read.query_sequence:
                # Reverse complement the entire read sequence
                rc_seq = reverse_complement(read.query_sequence)
                # After reverse complement, left and right clips are swapped
                # and the sequences need to be extracted from the RC sequence
                if right_clip_len > 0:  # Original right clip becomes left in RC
                    left_rc_seq = rc_seq[:right_clip_len]
                    fasta_handle.write(f">{qname}|side=left|strand={strand}|cigar={cigar}\n")
                    fasta_handle.write(f"{left_rc_seq}\n")
                
                if left_clip_len > 0:  # Original left clip becomes right in RC
                    right_rc_seq = rc_seq[-left_clip_len:]
                    fasta_handle.write(f">{qname}|side=right|strand={strand}|cigar={cigar}\n")
                    fasta_handle.write(f"{right_rc_seq}\n")
            else:
                # Forward strand or no sequence - use original orientation
                if left_seq:
                    fasta_handle.write(f">{qname}|side=left|strand={strand}|cigar={cigar}\n")
                    fasta_handle.write(f"{left_seq}\n")
                
                if right_seq:
                    fasta_handle.write(f">{qname}|side=right|strand={strand}|cigar={cigar}\n")
                    fasta_handle.write(f"{right_seq}\n")
    
    if fasta_handle:
        fasta_handle.close()
        print(f"\nSoft-clipped sequences written to: {out_fasta}")
    
    bam.close()


def main():
    """Main function for junction reads CLI."""
    parser = argparse.ArgumentParser(
        description='Find reads at junction coordinates and report soft-clipping'
    )
    parser.add_argument(
        '--bam',
        required=True,
        help='Path to BAM file aligned to modified nuclear genome (sorted, indexed)'
    )
    parser.add_argument(
        '--chrom',
        required=True,
        help='Chromosome/contig name exactly as in the report (e.g., NC_134080.1)'
    )
    parser.add_argument(
        '--report',
        help='Path to removed_regions_report.txt (required if --pos not provided)'
    )
    parser.add_argument(
        '--region',
        help='Region name to analyze (required if using --report)'
    )
    parser.add_argument(
        '--pos',
        type=int,
        help='Junction position (J_MOD, 1-based). If provided, --report is not needed'
    )
    parser.add_argument(
        '--out-fasta',
        help='Output FASTA file for soft-clipped sequences (optional)'
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not Path(args.bam).exists():
        print(f"Error: BAM file '{args.bam}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Check for BAM index
    bam_index = Path(args.bam + '.bai')
    if not bam_index.exists():
        bam_index = Path(str(Path(args.bam).with_suffix('')) + '.bai')
        if not bam_index.exists():
            print(f"Error: BAM index file not found. Please index the BAM file with 'samtools index'", file=sys.stderr)
            sys.exit(1)
    
    # Determine J_MOD
    j_mod = None
    
    if args.pos:
        j_mod = args.pos
        print(f"Using provided position: {j_mod}")
    elif args.report:
        if not args.region:
            print("Error: --region is required when using --report", file=sys.stderr)
            sys.exit(1)
        
        if not Path(args.report).exists():
            print(f"Error: Report file '{args.report}' not found", file=sys.stderr)
            sys.exit(1)
        
        # Parse report
        regions = parse_removed_regions_report(args.report)
        
        # Find the region
        if args.chrom not in regions:
            print(f"Error: Chromosome '{args.chrom}' not found in report", file=sys.stderr)
            sys.exit(1)
        
        region_found = False
        for region_name, start, end, length, shifted_start in regions[args.chrom]:
            if region_name == args.region:
                j_mod = shifted_start
                region_found = True
                print(f"Found region '{args.region}' in report: Shifted Start = {j_mod}")
                break
        
        if not region_found:
            print(f"Error: Region '{args.region}' not found for chromosome '{args.chrom}' in report", file=sys.stderr)
            available = [r[0] for r in regions[args.chrom]]
            print(f"Available regions: {', '.join(available)}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Error: Either --pos or --report (with --region) must be provided", file=sys.stderr)
        sys.exit(1)
    
    # Analyze junction reads
    analyze_junction_reads(args.bam, args.chrom, j_mod, args.out_fasta)


if __name__ == '__main__':
    main()
