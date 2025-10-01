# Example Usage Scenarios

This document provides practical examples of using the genomic region removal tool.

## Scenario 1: Removing Telomeres

Create `telomeres.txt`:
```
Telomere_Chr1_5prime     1          15000
Telomere_Chr1_3prime     4595000    4610000
```

Run:
```bash
./remove_regions.sh -g Ntab_nuclear.fna -r telomeres.txt -o Ntab_no_telomeres
```

## Scenario 2: Removing Repeat Regions

Create `repeats.txt`:
```
LTR_Retro_1      100000    125000
LINE_element_1   250000    255000
SINE_element_1   500000    502000
```

Run:
```bash
python3 remove_genomic_regions.py Ntab_nuclear.fna repeats.txt clean_genome
```

## Scenario 3: Removing Centromeres and Gaps

Create `structural_regions.txt`:
```
# Centromeric regions
Centromere_Chr1         2300000    2350000

# Assembly gaps  
Gap_scaffold_1          3500000    3500100
```

Execute:
```bash
./remove_regions.sh -g Ntab_nuclear.fna -r structural_regions.txt -o cleaned
```

## Important Notes

1. **Coordinates**: Always use coordinates from the ORIGINAL genome
2. **Testing**: Test with small regions first
3. **Backup**: Keep original genome files safe
4. **Verification**: Review the removal report after processing

## Common Region Types

### Telomeres
```
Telomere_left    1       10000
Telomere_right   9990000 10000000
```

### Repeats
```
Repeat_LTR_1     200000  225000
Repeat_LINE_1    400000  415000
```

### Quality Control
```
LowQual_1        100000  101000
HighN_region     500000  501500
```

For detailed documentation, see README.md, QUICKSTART.md, and WORKFLOW.md.
