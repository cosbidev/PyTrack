import json
import os
from pathlib import Path

import requests


def extract_streetview_pic(point, api_key, size="640x640", heading=90, pitch=-10):
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
    # if (meta["pano_id"] != PREV_PAN_ID) and (meta["status"] == "OK"):
    #    PREV_PAN_ID = meta["pano_id"]
    #    pic_response = requests.get(pic_base, params=pic_params)

    #       pic = pic_response.content
    #        pic_response.close()
    #  else:
    #     meta = None
    #    pic = None
    pic_response = requests.get(pic_base, params=pic_params)
    pic = pic_response.content
    pic_response.close()

    return pic, meta


def save_streetview(pic, meta, folder_path):
    Path(os.path.join(folder_path)).mkdir(parents=True, exist_ok=True)

    with open(os.path.join(folder_path, 'pic.png'), 'wb') as file:
        file.write(pic)

    with open(os.path.join(folder_path, 'metadata.json'), 'w+') as out_file:
        json.dump(meta, out_file)
