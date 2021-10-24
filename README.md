# Business Locator
Business locator using Google Services API in Python

# Instructions
1. Create input file in csv (business_list.csv). CSV columns are as follows:
    - Business Name, 1F1Street1, 1F1Street2, 1F1City, 1F1State, 1F1Country
2. Rename **creds_SAMPLE.py** to **creds.py** and put your Google Maps API KEY
    * Your API should have Geocoding API, Maps JavaScript API and Places API enabled
3. Create your virtual environment.

# Install dependencies
```
pip install -r requirements.txt --no-index
```
# Run the program
```
python advisor_locator.py
```