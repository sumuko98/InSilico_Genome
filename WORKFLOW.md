# Genomic Region Removal Workflow

## Overview
This document illustrates the complete workflow for removing genomic regions while maintaining coordinate tracking.

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    INPUT FILES                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Genome File (FASTA)                                         │
│     Ntab_nuclear.fna                                            │
│     >Chromosome1                                                │
│     ATCGATCG...                                                 │
│                                                                  │
│  2. Regions File (TSV/Space-separated)                          │
│     regions_to_remove.txt                                       │
│     Region1    1000    2000                                     │
│     Region2    5000    5500                                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESSING STEPS                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Step 1: Parse Input Files                                      │
│    • Read genome sequence                                       │
│    • Parse regions to remove                                    │
│    • Validate coordinates                                       │
│                                                                  │
│  Step 2: Sort and Validate Regions                              │
│    • Sort regions by start position                             │
│    • Check for overlaps                                         │
│    • Validate boundaries                                        │
│                                                                  │
│  Step 3: Remove Regions Sequentially                            │
│    • Process regions from start to end                          │
│    • Track original coordinates                                 │
│    • Adjust internal positions                                  │
│    • Calculate cumulative offset                                │
│                                                                  │
│  Step 4: Generate Outputs                                       │
│    • Write modified FASTA                                       │
│    • Create removal report                                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OUTPUT FILES                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Modified Genome (FASTA)                                     │
│     output_modified.fna                                         │
│     >Chromosome1                                                │
│     ATCG... (with regions removed)                              │
│                                                                  │
│  2. Removal Report (Text)                                       │
│     output_removed_regions.txt                                  │
│     • Statistics summary                                        │
│     • List of removed regions                                   │
│     • Original coordinates preserved                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Coordinate Tracking Example

### Before Removal (Original Genome)
```
Position:  1    100   200   500   600   1000  1100  1500
           |-----|-----|-----|-----|-----|-----|-----|
Sequence:  AAAAA[RRR]BBB[RRR]CCCCC[RRRR]DDDDD
                 ^         ^         ^
                 |         |         |
              Region1   Region2   Region3
              (100-200) (500-600) (1000-1100)
```

### After Removal (Modified Genome)
```
Position:  1    100        400        800
           |-----|----------|----------|
Sequence:  AAAAABBBCCCCCDDDD
           
Original coordinates maintained in report:
  Region1: 100-200   (removed 101 bp)
  Region2: 500-600   (removed 101 bp)
  Region3: 1000-1100 (removed 101 bp)
```

### Key Features

1. **Original Coordinates Preserved**
   - All reports reference original genome positions
   - Easy cross-referencing with other analyses
   - No manual coordinate conversion needed

2. **Sequential Processing**
   - Regions removed in genomic order
   - Cumulative offset tracked automatically
   - Internal coordinates adjusted transparently

3. **Comprehensive Documentation**
   - Every removed region is named
   - Original positions recorded
   - Statistics calculated automatically

## Usage Commands

### Basic Usage
```bash
./remove_regions.sh -g Ntab_nuclear.fna -r regions.txt -o output
```

### Advanced Usage
```bash
# Custom genome file
./remove_regions.sh -g my_genome.fna -r my_regions.txt -o result

# Using Python directly
python3 remove_genomic_regions.py genome.fna regions.txt prefix
```

## Understanding the Report

The removal report includes:

1. **Header Section**
   - Date and time of processing
   - Original sequence length
   - Final sequence length
   - Total bases removed
   - Number of regions removed

2. **Regions Table**
   - Region name (from input file)
   - Original start position
   - Original end position
   - Length in base pairs

3. **Footer Notes**
   - Coordinate system explanation
   - Processing order information

## Example Output

```
Genomic Regions Removal Report
================================================================================
Date: 2024-10-01 12:00:00
Original sequence length: 1,000,000 bp
Final sequence length: 997,000 bp
Total bases removed: 3,000 bp
Number of regions removed: 3

Removed Regions (coordinates are 1-based, inclusive):
--------------------------------------------------------------------------------
Region Name          Original Start  Original End    Length (bp) 
--------------------------------------------------------------------------------
Telomere_left        1               1,000           1,000       
Repeat_region        500,000         500,999         1,000       
Telomere_right       999,001         1,000,000       1,000       

Note: All coordinates refer to positions in the ORIGINAL sequence.
      Regions are removed in order from start to end of the genome.
```

## Validation

The tool automatically:
- ✓ Validates coordinate ranges
- ✓ Checks for overlapping regions
- ✓ Adjusts out-of-bounds positions
- ✓ Handles edge cases gracefully
- ✓ Provides helpful warning messages

## Best Practices

1. **Always backup your original genome file**
2. **Review the removal report before using the modified genome**
3. **Use descriptive region names for easy identification**
4. **Sort regions for easier verification (optional)**
5. **Check for and resolve overlapping regions**
6. **Validate that removed regions match your expectations**

## Integration with Other Tools

The modified genome can be used with:
- Genome browsers (IGV, UCSC Genome Browser)
- Alignment tools (BLAST, BLAT)
- Assembly tools (SPAdes, Canu)
- Annotation pipelines (MAKER, Augustus)
- Any tool accepting FASTA format

Simply use the `*_modified.fna` file as input to these tools.
