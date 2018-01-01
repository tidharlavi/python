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
from bs4.element import Comment
import json

# get exception info
import sys 
import traceback

from binascii import a2b_base64 # decode embedded images
from PIL import Image

from pyvirtualdisplay import Display # Chrome headless
from selenium import webdriver 

import urlparse # parse url
import urllib # parse url

class image_details(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
from enum import Enum
class advertisers(Enum):
     doubleclick = 10


import time # Measure execution time
class Stats(object):

    def __init__(self, statsList=[]):
        self.stats = {}

        for stat in statsList:
            self.stats[stat] = 0

    def Get(self):
        return self.stats

    def Incr(self, key):
        if key in self.stats:
            self.stats[key] += 1
        else:
            self.stats[key] = 1

    def TimeStart(self, key):
        self.stats[key] = time.time()

    def TimeEnd(self, key):
        timeStart = self.stats[key]
        timeEnd = time.time()
        self.stats[key] = timeEnd - timeStart

    def Add(self, key, val):
        self.stats[key] = val 

    def GetVal(self, key):
        return self.stats[key]
    
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

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def text_from_soup(soup):
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)

def bs_test(html_source):        
    soup = BeautifulSoup(html_source, 'html.parser')

    images = []
    for img in soup.findAll('img'):
        for img_attr in ['src', 'alt', 'title']:
            print img_attr + " = " + (img.get(img_attr))
               
        img_dtl = dict()
        
        soup_p = img
        for i in range(0, depth):
            print "depth = " + str(i) + "==========================="
            soup_p = soup_p.parent
            if soup_p is None:
                break
            
            if soup_p.name == 'a' and not "href" in img_dtl:
                print "href = " + soup_p.get("href")
                img_dtl["href"] = soup_p.get("href")
                
            print text_from_soup(soup_p)
        
        images.append(img_dtl)    
     
    print(len(images))
    
    
import cssutils
def bs_test1(html_source):
    
    
    soup = BeautifulSoup(html_source, 'html.parser')
    
    stat = Stats()
    img_dtl_arr = []
    
    
    styles = soup.findAll(style=re.compile("background-image"))
    for style in styles:
        img_dtl = image_details()
        
        div_style = style.get('style')
        style_attr = cssutils.parseStyle(div_style)
        url = style_attr['background-image']
        
        img_dtl.src = url
        if img_dtl.src is None:
            stat.Incr("style_no_src")
            
        img_dtl_arr.append(img_dtl)
        

    for index, img_dtl in enumerate(img_dtl_arr, start=0):
        #print "New image ==========================="
        img_soup_arr = soup.findAll(style=re.compile(img_dtl.src))
        if len(img_soup_arr) != 1:
            stat.Incr("same_src_img_"+str(len(img_soup_arr)))
            #print("Error: len(img_soup_arr)=" + str(len(img_soup_arr)))
            continue
            
        img_soup = img_soup_arr[0]
        
        img_soup_p = img_soup.parent
        for i in range(1, depth):
            #print "depth = " + str(i) + "==="
            if img_soup_p is None or img_soup_p.name in ["body", "html"]:
                stat.Incr("reached_end")
                break
            
            if img_soup_p.name == 'a' and not hasattr(img_dtl, 'link'):
                img_dtl.link = img_soup_p.get("href")
                stat.Incr("found_link_in_"+str(i))
                
                if "doubleclick" in img_dtl.link:
                    img_dtl.adv = advertisers.doubleclick
                    stat.Incr("found_adv_"+advertisers.doubleclick)
            
            text = text_from_soup(img_soup_p).strip()
            if text and not hasattr(img_dtl, 'text'):
                img_dtl.text = text
                stat.Incr("found_text_in_"+str(i))
                
            img_soup_p = img_soup_p.parent
                
        print(str(index) + ": " + ', '.join("%s: %s" % item for item in vars(img_dtl).items()) + "'." )
        
    print("Statistics '"+json.dumps(stat.Get(), sort_keys=True, indent=4)+"'.")



    stat = Stats()
    img_dtl_arr = []
    
    images = soup.findAll('img')
    
    for img in images:
        img_dtl = image_details()
        
        
        img_dtl.src = img.get("src")
        if img_dtl.src is None:
            stat.Incr("no_src")
            
        img_dtl.id = img.get("id")
        if img_dtl.id is None:
            stat.Incr("no_id")
            
        img_dtl.classattr = img.get("class")
        if img_dtl.classattr is None:
            stat.Incr("no_class")
            
        img_dtl.alt = img.get("alt")
        if img_dtl.alt is None:
            stat.Incr("no_alt")
            
        img_dtl.title = img.get("title")
        if img_dtl.title is None:
            stat.Incr("no_title")
        
        img_dtl_arr.append(img_dtl)
        
    for index, img_dtl in enumerate(img_dtl_arr, start=0):
        #print "New image ==========================="
        img_soup_arr = soup.findAll('img', {'src': img_dtl.src})
        if len(img_soup_arr) != 1:
            stat.Incr("same_src_img_"+str(len(img_soup_arr)))
            #print("Error: len(img_soup_arr)=" + str(len(img_soup_arr)))
            continue
            
        img_soup = img_soup_arr[0]
        
        img_soup_p = img_soup.parent
        for i in range(1, depth):
            #print "depth = " + str(i) + "==="
            if img_soup_p is None or img_soup_p.name in ["body", "html"]:
                stat.Incr("reached_end")
                break
            
            if img_soup_p.name == 'a' and not hasattr(img_dtl, 'link'):
                img_dtl.link = img_soup_p.get("href")
                stat.Incr("found_link_in_"+str(i))
                
                if "doubleclick" in img_dtl.link:
                    img_dtl.adv = advertisers.doubleclick
                    stat.Incr("found_adv_"+advertisers.doubleclick)
            
            text = text_from_soup(img_soup_p).strip()
            if text and not hasattr(img_dtl, 'text'):
                img_dtl.text = text
                stat.Incr("found_text_in_"+str(i))
                
            img_soup_p = img_soup_p.parent
                
        print(str(index) + ": " + ', '.join("%s: %s" % item for item in vars(img_dtl).items()) + "'." )
        
    print("Statistics '"+json.dumps(stat.Get(), sort_keys=True, indent=4)+"'.")

##### Running code

#url = 'http://www.ynet.co.il/articles/0,7340,L-4809441,00.html',
#url = 'http://www.ynet.co.il'
url = None
#html_file = "/home/eliad/workspace/python.tests/html_pages/bs_test.html"
#html_file = '/home/eliad/workspace/python.tests/html_pages/www.ynet.co.il.html'
html_file = '/home/eliad/workspace/python.tests/html_pages/www.ynet.co.il%2Farticles%2F0%2C7340%2CL-4809441%2C00.html.txt'
#html_file = None
depth = 4

html_source = None

if html_source is None and html_file is not None:
    with open(html_file, 'r') as file:
        #html_source = file.read().decode('ascii','ignore')
        html_source = file.read()

if html_source is None and url is not None:
    print("Going to extract url '"+url+"'.")
    
    domain = GetStripDomain(url)
    
    html_file = "/home/eliad/workspace/python.tests/html_pages/" + EncodeUrl(url) + ".html"
    
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

if html_source is not None:
    bs_test1(html_source)
    
                
print("End !!!")  
        
        
        
    
    