# KPU AGC General Resources
## Introduction
Welcome! This repository contains general scripts used throughout the projects at the Kwantlen Polytechnic University Applied Genomics Centre. Scripts are organized into directories based on their function. A brief description of each script is listed below.


Additionally, the [wiki](https://github.com/KPU-AGC/general-resources/wiki) contains documentation for each of the scripts as well as general procedures and guidelines for maintaining the bioinformatics resources of the lab.

## blast
Scripts and documents related to the use of NCBI BLAST+ 2.12.0.


| Script | Description |
| -------- | -------- |
|**blast_commands.txt** | contains commonly used commands when working with the NCBI BLAST+ 2.12.0 program |
|**generate_taxid_map.py** | generate a taxid file from Genbank file containing all sequences of interest |
|**process_genbank_db.py** | generate both a .fasta file containing all sequences in Genbank file, as well as a metadata .csv file |

## examples
Examples of how we use common Python modules and documentation templates. 


| Script | Description |
| -------- | -------- |
| **argparse_example.py** | contains example implementation of argparse |
| **docstrings_example.py** | contains example docstring formats for our scripts |
| **pathlib_example.py** | contains commonly used code when working with pathlib module |
| **slurm_scheduler_example.sh** | contains example of slurm scheduler script |
| **template.py** | template of our Python scripts |

## miscellaneous
Miscellaneous scripts for dealing with common file types. 


| Script | Description |
| -------- | -------- |
| **batch_rename.py** | used to sanitize SeqStudio ab1 file names to fit the formats required for our scripts |
| **batch_reverse_complement.py** | generate reverse complements of several sequences |
| **convert_gb_fasta.py** | extract .fasta sequences from Genbank files |
| **bisearch_primer_design.py** | design bisulfite PCR primers for a given target region |
| **generate_sequence.py** | in-silico generation of random DNA sequences |
| **read_sim_vcf_prep.py** |  |
| **calc_ta.py** | calculate melting temperatures of several primer sets |

## sanger-processing
Scripts related to working with SeqStudio ab1 files.

 
| Script | Description |
| -------- | -------- |
| **sanger_qc.py** | automated QC of Sanger sequences |
| **sanger_sequence_trim.py** | automated trimming of Sanger sequences (SeqStudio ab1 files) |
| **generate_seqstudio_qc.py** | generate SeqStudio QC .csv file from solely the ab1 files (used if the original QC .csv is lost) |


## sequence-analysis
Scripts related to sequence analysis tasks. 


| Script | Description |
| -------- | -------- |
| **species_aligner_analysis.py** | from a Genbank file containing multiple entries, generate alignments for each species within the GenBank file. |
