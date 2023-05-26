#!/usr/bin/env python3
__description__ =\
"""
Purpose: A needlessly-graphical visualizer for GenBank files.
"""
__author__ = "Erick Samera"
__version__ = "1.0.0"
__comments__ = "stable enough"
# --------------------------------------------------
from argparse import (
    Namespace,
    ArgumentParser,
    RawTextHelpFormatter)
from pathlib import Path
# --------------------------------------------------
import time
import random
import subprocess
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
        help='path of GENBANK file')
    parser.add_argument('-s', '--scroll-speed',
        metavar='<INT>',
        type=float,
        default=100,
        help='ms scrollspeed')


    # --------------------------------------------------
    args = parser.parse_args()

    return args
# --------------------------------------------------
TERMINAL_COLORS = {
    'BLACK': '\33[40m',
    'BLUE': '\33[44m', 
    'PURPLE': '\33[45m',
    'RED': '\33[41m',
    'GREEN': '\33[42m',
    'BLINK': '\33[5m',
    'GREY': '\33[90m',
    'END': '\033[0m',
}

NUCLEOTIDES = {
    'A': {'reverse_complement': 'T', 'color': TERMINAL_COLORS['GREEN']+'A'+TERMINAL_COLORS['END']},
    'T': {'reverse_complement': 'A', 'color': TERMINAL_COLORS['RED']+'T'+TERMINAL_COLORS['END']},
    'C': {'reverse_complement': 'G', 'color': TERMINAL_COLORS['BLUE']+'C'+TERMINAL_COLORS['END']},
    'G': {'reverse_complement': 'C', 'color': TERMINAL_COLORS['BLACK']+'G'+TERMINAL_COLORS['END']},
    'N': {'reverse_complement': 'N', 'color': TERMINAL_COLORS['RED']+'N'+TERMINAL_COLORS['END']},
}

# --------------------------------------------------
def _get_structure(n:str, i, _color_nuc=True, _color_rev_comp=False) -> str:

    r = NUCLEOTIDES[n.upper()].get('reverse_complement')
    
    _nuc_struc = {
        0:  f"       {n}{r}   ",
        1:  f"     {n}--{r}   ",
        2:  f"  {n}====---{r} ",
        3:  f" {n}=====---{r} ",
        4:  f" {n}---====={r} ",
        5:  f"  {n}--===={r}  ",
        6:  f"    {n}--{r}    ",
        7:  f"     {n}{r}     ",
        8:  f"    {r}{n}      ",
        9:  f"    {r}--{n}    ",
        10: f"  {r}--===={n}  ",
        11: f" {r}---====={n} ",
        12: f" {r}=====---{n} ",
        13: f"  {r}====--{n}  ",
        14: f"    {r}--{n}    ",
        15: f"      {r}{n}    ",
    }

    str = _nuc_struc.get(i % 16)\
        .replace('-', f"{TERMINAL_COLORS['GREY']}-{TERMINAL_COLORS['END']}")\
        .replace('=', f"{TERMINAL_COLORS['GREY']}={TERMINAL_COLORS['END']}")\
        .replace(n, NUCLEOTIDES[n.upper()].get('color') if _color_nuc else n)\
        .replace(r, NUCLEOTIDES[r.upper()].get('color') if _color_rev_comp else f"{TERMINAL_COLORS['GREY']}{r}{TERMINAL_COLORS['END']}")

    return str
# --------------------------------------------------
def main() -> None:
    """
    """
    args = get_args()

    _TERMINAL_SIZE = 50
    
    input_seq = SeqIO.read(args.input, 'genbank')


    # generate initial structure
    lines_to_print = []
    for i, nucleotide in enumerate(input_seq.seq):
        lines_to_print.append({'visual_line': _get_structure(nucleotide, i)})
    
    # generate add annotations:

    feature_types = sorted(set([feature.type for feature in input_seq.features]))
    ANNOTATION_COLORS = {key: value for key, value in zip(feature_types, ['BLACK', 'BLUE', 'PURPLE', 'RED', 'GREEN']*len(feature_types))}
    DIRECTIONALITY = {
         1: '↓',
        -1: '↑',
         0: '|',
    }

    for feature in input_seq.features:
        if feature.type not in ('CDS', 'gene'): continue
        for i, nuc in enumerate(input_seq.seq[int(feature.location.start):int(feature.location.end)]):
            lines_to_print[int(feature.location.start)+i]['visual_line'] += f"{TERMINAL_COLORS[ANNOTATION_COLORS[feature.type]]} {DIRECTIONALITY[feature.strand]} {TERMINAL_COLORS['END']}"
            if 'annotations_visible' not in lines_to_print[int(feature.location.start)+i]: lines_to_print[int(feature.location.start)+i]['annotations_visible'] = []
            lines_to_print[int(feature.location.start)+i]['annotations_visible'].append(feature.qualifiers)


    subprocess.run('clear')
    for i_line, line in enumerate(lines_to_print):
        screen_lines = []
        if i_line <= _TERMINAL_SIZE:
            screen_lines = '\n'.join([line['visual_line'] for line in lines_to_print[0:i_line] + [{'visual_line': ''}]*(_TERMINAL_SIZE-i_line)])
        elif i_line+_TERMINAL_SIZE >= len(lines_to_print):
            screen_lines = '\n'.join([line['visual_line'] for line in lines_to_print[i_line-_TERMINAL_SIZE:len(lines_to_print)] + [{'visual_line': ''}]*(_TERMINAL_SIZE-i_line)])
        else: 
            lines_instance = lines_to_print[i_line:i_line+_TERMINAL_SIZE]
            screen_lines = '\n'.join([line['visual_line'] for line in lines_instance])
        print(screen_lines)
        time.sleep(args.scroll_speed/1000)
# --------------------------------------------------
if __name__ == '__main__':
    main()
