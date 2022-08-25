from argparse import ArgumentParser

def parse_args(): 
    #Create ArgumentParser object; main entry point
    parser = ArgumentParser('This is an argument parser.', epilog='V0.1')
    #Adding arguments
    parser.add_argument(
        'positional_argument',
        type=int,
        action='store',
        help='This is a positional argument.'
    )
    parser.add_argument(
        '-o', '--optional_argument',
        dest='optional_argument',
        action='store_true',
        help='This is an optional argument',
    )
    #Read the arguments
    args = parser.parse_args()
    #To access the arguments, use dot operator
    positional_argument = args.positional_argument
    #The name of optional arguments is the string provided to dest
    optional_argument = args.optional_argument

    return args