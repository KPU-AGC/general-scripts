#!/usr/bin/env python3
__description__ =\
"""
Purpose: Script for robust update of BLAST databases.
TODO: adjust the --blastdb-path to just blastdb once testing is done.
"""
__author__ = "Erick Samera"
__version__ = "1.0.0"
__comments__ = "stable enough"
# --------------------------------------------------
from argparse import (
    Namespace,
    ArgumentParser,
    RawTextHelpFormatter)
import pathlib
import subprocess
import multiprocessing
import logging
import urllib.request, json
from datetime import datetime
# --------------------------------------------------
def get_args() -> Namespace:
    """ Get command-line arguments """

    parser = ArgumentParser(
        description=__description__,
        epilog=f"v{__version__} : {__author__} | {__comments__}",
        formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        'input_db',
        type=str,
        help="")
    parser.add_argument(
        '--blastdb-path',
        type=pathlib.Path,
        default=pathlib.Path('/home/agc/Documents/ref/blastdb2'),
        help="the root directory containing blastdb [default: /home/agc/Documents/ref/blastdb]")
    parser.add_argument(
        '--no-md5-check',
        action='store_true',
        help="skip md5 checking [default: False]")
    parser.add_argument(
        '--decompress',
        action='store_true',
        help="automatically decompress downloaded database files [default: False]")
    parser.add_argument(
        '--threads',
        type=int,
        default=0,
        help="set the number of threads to perform downloads in parallel (0=all) [default: 0]")

    args = parser.parse_args()

    # --------------------------------------------------
    if args.threads == 0: args.threads = None
    if args.input_db == 'list':
        with urllib.request.urlopen(f"https://ftp.ncbi.nlm.nih.gov/blast/db/blastdb-manifest.json") as url:
            print('INFO: Available BLAST databases (case-sensitive): ')
            db_dict: dict = json.load(url)
            for db_name in [db_name for db_name in db_dict.keys() if db_name not in ["version"]]: print(db_name)
        quit()
    if args.input_db == 'list_full':
        with urllib.request.urlopen(f"https://ftp.ncbi.nlm.nih.gov/blast/db/blastdb-manifest.json") as url:
            print('INFO: Available BLAST databases (case-sensitive): ')
            db_dict: dict = json.load(url)
            print('\t'.join(['db_name', 'description', 'last_updated', 'size (GB)']))
            for db_name in [(db_name,  db_dict[db_name]['dbtype'], db_dict[db_name]['description'], db_dict[db_name]['last_updated'], str(db_dict[db_name]['size'])) for db_name in db_dict.keys() if db_name not in ["version"]]: 
                print('\t'.join(db_name))
        quit()

    with urllib.request.urlopen(f"https://ftp.ncbi.nlm.nih.gov/blast/db/blastdb-manifest.json") as url:
        #logging.info(f"Reached ftp.ncbi.nlm.nih.gov and parsed {input_db_str}-nucl-metadata.json .")
        if args.input_db not in list(json.load(url).keys()):
            parser.error(f"{args.input_db} not in available list of db. Consider using 'list' to list available options (or 'list_full' for more database information). ")

    return args
# --------------------------------------------------

def _newer_version_exists(current_ver_date: str, last_updated_date: str) -> bool:
    """
    """
    "2024-07-16T00:00:00"
    if datetime.strptime(current_ver_date, "%Y-%m-%dT%H:%M:%S") < datetime.strptime(last_updated_date, "%Y-%m-%dT%H:%M:%S"): return True
    else: return False

def _get_json(input_db_str: str) -> None:
    """
    """
    logging.info(f"Trying to reach https://ftp.ncbi.nlm.nih.gov ...")
    with urllib.request.urlopen(f"https://ftp.ncbi.nlm.nih.gov/blast/db/{input_db_str}-nucl-metadata.json") as url:
        logging.info(f"Reached ftp.ncbi.nlm.nih.gov and parsed {input_db_str}-nucl-metadata.json .")
        data = json.load(url)
        return data

def _get_current_version(input_path: pathlib.Path) -> str:
    """
    """
    with open(input_path) as input_file:
        current_version = input_file.read().strip()
    return current_version

def _check_md5(input_path: pathlib.Path) -> str:
    """
    """
    command = f'md5sum {input_path}'
    result = subprocess.run(command, shell=True, capture_output=True)
    return result.stdout.decode().split(' ')[0]

