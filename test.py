import geocoder
g = geocoder.ip('me')
latitude, longitude = g.latlng
print(latitude, longitude)