# InSilico_Genome

A tool for processing multi-chromosome FASTA files by removing specified genomic regions.

## Features

- Process multi-FASTA files with multiple chromosomes
- Remove specific regions from each chromosome based on coordinates
- Generate detailed reports of removed regions with coordinate transformation tracking
- Track "Shifted Start" positions to help map coordinates between original and modified sequences
- Preserve original chromosome headers
- Handle chromosomes with no regions to remove

## Installation

No special installation required. Just Python 3.6+ standard library.

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
- Start and end coordinates (1-based, original sequence coordinates)
- Length of each removed region
- **Shifted Start**: The position where each region would start in the modified sequence (useful for coordinate transformation)
- Total count of removed regions per chromosome

The "Shifted Start" column helps track coordinate transformations. For example, if Region1 (positions 10-20) is removed, a subsequent Region2 starting at position 50 in the original sequence would have a shifted start of 39 in the modified sequence (50 - 11 bp removed = 39).

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