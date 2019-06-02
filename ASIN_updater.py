import gspread
from oauth2client.service_account import ServiceAccountCredentials
from amazon_bot_with_asin import AmazonBot
from email_alert import EmailAlert
import numpy as np

class PriceUpdater(object):

       def __init__(self,spreadsheet_name):
              self.ASINs_col = 1
              self.price_old_col = 2
              self.price_new_col = 3
              self.url_col = 4
              self.product_name_col = 5

              scope=["https://spreadsheets.google.com/feeds",
                     "https://www.googleapis.com/auth/drive"]

              creds=ServiceAccountCredentials.from_json_keyfile_name("client_secret.json",scope)

              client=gspread.authorize(creds)

              self.sheet=client.open(spreadsheet_name).sheet1

       def get_items(self):
           items = self.sheet.col_values(self.ASINs_col)[1:]

           amazon_bot = AmazonBot(items)
           new_prices, urls, names = amazon_bot.search_items()

           stuff_record=self.sheet.get_all_records()
           old_prices = [item["price_new"] for item in stuff_record]
           old_prices = [0 if type(x) == str else x for x in old_prices]

           for i in range(len(items)):
               for op, np in zip(old_prices, new_prices):
                   if np > op  or np==0.00:
                        self.sheet.update_cell(i + 2, self.price_old_col, new_prices[i])
               self.sheet.update_cell(i + 2, self.url_col, urls[i])
               self.sheet.update_cell(i + 2, self.product_name_col, names[i])


           email_urls = []
           for i, (op, np) in enumerate(zip(old_prices, new_prices)):
               if np - op > 10:
                   email_urls.append(urls[i])

           return ([f"{i} {x} " for i,x in enumerate(email_urls)])



price_updater=PriceUpdater("ASIN")
price_updater.get_items()

#email=EmailAlert("Google Sheet Updated",price_updater.get_items())
#email.send_email()
