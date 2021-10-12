import requests
import pandas as pd
import datetime
import csv
import os
import os.path
import time
import re
import sys

# Find the coordinate of the address
def geocoding(address):
    
    url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + address + "&key=AIzaSyBqZC8t0PfJndRjPd_Mg9f68wrhRbENBF4"

    payload={}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    results = response.json()

    if results['status'] == 'OK':
        coordinate = {
            'lat': results['results'][0]['geometry']['location']['lat'],
            'lng': results['results'][0]['geometry']['location']['lng']
        }
    else:
        coordinate = 'none'

    return coordinate
    

# Find the place_id of the Business
def find_place(businessObject):
    
    place_id = ''
    address = businessObject['address']

    remove_non_word = re.sub(r"[^\w\s]", '', address)
    parse_address = re.sub(r"\s+", '+', remove_non_word)

    print(f'Retrieving {remove_non_word} business ID.')

    coordinate = geocoding(parse_address)

    business_name = businessObject['name']
    b_remove_non_word = re.sub(r"[^\w\s]", '', business_name)
    limit_business_name = b_remove_non_word.split(' ')[:4]
    stripped_name = ' '.join(limit_business_name)
    
    if coordinate != 'none':
        lat = str(coordinate['lat'])
        lng = str(coordinate['lng'])

        try:
            url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=" + stripped_name + "&inputtype=textquery&locationbias=circle:2000@" + lat + "," + lng +"&fields=place_id&key=AIzaSyBqZC8t0PfJndRjPd_Mg9f68wrhRbENBF4"

            payload={}
            headers = {}

            response = requests.request("GET", url, headers=headers, data=payload)

            results = response.json()

            place_id = results['candidates'][0]['place_id']

        except:
            place_id = 'none'
    else:
        pass

    return place_id

# When Google API terminates connection because of limit
def process_csv_output(csv_data):

    time_start = csv_data["time_start"]
    b_name = csv_data["b_name"]
    b_phone_number = csv_data["b_phone_number"]
    b_address = csv_data["b_address"]
    b_website = csv_data["b_website"]
    b_gmb_url = csv_data["b_gmb_url"]
    b_name_not_existed = csv_data["b_name_not_existed"]
    b_add_not_existed = csv_data["b_add_not_existed"]


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

    # Save recaptchaed requests to a CSV file
    if b_name_not_existed:
        no_gmb_data = {"Business Name":b_name_not_existed, "Address": b_add_not_existed}
        df2 = pd.DataFrame(data=no_gmb_data)
        df2.index+=1
        directory2 = os.path.dirname(os.path.realpath(__file__))
        filename2 = "gmb_not_existing" + now + ".csv"
        file_path2 = os.path.join(directory2,'no_google_business_address/', filename2)
        df2.to_csv(file_path2)

    print('Your files are ready.')
    print(' ')
    sys.exit()

# Get the Business details
def place_details():

    time_start = datetime.datetime.now().replace(microsecond=0)
    business_ids = []
    b_name = []
    b_phone_number = []
    b_address = []
    b_website = []
    b_gmb_url = []
    b_name_not_existed = []
    b_add_not_existed = []

    print(f'Fetching Business IDs using Geocoding...')
    print(' ')

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

            if business_id != 'none':
                business_ids.append(business_id)
            else:
                b_name_not_existed.append(business_name)
                b_add_not_existed.append(address)
                pass
            
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
            print(f'{name} details retrieved successfully...')
            print(' ')
            time.sleep(1)

        except requests.exceptions.ConnectionError as e:
            print('Connection terminated...\n')
            csv_data = {
                'b_name': b_name,
                'b_phone_number': b_phone_number,
                'b_address': b_address,
                'b_website': b_website,
                'b_gmb_url': b_gmb_url,
                'b_name_not_existed': b_name_not_existed,
                'b_add_not_existed': b_add_not_existed,
                'time_start': time_start

            }
            process_csv_output(csv_data)

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

    # Save recaptchaed requests to a CSV file
    if b_name_not_existed:
        no_gmb_data = {"Business Name":b_name_not_existed, "Address": b_add_not_existed}
        df2 = pd.DataFrame(data=no_gmb_data)
        df2.index+=1
        directory2 = os.path.dirname(os.path.realpath(__file__))
        filename2 = "gmb_not_existing" + now + ".csv"
        file_path2 = os.path.join(directory2,'no_google_business_address/', filename2)
        df2.to_csv(file_path2)

    print('Your files are ready.')
    print(' ')

if __name__ == '__main__':
    place_details()
