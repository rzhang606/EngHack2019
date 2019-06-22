import pandas as pd
import folium
import requests
import json

#FUNCTION DECLARATIONS
def retrieveJSON():
    URL = "https://yathinosaur.api.stdlib.com/http-project@dev/receive_events/"

    postData = {"latitude": 43, "longitude": -80}
    r = requests.post(url = URL, data = postData)
    returned = r.text

    #create json file
    with open('data.json', 'w') as outfile:
        json.dump(returned, outfile, ensure_ascii=False, indent=2)

    return 0    
# END FUNCTION DECLARATIONS


#retrieve data from api -- 
retrieveJSON()

#build the map --
map = folium.Map(location=[43.471965, -80.538232], zoom_start=15)

points = folium.FeatureGroup(name="Points")
points.add_child(folium.Marker(location=[43.4719, -80.5382], popup="We are here!", icon=folium.Icon(color='green')))

with open('data.json', 'r') as json_file:
    json_data = json.loads(json.load(json_file))
    #print(json_data["distinctQueryResult"]["rows"][0]['fields'])

    length = len(json_data["distinctQueryResult"]["rows"])
    myrange = length if length < 10 else 10

    for i in range(myrange):
        eventObject = json_data["distinctQueryResult"]["rows"][i]["fields"]
        points.add_child(folium.Marker(location=[eventObject['Latitude'], eventObject['Longitude']],
        popup="%s \n Description: %s" % (eventObject['Event'], eventObject['Description']), icon=folium.Icon(color='green')))
    

map.add_child(points)


map.save("enghack.html")
