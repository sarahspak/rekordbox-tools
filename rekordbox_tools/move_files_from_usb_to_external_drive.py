import os
import glob
import shutil
from pathlib import Path
import time
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import subprocess
from threading import Lock


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def get_filenames(folder, dest_dir, lock, active_count):
    with lock:
        active_count += 1
        logging.info(f"Worker started for {folder}. Active workers: {active_count}")
    try:
        for root, dirs, files in os.walk(folder):
            for file in files:
                source_file = os.path.join(root, file)
                dest_file = os.path.join(dest_dir, Path(source_file).name)
                try:
                    shutil.move(source_file, dest_file)
                except Exception as e:
                    logging.error(f"Error moving {source_file} to {dest_file}: {e}")
    finally:
        with lock:
            active_count -= 1
            logging.info(f"Worker finished for {folder}. Active workers: {active_count}")


def move_files(source_dir, dest_dir):
    # add timing using logging and time module
    start_time = time.time()
    logging.info(f"Started at {start_time}")
    # get a list of all folders under source_dir
    raw_folders = glob.glob(f"{source_dir}/*/")
    folders = raw_folders[0:2]
    print(folders)
    active_count = 0
    lock = Lock()
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(get_filenames, folder, dest_dir, lock, active_count): folder
            for folder in folders
        }
        for future in as_completed(futures):
            folder = futures[future]
            try:
                future.result()
            except Exception as exc:
                logging.error(f"{folder} generated an exception: {exc}")
            else:
                logging.info(f"Completed moving files for {folder}")
    end_time = time.time()
    logging.info(f"Ended at {end_time}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Move files from USB to external drive")
    parser.add_argument(
        "-sd",
        "--source_dir",
        type=str,
        help="Source directory",
        default="/Volumes/sp_stick/raw/Playlist/",
    )
    parser.add_argument(
        "-dd",
        "--dest_dir",
        type=str,
        help="Destination directory",
        default="/Volumes/Samsung_T5/DJ_Music_Library/",
    )
    args = parser.parse_args()
    source_dir = args.source_dir
    dest_dir = args.dest_dir

    if not os.path.exists(source_dir):
        raise Exception(f"Source directory {source_dir} does not exist.")
    elif not os.path.exists(dest_dir):
        raise Exception(f"Destination directory {dest_dir} does not exist.")
    else:
        move_files(source_dir, dest_dir)
        print(f"Files moved from {source_dir} to {dest_dir}.")
