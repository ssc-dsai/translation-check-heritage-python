import csv
import logging
import re
import sqlite3
import time

import bs4
import pandas as pd
import scrapy
from haystack.nodes import PreProcessor
from scrapy.utils.python import to_native_str

logging.getLogger('scrapy').setLevel(logging.CRITICAL)

strippeddata = {}

# Instantiate preprocessor
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
    urls = []
    # furls = []
    eresults = {}
    fresults = {}
    estatus = {}
    fstatus = {}
    dstatus = {}

    def start_requests(self):
        df = pd.read_excel(
            'data/test data.xlsx')
        count = 0
        for index, row in df.iterrows():
            count += 1
            # if count == 11:
            #     break
            # , "handle_httpstatus_all": True}
            site = {"language": "en", "pairid": count,
                    "url": row["EnglishURL"], "altURL": row["FrenchURL"], "OriginalURL": row["EnglishURL"], "playwright": True, "playwright_include_page": True}
            yield scrapy.Request(url=site["url"], callback=self.parse, meta=site)
            # , "handle_httpstatus_all": True}
            site = {"language": "fr", "pairid": count,
                    "url": row["FrenchURL"], "altURL": row["EnglishURL"], "OriginalURL": row["FrenchURL"], "playwright": True, "playwright_include_page": True}
            yield scrapy.Request(url=site["url"], callback=self.parse, meta=site)

    async def parse(self, response):

        # Remove the HTML from the response body      
        strippeddata["content"] = bs4.BeautifulSoup(response.body, "lxml").get_text()
        htmlcontent=processor.process([strippeddata])
        print("HTML Content", htmlcontent)
                

        # text = [line for line in text.split('\n') if line.strip() != '']
        text=[]
        for i in range(0, len(htmlcontent)-1):
            text.append(htmlcontent[i].content.replace("\n", " "))


        # Remove lines with less than 5 words
        # text = [line for line in text if len(line.split()) > 5]
        text = '\n'.join(text)

        # Screenshot the page
        page= response.meta["playwright_page"]
        pairid=str(response.meta["pairid"])
        language=response.meta["language"]
        await page.screenshot(path="screenshots/"+pairid+"-"+language+".png", full_page=True)

        buffer = await page.screenshot(full_page=True)
        await page.close()

        # Yield selected reponse fields
        yield {'status': response.status, 'url': response.meta["OriginalURL"], 'language': response.meta["language"], 'text': text, "image": buffer, "pairid": response.meta["pairid"]}
