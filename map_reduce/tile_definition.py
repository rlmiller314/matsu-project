from math import floor

def tileIndex(depth, longitude, latitude):
    "Inputs a depth and floating-point longitude and latitude, outputs a triple of index integers."
    if abs(latitude) > 90.: raise ValueError("Latitude cannot be %s" % str(latitude))
    longitude += 180.
    latitude += 90.
    while longitude <= 0.: longitude += 360.
    while longitude > 360.: longitude -= 360.
    longitude = int(floor(longitude/360. * 2**(depth+1)))
    latitude = min(int(floor(latitude/180. * 2**(depth+1))), 2**(depth+1) - 1)
    return depth, longitude, latitude

def tileName(depth, longitude, latitude):
    "Inputs an index-triple, outputs a string-valued name for the index."
    return "T%02d-%05d-%05d" % (depth, longitude, latitude)  # constant length up to depth 15

def tileCorners(depth, longitude, latitude):
    "Inputs an index-triple, outputs the floating-point corners of the tile."
    longmin = longitude*360./2**(depth+1) - 180.
    longmax = (longitude + 1)*360./2**(depth+1) - 180.
    latmin = latitude*180./2**(depth+1) - 90.
    latmax = (latitude + 1)*180./2**(depth+1) - 90.
    return longmin, longmax, latmin, latmax

