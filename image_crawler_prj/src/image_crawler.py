'''
Created on Dec 5, 2017

@author: eliad
'''

### Normal Running
import object_model
import crawler

### testing
import extract_keywords
from object_model import image_details
import loader
from datetime import datetime # datetime now
import extractor
import common
import config

#url = "https://www.ynet.co.il/home/0,7340,L-544,00.html"
#url = "https://www.ynet.co.il/articles/0,7340,L-5063578,00.html"
#url = "https://www.ynet.co.il/articles/0,7340,L-5063952,00.html"
#url = "https://www.nytimes.com/"
#url = "https://www.nytimes.com/2017/12/29/opinion/dont-cheer-as-the-irs-grows-weaker.html"
url = 'https://www.nytimes.com/2009/06/28/books/review/Mallon2-t.html'


##################
# Logging
##################
import logging
LOGGING_FILE_NAME = ""
loggingFormat = '%(asctime)-15s|%(levelname)s|%(name)s|%(funcName)s|%(lineno)d|%(message)s'
logging.basicConfig(level=logging.INFO, format=loggingFormat, filename=LOGGING_FILE_NAME)

log = logging.getLogger(__name__)

#logging.root.level = logging.INFO
#logging.root.format = loggingFormat

log.info("Start !!!")


class dummy(object):
    def __init__(self):
        print("dummy`")

# Validation
import pymongo
mongo_server_delay = 5
try:
    client = pymongo.MongoClient(serverSelectionTimeoutMS=mongo_server_delay)
    client.server_info()
except pymongo.errors.ServerSelectionTimeoutError as err:
    # do whatever you need
    log.error("No mongo server found !!!")
    exit(1)
    
### Normal running
#if True:
if True:
    crlr = crawler.Crawler({})
    url_info = object_model.url_info.UrlInfo({
                                          "url": url,
                                          "initiator_type": object_model.url_info.UrlInfoInitiatorTypeEnum.manual,
                                          "initiator_id": "eliad",
                                          "depth_max": 1,
                                          })
    crlr.insert_urls([ url_info ])

### Testing
from PIL import Image
if False:
    #fileName = '/home/eliad/python/image_crawler/images_sig_db/image_2f93f346-4768-4238-ab69-49f3559e88c3.'
    fileName = '/home/eliad/python/image_crawler/images_sig_db/image_2fbedcd2-1dcb-4490-8849-ec7c3d54ed29.jpg'
    with Image.open(fileName) as im:
            # fill img object
            image_height = im.size[1]
            image_width = im.size[0]
            image_format = im.format
            print("image_format=" + image_format)
            extension = ""
            if not extension:
                extension = im.format.lower()
            print("extension=" + extension)
            

#if False:
#from google_images_download_master.google_images_download import google_images_download
#if True:
#    response = google_images_download.googleimagesdownload()
#    response.download({"keywords": "bitcoin"})
    
if False:
#if True:
    ext_keywords = extract_keywords.ExtractKeywords({})
    ext_keywords.extract_keywords(url = url)
    
    page_title = ext_keywords.page_title.encode('ascii', 'ignore')
    metatag_keywords = ext_keywords.page_meta_keywords.encode('ascii', 'ignore')
    metatag_desription = ext_keywords.page_meta_desription.encode('ascii', 'ignore')
    page_keywords = ext_keywords.keywords
    
if False:
#if True:
    ldr =  loader.Loader()
    
    image_details_arr = []
    
    img_dtl = dummy()
    img_dtl.path = "/home/eliad/python/image_crawler/images_db/nytimes.com/www.nytimes.com/2018_02_19-00/images/00stagesSS-slide-4CEZ-largeHorizontal375.jpg"
    img_dtl.website_src_url = "www.nytimes.com"
    img_dtl.time = datetime.utcnow()
    
    image_details_arr.append(img_dtl)
    
    ldr.load_image_details_array(image_details_arr)

if False:
    ext = extractor.extractor()
    
    img_dtl_arr = []
                   
    img_dtl = dummy()
    img_dtl.id = "aaa"
    img_dtl.browser_width = 2
    img_dtl.browser_height = 3
    img_dtl_arr.append(img_dtl)
    
    img_dtl = dummy()
    img_dtl.id = "bbb"
    img_dtl.browser_width = 4
    img_dtl.browser_height = 5
    img_dtl_arr.append(img_dtl)
    
    img_dtl = dummy()
    img_dtl.id = "ccc"
    img_dtl.browser_width = 1
    img_dtl.browser_height = 2
    img_dtl_arr.append(img_dtl)
    
    img_dtl = dummy()
    img_dtl.id = "ddd"
    img_dtl.browser_width = 20
    img_dtl.browser_height = 1
    img_dtl_arr.append(img_dtl)
    
    ext.process_images(img_dtl_arr)
     
if False:
    stats_a = common.Stats()
    stats_a.Incr("a")
    stats_a.Incr("aa")
    stats_a.Add("aaa", 5)
    
    stats_b = common.Stats()
    stats_b.Incr("ba")
    stats_b.Incr("baa")
    stats_b.Add("baaa", 5)
    
    stats_c = common.Stats()
    stats_c.Incr("c")
    stats_c.add_stats(stats_a)
    stats_c.add_stats(stats_b, "dd")
    
    log.info("stats_cr: '%s'.", stats_c.Print(pretty=False))

