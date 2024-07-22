import argparse
import io
import logging
import mimetypes
import subprocess
from typing import List

from mutagen.flac import FLAC, Picture
from PIL import Image
from pyrekordbox import Rekordbox6Database, show_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)
# Determine the bit depth per channel
mode_to_bit_depth = {
    "1": 1,  # 1-bit pixels, black and white, stored with one pixel per byte
    "L": 8,  # 8-bit pixels, grayscale
    "P": 8,  # 8-bit pixels, mapped to any other mode using a color palette
    "RGB": 8 * 3,  # 8-bit pixels, true color (3x8-bit per pixel)
    "RGBA": 8 * 4,  # 8-bit pixels, true color with transparency mask (4x8-bit per pixel)
}


def create_picture(image_file: str) -> Picture:
    # getting data from open(image_file) works, but getting it from PIL doesn't seem to work - maybe bc PIL is
    # dropping some bytes?
    image_data = open(image_file, "rb").read()
    pic = Picture()
    pic.data = image_data

    imagefile = io.BytesIO(image_data)
    imagefile.seek(0)
    img = Image.open(imagefile)
    pic.width, pic.height = img.size
    pic.depth = mode_to_bit_depth.get(img.mode, None)
    pic.desc = "Cover Art"
    pic.type = 3  # 3 is for cover (front)

    try:
        pic.mime = mimetypes.guess_type(image_file)[0]
    except Exception as e:
        raise Exception(f"Error getting mime type: {e}") from e
    return pic


def attach_picture_to_file(audio_file: str, picture: Picture) -> None:
    audio = FLAC(audio_file)
    # attach picture
    audio.clear_pictures()
    audio.add_picture(picture)
    # save
    audio.save()
    return


def find_all_tracks_with_same_album(audio_file: str) -> List[str]:
    """Use rekordbox to find all tracks with the same album and return a list of audio_files that we need to
    attach the album artwork to"""
    # TODO: make sure we have key
    try:
        logger.info(show_config())
    except Exception as e:
        logger.error(e)
        subprocess.run("""python -m pyrekordbox download-key""")

    db = Rekordbox6Database()
    results = db.get_content(FolderPath=f"{audio_file}").all()
    if len(results) != 1:
        raise Exception(
            f"We should only be getting 1 result for {audio_file} but we have {len(results)} - this may mean we have a duplicate"
        )
    album_id = results[0].AlbumID
    # Get ImagePath for all tracks in the same album
    results = db.get_content(AlbumID=f"{album_id}").all()
    return results


def attach_existing_album_art_to_tracks(results: List) -> None:
    """Takes a list of results from db query (all tracks from same album and attaches image path if it exists"""
    db = Rekordbox6Database()

    valid_image_path_for_album = list(set([c.ImagePath for c in results if c.ImagePath]))
    if len(valid_image_path_for_album) >= 1:
        new_image_path = valid_image_path_for_album[0]
    else:
        raise Exception("Cannot find a valid path for image")
    for c in results:
        if c.ImagePath is None or c.ImagePath == "":
            # TODO: update with
            c.ImagePath = new_image_path
            logger.info(
                f"commiting change to imagePath for {c.FileNameL} from None to {new_image_path}"
            )
            db.commit()
        else:
            pass


def main(audio_file: str, image_file: str) -> None:
    # picture = create_picture(image_file)
    # attach_picture_to_file(audio_file, picture)
    # logger.info(f"All done attaching cover image to {audio_file}")
    results = find_all_tracks_with_same_album(audio_file)
    logger.info(results)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--file",
        default="/Volumes/Samsung_T5/DJ_Music_Library/18 - Anunaku - Venus.flac",
        help="input audio file",
    )
    parser.add_argument(
        "-i",
        "--image_file",
        default="/Volumes/Samsung_T5/album_art/anunaku-063.jpeg",
        help="input image file",
    )
    args = parser.parse_args()
    main(args.file, args.image_file)
