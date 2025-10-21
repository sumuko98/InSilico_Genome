# InSilico_Genome

A tool for processing multi-chromosome FASTA files by removing specified genomic regions and analyzing reads at junction sites.

## Features

- Process multi-FASTA files with multiple chromosomes
- Remove specific regions from each chromosome based on coordinates
- Generate detailed reports of removed regions
- Preserve original chromosome headers
- Handle chromosomes with no regions to remove
- Analyze reads at junction sites created by region removal
- Extract soft-clipped sequences from reads at junctions

## Installation

### Basic Requirements

Python 3.6+ standard library for `remove_regions.py`.

### Junction Analyzer Requirements

For `junction_analyzer.py`:
```bash
pip install pysam
```

## Usage

### remove_regions.py

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

#### Example

```bash
python3 remove_regions.py sample_input.fasta regions_to_remove.txt -o output.fasta -r report.txt
```

### junction_analyzer.py

Analyzes reads at junction sites created by region removal.

#### Basic Usage

```bash
python3 junction_analyzer.py --bam <input.bam> --chrom <chromosome> --log <removed_regions_report.txt> --out-tsv <output.tsv> [--out-fasta <output.fasta>]
```

#### Arguments

- `--bam`: Input BAM file with aligned reads (required)
- `--chrom`: Chromosome to analyze (required)
- `--log`: removed_regions_report.txt file from remove_regions.py (required)
- `--out-tsv`: Output TSV file with read information (required)
- `--out-fasta`: Optional output FASTA file for soft-clipped sequences

#### Example

```bash
python3 junction_analyzer.py --bam aligned_reads.bam --chrom NC_134080.1 --log removed_regions_report.txt --out-tsv junction_reads.tsv --out-fasta softclips.fasta
```

#### Output Format

**TSV Output** contains:
- `qname`: Read name
- `chrom`: Chromosome
- `ref_start`: Reference start position (1-based)
- `J_MOD`: Junction position where the read was found
- `strand`: Read strand (+/-)
- `cigar`: CIGAR string
- `left_clip`: Number of soft-clipped bases on the left
- `right_clip`: Number of soft-clipped bases on the right
- Summary line: Total overlapping reads and reads with any soft-clipping

**FASTA Output** (optional) contains:
- Soft-clipped sequences from reads at junctions
- Header format: `>{qname}|side=left/right|strand=+/-|cigar=CIGAR`
- Sequences are in reference-forward orientation (reverse-complemented if needed)

#### How It Works

1. **Parse Junction Sites**: Extracts "Shifted Start" positions from the removed_regions_report.txt
2. **Fetch Reads**: Uses pysam to fetch reads at junction sites
3. **Filter Reads**: Selects reads that either:
   - End immediately before the junction
   - Start exactly at the junction
4. **Extract Information**: Parses CIGAR strings to extract soft-clipping information
5. **Output**: Writes TSV with read details and optionally FASTA with soft-clipped sequences

### Example Workflow

```bash
# Step 1: Remove regions from genome
python3 remove_regions.py sample_input.fasta regions_to_remove.txt -o output.fasta -r report.txt

# Step 2: Analyze reads at junctions
python3 junction_analyzer.py --bam aligned_reads.bam --chrom NC_134080.1 --log report.txt --out-tsv junction_reads.tsv --out-fasta softclips.fasta
```

## Output

### remove_regions.py Output

#### Modified FASTA File

The output FASTA file contains all chromosomes with specified regions removed. The original chromosome headers are preserved.

#### Report File

The report file contains:
- List of all removed regions for each chromosome
- Start and end coordinates (1-based)
- Length of each removed region
- Shifted Start positions (junction sites)
- Total count of removed regions per chromosome

### junction_analyzer.py Output

#### TSV File

Contains read information with columns:
- qname, chrom, ref_start, J_MOD, strand, cigar, left_clip, right_clip
- Summary line with total overlapping reads and reads with soft-clipping

#### FASTA File (optional)

Contains soft-clipped sequences from reads at junctions:
- Separate entries for left and right clips
- Sequences in reference-forward orientation
- Headers with read name, side, strand, and CIGAR information

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