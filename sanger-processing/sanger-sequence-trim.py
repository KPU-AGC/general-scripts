"""
Author : Michael Ke
Date   : 2022-08-22
Purpose: From ab1 files, trims and outputs sequence as fasta files. 
"""
from argparse import ArgumentParser
from pathlib import Path
import csv
from Bio import SeqIO

def parse_args(): 
    parser = ArgumentParser(
        description='Process ab1 files and get Mott algorithm-trimmed sequences',
        epilog='V1.0.0'
        )
    parser.add_argument(
        'ab1_path', 
        action='store', 
        type=Path,
        help = 'path to ab1 sequence files'
    )
    parser.add_argument(
        '-c', '--concat',
        dest='con_flag',
        action='store_true',
        help='Flag to concatenate by primers'
    )
    parser.add_argument(
        '-o', '--output',
        dest='output_path',
        action='store',
        default=None,
        type=Path, 
        help='output path for metadata file and fastas'
    )
    args = parser.parse_args()

    if not(args.output_path): 
        args.output_path = args.ab1_path

    return (args)

def main():
    
    args = parse_args()
    ab1_path = args.ab1_path
    con_flag = args.con_flag
    output_path = args.output_path
    metadata = [] 

    ab1_data = []
    ab1_file_paths = []

    #Get all ab1 files in directory
    try: 
        ab1_iter = ab1_path.glob('*.ab1')
        for ab1_file_path in ab1_iter: 
            ab1_file_paths.append(ab1_file_path)
    except: 
        #TODO: HANDLE EXCEPTIONS
        pass

    for ab1_file_path in ab1_file_paths:
        ab1_file = SeqIO.read(ab1_file_path, 'abi')
        ab1_file_trim = SeqIO.read(ab1_file_path, 'abi-trim')

        #Determine how much Mott's trimming algorithm removed from the sequence.
        #Left trim is found by searching the first 5 nucleotides of the trimmed sequence
        #in the original file. 
        left_trim = ab1_file.seq.find(ab1_file_trim.seq[0:5])-1
        right_trim = len(ab1_file.seq) - len(ab1_file_trim) - left_trim

        #To allow for manual correction of ID, the ab1 file name ID is used instead of the ab1 file ID
        ab1_file_id = '_'.join(ab1_file_path.stem.split('_')[0:2])
        if ab1_file_trim.id != ab1_file_id: 
            print(f'{ab1_file_path.stem} ID differs from filename ID. Changing ID to filename ID..')
            ab1_file_trim.id = ab1_file_id
        #quality_score = sum(ab1_file.letter_annotations['phred_quality'])/len(ab1_file.letter_annotations['phred_quality'])
        metadata.append((ab1_file_trim.id, ab1_file.annotations['abif_raw']['TrSc1'], ab1_file.annotations['abif_raw']['PuSc1'], left_trim, right_trim))
        ab1_data.append(ab1_file_trim)

    #Output fasta files
    if con_flag: 
        fasta_output_path = output_path.joinpath(f'all_sequences.fasta') 
        SeqIO.write(ab1_data, fasta_output_path, 'fasta')
    else:  
        for data in ab1_data: 
            fasta_output_path = output_path.joinpath(f'{data.id}_trimmed.fasta')
            SeqIO.write(data, fasta_output_path, 'fasta')

    #Output metadata
    metadata_path = output_path.joinpath('metadata.csv')
    metadata.sort(key= lambda x : (x[0].split('_')[1], x[0].split('_')[0]))
    with open(metadata_path, 'w', newline='') as metadata_file:  
        csvwriter = csv.writer(metadata_file)
        csvwriter.writerow(('ID', 'trace_score', 'median_pup', 'left_trim','right_trim'))
        csvwriter.writerows(metadata)

if __name__ == '__main__':
    main()