# Concert Scrape

These tools search for and scrape concerts. It saves the resulting concerts:

* https://docs.google.com/spreadsheets/d/1D1BiS6txPVsfIiGpK1TRyeoUht_5dEEL_C6P9j5SMjA/edit?usp=sharing 

## Setup

```sh
python3 -m venv venv
. venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

For uploading results to the Google Sheets, setup and download the Google Service Account token, that has permission to write to the sheet:

* Go to [Google Cloud Console](https://console.cloud.google.com/)
* Select project "Job Scraper" (or create it)
* In APIs, enable the Google Sheets API
* In Google Sheets API, create a Service Account, noting its email address
* Download the service account key JSON file as `~/.gcloud/scraper-service-account-key.json`
* In the Sheet, share it with the service account's email address

## Run

```
. venv/bin/activate
python3 scrape.py
```
