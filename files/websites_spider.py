import csv
import re
import sqlite3
import time

import bs4
import pandas as pd
import scrapy
from haystack.nodes import PreProcessor
from scrapy.utils.python import to_native_str


# Set to a non-zero number to break the loop after a certain number of URLs
SETBREAK=5

# The text converter will ignore paragraphs with less than this number of words
MINWORDS=5

# Hold the bs4 stripped text
strippeddata = {}

# Leverage Haystack's preprocessor to clearn up text
processor = PreProcessor(
    clean_empty_lines=False,
    clean_whitespace=True,
    clean_header_footer=True,
    split_by="word",
    split_length=10,
    split_respect_sentence_boundary=True,
    split_overlap=0
)

class SitesSpider(scrapy.Spider):
    name = "websites"

    def start_requests(self):
        # Read the spreadsheet with the list of URLs
        df = pd.read_excel(
            'data/test data.xlsx')
        count = 0

        # Iterate through the rows of the spreadsheet
        for index, row in df.iterrows():
            count += 1

            # Check to see if we've hit the break
            if count == SETBREAK:
                break

            # Site metadata passed to the URL request for 
            # the first of the URL pairs.
            # Also, enable playwright for page rendering and capturing
            # the page screenshot
                    #    site = {"language": "en", "pairid": count,
                    # "url": row["EnglishURL"], "altURL": row["FrenchURL"], "OriginalURL": row["EnglishURL"], "playwright": True, "playwright_include_page": True}
            site = {"language": "en", "pairid": count,
                    "url": row["EnglishURL"], "playwright": True, 
                    "playwright_include_page": True}

            # Pass the request back to the Scrapy URL retriever
            yield scrapy.Request(url=site["url"], callback=self.parse, meta=site)
            # , "handle_httpstatus_all": True}
            # site = {"language": "fr", "pairid": count, "url": row["FrenchURL"], "altURL": row["EnglishURL"], "OriginalURL": row["FrenchURL"], "playwright": True, "playwright_include_page": True}

            # Site metadata passed to the URL request for 
            # the second of the URL pairs.
            # Also, enable playwright for page rendering and capturing
            # the page screenshot
            site = {"language": "fr", "pairid": count, 
            "url": row["FrenchURL"], 
            "playwright": True, "playwright_include_page": True}

            # Pass the request back to the Scrapy URL retriever
            yield scrapy.Request(url=site["url"], callback=self.parse, meta=site)

    async def parse(self, response):

        # Remove the HTML from the response body      
        pagetext = bs4.BeautifulSoup(response.body, "lxml").get_text()

        
        # Remove lines with less than MINWORD words
        # text=[]
        text = '\n'.join([line for line in pagetext.split("\n") if len(line.split()) >= MINWORDS])
    

  
        # print("HTML Before stripping: ", strippeddata["content"])
        # print("HTML Content", htmlcontent)
                

        # text = [line for line in text.split('\n') if line.strip() != '']
        # text=[]
        # for i in range(0, len(htmlcontent)-1):
        #     text.append(htmlcontent[i].content.replace("\n", " "))

        # text=processor.process(text)

        # text = '\n'.join(text)
        # print("\n\n\n\n***\nText: ", text)

        # text = [line for line in text.split('\n') if line.strip() != '']


        # Screenshot the page
        page= response.meta["playwright_page"]
        pairid=str(response.meta["pairid"])
        language=response.meta["language"]
        await page.screenshot(path="screenshots/"+pairid+"-"+language+".png", full_page=True)

        buffer = await page.screenshot(full_page=True)
        await page.close()

        # Yield selected reponse fields
        yield {'status': response.status, 'url': response.meta["url"], 'language': response.meta["language"], 'text': text, "image": buffer, "pairid": response.meta["pairid"]}
