def identify_reads(junctions, reads):
    identified_reads = []
    for j_mod in junctions:
        for read in reads:
            rstart, rend = read.start, read.end
            # Keep only reads that end immediately before the junction
            if rend == j_mod - 1:
                identified_reads.append(read)
            # Keep only reads that start exactly at the junction
            elif rstart + 1 == j_mod:
                identified_reads.append(read)
    return identified_reads
