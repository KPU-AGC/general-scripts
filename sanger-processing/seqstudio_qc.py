#!/usr/bin/env python3
__description__ =\
"""
Purpose: Create a QC .csv file, similar to the SeqStudio.
"""
__author__ = "Erick Samera"
__version__ = "1.0.0"
__comments__ = "lmao it works"
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
    parser.add_argument(
        'input_path',
        type=Path,
        help="path of directory containing (.ab1) files")

    args = parser.parse_args()

    # parser errors and processing
    # --------------------------------------------------
    if not args.input_path.is_dir(): parser.error("Input must be a directory!") 

    return args
# --------------------------------------------------
def _generate_csv(_output_path: Path, _contents: list) -> None:
    """
    Generate a SeqStudio-like .csv file from a list of .ab1 file data.

    Parameters:
        _output_path: Path
            the path of the output file
        _contents: list(ab1_data)
            list of ab1 data processed by _get_values()
    
    Returns
        (None)
    """

    header = ','.join(["Sample File Name","Sample Name","Well ID","Cap#","Median PUP","Trace Score","CRL","Signal Strength","Run Module", "Pass/Fail"])

    with open(_output_path, mode='w', encoding='utf-8') as output_file:
        output_file.write(header+'\n')
        for result in sorted(_contents, key=lambda x: x[-1]):
            output_file.write(','.join([str(field) for field in result[:-1]]) +'\n')
    return None
def _get_values(_path: Path) -> dict:
    """
    Given an .ab1 path, process it and return dictionary of processed data.

    Parameters:
        _path: Path
            path of .ab1 file to process
    
    Returns:
        (dict)
            dictionary with key being the plate it belongs to, and tuple of processed data
    """

    file_name = _path.name

    seq_object = SeqIO.read(_path, 'abi').annotations['abif_raw']
    sample_name = seq_object.get('SMPL1').decode()
    well_id = seq_object.get('TUBE1').decode()
    cap_num = seq_object.get('LANE1')
    median_pup = seq_object.get('PuSc1', 0)
    trace_score = seq_object.get('TrSc1', 0)
    crl = seq_object.get('CRLn1', 0)
    signal_strength = sum(seq_object.get('S/N%1'))/len(seq_object.get('S/N%1'))
    run_module = seq_object.get('RMdN1').decode()
    plate_name = seq_object.get('CTNM1').decode()

    runtime = seq_object.get('RUND3').replace('-', '') + seq_object.get('RUNT3').replace(':', '')

    qc_scores = [seq_object.get(qc_score, b'fail').decode() for qc_score in ('CRLn2', 'QV202', 'TrSc2')]
    if 'fail' in qc_scores: pass_fail = 'fail'
    elif 'check' in qc_scores: pass_fail = 'check'
    else: pass_fail = 'pass'

    return {plate_name: (file_name, sample_name, well_id, cap_num, median_pup, trace_score, crl, signal_strength, run_module, pass_fail, runtime)}
def _parse_dir(_abi_dir: Path) -> dict:
    """
    Parse a directory containing .ab1 files and return a dictionary of data per plate.

    Parameters:
        _abi_dir: Path
            path of directory containing .ab1 files.
        
    Returns:
        (dict)
            summarized dictionary of .ab1 files per plate.
    """

    csv_dict: dict = {}
    processed_values = [_get_values(ab1_file) for ab1_file in _abi_dir.glob('*.ab1')]
    for processed_value in processed_values:
        key = list(processed_value.keys())[0]
        if key in csv_dict: csv_dict[key].append([processed_value[key]][0])
        else:
            csv_dict[key] = [[processed_value[key]][0]]
    
    return csv_dict
def main() -> None:
    """ Insert docstring here """

    args = get_args()
    csv_dict: dict = _parse_dir(args.input_path)
    for key in csv_dict:
        output_path = args.input_path.parent.joinpath(f'{key}.csv')
        _generate_csv(output_path, csv_dict[key])
# --------------------------------------------------
if __name__ == '__main__':
    main()
