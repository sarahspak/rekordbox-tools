"""Remove numbers from the start of the filename"""

import argparse
import logging
import os
import re

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


def recursive_filelist(directory: str, suffix: str) -> list:
    file_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(f".{suffix}"):
                file_list.append(os.path.join(root, file))
    return file_list


def main(base_dir: str, suffix: str, dry_run: bool) -> int:
    file_list = recursive_filelist(base_dir, suffix)

    # for each file in the folder, check if the file name starts with a number and "-" and a space
    # if it does, rename the file to the number and move it to the root folder
    for full_file in file_list:
        filepath = "/".join(full_file.split("/")[:-1])
        file = full_file.split("/")[-1]
        if re.match(r"^\d+ - .*", file):
            new_file_name = re.sub(r"^\d+ - ", "", file)
            if dry_run:
                logger.info(
                    f"old file is {filepath}/{file}, new file is {filepath}/{new_file_name}"
                )
            else:
                os.rename(filepath + f"/{file}", filepath + f"/{new_file_name}")
    logger.info("all done!")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Remove the numbers that Tidal downloads have by default"
    )
    parser.add_argument(
        "--base_dir",
        type=str,
        help="The source directory containing files we want to rename.",
        default="/Volumes/Samsung_T5/DJ_Music_Library_new/",
    )
    parser.add_argument("-s", "--suffix", default="aiff")
    parser.add_argument("-d", "--dry-run", default=False)
    args = parser.parse_args()
    main(base_dir=args.base_dir, suffix=args.suffix, dry_run=args.dry_run)
