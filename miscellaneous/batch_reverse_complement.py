#!/usr/bin/env python3
__description__ =\
"""
Purpose: Script to quickly generate reverse complement fastas.
"""
__author__ = "Michael Ke; Erick Samera"
__version__ = "1.0.0"
__comment__ = 'stable'
#TODO: deal with multi-FASTA input

# --------------------------------------------------
from argparse import (
    Namespace,
    ArgumentParser,
    RawTextHelpFormatter)
from pathlib import Path
# --------------------------------------------------
from Bio import Seq, SeqIO
# --------------------------------------------------
def get_args() -> Namespace:
    """ Get command-line arguments """

    parser = ArgumentParser(
        description=f"{__description__}",
        epilog=f"v{__version__} : {__author__} | {__comment__}",
        formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        'input_path',
        type=Path,
        help="path of directory containing single-entry .fasta files")
    parser.add_argument(
        '-o',
        '--out',
        dest='output_path',
        metavar='PATH',
        type=Path,
        help="path of directory to output reverse-complemented .fasta files (default: in-place)")
    parser.add_argument(
        '-a',
        '--append_rev_com',
        dest='append_rev_com',
        action='store_true',
        help="specify whether FASTA header should now include (rev-com)")

    args = parser.parse_args()

    # parser errors and processing
    # --------------------------------------------------
    if not args.output_path: args.output_path = args.input_path
    if not args.input_path.exists(): parser.error("Input path doesn't exist!")
    if not args.output_path.exists(): parser.error("Output path doesn't exist!")

    return args
# --------------------------------------------------
def rev_com_fasta(seq_object_arg: Seq, append_rev_com_arg: bool) -> Seq:
    """
    Given a SeqObject, return the reverse complement.
    """
    new_seq_object = seq_object_arg

    # adjust the header id, name, and description
    new_seq_object.id = seq_object_arg.id

    if seq_object_arg.id == seq_object_arg.name == seq_object_arg.description:
        new_seq_object.name = ""
        new_seq_object.description = "(rev-com)" if append_rev_com_arg else ""
    else:
        # if the header isn't a single identifier (i.e., the same identifier for the id, name, and description),
        # append (rev-com) to the description
        new_seq_object.description = new_seq_object.description + " (rev-com)" if append_rev_com_arg else new_seq_object.description

    # perform reverse complement
    new_seq_object.seq = seq_object_arg.seq.reverse_complement()

    return new_seq_object
# --------------------------------------------------
def main() -> None:
    """ Insert docstring here """

    args = get_args()

    seq_object_stack: dict = {}

    if args.input_path.is_dir():
        seq_object_stack = {file.stem: SeqIO.read(file.resolve(), 'fasta') for file in args.input_path.glob('*.fasta')}
    elif args.input_path.is_file():
        seq_object_stack = {args.input_path.stem: SeqIO.read(args.input_path, 'fasta')}

    reverse_complemented_fastas: dict = {seq_object: rev_com_fasta(seq_object_stack[seq_object], args.append_rev_com) for seq_object in seq_object_stack}

    for fasta in reverse_complemented_fastas:
        SeqIO.write(reverse_complemented_fastas[fasta], args.output_path.joinpath(f'{fasta}_REV.fasta'), 'fasta')

    return None
# --------------------------------------------------
if __name__ == '__main__': 
    main()
