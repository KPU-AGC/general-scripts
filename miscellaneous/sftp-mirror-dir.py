#!/usr/bin/env python3
__description__ =\
"""
Purpose: Script to recursively download files from a given sftp server.

Easiest usage (Use absolute paths!):
python {script_name.py} \
--local-root-dir {} \
--remote-root-dir {} \
--hostname {} \
--username {} \
--password {}
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
from datetime import datetime
import paramiko
import stat
import logging
# --------------------------------------------------
def get_args() -> Namespace:
    """ Get command-line arguments """

    parser = ArgumentParser(
        description=__description__,
        epilog=f"v{__version__} : {__author__} | {__comments__}",
        formatter_class=RawTextHelpFormatter)
    parser.add_argument('--local-root-dir',
        type=Path,
        required=True,
        help="the absolute path of the local directory to dowload files to.")
    parser.add_argument('--remote-root-dir',
        type=Path,
        required=True,
        help="the absolute path of the remote directory to recursively download files from.")
    parser.add_argument('--hostname',
        type=str,
        required=True,
        help="remote hostname (server name)")
    parser.add_argument('--username', '-u',
        type=str,
        required=True,
        help="username")
    parser.add_argument('--password', '-p',
        type=str,
        required=False,
        help="password")
    parser.add_argument('--force', '-f',
        action='store_true',
        help="if the local root doesn't exist, make it. This is to prevent pathing errors.")

    args = parser.parse_args()

    # parser errors and processing
    # --------------------------------------------------
    # ensure absolute paths
    if not all([
        args.local_root_dir.is_absolute(),
        args.remote_root_dir.is_absolute()
        ]): parser.error('Use absolute paths!')
    # check to see if the local path exists, prevent pathing errors
    if not args.force:
        if not args.local_root_dir.exists() or not args.local_root_dir.is_dir(): parser.error('Use an existing local root or pass -f/--force !')

    return args
# --------------------------------------------------
def download_files_recursively(sftp, remote_dir: Path, local_dir: Path) -> None:
    """
    Function recursively downloads files from a given remote directory.

    Parameters:
        (sftp):
            the sftp instance from paramiko
        remote_dir: Path
            the remote directory to download files from
        local_dir: Path
            the local directory to download files to
    
    Returns:
        None
    """

    # Check if the local directory exists, create if not
    if not Path(local_dir).exists(): Path(local_dir).mkdir()

    # List files in the remote directory
    files = sftp.listdir(str(remote_dir))

    for file_name in files:

        remote_path: Path = remote_dir.joinpath(file_name)
        local_path: Path = local_dir.joinpath(file_name)
        fileattr = sftp.lstat(str(remote_path))

        # if the file is a directory, recursively deal with downloading contents
        if stat.S_ISDIR(fileattr.st_mode):
            if Path(local_path).exists(): logging.info(f"Skipping {file_name} (already exists locally) .")
            
            new_remote_dir: Path = remote_dir.joinpath(file_name)
            new_local_dir: Path = local_dir.joinpath(file_name)
            logging.info(f"Descending into {file_name} ...")
            download_files_recursively(sftp, new_remote_dir, new_local_dir)

        # if the file is a file, just perform regular checking
        if stat.S_ISREG(fileattr.st_mode):
            # check if the file exists locally
            if Path(local_path).exists(): logging.info(f"Skipping {file_name} (already exists locally) .")
            else:
                # download the file
                logging.info(f"Downloading {file_name} ...")
                try: 
                    sftp.get(str(remote_path), str(local_path))
                    logging.info(f"Downloaded {file_name} .")
                except: logging.warning(f'Something bad happened downloading {file_name} !')

def main() -> None:
    """ Main stuff. """
    
    args = get_args()

    runtime = datetime.now().strftime('%Y%m%d-%H%M%S')
    logging.basicConfig(
        encoding='utf-8',
        level=logging.INFO,
        handlers=[
            logging.FileHandler(Path(__file__).parent.joinpath(f'{runtime}_sftp-transfer.log')),
            logging.StreamHandler()],
        datefmt='%Y-%m-%d %H:%M:%S',
        format='%(asctime)s %(levelname)s : %(message)s')

    # Connect to the SFTP server
    with paramiko.Transport((args.hostname, 22)) as transport:
        try: transport.connect(username=args.username, password=args.password)
        except paramiko.ssh_exception.AuthenticationException: logging.warning(f'Bad login !!!'); return None
        
        with transport.open_sftp_client() as sftp:
            # Start recursive file download
            try:
                logging.info(f'Beginning file transfer. ')
                download_files_recursively(sftp, args.remote_root_dir, args.local_root_dir)
            except: logging.warning(f'Something bad happened during the file transfer !')

if __name__ == '__main__':
    main()
