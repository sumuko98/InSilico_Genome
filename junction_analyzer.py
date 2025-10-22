#!/usr/bin/env python3
"""
Script to analyze reads at junction sites created by region removal.

This script:
1. Parses the removed_regions_log.txt to extract junction sites (shifted start positions)
2. Maps reads to the modified genome using minimap2 (via mappy)
3. Analyzes reads at junction sites to identify soft-clipped sequences
4. Outputs TSV with detailed information about reads at each junction
"""

import sys
import argparse
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from collections import defaultdict


def parse_removed_regions_log(log_file: str) -> Dict[str, List[int]]:
    """
    Parse the removed_regions_log.txt file to extract junction sites.
    
    Args:
        log_file: Path to the removed regions report file
        
    Returns:
        Dictionary mapping chromosome IDs to list of junction sites (shifted start - 1)
    """
    junctions = defaultdict(list)
    current_chrom = None
    
    with open(log_file, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Detect chromosome line
            if line.startswith("Chromosome:"):
                current_chrom = line.split("Chromosome:")[1].strip()
            
            # Parse data lines (skip headers and separators)
            elif current_chrom and line and not line.startswith('-') and \
                 not line.startswith('Region Name') and \
                 not line.startswith('Total') and \
                 not line.startswith('Removed') and \
                 not line.startswith('='):
                
                # Parse the line: Region Name, Start, End, Length, Shifted Start
                parts = line.split()
                if len(parts) >= 5:
                    try:
                        shifted_start = int(parts[4])
                        # Junction site is at shifted_start - 1
                        junction_site = shifted_start - 1
                        if junction_site >= 0:  # Only add valid junction sites
                            junctions[current_chrom].append(junction_site)
                    except (ValueError, IndexError):
                        # Skip lines that don't match expected format
                        pass
    
    return dict(junctions)


def parse_cigar(cigar_str: str) -> Tuple[int, int]:
    """
    Parse CIGAR string to extract soft-clip lengths.
    
    Args:
        cigar_str: CIGAR string from alignment
        
    Returns:
        Tuple of (left_softclip_length, right_softclip_length)
    """
    if not cigar_str:
        return 0, 0
    
    left_clip = 0
    right_clip = 0
    
    # Parse CIGAR operations
    operations = []
    current_num = ""
    
    for char in cigar_str:
        if char.isdigit():
            current_num += char
        else:
            if current_num:
                operations.append((int(current_num), char))
                current_num = ""
    
    # Check first operation for left soft clip
    if operations and operations[0][1] == 'S':
        left_clip = operations[0][0]
    
    # Check last operation for right soft clip
    if operations and operations[-1][1] == 'S':
        right_clip = operations[-1][0]
    
    return left_clip, right_clip


def extract_softclip_sequence(read_seq: str, left_clip: int, right_clip: int) -> Tuple[str, str]:
    """
    Extract soft-clipped sequences from read.
    
    Args:
        read_seq: Full read sequence
        left_clip: Length of left soft clip
        right_clip: Length of right soft clip
        
    Returns:
        Tuple of (left_softclip_seq, right_softclip_seq)
    """
    left_seq = ""
    right_seq = ""
    
    if left_clip > 0 and len(read_seq) >= left_clip:
        left_seq = read_seq[:left_clip]
    
    if right_clip > 0 and len(read_seq) >= right_clip:
        right_seq = read_seq[len(read_seq) - right_clip:]
    
    return left_seq, right_seq


def analyze_reads_at_junctions(
    sam_file: str,
    junctions: Dict[str, List[int]],
    chrom: Optional[str] = None,
    extract_fasta: bool = False
) -> List[Tuple]:
    """
    Analyze reads at junction sites from SAM file.
    
    Args:
        sam_file: Path to SAM file
        junctions: Dictionary of chromosome to junction sites
        chrom: Optional specific chromosome to analyze
        extract_fasta: Whether to extract soft-clipped sequences
        
    Returns:
        List of tuples containing read information at junctions
    """
    try:
        import pysam
    except ImportError:
        print("Error: pysam is required but not installed.", file=sys.stderr)
        print("Please install it with: pip install pysam", file=sys.stderr)
        sys.exit(1)
    
    results = []
    
    # Filter chromosomes if specific one requested
    chroms_to_analyze = [chrom] if chrom else junctions.keys()
    
    # Open SAM/BAM file
    try:
        samfile = pysam.AlignmentFile(sam_file, "r")
    except Exception as e:
        print(f"Error opening SAM file: {e}", file=sys.stderr)
        sys.exit(1)
    
    for chrom_id in chroms_to_analyze:
        if chrom_id not in junctions:
            continue
        
        junction_sites = junctions[chrom_id]
        
        try:
            # Fetch reads for this chromosome
            for read in samfile.fetch(chrom_id):
                if read.is_unmapped:
                    continue
                
                # Get read alignment positions
                read_start = read.reference_start  # 0-based
                read_end = read.reference_end      # 0-based, exclusive
                
                if read_end is None:
                    continue
                
                # Check if read ends at any junction site
                for junction_site in junction_sites:
                    # A read is "at the junction" if it ends at junction_site
                    # Since read_end is exclusive and junction_site is 0-based position before shifted start,
                    # we check if read_end - 1 == junction_site
                    if read_end - 1 == junction_site or read_start <= junction_site < read_end:
                        # Parse CIGAR for soft clips
                        cigar_str = read.cigarstring if read.cigarstring else ""
                        left_clip, right_clip = parse_cigar(cigar_str)
                        
                        # Extract sequences if requested
                        left_seq = ""
                        right_seq = ""
                        if extract_fasta and (left_clip > 0 or right_clip > 0):
                            read_seq = read.query_sequence
                            if read_seq:
                                left_seq, right_seq = extract_softclip_sequence(
                                    read_seq, left_clip, right_clip
                                )
                        
                        # Record read information
                        results.append((
                            read.query_name,
                            chrom_id,
                            junction_site,
                            read_start,
                            read_end - 1,  # Make end inclusive for reporting
                            read.mapping_quality,
                            cigar_str,
                            left_clip,
                            right_clip,
                            left_seq,
                            right_seq
                        ))
                        break  # Only count this read once per junction
        
        except Exception as e:
            print(f"Warning: Could not fetch reads for {chrom_id}: {e}", file=sys.stderr)
            continue
    
    samfile.close()
    return results


def map_reads_with_mappy(reads_file: str, reference_file: str, output_sam: str, preset: str = "map-ont"):
    """
    Map reads to reference genome using mappy and output SAM file.
    
    Args:
        reads_file: Path to reads FASTA/FASTQ file
        reference_file: Path to reference genome FASTA
        output_sam: Path to output SAM file
        preset: Minimap2 preset (default: map-ont)
    """
    try:
        import mappy
    except ImportError:
        print("Error: mappy is required but not installed.", file=sys.stderr)
        print("Please install it with: pip install mappy", file=sys.stderr)
        sys.exit(1)
    
    print(f"Mapping reads from {reads_file} to {reference_file}...")
    print(f"Using preset: {preset}")
    
    # Load reference
    try:
        aligner = mappy.Aligner(reference_file, preset=preset)
        if not aligner:
            raise RuntimeError("Failed to create aligner")
    except Exception as e:
        print(f"Error loading reference: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Open output SAM file
    with open(output_sam, 'w') as sam_out:
        # Write SAM header
        sam_out.write("@HD\tVN:1.0\tSO:unsorted\n")
        
        # Write reference sequences
        for name, length in zip(aligner.seq_names, aligner.seq_lens):
            sam_out.write(f"@SQ\tSN:{name}\tLN:{length}\n")
        
        # Process reads
        read_count = 0
        mapped_count = 0
        
        # Read input file
        try:
            with open(reads_file, 'r') as f:
                seq_name = None
                seq = []
                
                for line in f:
                    line = line.strip()
                    if line.startswith('>') or line.startswith('@'):
                        # Process previous sequence
                        if seq_name and seq:
                            read_seq = ''.join(seq)
                            read_count += 1
                            
                            # Align read
                            for hit in aligner.map(read_seq):
                                mapped_count += 1
                                # Write SAM line
                                flag = 0 if hit.strand == 1 else 16
                                sam_out.write(
                                    f"{seq_name}\t{flag}\t{hit.ctg}\t{hit.r_st + 1}\t"
                                    f"{hit.mapq}\t{hit.cigar_str}\t*\t0\t0\t{read_seq}\t*\n"
                                )
                        
                        # Start new sequence
                        seq_name = line[1:].split()[0]  # Remove > or @ and get first word
                        seq = []
                    else:
                        # Handle FASTQ quality lines (skip lines starting with +)
                        if not line.startswith('+'):
                            seq.append(line)
                
                # Process last sequence
                if seq_name and seq:
                    read_seq = ''.join(seq)
                    read_count += 1
                    
                    for hit in aligner.map(read_seq):
                        mapped_count += 1
                        flag = 0 if hit.strand == 1 else 16
                        sam_out.write(
                            f"{seq_name}\t{flag}\t{hit.ctg}\t{hit.r_st + 1}\t"
                            f"{hit.mapq}\t{hit.cigar_str}\t*\t0\t0\t{read_seq}\t*\n"
                        )
        
        except Exception as e:
            print(f"Error processing reads: {e}", file=sys.stderr)
            sys.exit(1)
    
    print(f"Processed {read_count} reads, generated {mapped_count} alignments")
    print(f"SAM file written to: {output_sam}")


def write_tsv_output(output_file: str, results: List[Tuple], include_sequences: bool = False):
    """
    Write results to TSV file.
    
    Args:
        output_file: Path to output TSV file
        results: List of read information tuples
        include_sequences: Whether to include soft-clipped sequences in output
    """
    with open(output_file, 'w') as f:
        # Write header
        header_fields = [
            "read_name",
            "chromosome",
            "junction_site",
            "read_start",
            "read_end",
            "mapping_quality",
            "cigar",
            "left_softclip_length",
            "right_softclip_length"
        ]
        
        if include_sequences:
            header_fields.extend(["left_softclip_seq", "right_softclip_seq"])
        
        f.write("\t".join(header_fields) + "\n")
        
        # Write data
        for result in results:
            if include_sequences:
                fields = result  # All fields including sequences
            else:
                fields = result[:9]  # Exclude sequence fields
            
            f.write("\t".join(str(x) for x in fields) + "\n")
    
    print(f"Results written to: {output_file}")


def main():
    """Main function to analyze junction reads."""
    parser = argparse.ArgumentParser(
        description='Analyze reads at junction sites created by region removal'
    )
    
    # Input files
    parser.add_argument(
        '--log',
        required=True,
        help='Removed regions log file (output from remove_regions.py)'
    )
    parser.add_argument(
        '--reference',
        required=True,
        help='Modified reference genome FASTA (output from remove_regions.py)'
    )
    parser.add_argument(
        '--reads',
        help='Reads file (FASTA or FASTQ) - required if --sam not provided'
    )
    parser.add_argument(
        '--sam',
        help='Pre-aligned SAM file - if provided, skips alignment step'
    )
    
    # Options
    parser.add_argument(
        '--chrom',
        help='Analyze specific chromosome only (optional)'
    )
    parser.add_argument(
        '--preset',
        default='map-ont',
        help='Minimap2 preset for alignment (default: map-ont)'
    )
    
    # Output files
    parser.add_argument(
        '--out-tsv',
        default='junctions_output.tsv',
        help='Output TSV file (default: junctions_output.tsv)'
    )
    parser.add_argument(
        '--out-sam',
        default='aligned_reads.sam',
        help='Output SAM file (default: aligned_reads.sam)'
    )
    parser.add_argument(
        '--out-fasta',
        action='store_true',
        help='Include soft-clipped sequences in output'
    )
    
    args = parser.parse_args()
    
    # Validate input files
    if not Path(args.log).exists():
        print(f"Error: Log file '{args.log}' not found", file=sys.stderr)
        sys.exit(1)
    
    if not Path(args.reference).exists():
        print(f"Error: Reference file '{args.reference}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Parse junction sites from log
    print("Parsing removed regions log...")
    junctions = parse_removed_regions_log(args.log)
    
    if not junctions:
        print("Warning: No junction sites found in log file", file=sys.stderr)
        sys.exit(0)
    
    print(f"Found junction sites in {len(junctions)} chromosome(s):")
    for chrom, sites in junctions.items():
        print(f"  {chrom}: {len(sites)} junction site(s) at positions {sites}")
    
    # Determine SAM file to use
    sam_file = args.sam
    
    # If no pre-aligned SAM file provided, do alignment
    if not sam_file:
        if not args.reads:
            print("Error: Either --reads or --sam must be provided", file=sys.stderr)
            sys.exit(1)
        
        if not Path(args.reads).exists():
            print(f"Error: Reads file '{args.reads}' not found", file=sys.stderr)
            sys.exit(1)
        
        # Map reads using mappy
        map_reads_with_mappy(args.reads, args.reference, args.out_sam, args.preset)
        sam_file = args.out_sam
    else:
        if not Path(sam_file).exists():
            print(f"Error: SAM file '{sam_file}' not found", file=sys.stderr)
            sys.exit(1)
    
    # Analyze reads at junctions
    print("\nAnalyzing reads at junction sites...")
    results = analyze_reads_at_junctions(
        sam_file,
        junctions,
        args.chrom,
        args.out_fasta
    )
    
    if not results:
        print("No reads found at junction sites")
    else:
        print(f"Found {len(results)} read(s) at junction sites")
        
        # Write output TSV
        write_tsv_output(args.out_tsv, results, args.out_fasta)
    
    print("\nAnalysis complete!")


if __name__ == '__main__':
    main()
