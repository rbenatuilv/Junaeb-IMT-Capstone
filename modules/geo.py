import requests
import geopandas as gpd
from typing import Union
from shapely.geometry import Point
import math


def get_coords_osm(address: str, verbose=1) -> tuple[float, float]:
    """
    Get the coordinates of a given address, using Open Street Map API.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json"}
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if response.status_code == 200 and len(data) > 0:
            return float(data[0]["lat"]), float(data[0]["lon"])
        else:
            if verbose > 0:
                print('Unable to retrieve coordinates:', 
                      data['error_message'])
            return None
    except requests.exceptions.RequestException as e:
        print('Request error:', str(e))
        return None


def get_coords_google(address: str, api_key: str, verbose=1) -> tuple[float, float]:
    """
    Get the coordinates of a given address, using Google Maps API 
    (API Key needed).
    """

    endpoint = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': address,
        'key': api_key
    }

    try:
        response = requests.get(endpoint, params=params)
        data = response.json()
        if response.status_code == 200 and data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            latitude = location['lat']
            longitude = location['lng']
            return latitude, longitude
        else:
            if verbose > 0:
                print('Unable to retrieve coordinates:', 
                      data['error_message'])
            return None

    except requests.exceptions.RequestException as e:
        print('Request error:', str(e))
        return None


def convert_to_degrees(meters: float) -> float:
    """
    Convert a given distance in meters to degrees.
    """
    earth_radius = 6371000  # meters
    conversion_factor = 2 * math.pi * earth_radius / 360
    return meters / conversion_factor


def convert_to_meters(degrees: float) -> float:
    """
    Convert a given distance in degrees to meters.
    """
    earth_radius = 6371000  # meters
    conversion_factor = 2 * math.pi * earth_radius / 360
    return degrees * conversion_factor


def nearest_points(coords: Union[tuple, Point], 
                   gdf: gpd.GeoDataFrame, 
                   k: int, max_radius: int, margin=5, 
                   index: int = -1) -> tuple[int, list]:
    """
    NOTE: NOT TESTED YET

    Compute the nearest points to a given coordinate, from a GeoDataFrame.
    `k` is the number of points to search for. `max_radius` is the maximum radius 
    to search for points. A `margin` parameter can be modified to search for 
    more points, if the number of points found is less than `k`. Returns the amount
    of points found and a list with the indices of the points.
    """

    if isinstance(coords, tuple):
        coords = Point(coords[::-1])

    # Create a spatial index
    sindex = gdf.sindex

    ran = range(k, k + margin)
    lon = 0
    r = max_radius
    u = max_radius
    l = 0

    memo = None
    while lon not in ran and u - l > 0:
        buff = coords.buffer(r)
        possible_matches_index = list(sindex.intersection(buff.bounds))
        possible_matches = gdf.iloc[possible_matches_index]
        precise_matches = possible_matches[possible_matches.intersects(buff)]
        lon = len(precise_matches)

        if lon < k:
            l = r + 1
        else:
            memo = precise_matches
            u = r - 1

        r = (u + l) // 2

    if l > max_radius:
        memo = precise_matches
    memo = [row.Index for row in memo.itertuples() if row.Index != index]
    return lon, memo
