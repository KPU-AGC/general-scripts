import csv
import pathlib
import argparse

def check_scores(pup_score, trace_score, min_pup_score, min_trace_score):
    if (int(pup_score) >= min_pup_score) and (int(trace_score) >= min_trace_score):
        return True
    else: 
        return False

def parse_args(): 
    """
    Arguments: 
    1) qc_data - path to the qc .csv file
    2) ab1_path: path to all of the ab1 files
    """
    parser = argparse.ArgumentParser(description='Automated QC of sanger electropherograms.')
    parser.add_argument(
        'qc_path',
        action='store',
        type=pathlib.Path, 
        help='Path to QC .csv file generated by the SeqStudio' 
    )
    parser.add_argument(
        '--min_pup', '-p',
        action='store',
        type=int,
        dest='min_pup_score',
        default=15,
        help='Minimum pup score for the sequence to be considered usable'
    )
    parser.add_argument(
        '--min_trace', '-t',
        action='store',
        type=int,
        dest='min_trace_score', 
        default=30,
        help='Minimum mean trace score for the sequence to be considered usable'
    )
    args = parser.parse_args()
    return (args.qc_path, args.min_pup_score, args.min_trace_score)

def main(qc_path, min_pup_score, min_trace_score): 
    qc_data = []
    qc_file = open(qc_path, 'r')
    qc_reader = csv.reader(qc_file)
    for row in qc_reader: 
        qc_data.append(row)
    #Find data header row
    flag_header = 0
    data_header = None
    for i in range(1, len(qc_data)):
        if qc_data[i][0] == 'Sample File Name': 
            data_header = i
            break
    #Flag headers: 
    #Sample File Name, QC, Issues
    #Data headers: 
    #Sample File Name, Sample Name, Well ID, Cap#, Median PUP, Trace Score, CRL, Signal Strength
    qc_pass = []
    for i in range(data_header+1, len(qc_data)): 
        if check_scores(qc_data[i][4], qc_data[i][5], min_pup_score, min_trace_score) is True: 
            qc_pass.append((qc_data[i][1], qc_data[i][4], qc_data[i][5]))
    #Data output: 
    output_file = open('qc_report.csv', 'w', newline='')
    csv_writer = csv.writer(output_file)
    csv_writer.writerow(('Sample name', 'Median PUP', 'Trace Score'))
    csv_writer.writerows(qc_pass)

if __name__ == '__main__': 
    qc_path, min_pup_score, min_trace_score = parse_args()
    main(qc_path, min_pup_score, min_trace_score)
