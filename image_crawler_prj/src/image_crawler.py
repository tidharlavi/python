'''
Created on Dec 5, 2017

@author: eliad
'''

### Normal Running
import object_model
import crawler

### testing
import extract_keywords

#url = "https://www.ynet.co.il/home/0,7340,L-544,00.html"
#url = "https://www.ynet.co.il/articles/0,7340,L-5063578,00.html"
#url = "https://www.ynet.co.il/articles/0,7340,L-5063952,00.html"
url = "https://www.nytimes.com/"
#url = "https://www.nytimes.com/2017/12/29/opinion/dont-cheer-as-the-irs-grows-weaker.html"


### Normal running
if True:
#if False:
    crlr = crawler.Crawler({})
    url_info = object_model.url_info.UrlInfo({
                                          "url": url,
                                          "initiator_type": object_model.url_info.url_info_initiator_type.manual,
                                          "initiator_id": "eliad",
                                          "depth_max": 2,
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
    

    
    
    
    
    


