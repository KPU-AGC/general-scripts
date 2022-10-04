"""
species_aligner_analysis.py - This script takes a Genbank file containing sequences from several different 
species at a specific target site, aligns the sequences by species, and generates consensus sequences for
each species. 

Author: Michael Ke
Version: 1.0
Date: September 1st 2022
"""

from argparse import ArgumentParser
from pathlib import Path
import csv
import subprocess
from Bio import SeqIO, AlignIO, Seq

def parse_args(): 
    parser = ArgumentParser('Analyze and align multiple sequences for genus-level analysis')
    parser.add_argument(
        'gb_path', 
        action='store',
        type=Path,
        help='path to genbank file containing all data'
    )
    parser.add_argument(
        '--output',
        '-o',
        action='store',
        dest='output_path',
        default=None,
        type=Path,
        help='Output destination path',
    )
    parser.add_argument(
        '--min_cons',
        '-c',
        action='store',
        dest='min_cons',
        type=float,
        default=0.9,
        help='Minimum percentage (decimal format) of identical bases for consensus base to be called'
    )
    parser.add_argument(
        '--min_rep',
        '-r', 
        action='store',
        dest='min_rep',
        type=float,
        default=0.5,
        help='Minimum number of sequences represented for consensus to be generated',
    )
    args = parser.parse_args()

    if args.output_path is None: 
        args.output_path = args.gb_path.parent

    return args

def parse_gb(gb_path : Path) -> list: 
    """
    Parse a Genbank file and produce a dictionary containing lists of SeqRecords
    organised by species. 

    Parameters: 
    gb_path - path to the Genbank file

    Return: 
    species_dict - key corresponds to species name, lists of SeqRecords belonging 
    to that species. 
    """
    list_gb_data = [gb for gb in SeqIO.parse(gb_path, 'gb')]
    species_dict = {
        'unknown':[]
    }
    
    for gb_entry in list_gb_data: 
        species_key = gb_entry.annotations['organism']
        species_name = species_key.split(' ')[1]
        #If there's no clear species designation, append to unknown, 
        #Otherwise, append it to the correct species list
        if not(species_name in ['sp.', 'aff.', 'cf.']):
            if species_key not in species_dict:
                species_dict[species_key] = [gb_entry]
            else: 
                species_dict[species_key].append(gb_entry)
        else: 
             species_dict['unknown'].append(gb_entry)
    
    return species_dict

def get_consensus(alignment, min_con, min_rep):
    """
    Get the consensus sequence
    """
    cons_sequence = []
    
    #Determine sequence representation
    sequence_regions = []
    num_sequence = len(alignment)
    for sequence in alignment: 
        start_base = sequence.seq.ungap()[0]
        end_base = sequence.seq.ungap()[-1]
        start_index = sequence.seq.find(start_base) #inclusive
        end_index = sequence.seq.rfind(end_base)+1 #exclusive
        sequence_regions.append((start_index, end_index))
    
    seq_rep = []

    for position in range(alignment.get_alignment_length()): 
        seq_rep.append(0)
        for region in sequence_regions:
            if (position >= region[0]) and (position < region[1]): 
                seq_rep[position] = seq_rep[position] + 1
    
    seq_rep_ratio = [position/num_sequence for position in seq_rep]

    #Determine which sequences pass the min_rep score
    #Start with the left index
    #Finish with the right index
    num_sequence = len(alignment)
    left_index = 0
    reverse_right_index = -1
    while (seq_rep_ratio[left_index]) < min_rep: 
        left_index = left_index + 1
    while (seq_rep_ratio[reverse_right_index]) < min_rep: 
        reverse_right_index = reverse_right_index - 1
    right_index = alignment.get_alignment_length() + reverse_right_index + 1

    #Determine the dominant base at each position
    for position in range(left_index, right_index): 
        bases = alignment[:,position].upper()
        
        num_bases = seq_rep[position]

        counts = {
            'A':bases.count('A'),
            'C':bases.count('C'),
            'T':bases.count('T'),
            'G':bases.count('G'),
        }
        cons_base = max(counts, key=counts.get)
        if (counts[cons_base]/num_bases) >= min_con: 
            cons_sequence.append(cons_base)
        else: 
            cons_sequence.append('N')
    return ''.join(cons_sequence)

def main(): 
    args = parse_args()
    
    #Parse Genbank file data
    print('Parsing Genbank file..')
    species_dict = parse_gb(args.gb_path)
    print('Parsing complete!')

    #Generate metadata for entire analysis:
    print('Generating metadata...') 
    metadata_path = args.output_path.joinpath(f'{args.gb_path.stem}_metadata.csv')
    with open(metadata_path, 'w', newline='') as metadata_file: 
        num_species = len(species_dict.keys()) - 1 # -1 cause of 'unknown' key
        num_unknown = len(species_dict['unknown'])

        #Determine the number sequences available for each species
        seq_per_species = []
        for species in species_dict: 
            seq_per_species.append((species, len(species_dict[species])))
        seq_per_species.sort(key=lambda x: x[1], reverse=True)

        metadata_file.write(f'Total # of species: {str(num_species)}\n')
        metadata_file.write(f'# Sequences w/o species identity: {str(num_unknown)}\n')

        csv_writer = csv.writer(metadata_file)
        csv_writer.writerow(('species', '#_sequences'))
        csv_writer.writerows(seq_per_species)
    print('Metadata outputted!')

    #Output species fasta
    print('Outputting species fasta files...')
    species_path = args.output_path.joinpath('fasta')
    Path.mkdir(species_path, exist_ok=True)
    for species in species_dict: 
        species_fasta_path = species_path.joinpath(f'{species.replace(" ", "-")}.fasta')
        SeqIO.write(species_dict[species], species_fasta_path, 'fasta')
    print('Species fasta files outputted!')

    #Create alignments
    align_path = args.output_path.joinpath('aligned')
    Path.mkdir(align_path, exist_ok=True)
    print('Generating alignments..')
    for species_fasta_path in species_path.glob('*.fasta'): 
        print(f'{species_fasta_path.stem} being aligned...')
        aligned_fasta_path = align_path.joinpath(f'{species_fasta_path.stem}_aligned.fasta')
        mafft_args = [
            'mafft',
            '--auto',
            str(species_fasta_path),
        ]
        result = subprocess.run(mafft_args, capture_output=True)
        with open(aligned_fasta_path, 'w') as aligned_fasta: 
            decoded = result.stdout.decode('utf-8')
            aligned_fasta.write(decoded)
        print(f'{species_fasta_path.stem} aligned.')
    print('Alignments completed.')

    #Generate consensus sequences
    print('Generating consensus sequences...')
    consensus_path = args.output_path.joinpath('consensus')
    Path.mkdir(consensus_path, exist_ok=True)
    for alignment_fasta_path in align_path.glob('*.fasta'):
        species_name = alignment_fasta_path.stem.split('_')[0]
        print(f'Working on {species_name}')
        species_alignment = AlignIO.read(alignment_fasta_path, 'fasta')
        cons_seq = get_consensus(species_alignment, args.min_cons, args.min_rep)
        consensus_fasta_path = consensus_path.joinpath(f'{species_name}_consensus.fasta')
        with open(consensus_fasta_path, 'w') as consensus_fasta: 
            consensus_fasta.write(f'>{species_name}\n')
            consensus_fasta.write(f'{cons_seq}')
        print(f'{species_name} consensus: ')
        print(cons_seq)
    print('Consensus sequences generated!')

if __name__ == '__main__': 
    main()