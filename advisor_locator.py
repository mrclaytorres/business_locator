import requests
import csv
import os
import os.path
import time
import re

# Find the coordinate of the address
def geocoding(address):
    
    url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + address + "&key=AIzaSyBqZC8t0PfJndRjPd_Mg9f68wrhRbENBF4"

    payload={}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    results = response.json()

    coordinate = {
        'lat': results['results'][0]['geometry']['location']['lat'],
        'lng': results['results'][0]['geometry']['location']['lng']
    }

    return coordinate
    

# Find the place_id of the Business
def find_place(businessObject):
    
    address = businessObject['address']

    remove_non_word = re.sub(r"[^\w\s]", '', address)
    parse_address = re.sub(r"\s+", '+', remove_non_word)

    coordinate = geocoding(parse_address)

    business_name = businessObject['name']
    remove_non_word = re.sub(r"[^\w\s]", '', business_name)

    lat = str(coordinate['lat'])
    lng = str(coordinate['lng'])

    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=" + business_name + "&inputtype=textquery&locationbias=circle:2000@" + lat + "," + lng +"&fields=place_id&key=AIzaSyBqZC8t0PfJndRjPd_Mg9f68wrhRbENBF4"

    payload={}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    results = response.json()

    place_id = results['candidates'][0]['place_id']

    return place_id

# Get the Business details
def place_details():

    business_ids = []

    with open('business_list_Copy.csv') as f:
        reader = csv.DictReader(f)
        for line in reader:
            address = line['1F1Street1'] + ' ' + line['1F1Street2'] + ' ' + line['1F1City'] + ' ' + line['1F1State']
            business_name = line['Business Name']

            businessObject = {
                'name': business_name,
                'address': address
            }

            business_id = find_place(businessObject)
            business_ids.append(business_id)

    for businessID in business_ids:
        try:
            url = "https://maps.googleapis.com/maps/api/place/details/json?place_id=" + businessID + "&fields=name,formatted_phone_number,formatted_address,website,url&key=AIzaSyBqZC8t0PfJndRjPd_Mg9f68wrhRbENBF4"

            payload={}
            headers = {}

            response = requests.request("GET", url, headers=headers, data=payload)

            results = response.json()

            print(results['result']['name'])
            print(results['result']['formatted_phone_number'])
            print(results['result']['formatted_address'])
            print(results['result']['website'])
            print(results['result']['url'])
            print('-----------------------------')
            time.sleep(1)
            
        except:
            pass

if __name__ == '__main__':
    place_details()
