"""
sanger-sequence-trim.py - script to automate trimming and QC of ab1 sequencing files.


"""

__author__ = 'Michael Ke'
__version__ = '1.1.0'
__comments__ = 'stable'

#Standard libraries
from argparse import ArgumentParser
import csv
from pathlib import Path
from sys import exit
import csv
#Third-party modules
from Bio import SeqIO

def output_fastas(ab1_data: list, output_path: Path, con_flag: bool, single_flag: bool) -> None: 
    """
    Outputs the fastas either concatenated by primer set or into individual files
    """
    #Concatenate by primers
    if con_flag: 
        #Determine which primers are present
        primer_data = dict()
        for data in ab1_data: 
            primer_name = data.id.split('_')[1]
            if primer_name not in primer_data.keys(): 
                primer_data[primer_name] = []
                primer_data[primer_name].append(data)
            else: 
                primer_data[primer_name].append(data)
        
        #Write individual primer data
        for primer_name in primer_data.keys(): 
            fasta_output_path = output_path.joinpath(f'{primer_name}_sequences.fasta')
            #Write to 2-line format if specified; otherwise, follow standard FASTA format
            if single_flag: 
                SeqIO.write(primer_data[primer_name], fasta_output_path, 'fasta-2line')
            else:
                SeqIO.write(primer_data[primer_name], fasta_output_path, 'fasta')
    #No concatenation of FASTA sequences
    else:  
        for data in ab1_data: 
            fasta_output_path = output_path.joinpath(f'{data.id}_trimmed.fasta')
            SeqIO.write(data, fasta_output_path, 'fasta')

def parse_args(): 
    parser = ArgumentParser(
        description='Process ab1 files and get Mott algorithm-trimmed sequences',
        epilog='V1.1.0'
        )
    parser.add_argument(
        'ab1_path', 
        action='store',
        type=Path,
        help='Path to ab1 sequence files.'
    )
    parser.add_argument(
        '-o', '--output',
        dest='output_path',
        action='store',
        default=None,
        type=Path, 
        help='Output path for metadata file and fastas.'
    )
    parser.add_argument(
        '-c', '--concat',
        dest='con_flag',
        action='store_true',
        help='Flag to concatenate by primers.'
    )
    parser.add_argument(
        '-s', '--oneline',
        dest='single_flag',
        action='store_true',
        help='Flag to output each fasta entry onto one line.'
    )
    qc_group = parser.add_argument_group('qc_options')
    qc_group.add_argument(
        '-q', '--filter_qc',
        dest='qc_flag', 
        action='store_true',
        help='Flag to filter by trace score and median PUP score.'
    )
    qc_group.add_argument(
        '-t', '--min_trace',
        dest='min_trace',
        action='store',
        type=int,
        default=30,
        help='Minimum trace score for a sequence to be passed.',
    )
    qc_group.add_argument(
        '-p', '--min_pup', 
        dest='min_pup', 
        action='store',
        type=int,
        default=10,
        help='Minimum median PUP score for a sequence to be passed.'
    )
    
    args = parser.parse_args()

    if not(args.output_path): 
        args.output_path = args.ab1_path

    return (args)

def main():
    args = parse_args()

    #Setting up args
    ab1_path = args.ab1_path
    con_flag = args.con_flag
    single_flag = args.single_flag
    qc_flag = args.qc_flag
    min_trace = args.min_trace
    min_pup = args.min_pup
    output_path = args.output_path
    metadata = [] 

    ab1_data = []
    ab1_file_paths = []

    #Get all ab1 files in directory
    try: 
        if ab1_path.is_dir() is False:
            raise NotADirectoryError
        
        ab1_iter = ab1_path.glob('*.ab1')
        for ab1_file_path in ab1_iter: 
            ab1_file_paths.append(ab1_file_path)
        
        if len(ab1_file_paths) <= 0:
            raise ValueError
    except NotADirectoryError: 
        print('Not a directory. Terminating program..')
        exit()
    except ValueError:
        print('No ab1 files were found at the directory. Terminating program..')
        exit()

    #Trimming process for each file
    #------------------------------
    for ab1_file_path in ab1_file_paths:
        #Import
        ab1_file = SeqIO.read(ab1_file_path, 'abi')
        ab1_file_trim = SeqIO.read(ab1_file_path, 'abi-trim')

        #Determine how much Mott's trimming algorithm removed from the sequence.
        #Left trim is found by searching the first 5 nucleotides of the trimmed sequence
        #in the original file. 
        left_trim = ab1_file.seq.find(ab1_file_trim.seq[0:5])-1
        right_trim = len(ab1_file.seq) - len(ab1_file_trim) - left_trim

        #TODO: validation of proper filename convention
        #To allow for manual correction of ID, the ab1 file name ID is used instead of the ab1 file ID
        ab1_file_id = '_'.join(ab1_file_path.stem.split('_')[0:2])
        
        #Check: see if the ab1 file ID is the same as the filename ID. This is to allow for manual correction of sequence file names.
        if ab1_file_trim.id != ab1_file_id: 
            print(f'{ab1_file_trim.id} differs from filename {ab1_file_id}. Changing ID to filename ID..')
            ab1_file_trim.id = ab1_file_id

        #quality_score = sum(ab1_file.letter_annotations['phred_quality'])/len(ab1_file.letter_annotations['phred_quality'])

        #Trace score and PUP score in the ab1 file structure.
        #NOTE: these are lost in the trimmed file, so we have to go back to the original imported ab1 file in order
        #      to find these.
        trace_score = ab1_file.annotations['abif_raw']['TrSc1'] if 'TrSc1' in ab1_file.annotations['abif_raw'] else -1
        pup_score = ab1_file.annotations['abif_raw']['PuSc1'] if 'PuSc1' in ab1_file.annotations['abif_raw'] else -1

        #Check for QC flag
        if not qc_flag:
            ab1_data.append(ab1_file_trim)
        else: 
            if (
                trace_score > min_trace 
                and pup_score > min_pup
            ): 
                ab1_data.append(ab1_file_trim)
        metadata.append((ab1_file_trim.id, trace_score, pup_score, left_trim, right_trim))

    output_fastas(ab1_data, output_path, con_flag, single_flag)

    #Output metadata
    metadata_path = output_path.joinpath('metadata.csv')
    try: 
        metadata.sort(key= lambda x : (x[0].split('_')[1], x[0].split('_')[0]))
    except IndexError: 
        print('Sort failed due to filenames.')
    with open(metadata_path, 'w', newline='') as metadata_file:  
        csvwriter = csv.writer(metadata_file)
        csvwriter.writerow(('ID', 'trace_score', 'median_pup', 'left_trim','right_trim'))
        csvwriter.writerows(metadata)

if __name__ == '__main__':
    main()