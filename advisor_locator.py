import requests
import pandas as pd
import datetime
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

    time_start = datetime.datetime.now().replace(microsecond=0)
    business_ids = []
    b_name = []
    b_phone_number = []
    b_address = []
    b_website = []
    b_gmb_url = []

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

    print('Fetching business details in progress...')
    print(' ')

    for businessID in business_ids:
        try:
            url = "https://maps.googleapis.com/maps/api/place/details/json?place_id=" + businessID + "&fields=name,formatted_phone_number,formatted_address,website,url&key=AIzaSyBqZC8t0PfJndRjPd_Mg9f68wrhRbENBF4"

            payload={}
            headers = {}

            response = requests.request("GET", url, headers=headers, data=payload)

            results = response.json()

            name = results['result']['name']
            formatted_phone_number = results['result']['formatted_phone_number']
            formatted_address = results['result']['formatted_address']
            website = results['result']['website']
            url = results['result']['url']

            b_name.append(name if name != "" else 'none')
            b_phone_number.append(formatted_phone_number if formatted_phone_number != "" else 'none')
            b_address.append(formatted_address if formatted_address != "" else 'none')
            b_website.append(website if website != "" else 'none')
            b_gmb_url.append(url if url != "" else 'none')
            time.sleep(1)
            
        except:
            pass

    time_end = datetime.datetime.now().replace(microsecond=0)
    runtime = time_end - time_start
    print(f"Script runtime: {runtime}.")
    print(' ')

    # Save scraped URLs to a CSV file
    now = datetime.datetime.now().strftime('%Y%m%d-%Hh%M')
    print('Saving to a CSV file...')
    print(' ')
    data = {"Business Name":b_name,"Phone Number":b_phone_number, "Address":b_address, "Website":b_website, "GMB URL": b_gmb_url}
    df=pd.DataFrame(data=data)
    df.index+=1
    directory = os.path.dirname(os.path.realpath(__file__))
    filename = "business_details" + now + ".csv"
    file_path = os.path.join(directory,'csvfiles/', filename)
    df.to_csv(file_path)

    print('Your files are ready.')
    print(' ')

if __name__ == '__main__':
    place_details()
