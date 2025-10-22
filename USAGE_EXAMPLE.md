# Junction Analyzer Usage Example

This document provides a step-by-step example of using the InSilico_Genome tools.

## Step 1: Remove Regions from Genome

First, use `remove_regions.py` to remove specified regions from your genome:

```bash
python3 remove_regions.py sample_input.fasta regions_to_remove.txt \
    -o modified_genome.fasta \
    -r removed_regions_log.txt
```

This creates:
- `modified_genome.fasta`: The genome with regions removed
- `removed_regions_log.txt`: A report showing which regions were removed and their shifted start positions

Example output from `removed_regions_log.txt`:
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

Chromosome: NC_134081.1
----------------------------------------------------------------------------------------------------
Region Name          Start      End        Length     Shifted Start  
----------------------------------------------------------------------------------------------------
RegionX              5          25         21         5              

Total regions removed: 1
```

## Step 2: Analyze Reads at Junction Sites

Next, use `junction_analyzer.py` to analyze reads that align at the junction sites:

### Option A: With Raw Reads (Recommended)

If you have raw reads that need to be aligned:

```bash
python3 junction_analyzer.py \
    --log removed_regions_log.txt \
    --reference modified_genome.fasta \
    --reads your_reads.fastq \
    --preset map-ont \
    --out-tsv junctions_output.tsv \
    --out-sam aligned_reads.sam \
    --out-fasta
```

This will:
1. Parse the log file to identify junction sites
2. Align reads to the modified genome using minimap2
3. Identify reads at junction sites
4. Extract soft-clipped sequences
5. Output results to TSV

### Option B: With Pre-aligned Reads

If you already have aligned reads in SAM format:

```bash
python3 junction_analyzer.py \
    --log removed_regions_log.txt \
    --reference modified_genome.fasta \
    --sam pre_aligned.sam \
    --out-tsv junctions_output.tsv \
    --out-fasta
```

### Analyzing a Specific Chromosome

To analyze only a specific chromosome:

```bash
python3 junction_analyzer.py \
    --log removed_regions_log.txt \
    --reference modified_genome.fasta \
    --reads your_reads.fastq \
    --chrom NC_134080.1 \
    --out-tsv nc134080_junctions.tsv
```

## Understanding the Output

The output TSV file contains information about each read found at a junction site:

| Column | Description |
|--------|-------------|
| `read_name` | Name/ID of the read |
| `chromosome` | Chromosome where the read aligns |
| `junction_site` | Position of the junction site (0-based) |
| `read_start` | Start position of read alignment (0-based) |
| `read_end` | End position of read alignment (0-based, inclusive) |
| `mapping_quality` | MAPQ score from alignment |
| `cigar` | CIGAR string describing the alignment |
| `left_softclip_length` | Number of bases soft-clipped on left end |
| `right_softclip_length` | Number of bases soft-clipped on right end |
| `left_softclip_seq` | Sequence of left soft-clipped bases (if --out-fasta used) |
| `right_softclip_seq` | Sequence of right soft-clipped bases (if --out-fasta used) |

### Example Output

```tsv
read_name	chromosome	junction_site	read_start	read_end	mapping_quality	cigar	left_softclip_length	right_softclip_length	left_softclip_seq	right_softclip_seq
read001	NC_134080.1	9	5	40	60	10S30M5S	10	5	ACGTACGTAC	TGCAT
read002	NC_134080.1	38	30	50	55	5S20M	5	0	GCGCG	
read003	NC_134081.1	4	0	25	60	25M3S	0	3		CGT
```

## Junction Site Calculation

Junction sites are calculated as `Shifted Start - 1`:

From the example above:
- For Region1 with Shifted Start = 10, the junction site is at position 9
- For Region2 with Shifted Start = 39, the junction site is at position 38
- For Region3 with Shifted Start = 53, the junction site is at position 52
- For RegionX with Shifted Start = 5, the junction site is at position 4

A read is considered "at the junction" if it aligns at or overlaps the junction site, which typically indicates that the read spans across where a removed region used to be.

## Interpreting Soft Clips

Soft-clipped bases (indicated by 'S' in the CIGAR string) are parts of the read that don't align to the reference. At junction sites, these can be particularly interesting because they may represent:

1. **Sequence from the removed region**: If a read spans a junction, the soft-clipped portion might contain sequence that was removed
2. **Sequencing errors**: Especially at read ends
3. **Structural variations**: Other genomic variations in the sample

The `--out-fasta` option extracts these sequences so you can analyze them further.

## Requirements

Make sure you have the required dependencies installed:

```bash
pip install mappy pysam
```

- `mappy`: Python binding for minimap2 aligner (only needed if aligning reads)
- `pysam`: Python interface for SAM/BAM files (required for analysis)
