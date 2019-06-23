#!/usr/bin/env python3

import requests
import json

import sys
import os


api_key = 'Yelp-API-Key'
headers = {'Authorization': 'Bearer %s' % api_key}

url='https://api.yelp.com/v3/businesses/search'

def ParseJson(business_json, params):
    business_info = {}

    business_info["name"] = business_json["name"]
    business_info["rating"] = 'Rating: ' + str(business_json["rating"])
    business_info["latitude"] = business_json["coordinates"]["latitude"]
    business_info["longitude"] = business_json["coordinates"]["longitude"]
    if 'price' in business_json:
        business_info["price"] = 'Price: ' + business_json["price"]
    else:
        business_info["price"] = ''
    business_info["categories"] = 'Categories: ' 
    for categories in business_json["categories"]:
        business_info["categories"] = business_info["categories"] + categories["alias"] + ", "
    business_info["categories"] = business_info["categories"][:-2]
    business_info["type"] = params['term']

    return business_info

def FormatPost(business_dict):
    postdict = {}
    postdict["event"] = business_dict["name"]
    postdict["latitude"] = str(business_dict["latitude"])
    postdict["longitude"] = str(business_dict["longitude"])
    postdict["description"] = business_dict["rating"] + " || " + business_dict["price"] + " || " + business_dict["categories"]
    postdict["type"] = business_dict["type"]
    print(postdict)
    return postdict

def PostReq(business_dict):  # Sends a request with a link and info of businesses
    
    post_dict = FormatPost(business_dict)

    post_url = 'https://yathinosaur.api.stdlib.com/roid@dev/insert_roid_event/'
    try:
        post_dict_json = json.loads(json.dumps(post_dict))
        r = requests.post(url = post_url, data = post_dict_json, verify = False)
        print(r)
    except:
        print('[Error] Unable to post data.')

def WriteBusinesses(business_dict, filename):  # Writes businesses from given dictionary to given file
    #try:
    file = open(filename, 'ab')
    for business_id in business_dict:
        file.write(business_id.encode('utf-8'))
        file.write((str (business_dict[business_id]) + "\n").encode('utf-8'))
    file.close()
    #except:
        #print('[Error] Unable to write ad(s) to file.')


def ReadBusinesses(filename):  # Reads given file and creates a dict of businesses in file
    import ast
    if not os.path.exists(filename):  # If the file doesn't exist, it makes it.
        file = open(filename, 'w')
        file.close()

    business_dict = {}
    with open(filename, 'rb') as file:
        for line in file:
            if line.strip() != '':
                index = line.find('{'.encode('utf-8'))
                business_id = line[:index].decode('utf-8')
                dictionary = line[index:].decode('utf-8')
                dictionary = ast.literal_eval(dictionary)
                business_dict[business_id] = dictionary
    return business_dict

def scrape(params, old_dict, exclude_list, filename, skip_flag):
    business_dict = {}
    req = requests.get(url, params=params, headers=headers)
 
    parsed = json.loads(req.text)
    businesses = parsed["businesses"]

    for business in businesses:
        business_id = business['id'] # Get the business id
        if (business_id not in old_dict): # Skip businesses already found
                    print('[Okay] New business found! business id: ' + business_id)
                    business_dict[business_id] = ParseJson(business, params) # Parse data from business json
                    if not skip_flag: # if skip flag is set do not send request
                        if 'latitude' in business_dict[business_id] and 'longitude' in business_dict[business_id]:
                            PostReq(business_dict[business_id]) # Send out post request with new business
    if business_dict != {}:  # If dict not emtpy, write businesses to text file.
        WriteBusinesses(business_dict, filename) # Save businesses to file


def main(): # Main function, handles command line arguments and calls other functions for parsing business
    args = sys.argv
    if args[1] == '-h' or args[1] == '--help': # Print script usage help
        print('Usage: Yelp-Scraper.py URL [-f] [-e] [-s]\n')
        print('Positional arguments:')
        print(' URL\t\tUrl to scrape for businesses\n')
        print('Optional arguments:')
        print(' -h, --help  show this help message and exit')
        print(' -f\t\tfilename to store businesses in (default name is the url)')
        print(' -e\t\tword that will exclude an ad if its in the title (can be a single word or multiple words seperated by spaces')
        print(' -s\t\tflag that causes the program to skip sending an request. Useful if you want to index businesses but not be notified of them')
    else:
        term = args[1]
        location = "Waterloo, ON"
        # In the dictionary, term can take values like food, cafes or businesses like McDonalds
        params = {'term': term,'location': location}
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
        
    old_yelp_dict = ReadBusinesses(filename)
    print("[Okay] Yelp database succesfully loaded.")
    scrape(params, old_yelp_dict, exclude_list, filename, skip_flag)

if __name__ == "__main__":
    main()
