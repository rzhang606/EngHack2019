#!/usr/bin/env python3

import requests
import json

import datetime
import time
import sys
import os

search_url = 'https://www.eventbriteapi.com/v3/events/search/'

api_key = 'Eventbrite-API-Key'
headers = {
  'Authorization': 'Bearer %s' % api_key,
  'Content-Type': 'application/json'
}


def ParseEvent(event_json):  # Parses Event html trees and sorts relevant data into a dictionary
    event_info = {}
    
    event_info["name"] = event_json["name"]["text"]
    event_info["start"] = "Starts at: " + event_json["start"]["local"]
    event_info["description"] = event_json["description"]["text"]

    """if 'venue' in event_json:
        if 'latitude' in event_json["venue"]:
            event_info["latitude"] = event_json["venue"]["latitude"]
        elif 'address' in event_json["venue"]:
            if 'latitude' in event_json["venue"]["address"]:
                event_info["latitude"] = event_json["venue"]["address"]["latitude"]

    if 'venue' in event_json:
        if 'longitude' in event_json["venue"]:
            event_info["longitude"] = event_json["venue"]["longitude"]
        elif 'address' in event_json["venue"]:
            if 'longitude' in event_json["venue"]["address"]:
                event_info["longitude"] = event_json["venue"]["address"]["longitude"]"""

    if not('latitude' in event_info) and not('longitude' in event_info):
        request = requests.get('https://www.eventbriteapi.com/v3/venues/%s/' % event_json["venue_id"], headers=headers)
        parse = json.loads(request.text)

        if 'address' in parse:
            if 'latitude' in parse["address"]:
                event_info["latitude"] = parse["address"]["latitude"]
            if 'longitude' in parse["address"]:
                 event_info["longitude"] = parse["address"]["longitude"]

    
    if 'ticket_availability' in event_json:
        event_info["price"] = 'Price: ' + event_json["ticket_availability"]["minimum_ticket_price"]["major_value"] + " - " + event_json["ticket_availability"]["maximum_ticket_price"]["major_value"] + " " + event_json["ticket_availability"]["maximum_ticket_price"]["currency"]
    elif 'is_free' in event_json:
        if event_json["is_free"]:
            event_info["price"] = "Price: FREE"

    if 'category' in event_json:
        event_info["categories"] = 'Categories: ' + event_json["category"]["name"]

    return event_info


def WriteEvents(event_dict, filename):  # Writes ads from given dictionary to given file
    #try:
	file = open(filename, 'ab')
	for event_id in event_dict:
		file.write(event_id.encode('utf-8'))
		file.write((str(event_dict[event_id]) + "\n").encode('utf-8'))
	file.close()
    #except:
        #print('[Error] Unable to write event(s) to file.')


def ReadEvents(filename):  # Reads given file and creates a dict of events in file
    import ast
    if not os.path.exists(filename):  # If the file doesn't exist, it makes it.
        file = open(filename, 'w')
        file.close()

    event_dict = {}
    with open(filename, 'rb') as file:
        for line in file:
            if line.strip() != '':
                index = line.find('{'.encode('utf-8'))
                event_id = line[:index].decode('utf-8')
                dictionary = line[index:].decode('utf-8')
                dictionary = ast.literal_eval(dictionary)
                event_dict[event_id] = dictionary
    return event_dict

def FormatDisc(event_dict):
    description = ""
    if 'description' in event_dict:
        if description != "":
            description = description + " || "
        description = description + event_dict["description"]
    if 'start' in event_dict:
        if description != "":
            description = description + " || "
        description = event_dict["start"]
    if 'price' in event_dict:
        if description != "":
            description = description + " || "
        description = event_dict["price"]
    if 'categories' in event_dict:
        if description != "":
            description = description + " || "
        description = event_dict["categories"]

    return description

def FormatPost(event_dict):
    postdict = {}
    postdict["event"] = event_dict["name"]
    postdict["latitude"] = str(event_dict["latitude"])
    postdict["longitude"] = str(event_dict["longitude"])
    postdict["description"] = FormatDisc(event_dict)
    postdict["type"] = 'events'
    print(postdict)
    return postdict

def PostReq(event_dict):  # Sends a request with a link and info of new Events
    
    post_dict = FormatPost(event_dict)

    post_url = 'https://yathinosaur.api.stdlib.com/roid@dev/insert_roid_event/'
    try:
        post_dict_json = json.loads(json.dumps(post_dict))
        r = requests.post(url = post_url, data = post_dict_json, verify = False)
        print(r)
    except:
        print('[Error] Unable to post data.')

def scrape(params, old_event_dict, exclude_list, filename, skip_flag):  # Pulls page data from a given kijiji url and finds all events on each page
    # Initialize variables for loop
    event_dict = {}

    req = requests.get(search_url, params = params, headers = headers)

    parsed = json.loads(req.text)

    eventbrite_events = parsed["events"]
        
    for event in eventbrite_events:  # Creates a dictionary of all events with event id being the keys.
        event_id = event['id'] # Get the event id
        if (event_id not in old_event_dict): # Skip third-party events and events already found
            print('[Okay] New event found! event id: ' + event_id)
            event_dict[event_id] = ParseEvent(event) # Parse data from event
            if not skip_flag: # if skip flag is set do not send request
                if 'latitude' in event_dict[event_id] and 'longitude' in event_dict[event_id]:
                    PostReq(event_dict[event_id]) # Send out post request with new events


    if event_dict != {}:  # If dict not emtpy, write events to text file.
        WriteEvents(event_dict, filename) # Save events to file

def main(): # Main function, handles command line arguments and calls other functions for parsing events
    args = sys.argv
    if args[1] == '-h' or args[1] == '--help': # Print script usage help
        print('Usage: Eventbrite-Scraper.py URL [-f] [-e] [-s]\n')
        print('Positional arguments:')
        print(' URL\t\tUrl to scrape for events\n')
        print('Optional arguments:')
        print(' -h, --help  show this help message and exit')
        print(' -f\t\tfilename to store events in (default name is the url)')
        print(' -e\t\tword that will exclude an event if its in the title (can be a single word or multiple words seperated by spaces')
        print(' -s\t\tflag that causes the program to skip sending a request. Useful if you want to index events but not be notified of them')
    else:
        params = {'sort_by': 'date', 'location.latitude': '43.4671806', 'location.longitude': '-80.55019279999999', 'location.within': '10km'}
        skip_flag = False
        if '-f' in args:
            filename = args.pop(args.index('-f') + 1)
            filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
            args.remove('-f')
        else:
            filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), url_to_scrape)
        if '-s' in args:
            skip_flag = True
            args.remove('-s')
        if '-e' in args:
            exclude_list = args[args.index('-e') + 1:]
        else:
            exclude_list = list()
        
    old_event_dict = ReadEvents(filename)
    print("[Okay] Event database succesfully loaded.")
    scrape(search_url, old_event_dict, exclude_list, filename, skip_flag)

if __name__ == "__main__":
    main()
