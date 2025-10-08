def contains_lat_lon(object: list):
    return any('lat' or 'lon' in attr for attr in object)