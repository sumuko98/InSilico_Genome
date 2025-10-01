# Quick Start Guide for Genomic Region Removal Tool

## Example Usage for Nicotiana Tabacum

### 1. Prepare Your Genome File
Place your `Ntab_nuclear.fna` file in the repository directory.

### 2. Create Your Regions File
Create a file named `regions_to_remove.txt` with the regions you want to remove:

```
# Example regions for Nicotiana Tabacum
# Format: region_name    start_position    end_position

# Remove telomeric regions
Telomere_Chr1_left      1               10000
Telomere_Chr1_right     4600000         4610000

# Remove repetitive sequences
Repeat_region_1         125000          126500
Repeat_region_2         250000          251000

# Remove centromeric regions
Centromere_Chr1         2300000         2305000
```

### 3. Run the Tool

**Option A: Using the bash wrapper (recommended)**
```bash
./remove_regions.sh -g Ntab_nuclear.fna -r regions_to_remove.txt -o Ntab_modified
```

**Option B: Using Python directly**
```bash
python3 remove_genomic_regions.py Ntab_nuclear.fna regions_to_remove.txt Ntab_modified
```

### 4. Check the Output

Two files will be created:

**Modified Genome:** `Ntab_modified_modified.fna`
- Contains the genome with specified regions removed
- Maintains FASTA format
- Ready for downstream analysis

**Removal Report:** `Ntab_modified_removed_regions.txt`
- Lists all removed regions with original coordinates
- Shows before/after statistics
- Documents the exact changes made

## Understanding the Output

### Removal Report Example:
```
Genomic Regions Removal Report
================================================================================
Date: 2024-10-01 12:00:00
Original sequence length: 4,610,000 bp
Final sequence length: 4,575,500 bp
Total bases removed: 34,500 bp
Number of regions removed: 6

Removed Regions (coordinates are 1-based, inclusive):
--------------------------------------------------------------------------------
Region Name              Original Start  Original End    Length (bp) 
--------------------------------------------------------------------------------
Telomere_Chr1_left       1               10,000          10,000      
Repeat_region_1          125,000         126,500         1,501       
Repeat_region_2          250,000         251,000         1,001       
Centromere_Chr1          2,300,000       2,305,000       5,001       
Telomere_Chr1_right      4,600,000       4,610,000       10,001      

Note: All coordinates refer to positions in the ORIGINAL sequence.
```

### Key Points:
- **All coordinates in the report refer to the ORIGINAL genome** - this makes it easy to cross-reference with other analyses
- Regions are processed in order from start to end
- The tool automatically adjusts internal coordinates to maintain accuracy
- No manual coordinate conversion needed!

## Common Use Cases

### 1. Remove Telomeric Regions
```
Telomere_left    1       5000
Telomere_right   9995000 10000000
```

### 2. Remove Centromeric Regions
```
Centromere_Chr1  5000000  5010000
Centromere_Chr2  3000000  3008000
```

### 3. Remove Repetitive Elements
```
Repeat_LTR_1     100000   105000
Repeat_LTR_2     500000   505000
Repeat_SINE_1    1000000  1001000
```

### 4. Remove Low Quality Regions
```
LowQual_region1  2500000  2510000
Gap_region1      3000000  3002000
```

## Tips

1. **Sort your regions:** The tool handles unsorted regions, but sorted input makes the report easier to read
2. **Use descriptive names:** This helps identify regions in the report
3. **Check for overlaps:** The tool will warn you if regions overlap
4. **Validate coordinates:** Make sure start < end for each region
5. **Backup your original:** Always keep a copy of the original genome file

## Troubleshooting

**Error: Genome file not found**
- Make sure the genome file path is correct
- Check that you're in the right directory

**Warning: Overlapping regions**
- Review your regions file for overlaps
- Overlapping regions may indicate an error in your input

**Error: Invalid coordinates**
- Ensure start position ≤ end position
- Check that positions are within the genome length
- Verify coordinates are positive integers

## Next Steps

After removing regions, you can:
1. Use the modified genome for assembly validation
2. Run annotations on the cleaned genome
3. Compare with other genome assemblies
4. Perform phylogenetic analyses
5. Use in any downstream bioinformatics pipeline

The modified genome is a standard FASTA file and can be used with any tool that accepts FASTA input.
