"""
species_aligner_analysis.py - This script takes a Genbank file containing sequences from several different 
species at a specific target site, aligns the sequences by species, and generates consensus sequences for
each species. 

Classes: 
GenbankHandler : object that handles Genbank files

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

def main(): 
    args = parse_args()
    species_dict = parse_gb(args.gb_path)

    #Generate metadata for entire analysis: 
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

    #Output species fasta
    species_path = args.output_path.joinpath('fasta')
    Path.mkdir(species_path, exist_ok=True)
    for species in species_dict: 
        species_fasta_path = species_path.joinpath(f'{species.replace(" ", "-")}.fasta')
        SeqIO.write(species_dict[species], species_fasta_path, 'fasta')
    
    #Create alignments
    align_path = args.output_path.joinpath('aligned')
    

if __name__ == '__main__': 
    main()