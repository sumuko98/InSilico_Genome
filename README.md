# InSilico_Genome

A tool for removing specified genomic regions from genome FASTA files while tracking original coordinates.

## Overview

This tool is designed to work with nuclear genome sequences (e.g., Nicotiana Tabacum - Ntab_nuclear.fna) and allows you to:
- Specify genomic regions to be removed
- Automatically name and track each region
- Maintain original coordinate references (preventing coordinate shifts)
- Generate a detailed report of removed regions with their original positions

## Features

- **Coordinate Preservation**: All removed regions are documented with their original genomic coordinates
- **Sequential Processing**: Regions are processed in order, with coordinate adjustments tracked for each removal
- **Comprehensive Reporting**: Generates a detailed report showing:
  - Original positions of removed regions
  - Length of each removed region
  - Total bases removed
  - Before/after sequence statistics
- **Flexible Input**: Accepts tab-separated or space-separated region files
- **Validation**: Checks for overlapping regions and invalid coordinates

## Quick Start

### Prerequisites

- Python 3.6 or higher
- Bash (for the wrapper script)

### Basic Usage

1. **Prepare your regions file** (tab or space separated):
   ```
   Region1    1000    2000
   Region2    5000    5500
   Region3    10000   10500
   ```

2. **Run the removal tool**:
   ```bash
   # Using the bash wrapper (recommended)
   ./remove_regions.sh -g Ntab_nuclear.fna -r regions_to_remove.txt -o output
   
   # Or directly with Python
   python3 remove_genomic_regions.py Ntab_nuclear.fna regions_to_remove.txt output
   ```

3. **Check the outputs**:
   - `output_modified.fna` - Modified genome with regions removed
   - `output_removed_regions.txt` - Detailed report of removed regions

## Usage Examples

### Example 1: Using default filenames
```bash
# Create your regions file
cp example_regions.txt regions_to_remove.txt
# Edit regions_to_remove.txt with your specific regions

# Run with defaults (expects Ntab_nuclear.fna in current directory)
./remove_regions.sh
```

### Example 2: Custom files
```bash
./remove_regions.sh -g my_genome.fna -r my_regions.txt -o my_output
```

### Example 3: Direct Python script
```bash
python3 remove_genomic_regions.py input.fna regions.txt result
```

## Input File Formats

### Genome File (FASTA format)
```
>Chromosome1
ATCGATCGATCGATCG...
```

### Regions File
Tab-separated or space-separated values with three columns:

```
# region_name    start_position    end_position
Region1          1000              2000
Region2          5000              5500
TelomericRegion  10000             10500
```

**Important Notes:**
- Coordinates are 1-based and inclusive
- Start position must be ≤ end position
- All positions refer to the ORIGINAL genome sequence
- Lines starting with `#` are treated as comments
- Empty lines are ignored

## Output Files

### Modified Genome File (`*_modified.fna`)
FASTA file with specified regions removed, maintaining FASTA format standards (80 characters per line).

### Removal Report (`*_removed_regions.txt`)
Detailed report including:
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
Region1              1,000           2,000           1,001       
Region2              5,000           5,500           501         
Region3              10,000          10,500          501         

Note: All coordinates refer to positions in the ORIGINAL sequence.
      Regions are removed in order from start to end of the genome.
```

## How It Works

1. **Region Parsing**: The tool reads your regions file and validates all coordinates
2. **Sequential Removal**: Regions are processed from start to end of the genome
3. **Coordinate Tracking**: Each removal is tracked with:
   - Original coordinates (in the input genome)
   - Adjusted coordinates (accounting for previous removals)
   - Region length and name
4. **Report Generation**: A comprehensive report is created documenting all changes

### Coordinate System

The tool maintains two coordinate systems:
- **Original Coordinates**: Positions in the input genome (used in the report)
- **Adjusted Coordinates**: Positions accounting for previous removals (used internally)

This ensures that all reported positions always refer back to the original genome, making it easy to:
- Cross-reference with annotations
- Compare with other analyses
- Understand exactly what was removed

## Command-Line Options

### Bash Wrapper Script (`remove_regions.sh`)
```
Options:
  -g    Genome file in FASTA format (default: Ntab_nuclear.fna)
  -r    Regions file with regions to remove (default: regions_to_remove.txt)
  -o    Output prefix for generated files (default: Ntab_nuclear_modified)
  -h    Display help message
```

### Python Script (`remove_genomic_regions.py`)
```
Usage: python3 remove_genomic_regions.py <genome_file> <regions_file> <output_prefix>
```

## Error Handling

The tool includes comprehensive error checking:
- **Invalid coordinates**: Automatically corrected or skipped with warnings
- **Overlapping regions**: Detected and reported
- **Out-of-bounds positions**: Adjusted to valid ranges
- **Missing files**: Clear error messages
- **Invalid file formats**: Graceful handling with helpful messages

## Example Workflow for Nicotiana Tabacum

```bash
# 1. Place your genome file
#    Ntab_nuclear.fna

# 2. Create regions file based on your analysis
cat > regions_to_remove.txt << EOF
Telomere1        1           5000
RepeatRegion1    125000      126000
Telomere2        9995000     10000000
EOF

# 3. Run the tool
./remove_regions.sh

# 4. Review the report
cat Ntab_nuclear_modified_removed_regions.txt

# 5. Use the modified genome
# The modified genome is in Ntab_nuclear_modified_modified.fna
```

## Files in This Repository

- `remove_genomic_regions.py` - Main Python script
- `remove_regions.sh` - Bash wrapper script for convenience
- `example_regions.txt` - Example regions file template
- `README.md` - This documentation

## Contributing

Feel free to submit issues or pull requests if you have suggestions for improvements.

## License

This project is open source and available for academic and research use.