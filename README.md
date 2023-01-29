# Translation verification scripts

## Setting up the system
1. Clone the repository.
2. cd into the ```web-translation-compare``` directory.
3. If you're using ```conda``` or ``virtualenv```, create the environment and retrieve the neede libraries with ``` pip install -r requirements.txt```.  Note that some NLP libraries work best with older versions of python.  I'm using Python 3.9x.
4. Create a new scrapy project with ```scrapy startproject websites```.
5. Copy files into the new scrapy project
    ```cp files/settings.py websites/websites/```
    ```cp files/pipelines.py websites/websites```
    ```cp files/websites_spider.py websites/websites/spiders```
    ```cd websites```
    ```scrapy crawl websites```

## What does it do
This repository contains code to score the similarity of French and English web pages.
The process is broken down into three steps.
1. First the pages under review are downloaded with Scrapy, stripped of HTML tags and saved to a SQLite database.
2. The ```translate.py``` script scans through the database and translates English content to French, French to English and then both source languages to Spanish.
3. The ```compare.py``` script scores the language pairs for similarity, for example, the two Spanish translations, French and French translation, and the English and English translation.

## Step 1: Retrieving the web pages
Scrapy (https://scrapy.org/) is a Python framework to crawl
websites.  We create standard scrapy project called ```websites``` and replace three critical files with our own.  They are:
* ```settings.py```- the settings used by the project controling caching, extra modules and redirection.
* ```pipelines.py```- a custom module that saves the crawl results to a SQLite database (websites.db).
* ```websites_spider.py```- a script that retreives the list of URLs to be crawled, renders the content using a headless browser, and extracts the text from the page.  The results are passed to the ```pipelines.py``` script.

### ```websites_spider.py```
The script extends the ```Scrapy.spider``` class with two methods.

The ```start_requests``` function uses Pandas to open an __Excel__ spreadsheet containing the source URLs. The script uses a ```pairid``` to associate the French and English versions of a site's web pages.

Capturing a web page as served from the website often doesn't give what the browser sees- scraping content from many sites resulted in moved temporarily (302) and moved permanently (302) errors frm the server, largely because web pages are often dynamically assembled on the client's browser.

The solution is to process scraped content through a __headless browser__.  Fortunately, Scrapy comes with a middleware component (*scrapy-playwright*) that renders the page in a hidden browser and passes the results back to scrapy for further processing.

The *Playwright* integration is enabled  in the ```settings.py``` and through adding parameters to the ```meta``` attribute when passing the Scrapy request object with the *yield* keyword.

Another benefit of the *Playwright* module is that it allows a snapshot of the page to be saved in the _snapshots_ directory- this can be used to verify the results of the scrape.

The ```parse``` function takes the page's browser rendering and extracts the text using Python's *BeautifulSoup* XML parser.

All lines with less than a minimum number of words are stripped from the text in an attempt to remove some of the common page navigation elements

The ```pipelines.py``` script takes the URL, screenshot, language and text from the crawl and pushes the content into an SQLite database.  If the database and ```source``` table exists, the script will just append the data to the table.  If the database doesn't exist, the script will just create it.

The ```settings.py``` is fairly standard with one exception. As of the current release, enabling content caching will break the *Playwright* page snapshotting functionality.



