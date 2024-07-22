import argparse
import logging
import shutil
import subprocess

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


def main(link: str, tidal_output_dir: str, base_library_dir: str) -> None:
    # Find the full path of the 'pyenv' executable
    _activate_tidal_dl_pyenv()
    # then run tidal-dl -l <link> -q "Master" -o <output_dir>
    try:
        tidal_dl_path = _check_path_exists("tidal-dl")
        subprocess.run(
            [tidal_dl_path, "-l", link, "-q", "Master", "-o", tidal_output_dir],
            check=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
    except Exception as e:
        raise RuntimeError(f"Error running tidal-dl: {e}") from e
    # move everything from {tidal_output_dir} into {base_library_dir}/
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
    # delete the Playlist folder
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
    # convert all the flac files to aiff
    try:
        subprocess.run(
            f"find {base_library_dir}/ -name '*.flac' -print0 | "
            + "xargs -0 -I {} "
            + f"xld -f aif -o {base_library_dir}/"
            + "--raw {}",
            shell=True,
            check=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
    except Exception as e:
        raise RuntimeError(f"Error converting flac files to aiff: {e}") from e

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

    # then run python3 rename_files_no_numbers.py --base_dir {base_library_dir}/ --suffix aiff
    try:
        subprocess.run(
            f"python3 rename_files_no_numbers.py --base_dir {base_library_dir} --suffix aiff",
            shell=True,
            check=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
    except Exception as e:
        raise RuntimeError(f"Error renaming files: {e}") from e
    logger.info("All done! Don't forget to add the files to rekordbox.")
    return


def _check_path_exists(executable_name: str) -> str:
    _path = shutil.which(executable_name)
    if _path is None:
        raise RuntimeError(f"{executable_name} executable not found")
    return _path


def _activate_tidal_dl_pyenv() -> None:
    pyenv_path = _check_path_exists("pyenv")
    if pyenv_path is None:
        raise RuntimeError("pyenv executable not found")
    try:
        subprocess.run(
            [pyenv_path, "activate", "tidal-dl"],
            check=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
    except Exception as e:
        raise RuntimeError(f"Error activating pyenv: {e}") from e


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
