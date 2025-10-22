# InSilico_Genome

A tool for processing multi-chromosome FASTA files by removing specified genomic regions and analyzing reads at junction sites.

## Features

- Process multi-FASTA files with multiple chromosomes
- Remove specific regions from each chromosome based on coordinates
- Generate detailed reports of removed regions
- Preserve original chromosome headers
- Handle chromosomes with no regions to remove
- Analyze reads at junction sites created by region removal
- Extract soft-clipped sequences at junctions

## Installation

### Basic Requirements
- Python 3.6+ standard library (for `remove_regions.py`)

### Junction Analyzer Requirements
For `junction_analyzer.py`, additional packages are needed:
```bash
pip install mappy pysam
```

These packages provide:
- `mappy`: Python binding for minimap2 aligner
- `pysam`: Python interface for SAM/BAM files

## Usage

### Basic Usage

```bash
python3 remove_regions.py <input_fasta> <regions_file> [options]
```

### Arguments

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

## Output

### Modified FASTA File

The output FASTA file contains all chromosomes with specified regions removed. The original chromosome headers are preserved.

### Report File

The report file contains:
- List of all removed regions for each chromosome
- Start and end coordinates (1-based)
- Length of each removed region
- Total count of removed regions per chromosome

## Sample Files

The repository includes sample files for testing:
- `sample_input.fasta`: Example multi-chromosome FASTA file
- `regions_to_remove.txt`: Example regions file

## How It Works

1. **Parse FASTA**: Reads the multi-FASTA file and extracts each chromosome sequence
2. **Parse Regions**: Reads the regions file and organizes regions by chromosome
3. **Remove Regions**: For each chromosome, removes specified regions while preserving the rest
4. **Write Output**: Generates modified FASTA file and detailed report

## Junction Analyzer Usage

After running `remove_regions.py`, use `junction_analyzer.py` to analyze reads at junction sites:

### Basic Usage

```bash
python3 junction_analyzer.py --log removed_regions_report.txt \
                              --reference output_modified.fasta \
                              --reads your_reads.fastq \
                              --out-tsv junctions_output.tsv
```

### Arguments

**Required:**
- `--log`: Removed regions log file (output from remove_regions.py)
- `--reference`: Modified reference genome FASTA (output from remove_regions.py)
- `--reads`: Reads file (FASTA or FASTQ) - required if --sam not provided
- `--sam`: Pre-aligned SAM file - if provided, skips alignment step

**Optional:**
- `--chrom`: Analyze specific chromosome only
- `--preset`: Minimap2 preset for alignment (default: map-ont)
- `--out-tsv`: Output TSV file (default: junctions_output.tsv)
- `--out-sam`: Output SAM file (default: aligned_reads.sam)
- `--out-fasta`: Include soft-clipped sequences in output

### What it does

1. **Parses junction sites**: Extracts "Shifted Start" positions from the log file and calculates junction sites (shifted start - 1)
2. **Maps reads**: Uses minimap2 (via mappy) to align reads to the modified genome
3. **Identifies junction reads**: Finds reads that align at or near junction sites
4. **Analyzes soft clips**: Extracts CIGAR information and soft-clipped sequences
5. **Outputs results**: Creates a TSV file with detailed information about each read at junctions

### Output Format

The output TSV file contains the following columns:
- `read_name`: Name of the read
- `chromosome`: Chromosome where the read aligns
- `junction_site`: Position of the junction site (0-based)
- `read_start`: Start position of the read alignment (0-based)
- `read_end`: End position of the read alignment (0-based, inclusive)
- `mapping_quality`: Mapping quality score
- `cigar`: CIGAR string of the alignment
- `left_softclip_length`: Length of soft clip at the left end
- `right_softclip_length`: Length of soft clip at the right end
- `left_softclip_seq`: Sequence of left soft clip (if --out-fasta specified)
- `right_softclip_seq`: Sequence of right soft clip (if --out-fasta specified)

### Example

```bash
# First, remove regions
python3 remove_regions.py sample_input.fasta regions_to_remove.txt \
    -o modified.fasta -r report.txt

# Then, analyze junctions
python3 junction_analyzer.py --log report.txt \
                              --reference modified.fasta \
                              --reads nanopore_reads.fastq \
                              --preset map-ont \
                              --out-fasta \
                              --out-tsv junctions.tsv
```

## Notes

- The script handles any number of chromosomes and regions
- Chromosomes with no regions to remove are included unchanged in the output
- Regions are specified using 1-based coordinates (biological standard)
- The script validates that input files exist before processing
- Junction sites are calculated as "Shifted Start - 1" from the removed regions report
- Reads are considered "at the junction" if they align at or overlap the junction site