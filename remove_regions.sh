#!/bin/bash
# Wrapper script to remove genomic regions from Nicotiana Tabacum genome

set -e  # Exit on error

# Default values
GENOME_FILE="Ntab_nuclear.fna"
REGIONS_FILE="regions_to_remove.txt"
OUTPUT_PREFIX="Ntab_nuclear_modified"

# Function to display usage
usage() {
    echo "Usage: $0 [-g genome_file] [-r regions_file] [-o output_prefix]"
    echo ""
    echo "Options:"
    echo "  -g    Genome file in FASTA format (default: Ntab_nuclear.fna)"
    echo "  -r    Regions file with regions to remove (default: regions_to_remove.txt)"
    echo "  -o    Output prefix for generated files (default: Ntab_nuclear_modified)"
    echo "  -h    Display this help message"
    echo ""
    echo "Example:"
    echo "  $0 -g Ntab_nuclear.fna -r my_regions.txt -o output"
    echo ""
    echo "Regions file format (tab or space separated):"
    echo "  region_name    start_position    end_position"
    echo ""
    echo "Output files:"
    echo "  {output_prefix}_modified.fna         - Modified genome sequence"
    echo "  {output_prefix}_removed_regions.txt  - Report of removed regions"
    exit 1
}

# Parse command line arguments
while getopts "g:r:o:h" opt; do
    case $opt in
        g)
            GENOME_FILE="$OPTARG"
            ;;
        r)
            REGIONS_FILE="$OPTARG"
            ;;
        o)
            OUTPUT_PREFIX="$OPTARG"
            ;;
        h)
            usage
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            usage
            ;;
    esac
done

# Check if Python script exists
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/remove_genomic_regions.py"

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: Python script not found at $PYTHON_SCRIPT" >&2
    exit 1
fi

# Check if input files exist
if [ ! -f "$GENOME_FILE" ]; then
    echo "Error: Genome file '$GENOME_FILE' not found!" >&2
    echo "Please specify a valid genome file with -g option" >&2
    exit 1
fi

if [ ! -f "$REGIONS_FILE" ]; then
    echo "Error: Regions file '$REGIONS_FILE' not found!" >&2
    echo "Please specify a valid regions file with -r option" >&2
    echo ""
    echo "You can use example_regions.txt as a template:"
    echo "  cp example_regions.txt regions_to_remove.txt"
    echo "  # Edit regions_to_remove.txt with your regions"
    echo "  $0"
    exit 1
fi

# Run the Python script
echo "=========================================="
echo "Genomic Regions Removal Tool"
echo "=========================================="
echo "Genome file: $GENOME_FILE"
echo "Regions file: $REGIONS_FILE"
echo "Output prefix: $OUTPUT_PREFIX"
echo ""

python3 "$PYTHON_SCRIPT" "$GENOME_FILE" "$REGIONS_FILE" "$OUTPUT_PREFIX"

echo ""
echo "=========================================="
echo "Process completed successfully!"
echo "=========================================="
