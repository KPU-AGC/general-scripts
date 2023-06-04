#!/usr/bin/env python3
__description__ =\
"""
Purpose: Extracts sequences from GenBank (.gb) and output as fasta file.
"""
__author__ = ["Michael Ke", "Erick Samera"]
__version__ = "2.0.0"
__comments__ = "stable enough"
# --------------------------------------------------
from argparse import (
    Namespace,
    ArgumentParser,
    RawTextHelpFormatter)
from pathlib import Path
# --------------------------------------------------
from Bio import SeqIO
# --------------------------------------------------
def get_args() -> Namespace:
    """ Get command-line arguments """

    parser = ArgumentParser(
        description=__description__,
        epilog=f"v{__version__} : {__author__} | {__comments__}",
        formatter_class=RawTextHelpFormatter)
    parser.add_argument('input',
        metavar='<PATH>',
        type=Path,
        nargs='+',
        help='path of GenBank file (.gb) or directory containing Genbank files')
    parser.add_argument('-o', '--out', dest='output_path',
        type=Path,
        default=None,
        help='directory to output .fasta files -- output in current working directory otherwise')

    # --------------------------------------------------
    args = parser.parse_args()

    if len(args.input)==1 and args.input[0].is_dir(): args.input = [file for file in args.input[0].glob('*.gb')]
    args.input = [file_path for file_path in args.input if Path(file_path).is_file()]
    if not args.output_path: args.output_path = Path.cwd()
    args.output_path.mkdir(exist_ok=True)
    if not args.input: parser.error("Invalid input. No files detected!")

    return args
# --------------------------------------------------
def main():
    """ Does the thing. """

    args = get_args()

    for genbank_file in args.input: 
        try: SeqIO.write(SeqIO.read(genbank_file, 'gb'), args.output.joinpath(f"{genbank_file.stem}.fasta"), 'fasta')
        except ValueError: print(f"ERROR: {genbank_file.name} may not be a GenBank (.gb) file.")

# --------------------------------------------------
if __name__ == "__main__":
    main()
