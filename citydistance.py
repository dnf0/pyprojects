'''
Work out the distance (user specified units) given two cities using haversine equation
'''

from pygeocoder import Geocoder
import numpy as np
import sys

def get_distance(locA, locB):
    #use haversine forumla
    earth_rad = 6371.0
    dlat = np.deg2rad(locB[0] - locA[0])
    dlon = np.deg2rad(locB[1] - locA[1])
    a = np.sin(dlat/2) * np.sin(dlat/2) + \
        np.cos(np.deg2rad(locA[0])) * np.cos(np.deg2rad(locB[0])) * \
        np.sin(dlon/2) * np.sin(dlon/2) 
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return earth_rad * c 

def get_latlongs(location):
    return Geocoder.geocode(location)[0].coordinates
        
def convert_km_to_miles(km):
    miles_per_km = 0.621371192
    return km * miles_per_km
    
def main():
    #get first city
    print 'Type the first City: '
    cityA = raw_input()
    
    #get second city
    print 'Type the second city: '
    cityB = raw_input()
    
    #get units
    units = ''
    while (units != 'km') & (units != 'm'):
        print 'Type distance units (miles or kilometers): '
        units = str.lower(raw_input())
        if units in ['clicks', 'km', 'kilometers', 'kilometer']:
            units = 'km'
        elif units in ['m', 'mile', 'miles']:
            units = 'm'
        else:
            print 'units not recognised, please try again'
            
    #find the distance in km
    try:
        distance = get_distance(get_latlongs(cityA),
                                get_latlongs(cityB))
        #display the distance
        if units == 'km':
            print str(distance),' km'   
        else:
            distance = convert_km_to_miles(distance)
            print str(distance), ' miles' 
            
    except:
        print 'Error raised.  Are the input cities correct?'
        
            
if __name__ == '__main__':
    sys.exit(main())