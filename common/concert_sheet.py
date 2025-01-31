import json
import os

from gspread_pandas import Spread
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
import pandas as pd

class SheetHandler:
    def __init__(self, spread='1D1BiS6txPVsfIiGpK1TRyeoUht_5dEEL_C6P9j5SMjA'):
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        # Load credentials from service account file
        key_path = os.path.expanduser('~/.gcloud/scraper-service-account-key.json')
        if os.path.exists(key_path):
            # for local use
            creds = ServiceAccountCredentials.from_service_account_file(
                key_path,
                scopes=SCOPES
            )
        else:
            # for GitHub Actions use
            service_account_info = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')
            if not service_account_info:
                raise ValueError("GOOGLE_SERVICE_ACCOUNT_KEY environment variable not found")
            service_account_dict = json.loads(service_account_info)
            creds = ServiceAccountCredentials.from_service_account_info(
                service_account_dict,
                scopes=SCOPES
            )

        self.spread = Spread(creds=creds, spread=spread)
        self._ensure_sheet_exists()

    def _ensure_sheet_exists(self):
        try:
            self.spread.sheet.get()
        except Exception as e:
            self.spread.sheet.insert()

    def get_all_data(self) -> pd.DataFrame:
        try:
            return self.spread.sheet_to_df(index=False)
        except Exception as e:
            print(f"ERROR reading sheet: {e}")
            return pd.DataFrame()

    def update_concert(self, concert_scrape):
        try:
            # Convert Concert model to dict
            concert_dict = concert_scrape.model_dump(mode='json') | concert_scrape.concert.model_dump(mode='json')
            del concert_dict['concert']
            # Convert nested objects to JSON strings, as CSV rows cope with nested dicts
            concert_dict['performers'] = json.dumps(concert_dict['performers'])
            concert_dict['programme'] = json.dumps(concert_dict['programme'])
            
            # Get existing data
            df = self.get_all_data()
            
            # Update or append
            if concert_dict['url'] in df['url'].values:
                idx = df[df['url'] == concert_dict['url']].index[0]
                for col in concert_dict:
                    if col in df.columns:
                        df.at[idx, col] = concert_dict[col]
            else:
                new_df = pd.DataFrame([concert_dict])
                df = pd.concat([df, new_df], ignore_index=True)
            
            # Write back to sheet
            self.spread.df_to_sheet(df, index=False, replace=True)
            
        except Exception as e:
            print(f"ERROR updating sheet: {e}")
            raise
