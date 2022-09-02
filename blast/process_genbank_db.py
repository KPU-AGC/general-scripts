"""
process_genbank_db.py: GenBank Processing Scripts

This script performs two functions: 
1) Creates .fasta file containing sequences from an input GenBank file
2) Generates a metadata file describing each accession of the GenBank file. 

This tool accepts the path to a single GenBank file. 

Requires SeqIO from BioPython ('biopython') and 'pandas'.

Author: Michael Ke
Version: 1.2.0
Date Last Modified: 2022-08-29
"""

# MODULES
# --------------------------------------------------
from argparse import (
    Namespace,
    ArgumentParser,
    RawDescriptionHelpFormatter)
from pathlib import Path
import pandas as pd
from Bio import SeqIO

# ARGPARSE
# --------------------------------------------------
def get_args() -> Namespace:
    """ Get command-line arguments """

    parser = ArgumentParser(
        description='This is an example description',
        epilog='v1.1.0: <insert name here>',
        formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument(
        'input_path',
        type=Path,
        help='path of input')
    parser.add_argument(
        '-o',
        '--out',
        dest='output_path',
        type=Path,
        default=None,
        help='path of output')
    args = parser.parse_args()

    # HANDLE EXCEPTIONS
    # --------------------------------------------------
    args.input_path = args.input_path.resolve()

    # resolve the output path if it's defined
    if args.output_path:
        args.output_path = args.output_path.resolve()

    return args
# --------------------------------------------------
def output_fasta(list_fasta: list, path: Path) -> None:
    """
    Function creates .fasta files
    Parameters: 
        list_fasta (list): list containing fasta strings
        path (Path) - path without suffix
    Returns: 
        None
    """
    with open(path, 'w', encoding='UTF8') as output_file:
        for fasta in list_fasta: 
            output_file.write(fasta)

    return None
def _retrieve_metadata(gb_entry) -> dict:
    """
    Parse GenBank entry to obtain relevant metadata information

    Parameters: 
        gb_entry: SeqRecord object

    Returns: 
        metadata - tuple of metadata
    """ 
    def get_source_index(features) -> int:
        """
        Get the index of the 'source' entry for GenBank entry

        Parameters: 
            features - feature table of a GenBank entry
        Returns: 
            index - int - position of 'source' entry in feature table
        """
        index = None
        for feature in features: 
            if feature.type == "source":
                index = features.index(feature)
        return index
    def get_source_qualifiers(source_qual) -> list:
        """
        Get qualifiers of interest for source

        Parameters: 
            source_qual - qualifiers in source

        Returns: 
            qual - list - contains qualifiers of interest
        """
        quals = []
        interest = ('isolate', 'host', 'country')
        for qual in interest: 
            if qual in source_qual:
                if len(source_qual[qual]) == 1: 
                    quals.append(source_qual[qual][0])
                else: 
                    quals.append(','.join(source_qual[qual]))
            else: 
                quals.append(None)
        return quals

    #Get qualifiers from 'source' feature
    source_index = get_source_index(gb_entry.features)
    source_qualifiers = get_source_qualifiers(gb_entry.features[source_index].qualifiers)

    metadata = {
        'acc':  gb_entry.id,
        'seq_len': len(gb_entry.seq),
        'desc': gb_entry.description,
        'organism': gb_entry.annotations['source'],
        'isolate': source_qualifiers[0],
        'host': source_qualifiers[1],
        'country': source_qualifiers[2],
        }
        
    return metadata
# --------------------------------------------------
def main() -> None:
    """ Insert docstring here """
    args = get_args()
    
    if args.input_path.is_file():
        #Continue program
        data = SeqIO.parse(args.input_path, 'gb')
        
        #fasta
        list_fasta = []

        #metadata
        metadata = {
            'acc': [],
            'seq_len': [],
            'desc': [],
            'organism': [],
            'isolate': [],
            'host': [],
            'country': [],
        }
        for entry in data: 
            list_fasta.append(entry.format('fasta'))
            meta = _retrieve_metadata(entry)
            
            # Add to metadata
            # For each key listed in the metadata dict above,
            # append the values in the retrieved metadata belonging to the same key
            for value in meta:
                metadata[value].append(meta[value])
        
        # DF
        print(len(metadata['acc']))
        print(len(metadata['seq_len']))
        print(len(metadata['desc']))
        print(len(metadata['organism']))
        print(len(metadata['isolate']))
        print(len(metadata['host']))
        print(len(metadata['country']))
        meta_df = pd.DataFrame(data=metadata)

        # Output
        output_fasta(list_fasta, args.output_path.joinpath(args.input_path.stem + '.fasta'))
        meta_df.to_csv(args.output_path.joinpath(args.input_path.stem + '_metadata.csv'), index=False)
    else: 
        print("Not a GenBank file.") 

# --------------------------------------------------
if __name__ == "__main__":
    main()
