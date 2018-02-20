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


#url = "https://www.ynet.co.il/home/0,7340,L-544,00.html"
#url = "https://www.ynet.co.il/articles/0,7340,L-5063578,00.html"
#url = "https://www.ynet.co.il/articles/0,7340,L-5063952,00.html"
url = "https://www.nytimes.com/"
#url = "https://www.nytimes.com/2017/12/29/opinion/dont-cheer-as-the-irs-grows-weaker.html"



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
if True:
#if False:
    crlr = crawler.Crawler({})
    url_info = object_model.url_info.UrlInfo({
                                          "url": url,
                                          "initiator_type": object_model.url_info.UrlInfoInitiatorTypeEnum.manual,
                                          "initiator_id": "eliad",
                                          "depth_max": 3,
                                          })
    crlr.insert_start_url(url_info)

### Testing
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
    
    img_dtl = image_details.ImageDetails()
    img_dtl.path = "/home/eliad/python/image_crawler/images_db/nytimes.com/www.nytimes.com/2018_02_19-00/images/00stagesSS-slide-4CEZ-largeHorizontal375.jpg"
    img_dtl.website_src_url = "www.nytimes.com"
    img_dtl.time = datetime.utcnow()
    
    image_details_arr.append(img_dtl)
    
    ldr.load_image_details_array(image_details_arr)

    
    
    
    
    


