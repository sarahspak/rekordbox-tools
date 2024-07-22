import argparse
import logging
import shutil
import subprocess

import rename_files_no_numbers

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


def main(link: str, tidal_output_dir: str, base_library_dir: str) -> None:
    dl_playlist_from_tidal(link, tidal_output_dir)
    # move files from {tidal_output_dir} into {base_library_dir}/
    move_from_tidal_output_to_library_dir(base_library_dir, tidal_output_dir)
    # delete Playlist folder
    delete_playlist_folder(base_library_dir)
    # convert flac to aiff
    convert_all_flac_to_aiff(base_library_dir)

    # clean up
    delete_all_files_ending_in_flac(base_library_dir)
    rename_files(base_library_dir)

    logger.info("All done! Don't forget to add the files to rekordbox.")
    return


def rename_files(base_library_dir: str) -> None:
    try:
        rename_files_no_numbers.main(base_dir=base_library_dir, suffix="aiff", dry_run=False)
    except Exception as e:
        raise RuntimeError(f"Error renaming files: {e}") from e


def dl_playlist_from_tidal(link: str, tidal_output_dir: str):
    try:
        subprocess.run(
            ["tidal-dl", "-l", link, "-q", "Master", "-o", tidal_output_dir],
            check=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
    except Exception as e:
        raise RuntimeError(f"Error running tidal-dl: {e}") from e


def move_from_tidal_output_to_library_dir(base_library_dir, tidal_output_dir):
    try:
        subprocess.run(
            f"mv {tidal_output_dir}/Playlist/*/*.flac {base_library_dir}/",
            shell=True,
            check=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
    except Exception as e:
        raise RuntimeError(f"Error moving files: {e}") from e


def delete_playlist_folder(base_library_dir):
    try:
        subprocess.run(
            f"rm -rf {base_library_dir}/Playlist",
            shell=True,
            check=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
    except Exception as e:
        raise RuntimeError(f"Error deleting Playlist folder: {e}") from e


def convert_all_flac_to_aiff(base_library_dir):
    try:
        subprocess.run(
            f"find {base_library_dir}/ -name '*.flac' -print0 | "
            + "xargs -0 -I {} "
            + f"xld -f aif -o {base_library_dir}/ "
            + "{}",
            shell=True,
            check=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
    except Exception as e:
        raise RuntimeError(f"Error converting flac files to aiff: {e}") from e


def delete_all_files_ending_in_flac(base_library_dir):
    # then delete all the files ending in .flac
    try:
        subprocess.run(
            f"find {base_library_dir}/ -name '*.flac' -delete",
            shell=True,
            check=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
    except Exception as e:
        raise RuntimeError(f"Error deleting flac files: {e}") from e


def _check_path_exists(executable_name: str) -> str:
    _path = shutil.which(executable_name)
    if _path is None:
        raise RuntimeError(f"{executable_name} executable not found")
    return _path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run tidal-dl and prepare files to be added to rekordbox"
    )
    parser.add_argument("-l", "--link", help="Tidal playlist URL link", required=True)
    parser.add_argument(
        "-o",
        "--tidal_output_dir",
        help="where to save tidal output",
        default="/Volumes/Samsung_T5/DJ_Music_Library_new",
    )
    parser.add_argument(
        "-b",
        "--base_library_dir",
        help="Base directory of the library",
        default="/Volumes/Samsung_T5/DJ_Music_Library_new",
    )

    args = parser.parse_args()
    main(
        link=args.link,
        tidal_output_dir=args.tidal_output_dir,
        base_library_dir=args.base_library_dir,
    )
