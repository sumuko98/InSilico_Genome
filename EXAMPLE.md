# Junction Analyzer Example

This document demonstrates a complete workflow using the InSilico_Genome tools.

## Step 1: Remove Regions from Genome

First, we use `remove_regions.py` to remove specified regions from a genome:

```bash
python3 remove_regions.py sample_input.fasta regions_to_remove.txt \
    -o output_modified.fasta \
    -r removed_regions_report.txt
```

This creates:
- `output_modified.fasta`: The genome with regions removed
- `removed_regions_report.txt`: A report showing junction sites (Shifted Start column)

Example report excerpt:
```
Chromosome: NC_134080.1
----------------------------------------------------------------------------------------------------
Region Name          Start      End        Length     Shifted Start  
----------------------------------------------------------------------------------------------------
Region1              10         20         11         10             
Region2              50         60         11         39             
Region3              75         82         8          53             
```

The "Shifted Start" column shows where junctions were created: positions 10, 39, and 53.

## Step 2: Align Reads to Modified Genome

Align your sequencing reads to the modified genome using your preferred aligner:

```bash
# Example with BWA
bwa index output_modified.fasta
bwa mem output_modified.fasta reads_R1.fastq.gz reads_R2.fastq.gz | \
    samtools sort -o aligned_reads.bam
samtools index aligned_reads.bam
```

## Step 3: Analyze Reads at Junction Sites

Use `junction_analyzer.py` to find reads at the junction sites:

```bash
python3 junction_analyzer.py \
    --bam aligned_reads.bam \
    --chrom NC_134080.1 \
    --log removed_regions_report.txt \
    --out-tsv junction_reads.tsv \
    --out-fasta softclip_sequences.fasta
```

### TSV Output Format

The TSV file contains information about reads at junction sites:

```
qname                    chrom         ref_start  J_MOD  strand  cigar      left_clip  right_clip
read1_spanning_junction  NC_134080.1   5          10     +       10M5S      0          5
read2_at_junction        NC_134080.1   10         10     +       3S20M      3          0
read3_reverse_junction   NC_134080.1   39         39     -       5S15M2S    5          2
# Summary: total_overlapping=3, with_any_softclip=3
```

Columns:
- `qname`: Read name
- `chrom`: Chromosome
- `ref_start`: Read start position (1-based)
- `J_MOD`: Junction position where the read was found
- `strand`: Read strand (+/-)
- `cigar`: CIGAR string
- `left_clip`: Number of soft-clipped bases on the left
- `right_clip`: Number of soft-clipped bases on the right

### FASTA Output Format

The FASTA file contains soft-clipped sequences in reference-forward orientation:

```
>read1_spanning_junction|side=right|strand=+|cigar=10M5S
GCTAT
>read2_at_junction|side=left|strand=+|cigar=3S20M
AGC
>read3_reverse_junction|side=left|strand=-|cigar=5S15M2S
TTAGC
>read3_reverse_junction|side=right|strand=-|cigar=5S15M2S
GC
```

Note: For reverse-strand reads, sequences are reverse-complemented to reference-forward orientation.

## Understanding Junction Detection

A read is considered "at the junction" if:

1. **It ends immediately before the junction**: The read's end position equals the junction position
2. **It starts exactly at the junction**: The read's start position equals the junction position

This ensures we capture reads that span or are adjacent to the removed regions.

## Analysis Tips

1. **Soft-clip analysis**: Soft-clipped sequences may contain parts of the removed regions or indicate structural variations
2. **Strand consideration**: The tool correctly handles both forward (+) and reverse (-) strand reads
3. **Multiple junctions**: Analyze each chromosome separately to examine reads at all junction sites
4. **Summary statistics**: The summary line in the TSV shows how many reads have soft-clipping, which can indicate junction complexity

## Example Analysis Workflow

```bash
# Analyze all chromosomes
for chrom in NC_134080.1 NC_134081.1 NC_134082.1; do
    python3 junction_analyzer.py \
        --bam aligned_reads.bam \
        --chrom $chrom \
        --log removed_regions_report.txt \
        --out-tsv junction_${chrom}.tsv \
        --out-fasta softclips_${chrom}.fasta
done

# Combine results
cat junction_*.tsv > all_junctions.tsv

# Analyze soft-clipped sequences (e.g., BLAST against original regions)
cat softclips_*.fasta > all_softclips.fasta
```
