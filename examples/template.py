"""
docstrings_example.py - This module is an example of how you should write docstrings. 
It will provide an example of module docstrings, class docstrings, and function docstrings. 

Classes: 
ExampleClass : class that is an example of a class

Functions: 
example_function : accepts an int and a str, and returns a dictionary of those parameters

Author: <author name>
Version: 1.0.0 <use semantic versioning>
Date Last Modified: <date last modified>
"""

# MODULES
# --------------------------------------------------
from argparse import (
    Namespace,
    ArgumentParser,
    RawDescriptionHelpFormatter)
from pathlib import Path

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
def main():
    """ Insert docstring here """
    args = get_args()
    
    # insert code here

# --------------------------------------------------
if __name__ == "__main__":
    main()