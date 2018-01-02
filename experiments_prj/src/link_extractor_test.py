'''
Created on Dec 12, 2017

@author: eliad
'''

if __name__ == '__main__':
    pass

import os # Check if folder/file exists/sizes
import time # used for unknown name
from datetime import datetime # datetime now
import urllib # url parsing
import urllib2 # Download images
#import json # pretty dump
import re # string parsing: extract url from style
from bs4 import BeautifulSoup

# get exception info
import sys 
import traceback

from binascii import a2b_base64 # decode embedded images
from PIL import Image

from pyvirtualdisplay import Display # Chrome headless
from selenium import webdriver 

import urlparse # parse url
import urllib # parse url

def EncodeUrl(url):
    tmpUrl = url.replace("http://","").replace("https://","")
    encodedFileName = urllib.quote(tmpUrl, '')
    return encodedFileName
    
def GetStripDomain(url):
    parseResult = urlparse.urlparse(url)
    urlDomain = "{0.netloc}".format(parseResult)

    stripUrlDomain = urlDomain
    if urlDomain.startswith('www.'):
        stripUrlDomain = urlDomain[4:]

    return stripUrlDomain

url_list = [
            'http://www.ynet.co.il/articles/0,7340,L-4809441,00.html',
            #'http://www.walla.co.il'
            ]

### Extract images from URL
for url in url_list:
    print("Going to extract url '"+url+"'.")
    
    domain = GetStripDomain(url)
    
    html_file = "/home/eliad/workspace/python.tests/html_pages/" + EncodeUrl(url) + ".txt"
    
    if (not os.path.isfile(html_file)):
        display = Display(visible=0, size=(800, 600))
        display.start()
        
        driver = webdriver.Chrome()
        #driver = webdriver.Firefox()
        driver.get(url);
                
        # save html source in local file
        html_source = driver.page_source.encode('utf-8')
        with open(html_file, 'w') as html_file_handler:
            html_file_handler.write(html_source)
            
    with open(html_file, 'r') as file:
        html_source = file.read().decode('ascii','ignore')
            
    soup = BeautifulSoup(html_source, 'html.parser')
    links = soup.find_all('a')

    internalLinks = []
    externalLinks = []
    for link in links:
        href = link.get('href')
        if (href is None) or (href in ["None",  "", "#"] or href.startswith("javascript:")):
            continue 

        linkDomain = GetStripDomain(href)

        if (linkDomain not in domain) and (("http" in href) or ("https" in href)):
            externalLinks.append(link)
        else:
            internalLinks.append(link)

print("externalLinks: ========================================================================================================")         
for link in externalLinks:
    print link.get('href')
    

print("internalLinks: ========================================================================================================")         
for link in internalLinks:
    print link.get('href')
            
print("End !!!")  
        
        
        
    
    