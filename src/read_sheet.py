import os
import time
import traceback

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from log import get_logger

log = get_logger(__name__)


class Drivi:
    __creds = None

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    def __init__(self) -> None:
        if os.path.exists('token.json'):
            self.__creds = Credentials\
                .from_authorized_user_file('token.json', self.SCOPES)

        if not self.__creds or not self.__creds.valid:
            if self.__creds and self.__creds.expired and self.__creds.refresh_token:
                self.__creds.refresh(Request())
            else:
                flow = InstalledAppFlow\
                    .from_client_secrets_file('credentials.json',
                                              self.SCOPES)

                self.__creds = flow.run_local_server(port=0)

            with open('token.json', 'w') as token:
                token.write(self.__creds.to_json())

    def read_spreadsheet(self,
                         spreadsheet_id: str,
                         range: str):
        try:
            try:
                service = build('sheets', 'v4', credentials=self.__creds)

                # Call the Sheets API
                sheet = service.spreadsheets()
                result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                            range=range,
                                            valueRenderOption='FORMULA').execute()

                values = result.get('values', [])

                return values
            except HttpError as err:
                raise
        except Exception:
            log.error(traceback.print_exc())
            raise
