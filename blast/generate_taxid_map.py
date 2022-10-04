#!/usr/bin/env python3
"""
Purpose: Generate a taxid map file for making a custom BLAST db
"""
__author__ = "Michael Ke; Erick Samera"
__version__ = "1.0.0"
__comment__ = 'stable enough'

# MODULES
# --------------------------------------------------
from argparse import (
    Namespace,
    ArgumentParser,
    RawDescriptionHelpFormatter)
from pathlib import Path
# --------------------------------------------------
from Bio import SeqIO
# --------------------------------------------------
# ARGPARSE
# --------------------------------------------------
def get_args() -> Namespace:
    """ Get command-line arguments """

    parser = ArgumentParser(
        #usage='%(prog)s',
        description="Generate a taxid map from .gb file data.",
        epilog=f"v{__version__} : {__author__} | {__comment__}",
        formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument(
        'input_path',
        type=Path,
        help="path of input (.gb) file")
    parser.add_argument(
        '-o',
        '--out',
        dest='output_path',
        metavar='PATH',
        type=Path,
        default=None,
        help="path of output directory (Default: in-place)")

    args = parser.parse_args()

    # HANDLE EXCEPTIONS
    # --------------------------------------------------
    args.input_path = args.input_path.resolve()

    # throw an error if the input file is not a file
    if not args.input_path.is_file():
        parser.error("Your input is not a file.")

    # throw an error if the input file doesn't exist
    if not args.input_path.exists():
        parser.error("The input (.gb) file doesn't exist.") 

    # resolve the output path if it's defined, else use the working directory
    if args.output_path:
        args.output_path = args.output_path.resolve()
    else:
        args.output_path = Path.cwd()

    return args

# --------------------------------------------------
def main():
    """ Generate a taxid map from .gb file data. """
    args = get_args()
    
    num_seq: int = 0
    num_unidentified: int = 0

    taxid_map_path: Path = args.output_path.joinpath(args.input_path.stem + '_taxid_map.txt')

    with open(taxid_map_path, 'w', encoding='UTF8') as taxid_map_file:
        for genbank_record in SeqIO.parse(args.input_path, 'gb'):
            try:
                annotations: str = genbank_record.annotations['accessions'][0]
                # in db_xref, find the entry with taxon and get the value associated with it
                taxid: str = [db_xref.split(':')[1] for db_xref in genbank_record.features[0].qualifiers['db_xref'] if 'taxon' in db_xref][0]
                taxid_map_file.write(f"{annotations} {taxid}\n")
                num_seq += 1
            except KeyError:
                # should handle cases where db_xref or accessions doesn't exist at all
                num_unidentified += 1
            except IndexError:
                # should handle cases where accessions list or taxid list is empty (i.e., no taxon in db_xref)
                num_unidentified += 1

    print(f'Total number of sequences: {num_seq}')
    print(f'Total number of sequences with no species: {num_unidentified}')
# --------------------------------------------------
if __name__ == "__main__":
    main()
