#?center=-26.131,28.170&zoom=18&size=640x640&scale=2&style=feature:poi|element:labels|visibility:off&style=feature:road|element:labels|visibility:off&key=AIzaSyDrkpShIXDSUW9H4r2EhU62KmEVsloMYS4
# Meters per pixel = 156543.03392 * Math.cos(latLng.lat() * Math.PI / 180) / Math.pow(2, zoom)
import urllib2

lat = -26.131
lng = 28.170
STATIC_BASE_URL = "https://maps.googleapis.com/maps/api/staticmap"
api_key = "AIzaSyDrkpShIXDSUW9H4r2EhU62KmEVsloMYS4"
imageurl = (STATIC_BASE_URL + "?" + 
            "center=" + str(lat) + "," + str(lng) + "&" + 
            "zoom=18&size=640x480&scale=2&style=feature:poi|element:labels|visibility:off&style=feature:road|element:labels|visibility:off"
            "&key=" + api_key)
                        
response = urllib2.urlopen(imageurl)
filename = "img1.png"
f = open(filename, "wb")
f.write(response.read())
f.close()