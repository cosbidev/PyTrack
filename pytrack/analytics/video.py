import json
import os
from pathlib import Path

import cv2
import requests

PREV_PAN_ID = None


def make_video(images, output_path, fourcc, fps=1, size=(640, 640), is_color=True):
    """ Makes video using xvid codec. Increase FPS for faster timelapse.

    Parameters
    ----------
    images: list
        List of the image paths to be added as frames to the video.
    output_path: str
        Path to output video, must end with .avi.
    fps: int, optional, default: 1
        Desired frame rate.
    size: tuple, optional, default: (640, 640)
        Size of the video frames.
    is_color: bool, optional, default: True
        If it is True, the encoder will expect and encode color frames, otherwise it will work with grayscale frames.

    :return: The function does not return anything. It directly saves the video at the position indicated in output_path.
    """
    vid = cv2.VideoWriter(output_path, fourcc, fps, size, is_color)
    for image in images:
        vid.write(cv2.imread(image))
    vid.release()
    cv2.destroyAllWindows()


def extract_streetview_pic(point, api_key, size="640x640", heading=90, pitch=-10):
    """ Extract street view pic.

    Parameters
    ----------
    point: tuple
        The lat/lng value of desired location.
    api_key: str
        Street View Static API key. It allows you to monitor your application's API usage in the Google Cloud Console,
        and ensures that Google can contact you about your application if necessary.
    size: str, optional, default: "640x640"
        Specifies the output size of the image in pixels.
    heading: int, optional, default: 90
        indicates the compass heading of the camera. Accepted values are from 0 to 360 (both values indicating North,
        with 90 indicating East, and 180 South). If no heading is specified, a value will be calculated that directs
        the camera towards the specified location, from the point at which the closest photograph was taken.
    pitch: int, optional, default: -10
        specifies the up or down angle of the camera relative to the Street View vehicle. This is often, but not always,
        flat horizontal. Positive values angle the camera up (with 90 degrees indicating straight up); negative values
        angle the camera down (with -90 indicating straight down).

    Returns
    -------
    pic: request.content
        Image get from Street View.
    meta: json
        Data about Street View panoramas.
    """

    global PREV_PAN_ID

    meta_base = 'https://maps.googleapis.com/maps/api/streetview/metadata?'
    pic_base = 'https://maps.googleapis.com/maps/api/streetview?'

    lat = point[0]
    lon = point[1]

    meta_params = {'key': api_key,
                   'location': f'{lat}, {lon}',
                   'source': 'outdoor'}

    pic_params = {
        'size': size,  # max 640x640 pixels
        'location': f'{lat}, {lon}',
        'heading': str(heading),
        'pitch': str(pitch),
        'key': api_key,
        'source': 'outdoor'
    }

    # Do the request and get the response data
    meta_response = requests.get(meta_base, params=meta_params)
    meta = meta_response.json()
    meta_response.close()
    if meta["status"] == "REQUEST_DENIED":
        print(meta)
    if (meta["status"] == "OK") and (meta["pano_id"] != PREV_PAN_ID):
        PREV_PAN_ID = meta["pano_id"]
        pic_response = requests.get(pic_base, params=pic_params)

        pic = pic_response.content
        pic_response.close()
    else:
        meta = None
        pic = None

    return pic, meta


def save_streetview(pic, meta, folder_path):
    """ Save streetview pic and metadata in the desired path.

    Parameters
    ----------
    pic: request.content
        Image get from Street View.
    meta: json
        Data about Street View panoramas.
    folder_path: str
        Desired path of the folder where save pic and metadata.

    :return: The function does not return anything. It directly saves the pic and metadata at the position indicated in folder_path.
    """
    Path(os.path.join(folder_path)).mkdir(parents=True, exist_ok=True)

    with open(os.path.join(folder_path, 'pic.png'), 'wb') as file:
        file.write(pic)

    with open(os.path.join(folder_path, 'metadata.json'), 'w+') as out_file:
        json.dump(meta, out_file)
