"""Don't use, use XLD instead."""

import logging
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

# Usage
input_directory = "/Users/sarahpak/Documents/DJ_Music_Library_FLAC_2024-06-16"
output_directory = "/Users/sarahpak/Documents/DJ_Music_Library_new"
SOURCE_TYPE = "flac"
DEST_TYPE = "aiff"


def get_audio_properties(input_file: str) -> tuple:
    """Get audio properties like sample rate and bit rate from the input file using ffprobe.
    :param input_file:
    :return: tuple of sample rate and bit rate
    """
    cmd = f"""ffprobe -v error -select_streams a:0 -show_entries stream=sample_rate,bit_rate -of default=noprint_wrappers=1:nokey=1 {input_file}"""

    result = subprocess.run(cmd, capture_output=True, text=True)
    sample_rate, bit_rate = result.stdout.split()
    return sample_rate, bit_rate


def convert_file(input_file: str, output_file: str) -> None:
    if os.path.exists(output_file):
        return
    sample_rate, bit_rate = get_audio_properties(input_file)

    command = [
        "ffmpeg",
        "-i",
        input_file,
        "-codec:a",
        "pcm_s16be",  # AIFF codec
        "-ar",
        sample_rate,  # Set sample rate
        "-b:a",
        bit_rate,  # Set bit rate
        "-map_metadata",
        "0",  # Copy metadata
        output_file,
    ]

    try:
        subprocess.run(command, check=True)
    except Exception as e:
        raise RuntimeError(f"Error converting {input_file} to {output_file}: {e}") from e


def convert_flac_to_aiff(
    input_dir: str, output_dir: str, max_workers: int, source_type: str, dest_type: str
) -> None:
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        raise FileNotFoundError(f"Output directory {output_dir} does not exist.")
        # os.makedirs(output_dir)

    # Create a list of (input_file, output_file) tuples
    files_to_convert = [
        (
            os.path.join(input_dir, filename),
            os.path.join(output_dir, filename.replace(f".{source_type}", f".{dest_type}")),
        )
        for filename in os.listdir(input_dir)
        if filename.endswith(f".{source_type}")
    ]

    # Use ThreadPoolExecutor to parallelize the conversion
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(convert_file, input_file, output_file): (input_file, output_file)
            for input_file, output_file in files_to_convert
        }

        for future in as_completed(future_to_file):
            input_file, output_file = future_to_file[future]
            try:
                future.result()
                logger.info(f"Converted {input_file} to {output_file}")
            except Exception as e:
                logger.info(f"Failed to convert {input_file}: {e}")


# Usage
convert_flac_to_aiff(
    input_directory, output_directory, max_workers=50, source_type=SOURCE_TYPE, dest_type=DEST_TYPE
)
