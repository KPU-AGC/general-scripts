#!/usr/bin/env python3
"""
Author : Michael Ke, Erick Samera
Date   : 2022-08-22
Purpose: Extracts sequences from GenBank (.gb) and output as fasta file
"""

# --------------------------------------------------
from argparse import (
    Namespace,
    ArgumentParser,
    RawDescriptionHelpFormatter)
from pathlib import Path
from Bio import SeqIO
# --------------------------------------------------
def get_args() -> Namespace:
    """ Get command-line arguments """

    parser = ArgumentParser(
        description='Program takes a .gb file/directory of .gb files and outputs .fasta',
        #usage='%(prog)s',
        epilog='v1.1.0: Michael Ke, Erick Samera',
        formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument(
        'input_path',
        type=Path,
        help='path of .gb file/directory of .gb files')
    parser.add_argument(
        '-o',
        '--out',
        dest='output_path',
        type=Path,
        default=None,
        help='directory to output .fasta files -- output in-place otherwise')
    args = parser.parse_args()

    # resolve the input path
    args.input_path = args.input_path.resolve()

    # resolve the output path if it's defined
    if args.output_path:
        args.output_path = args.output_path.resolve()

    return args
# --------------------------------------------------
def main():
    """ main """
    args = get_args()
    # if the input is a file
    if args.input_path.is_file():
        try:
            # set the output path
            if args.output_path:
                output_path = args.output_path
            else:
                output_path = args.input_path.parent

            # read and then write
            genbank_file = SeqIO.read(args.input_path, 'gb')
            SeqIO.write(
                genbank_file,
                output_path.joinpath(f'{args.input_path.stem}.fasta'),
                'fasta')
        except ValueError:
            print(f"ERROR: {args.input_path.name} may not be a GenBank (.gb) file.")
    # if the input is a directory
    elif args.input_path.is_dir():
        for genbank_file_path in args.input_path.glob('*.gb'):
            try:
                # set the output path
                if args.output_path:
                    output_path = args.output_path
                else:
                    output_path = args.input_path

                # read and then write
                genbank_file = SeqIO.read(genbank_file_path, 'gb')
                SeqIO.write(
                    genbank_file,
                    output_path.joinpath(f'{genbank_file_path.stem}.fasta'),
                    'fasta')
            except ValueError:
                print(f"ERROR: {genbank_file.name} may not be a GenBank (.gb) file.")

    # if the input is somehow neither a file nor a directory
    else:
        print("FATAL ERROR: Your input was neither a file nor a directory!")

# --------------------------------------------------
if __name__ == "__main__":
    main()