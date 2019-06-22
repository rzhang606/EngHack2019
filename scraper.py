import requests
import json

latitude = "43.6000"
longitude = "34.0000"

call = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" + latitude + "," + longitude + "&radius=3000&key=AIzaSyBHDiJkFLIemfsjbXEssGl4rV09SFXdkx8"
print(call)

places = requests.get(call).json()

print(str(places))