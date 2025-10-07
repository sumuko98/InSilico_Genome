# InSilico_Genome

A tool for processing multi-chromosome FASTA files by removing specified genomic regions, and analyzing reads at junction boundaries.

## Features

- Process multi-FASTA files with multiple chromosomes
- Remove specific regions from each chromosome based on coordinates
- Generate detailed reports of removed regions
- Preserve original chromosome headers
- Handle chromosomes with no regions to remove
- Analyze BAM files to find reads at junction coordinates
- Report soft-clipping information for junction reads
- Extract soft-clipped sequences in FASTA format

## Installation

### Basic Tool (remove_regions.py)

No special installation required. Just Python 3.6+ standard library.

### Junction Analysis Tool (junction_reads.py)

Requires Python 3.6+ and pysam:

```bash
pip install pysam
```

Also requires samtools to be available in your PATH for BAM file indexing.

## Usage

### Region Removal Tool

#### Basic Usage

```bash
python3 remove_regions.py <input_fasta> <regions_file> [options]
```

#### Arguments

- `input_fasta`: Path to the input multi-FASTA file
- `regions_file`: Path to the regions to remove file
- `-o, --output`: Output FASTA file (default: `output_modified.fasta`)
- `-r, --report`: Report file (default: `removed_regions_report.txt`)

### Regions File Format

The regions file should be organized by chromosome, with each chromosome section starting with its FASTA header code (e.g., `>NC_134080.1`), followed by lines containing the region name and coordinates (region_name, start, end):

```
>NC_134080.1
Region1    10    20
Region2    50    60
Region3    75    82

>NC_134081.1
RegionX    5     25

>NC_134082.1
```

**Note:** Coordinates are 1-based and inclusive (standard biological convention).

### Example

```bash
python3 remove_regions.py sample_input.fasta regions_to_remove.txt -o output.fasta -r report.txt
```

This will:
1. Read the multi-FASTA file `sample_input.fasta`
2. Read the regions to remove from `regions_to_remove.txt`
3. Remove specified regions from each chromosome
4. Write the modified sequences to `output.fasta`
5. Generate a detailed report in `report.txt`

### Junction Read Analysis Tool

The junction_reads.py tool analyzes BAM files to find reads at junction coordinates and report their soft-clipping information.

#### Basic Usage

```bash
python3 junction_reads.py --bam <bam_file> --chrom <chromosome> [--pos <position> | --report <report_file> --region <region_name>] [--out-fasta <output_fasta>]
```

#### Arguments

- `--bam`: Path to BAM file aligned to modified nuclear genome (sorted, indexed) [required]
- `--chrom`: Chromosome/contig name exactly as in the report (e.g., NC_134080.1) [required]
- `--pos`: Junction position (1-based, Shifted Start value). If provided, --report is not needed
- `--report`: Path to removed_regions_report.txt (required if --pos not provided)
- `--region`: Region name to analyze (required if using --report)
- `--out-fasta`: Output FASTA file for soft-clipped sequences (optional)

#### Examples

Using a specific position:
```bash
python3 junction_reads.py --bam aligned.bam --chrom NC_134080.1 --pos 39
```

Using the report file to find the junction:
```bash
python3 junction_reads.py --bam aligned.bam --chrom NC_134080.1 --report removed_regions_report.txt --region Region2
```

With FASTA output for soft-clipped sequences:
```bash
python3 junction_reads.py --bam aligned.bam --chrom NC_134080.1 --pos 39 --out-fasta clipped_seqs.fasta
```

#### Output

The tool prints a table with the following information for each read at the junction:
- QNAME: Read name
- CHROM: Chromosome name
- POS: Reference start position (1-based)
- J_MOD: Junction position (Shifted Start value)
- STRAND: +/- for forward/reverse strand
- CIGAR: CIGAR string
- LEFT_CLIP: Number of soft-clipped bases on the left
- RIGHT_CLIP: Number of soft-clipped bases on the right

If `--out-fasta` is specified, soft-clipped sequences are written in FASTA format with headers like:
```
>read_name|side=left|strand=+|cigar=10S40M
AAAAAAAAAA
```

For reverse strand reads, sequences are reverse-complemented to be in reference-forward orientation.

## Output

### Modified FASTA File

The output FASTA file contains all chromosomes with specified regions removed. The original chromosome headers are preserved.

### Report File

The report file contains:
- List of all removed regions for each chromosome
- Start and end coordinates (1-based)
- Length of each removed region
- **Shifted Start**: The position where the region would start in the modified sequence (used as junction coordinate)
- Total count of removed regions per chromosome

Example report format:
```
Removed Regions Report
====================================================================================================

Chromosome: NC_134080.1
----------------------------------------------------------------------------------------------------
Region Name          Start      End        Length     Shifted Start  
----------------------------------------------------------------------------------------------------
Region1              10         20         11         10             
Region2              50         60         11         39             
Region3              75         82         8          53             

Total regions removed: 3
```

## Sample Files

The repository includes sample files for testing:
- `sample_input.fasta`: Example multi-chromosome FASTA file
- `regions_to_remove.txt`: Example regions file

## How It Works

1. **Parse FASTA**: Reads the multi-FASTA file and extracts each chromosome sequence
2. **Parse Regions**: Reads the regions file and organizes regions by chromosome
3. **Remove Regions**: For each chromosome, removes specified regions while preserving the rest
4. **Write Output**: Generates modified FASTA file and detailed report

## Notes

- The script handles any number of chromosomes and regions
- Chromosomes with no regions to remove are included unchanged in the output
- Regions are specified using 1-based coordinates (biological standard)
- The script validates that input files exist before processing