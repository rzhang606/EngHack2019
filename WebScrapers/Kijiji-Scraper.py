#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json

import datetime
import time
import sys
import os



def ParseAd(html):  # Parses ad html trees and sorts relevant data into a dictionary
    ad_info = {}
    
    #description = html.find('div', {"class": "description"}).text.strip()
    #description = description.replace(html.find('div', {"class": "details"}).text.strip(), '')
    #print(description)
    try:
        ad_info["Title"] = html.find('a', {"class": "title"}).text.strip()
    except:
        print('[Error] Unable to parse Title data.')
        
    try:
        ad_info["Image"] = str(html.find('img'))
    except:
        print('[Error] Unable to parse Image data')

    try:
        ad_info["Url"] = 'http://www.kijiji.ca' + html.get("data-vip-url")
    except:
        print('[Error] Unable to parse URL data.')
        
    try:
        ad_info["Details"] = html.find('div', {"class": "details"}).text.strip()
    except:
        print('[Error] Unable to parse Details data.')   
        
    try:
        description = html.find('div', {"class": "description"}).text.strip()
        description = description.replace(ad_info["Details"], '')
        ad_info["Description"] = description
    except:
        print('[Error] Unable to parse Description data.')    

    try:
        ad_info["Date"] = html.find('span', {"class": "date-posted"}).text.strip()
    except:
        print('[Error] Unable to parse Date data.')    
    
    """try:
        location = html.find('div', {"class": "location"}).text.strip()
        location = location.replace(ad_info["Date"], '')        
        ad_info["Location"] = location
    except:
        print('[Error] Unable to parse Location data.')"""

    try:
        try:
            page = requests.get(ad_info["Url"]) # Get the html data from the URL
        except:
            print("[Error] Unable to load " + url)
            sys.exit(1)
    
        soup = BeautifulSoup(page.content, "html.parser")

        location = soup.find("span", itemprop="address").text.strip()

        ad_info["Location"] = location
    except:
        print('[Error] Unable to parse Location data.')

    #Code Bellow to Uses Geocoder.ca
    """try:
        location = ad_info["Location"].split(" ")
        geourl = 'https://geocoder.ca/?locate='
        for i in location:
            geourl = geourl + "%20" + i
        geourl = geourl + '&geoit=xml&json=1'
        print(geourl)
        r = requests.get(geourl)
        results = r.json()
        ad_info["latitude"] = results["latt"]
        ad_info["longitude"] =results["longt"]
    except:
        print('[Error] Unable to parse longitude & latitude data.')"""

    #Code Bellow to Uses Google Geocoding API
    try:
        location = ad_info["Location"].split(" ")
        API_Key = "Google-API-Key"
        geourl = 'https://maps.googleapis.com/maps/api/geocode/json?address='
        for i in location:
            geourl = geourl + "+" + i
        geourl = geourl + '&key=' + API_Key
        print(geourl)
        r = requests.get(geourl)
        results = r.json()
        rLocation = results["results"][0]["geometry"]["location"]
        ad_info["latitude"] = rLocation["lat"]
        ad_info["longitude"] =rLocation["lng"]
    except:
        print('[Error] Unable to parse longitude & latitude data.')

    try:
        ad_info["Price"] = html.find('div', {"class": "price"}).text.strip()
    except:
        print('[Error] Unable to parse Price data.')

    return ad_info


def WriteAds(ad_dict, filename):  # Writes ads from given dictionary to given file
    #try:
	file = open(filename, 'ab')
	for ad_id in ad_dict:
		file.write(ad_id.encode('utf-8'))
		file.write((str(ad_dict[ad_id]) + "\n").encode('utf-8'))
	file.close()
    #except:
        #print('[Error] Unable to write ad(s) to file.')


def ReadAds(filename):  # Reads given file and creates a dict of ads in file
    import ast
    if not os.path.exists(filename):  # If the file doesn't exist, it makes it.
        file = open(filename, 'w')
        file.close()

    ad_dict = {}
    with open(filename, 'rb') as file:
        for line in file:
            if line.strip() != '':
                index = line.find('{'.encode('utf-8'))
                ad_id = line[:index].decode('utf-8')
                dictionary = line[index:].decode('utf-8')
                dictionary = ast.literal_eval(dictionary)
                ad_dict[ad_id] = dictionary
    return ad_dict


