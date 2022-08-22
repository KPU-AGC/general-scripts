#!/usr/bin/env python3
"""
Author : Erick Samera
Date   : 2022-08-20
Purpose: Iterates over the files in a given directory and renames them with a new format.
"""

from argparse import (
    Namespace,
    ArgumentParser,
    RawTextHelpFormatter)
from pathlib import Path
from re import split
from shutil import copy, move
# --------------------------------------------------
def get_args() -> Namespace:
    """ Get command-line arguments """

    parser = ArgumentParser(
        description='Program parses filenames with standardized delimiters and renames them with a new format.',
        #usage='%(prog)s',
        epilog='v1.0.0 : We should put the versioning in the program.',
        formatter_class=RawTextHelpFormatter)
    function_group = parser.add_mutually_exclusive_group(required=True)
    function_group.add_argument(
        '--copy',
        dest='copy_arg',
        default=False,
        action='store_true',
        help='use this flag to make a copy of file to output directory')
    function_group.add_argument(
        '--rename',
        dest='rename_arg',
        default=False,
        action='store_true',
        help='use this flag to rename files and output to directory')
    parser.add_argument(
        '--input_fmt',
        dest='input_fmt',
        metavar='FMT',
        type=str,
        default=None,
        required=True,
        help='standardized format to use for input files \nexample: {sample_name}_{primer}_{well_position}_{rundate}_{runtime}\n ')
    parser.add_argument(
        '--output_fmt',
        dest='output_fmt',
        metavar='FMT',
        type=str,
        default=None,
        required=True,
        help='standardized format to use for output files \nexample: {sample_name}_{primer}_{rundate}_{runtime}\n ')
    parser.add_argument(
        '-i',
        '--in',
        dest='input_path',
        metavar='PATH',
        type=Path,
        default=None,
        required=True,
        help='path of directory containing input files to be renamed')
    parser.add_argument(
        '-o',
        '--out',
        dest='output_path',
        metavar='PATH',
        type=Path,
        default=None,
        required=True,
        help='path of directory to output the renamed files')

    args = parser.parse_args()

    args.input_path = args.input_path.resolve()
    args.output_path = args.output_path.resolve()
    return args
# --------------------------------------------------
def create_input_rule(input_fmt_arg: str) -> dict:
    """
    Function creates an input rule based on a given string.

    Parameters:
        input_fmt_arg (str): A given string in the rule format wherein {var} denotes variables between delimiters such as '-' or '_'

    Returns:
        (dict): input rule
            rule (list): list of variables
            delimiters (list): list of delimiter characters
    """
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    raw_rule = ['>'+var.strip() if var[0].upper() in alphabet else var for var in split('{|}', input_fmt_arg) if var.strip() != ""]
    delimiters = list(set([delimiter for delimiter in raw_rule if not delimiter.startswith('>')]))
    rule = [rule_value[1:] for rule_value in raw_rule if rule_value.startswith('>')]
    return {'rule': rule, 'delimiters': delimiters}
def process_file_with_input_rule(input_rule_dict_arg: dict, file_arg: Path) -> dict:
    """
    Function to process a filename with an input rule.

    Parameters:
        input_rule_dict_arg (dict): the input rule from the create_input_rule() method
        file_arg (Path): the file to process

    Returns:
        name_values_dict (dict): dict with the name values assigned to the variables that were set in the input rule
    """
    re_arg = '|'.join([delimiter.strip() for delimiter in input_rule_dict_arg['delimiters']])
    name_values_list = split(re_arg, file_arg.stem)
    name_values_dict = {}
    for rule_i, rule_name in enumerate(input_rule_dict_arg['rule']):
        name_values_dict[rule_name] = name_values_list[rule_i]
    return name_values_dict
def create_output_rule(output_fmt_arg: str) -> list:
    """
    Function creates an output rule based on a given string.

    Parameters:
        output_fmt_arg (str): A given string in the rule format wherein {var} denotes variables between delimiters such as '-' or '_'

    Returns:
        (dict): output rule
            rule (list): list of variables
    """
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    raw_rule = ['>'+var.strip() if var[0].upper() in alphabet else var for var in split('{|}', output_fmt_arg) if var.strip() != ""]
    return {'rule': raw_rule}
def return_file_with_output_rule(name_values_dict_arg: dict, output_rule_dict_arg: dict) -> str:
    """
    Function returns the new name with the variables mapped between the input and output.

    Parameters:
        name_values_dict_arg (dict): dict containing the mapped variables from the input
        output_rule_dict_arg (dict): dict containing the output rule

    Returns:
        (str): the new name after processing
    """
    new_name = ''
    for rule in output_rule_dict_arg['rule']:
        if rule.startswith('>'):
            try:
                new_name += name_values_dict_arg[rule[1:]]
            except KeyError:
                unknown_rule = '{'+rule[1:]+'}'
                print(f"WARNING !!! Couldn't find {unknown_rule} in input_format ")
                quit()
        else:
            new_name += rule
    return new_name
def main() -> None:
    """ iterates over the files """
    args = get_args()

    input_format = create_input_rule(args.input_fmt)
    output_format = create_output_rule(args.output_fmt)

    for file in args.input_path.glob('*'):
        if file.is_file():
            processed_file = process_file_with_input_rule(input_format, file)
            new_name = return_file_with_output_rule(processed_file, output_format)
            if args.copy_arg:
                copy(file, args.output_path.joinpath(f"{new_name}{file.suffix}"))
            elif args.rename_arg:
                move(file, args.output_path.joinpath(f"{new_name}{file.suffix}"))

# --------------------------------------------------
if __name__ == '__main__':
    main()