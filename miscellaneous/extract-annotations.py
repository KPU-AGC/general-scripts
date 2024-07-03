#!/usr/bin/env python3
__description__ =\
"""
Purpose: Given an input FASTA and region, add annotations from gff and vcf files to produce a GenBank file.
"""
__author__ = "Erick Samera"
__version__ = "2.0.0"
__comments__ = "easier to just wrap bcftools"
# --------------------------------------------------
from argparse import (
    Namespace,
    ArgumentParser,
    RawTextHelpFormatter)
from pathlib import Path
# --------------------------------------------------
import re
import subprocess
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation
# --------------------------------------------------
def get_args() -> Namespace:
    """ Get command-line arguments """

    parser = ArgumentParser(
        description=__description__,
        epilog=f"v{__version__} : {__author__} | {__comments__}",
        formatter_class=RawTextHelpFormatter)
    parser.add_argument('input_fasta',
        metavar="<FASTA FILE>",
        type=Path,
        help="input FASTA file")
    parser.add_argument('position',
        metavar="<COORDS>",
        type=str,
        help="chr:start-end / chr:start..end")
    parser.add_argument('--gff',
        type=Path,
        action='append',
        help="input GFF file (multiple accepted)")
    parser.add_argument('--vcf',
        type=Path,
        action='append',
        help="input VCF file (multiple accepted)")

    parser.add_argument('--desc',
        type=str,
        metavar="<STR>",
        default="{chromosome}:{start}-{end}",
        help="edit sequence description [default: {chromosome}:{start}-{end}]\n{chromosome}/{start}/{end} are evaluated as input coords.")

    args = parser.parse_args()

    # parser errors and processing
    # --------------------------------------------------
    # ensure that coords match format
    if not re.match(r".*:\d+(-|\.\.)\d+", args.position):
        parser.error("ERROR: Incorrect region format, must be (chr:start-end/chr:start..end)")
    if not _bcftools_installed(): 
        parser.error('ERROR: bcftools not installed! Please install it to continue.')

    return args
# --------------------------------------------------
def _parse_gff(_input_path: Path, _chromosome: str, _start: int, _end: int) -> list:
    """
    Function parses a GFF file and returns a list of features.

    ### Parameters:
        _input_path: Path
            path to the GFF file
        _chromosome: str
            chromosome target region
        _start: int
            integer genomic start position of target region
        _end: int
            integer genomic end position of target region
    
    ### Returns:
        (list) of features.
    """

    list_of_features: list = []

    with open(_input_path, encoding='utf-8') as input_gff_file:
        for line in input_gff_file.readlines():
            if line.startswith('#'): continue
            
            # parse gff file into respective relevant information
            line_chr, _, annot_type, line_pos_1, line_pos_2, _, line_strand, _, qualifiers = line.strip().split('\t')
            line_pos_1: int = int(line_pos_1); line_pos_2: int = int(line_pos_2)
            
            # skip if not in target region
            if not line_chr == _chromosome: continue
            if not ((_start < line_pos_1 < _end) or (_start < line_pos_2 < _end)): continue

            if line_pos_1 < line_pos_2:
                line_start: int = line_pos_1; line_end: int = line_pos_2; line_strand = +1
            elif line_pos_1 > line_pos_2:
                line_start: int = line_pos_2; line_end: int = line_pos_1; line_strand = -1

            if line_start < _start: line_start = _start
            if line_end > _end: line_end = _end

            relative_start: int = line_start - _start
            relative_end: int = line_end - line_start + relative_start + 1

            SeqFeature_to_append = SeqFeature(
                FeatureLocation(relative_start, relative_end, strand=line_strand),
                type=annot_type,
                qualifiers={key: value for key, value in [qualifier.split('=') for qualifier in qualifiers.split(';')]})
            list_of_features.append(SeqFeature_to_append)

    return list_of_features
def _parse_vcf(_input_path: Path, _chromosome: str, _start: int, _end: int) -> list:
    """
    Function parses a VCF file and returns a list of features.

    ### Parameters:
        _input_path: Path
            path to the vcf file
        _chromosome: str
            chromosome target region
        _start: int
            integer genomic start position of target region
        _end: int
            integer genomic end position of target region
    
    ### Returns:
        (list) of features.
    """

    list_of_annotations: list = []

    # try random access first
    command = f'bcftools view --no-header -r {_chromosome}:{_start}-{_end} {_input_path}'
    bcftools_result = subprocess.run(command, shell=True, capture_output=True)

    # and if not, just do by stream
    if bcftools_result.stderr.decode().strip() == f"Failed to read from {_input_path}: not compressed with bgzip":
        command = f'bcftools view --no-header -t {_chromosome}:{_start}-{_end} {_input_path}'
        bcftools_result = subprocess.run(command, shell=True, capture_output=True)

    for line in bcftools_result.stdout.decode().splitlines():
        if line.startswith('#'): continue
        
        # parse vcf file into respective relevant information
        line_chr, line_pos, rsid, *_ = line.strip().split('\t')
        line_pos: int = int(line_pos)

        # skip if not in target region
        if not line_chr == _chromosome: continue
        if not _start < line_pos < _end: continue
        relative_pos: int = line_pos - _start

        SeqFeature_to_append = SeqFeature(
                    FeatureLocation(relative_pos, relative_pos+1, strand=+1),
                    type="polymorphism")
        if rsid.replace('.', ''): SeqFeature_to_append.qualifiers['ID'] = rsid
        list_of_annotations.append(SeqFeature_to_append)

    return list_of_annotations
def _format_sequence_description(seq_desc_template: str, chromosome: str, start: int, end: int) -> str:
    """
    Formats the sequence description template with the given chromosome, start, and end.
    """
    return seq_desc_template.format(chromosome=chromosome, start=start, end=end)
def _bcftools_installed() -> bool:
    """
    Check if bcftools is installed.
    """
    command = 'bcftools'
    result = subprocess.run(command, shell=True, capture_output=True)
    if 'bcftools: not found' in result.stderr.decode().strip():
        return False
    return True
# --------------------------------------------------
def main() -> None:
    """ Main stuff. """

    args = get_args()
    chromosome, start, end = re.split('[:-]|\\.\\.', args.position)
    start: int = int(start); end: int = int(end)

    record_dict = SeqIO.index(str(args.input_fasta), "fasta")

    formatted_seq_desc: str = _format_sequence_description(args.seq_desc, chromosome, start, end)

    record_to_print = SeqRecord(
        Seq(record_dict[chromosome].seq[start-1:end]).upper(),
        id=chromosome,
        name="",
        description=formatted_seq_desc,
        annotations={"molecule_type": "DNA"}
    )

    annotations: list = []
    if args.gff: [annotations.extend(_parse_gff(annotation, chromosome, start, end)) for annotation in args.gff]
    if args.vcf: [annotations.extend(_parse_vcf(annotation, chromosome, start, end)) for annotation in args.vcf]
    for annotation in annotations: record_to_print.features.append(annotation)

    print(record_to_print.format('gb'))
# --------------------------------------------------
if __name__ == '__main__':
    main()
