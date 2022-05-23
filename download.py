import requests


def get_filters(network_type='drive'):
    osm_filters = dict()

    osm_filters['drive'] = ('["highway"]["area"!~"yes"]["access"!~"private"]'
                            '["highway"!~"abandoned|bridleway|bus_guideway|construction|corridor|cycleway|'
                            'elevator|escalator|footway|path|pedestrian|planned|platform|proposed|raceway|steps|track"]'
                            '["service"!~"emergency_access|parking|parking_aisle|private"]')

    return osm_filters[network_type]


def osm_download(bbox, network_type=None):
    # TODO: add network_type statement
    north, south, west, east = bbox

    osm_filters = get_filters(network_type='drive')

    url_endpoint = 'https://maps.mail.ru/osm/tools/overpass/api/interpreter'

    timeout = 180
    out_resp = 'json'

    overpass_settings = f'[out:{out_resp}][timeout:{timeout}]'

    query_str = f'{overpass_settings};(way{osm_filters}({south}, {west}, {north}, {east});>;);out;'

    response_json = requests.post(url_endpoint, data={'data': query_str})

    size_kb = len(response_json.content) / 1000
    print(f'Downloaded {size_kb:,.2f}kB')

    return response_json.json()
