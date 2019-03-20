import copy

URL_BASE = 'localhost:5000'
DATE_FOR_IMAGES = '03061999'
COMPRESSED_IMAGE_URL = '/api/images/scatter03061999_compressed.jpg'
FULL_IMAGE_URL = '/api/images/scatter03061999_full.jpg'
COMPRESSED_IMAGE_FILE_LOCATION = 'P61i5ZR_compressed.jpg'
FULL_IMAGE_FILE_LOCATION = 'P61i5ZR_full.jpg'

DEFAULT_NUM_IMAGES = 5

LAT_LONGS = [{'latitude': float(i), 'longitude': float(i)} for i in range(3)]

VOLCANO_HAZARD_TEMPLATES = {
    'type': 'volcanoes',
    'hazards': list()
}

HAZARD_INFO_TEMPLATE = {
    'hazard_id': 'VolcanoName',
    'name': 'Volcano Name',
    'location': {
        'latitude': 0.0,
        'longitude': 0.0
    },
    'last_updated': '05182019'
}

SUPPORTED_IMAGE_TYPES = ["geo_backscatter", "geo_coherence",
               "geo_interferogram", "ortho_backscatter",
               "ortho_coherence", "ortho_interferogram"]

def IMAGE_TYPE_DATA_TEMPLATE(num_images):
    return [
        {
            'date': DATE_FOR_IMAGES,
            'compressed_image_url': COMPRESSED_IMAGE_URL,
            'full_image_url': FULL_IMAGE_URL
        }
        for _ in range(num_images)
    ]

def HAZARD_DATA_TEMPLATE(num_images):
    return {
    'hazard_id': 'VolcanoName',
    'hazard_name': 'Volcano Name',
    'last_updated': '05182019',
    'location': {
        'latitude': 0.0,
        'longitude': 0.0
      },
    'images_by_satellite': {
        'satellite_id0': {image_type: IMAGE_TYPE_DATA_TEMPLATE(num_images) for image_type in SUPPORTED_IMAGE_TYPES},
        'satellite_id1': {image_type: IMAGE_TYPE_DATA_TEMPLATE(num_images) for image_type in SUPPORTED_IMAGE_TYPES},
    }
}



def get_all_volcano_summary_info():
    '''
    Generates and returns the data needed for the landing page endpoint(URL: /api/:hazard_type).

    This function injects the number of volcanoes returned and the lat-long info into the VOLCANO_HAZARD_TEMPLATES.
    :return: dict
    '''

    response = copy.deepcopy(VOLCANO_HAZARD_TEMPLATES)

    for latitude_longitude in LAT_LONGS:
        current_hazard = copy.deepcopy(HAZARD_INFO_TEMPLATE)
        current_hazard['location'] = latitude_longitude
        response['hazards'].append(current_hazard)

    return response

def get_volcano_hazard_info_by_id(hazard_id, image_types, satellites, max_num_images):
    response = copy.deepcopy(HAZARD_DATA_TEMPLATE(
        num_images=max_num_images if max_num_images is not 0 else DEFAULT_NUM_IMAGES))
    for satellite in HAZARD_DATA_TEMPLATE(DEFAULT_NUM_IMAGES)['images_by_satellite']:
        # TODO: TAKE CARE OF `satellites` being None case
        if len(image_types) != 0:
            for image_type in SUPPORTED_IMAGE_TYPES:
                # TODO: TAKE CARE OF `image_types` being None case
                if image_types is not None and image_type not in image_types:
                    del response['images_by_satellite'][satellite][image_type]
                    print("HERE2:", image_type)
                else:
                    if max_num_images > 0:
                        response['images_by_satellite'][satellite][image_type] = \
                            response['images_by_satellite'][satellite][image_type][:max_num_images]
                print("HERE3:", image_type)
        if len(satellites) != 0:
            if satellite not in satellites:
                del response['images_by_satellite'][satellite]

    return response


def get_image_file_location(image_id):
    print("FULL URL:", FULL_IMAGE_URL.split('/')[-1])
    if image_id == FULL_IMAGE_URL.split('/')[-1]:
        return FULL_IMAGE_FILE_LOCATION
    elif image_id == COMPRESSED_IMAGE_URL.split('/')[-1]:
        return COMPRESSED_IMAGE_FILE_LOCATION
    else:
        return None