def FormatPost(ad_dict):
    postdict = {}
    postdict["event"] = ad_dict["Title"]
    postdict["latitude"] = str(ad_dict["latitude"])
    postdict["longitude"] = str(ad_dict["longitude"])
    postdict["description"] = ad_dict["Description"] + " || " + ad_dict["Price"]
    postdict["type"] = 'shopping'
    print(postdict)
    return postdict

def PostReq(ad_dict):  # Sends a request with a link and info of new ads
    
    post_dict = FormatPost(ad_dict)

    post_url = 'https://yathinosaur.api.stdlib.com/roid@dev/insert_roid_event/'
    try:
        post_dict_json = json.loads(json.dumps(post_dict))
        r = requests.post(url = post_url, data = post_dict_json, verify = False)
        print(r)
    except:
        print('[Error] Unable to post data.')

def scrape(url, old_ad_dict, exclude_list, filename, skip_flag):  # Pulls page data from a given kijiji url and finds all ads on each page
    # Initialize variables for loop
    ad_dict = {}
    third_party_ad_ids = []
    
    while url: 
    
        try:
            page = requests.get(url) # Get the html data from the URL
        except:
            print("[Error] Unable to load " + url)
            sys.exit(1)
    
        soup = BeautifulSoup(page.content, "html.parser")
            
        kijiji_ads = soup.find_all("div", {"class": "regular-ad"})  # Finds all ad trees in page html.
        
        third_party_ads = soup.find_all("div", {"class": "third-party"}) # Find all third-party ads to skip them
        for ad in third_party_ads:
            third_party_ad_ids.append(ad['data-listing-id'])
            
    
        exclude_list = toLower(exclude_list) # Make all words in the exclude list lower-case
        #checklist = ['miata']
        for ad in kijiji_ads:  # Creates a dictionary of all ads with ad id being the keys.
            title = ad.find('a', {"class": "title"}).text.strip() # Get the ad title
            ad_id = ad['data-listing-id'] # Get the ad id
            if not [False for match in exclude_list if match in title.lower()]: # If any of the title words match the exclude list then skip
                #if [True for match in checklist if match in title.lower()]:
                if (ad_id not in old_ad_dict and ad_id not in third_party_ad_ids): # Skip third-party ads and ads already found
                    print('[Okay] New ad found! Ad id: ' + ad_id)
                    ad_dict[ad_id] = ParseAd(ad) # Parse data from ad
                    if not skip_flag: # if skip flag is set do not send request
                        if 'latitude' in ad_dict[ad_id] and 'longitude' in ad_dict[ad_id]:
                            PostReq(ad_dict[ad_id]) # Send out post request with new ads
        url = soup.find('a', {'title' : 'Next'})
        if url:
            url = 'https://www.kijiji.ca' + url['href']

    if ad_dict != {}:  # If dict not emtpy, write ads to text file.
        WriteAds(ad_dict, filename) # Save ads to file
            
def toLower(input_list): # Rturns a given list of words to lower-case words
    output_list = list()
    for word in input_list:
        output_list.append(word.lower())
    return output_list

def toUpper(title): # Makes the first letter of every word upper-case
    new_title = list()
    title = title.split()
    for word in title:
        new_word = ''
        new_word += word[0].upper()
        if len(word) > 1:
            new_word += word[1:]
        new_title.append(new_word)
    return ' '.join(new_title)

def main(): # Main function, handles command line arguments and calls other functions for parsing ads
    args = sys.argv
    if args[1] == '-h' or args[1] == '--help': # Print script usage help
        print('Usage: Kijiji-Scraper.py URL [-f] [-e] [-s]\n')
        print('Positional arguments:')
        print(' URL\t\tUrl to scrape for ads\n')
        print('Optional arguments:')
        print(' -h, --help  show this help message and exit')
        print(' -f\t\tfilename to store ads in (default name is the url)')
        print(' -e\t\tword that will exclude an ad if its in the title (can be a single word or multiple words seperated by spaces')
        print(' -s\t\tflag that causes the program to skip sending a request. Useful if you want to index ads but not be notified of them')
    else:
        url_to_scrape = args[1]
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
        
    old_ad_dict = ReadAds(filename)
    print("[Okay] Ad database succesfully loaded.")
    scrape(url_to_scrape, old_ad_dict, exclude_list, filename, skip_flag)

if __name__ == "__main__":
    main()
