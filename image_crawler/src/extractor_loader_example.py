'''
Created on Dec 5, 2017

@author: eliad
'''

import json # print beautify

# Image match
from elasticsearch import Elasticsearch
from image_match.elasticsearch_driver import SignatureES

# Local lib
import extractor
import loader
import common
#import image_details

# get exception info
import sys 
import traceback

print("Start !!!")

if __name__ == '__main__':
    pass

url_list = [
            #'http://www.ynet.co.il/articles/0,7340,L-4809441,00.html',
            #'http://www.walla.co.il',
            #'https://www.themarker.com/'
            #'https://www.google.co.il/search?client=ubuntu&channel=fs&q=google+images+bitcoin&ie=utf-8&oe=utf-8&gfe_rd=cr&dcr=0&ei=I8cwWrHFDq7L8gfw4r-ABg'
            'http://www.ynet.co.il//articles/0,7340,L-5057011,00.html'
            ]

### Extract images from URL
for url in url_list:
    print("Going to extract url '"+url+"'.")
    ext = extractor.extractor({
                               "dest_folder": "/home/eliad/python/image_crawler/images_db"
    })
    ext.extract_info(url)
    print("Statistics '"+json.dumps(ext.stats.Get(), sort_keys=True, indent=4)+"'.")
    
    # Go over extract images and add them to image
    es = Elasticsearch()
    ses = SignatureES(es)
    
    ldr =  loader.Loader({
                          "es": es,
                          "ses": ses,
                          })
    
    ldr.load_image_details_array(ext.image_details_arr)
    
    #img_dtl = image_details.image_details()
    #img_dtl.path = "/home/eliad/python/image_crawler/images_db/ynet.co.il/www.ynet.co.il%2Farticles%2F0%2C7340%2CL-4809441%2C00.html/images/1215857099989183103no.jpg"
    #img_dtl.domain = "ynet.co.il"
    #ext.image_details_arr.append(img_dtl)
    #ldr.load_image_details(img_dtl)

print("end")