def _read_md5(input_path: pathlib.Path) -> str:
    """
    """
    with open(input_path) as input_file:
        md5 = input_file.read().strip().split(' ')[0]
    return md5

def _decompress_file(input_path: pathlib.Path) -> None:
    """
    """
    command = f'tar -xzvf {input_path} -C {input_path.parent}'
    logging.info(f"Unzipping {input_path} ...")
    subprocess.run(command, shell=True, capture_output=True)
    logging.info(f"Unzipped {input_path} .")

def _download_from_url(target_url: str, destination_path, download_md5_arg, decompress_arg) -> None:
    """
    """
    filename = target_url.split('/')[-1]
    logging.info(f"Downloading {filename} to {destination_path.joinpath(filename)} ...")
    command = f'curl {target_url} --output {destination_path.joinpath(filename)}'
    result = subprocess.run(command, shell=True, capture_output=False)
    logging.info(f"Downloaded {filename} to {destination_path.joinpath(filename)} .")
    if download_md5_arg:

        logging.info(f"Also downloading {filename}.md5 to {destination_path.joinpath(filename)}.md5 ...")
        command = f'curl {target_url}.md5 --output {destination_path.joinpath(filename)}.md5'
        result = subprocess.run(command, shell=True, capture_output=False)
        logging.info(f"Downloaded {filename}.md5 to {destination_path.joinpath(filename)}.md5 .")

        logging.info(f"Comparing md5 signatures for {filename} ...")
        md5_downloaded:str = _read_md5(f'{destination_path.joinpath(filename)}.md5')
        md5_from_file: str = _check_md5(f"{destination_path.joinpath(filename)}")
        if not md5_downloaded==md5_from_file: 
            logging.warning(f"MD5 SIGNATURES {filename} DO NOT MATCH !")
            return None
        else: logging.info(f"md5 signatures for {filename} match .")

        if decompress_arg: _decompress_file(pathlib.Path(f"{destination_path.joinpath(filename)}"))

    return None

def _mp_wrap_download(threads_arg: int, url_list: list, destination_path: pathlib, download_md5_arg: bool, decompress_arg: bool) -> None:
    """
    """
    with multiprocessing.Pool(threads_arg if threads_arg else None) as pool:
        logging.info(f"Downloading database using {pool._processes} processes ...")
        results = pool.starmap(_download_from_url, [(url, destination_path, download_md5_arg, decompress_arg) for url in url_list])
    return None

def _log_params(args: Namespace) -> None:
    """Log argparse arguments to logfile"""
    logging.info(f"target blastdb: {args.input_db}")
    logging.info(f"download destination: {args.blastdb_path}")
    logging.info(f"skip md5 check: {args.no_md5_check}\n")
    return None
# --------------------------------------------------
def main() -> None:
    """
    """

    args = get_args()

    runtime = datetime.now().strftime('%Y%m%d-%H%M%S')
    logging.basicConfig(
        encoding='utf-8',
        level=logging.INFO,
        handlers=[
            logging.FileHandler(args.blastdb_path.joinpath(f"{args.input_db}_{runtime}.log")),
            logging.StreamHandler()],
        datefmt='%Y-%m-%d %H:%M:%S',
        format='%(asctime)s %(levelname)s : %(message)s')

    _log_params(args)
    
    json_dict: dict = _get_json(args.input_db)

    newest_version: str = json_dict['last-updated']
    if args.blastdb_path.joinpath(f"{args.input_db}.date").exists():
        current_version: str = _get_current_version(args.blastdb_path.joinpath(f"{args.input_db}.date"))
        logging.info(f"Current version was downloaded {current_version} .")
    else:
        current_version = None
        logging.info(f"Database has not been downloaded before .")
    logging.info(f"Newest version was updated {newest_version} .")

    if not current_version: download_database = True
    elif _newer_version_exists(current_version, newest_version): download_database = True
    else: 
        download_database = False
        logging.info(f"Database is up-to-date already !")

    if download_database:
        logging.info(f"A newer version exists! \n")
        _mp_wrap_download(args.threads, json_dict['files'], args.blastdb_path, not args.no_md5_check, args.decompress)
        logging.info(f"Download complete !")
        with open(args.blastdb_path.joinpath(f"{args.input_db}.date"), mode='w') as output_file:
            output_file.write(datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
if __name__=="__main__":
    main()
