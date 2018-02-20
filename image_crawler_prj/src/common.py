
# get exception info
import sys 
import traceback

# test 2

##################
# Stats
##################
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


##################
# URL parser
##################
import urlparse # parse url
import urllib # parse url
from collections import OrderedDict
class UrlParser(object):

    def __init__(self, url):
        self.url = url
        self.url_orig = url
        self.parseResult = urlparse.urlparse(url)

    def GetStripDomain(self):
        urlDomain = "{0.netloc}".format(self.parseResult)

        stripUrlDomain = urlDomain
        if urlDomain.startswith('www.'):
            stripUrlDomain = urlDomain[4:]

        return stripUrlDomain
    
    def get_domain(self):
        return "{0.netloc}".format(self.parseResult)

    def get_scheme(self):
        return "{0.scheme}".format(self.parseResult)
    
    def add_scheme(self):
        if self.parseResult.scheme:
            return self.url
        return "http://:" + self.url
    
    def remove_scheme(self):
        self.url = self.url.replace("http://","").replace("https://","")
        return self.url
    
    def EncodeUrl(self):
        tmpUrl = self.url.replace("http://","").replace("https://","")
        encodedFileName = urllib.quote(tmpUrl, '')
        return encodedFileName
    
    def encode_url(self):
        tmp_url = self.url_query_sort()
        tmp_url = tmp_url.replace("http://","").replace("https://","")
        encoded_url = urllib.quote(tmp_url, '')
        return encoded_url
    
    def url_query_sort(self):
        query_sorted_encoded = self.query_sort()
        
        if query_sorted_encoded:
            query_sorted_encoded = "?" + query_sorted_encoded
        
        self.url = "{0.scheme}://{0.netloc}{0.path}{1}".format(self.parseResult, query_sorted_encoded)
        
        return self.url
    
    def query_sort(self):
        query_dic = dict(urlparse.parse_qsl(urlparse.urlsplit(self.url).query))
        
        query_sorted = ""
        for key,value in sorted(query_dic.items()):
            query_sorted += key + "=" + value + "&"
            
        if len(query_sorted) > 1 and  query_sorted[-1:] == '&':
            query_sorted = query_sorted[:-1]
        
        query_sorted_encoded = urllib.urlencode(OrderedDict(query_dic))
        
        return query_sorted_encoded
    
    def url_complete_from_parent(self, parent_url = None, add_scheme = True, encode = False):
        domain = self.get_domain()
        if not domain and parent_url:
            domain = UrlParser(parent_url).get_domain()
            
        scheme = ""
        if add_scheme:
            scheme = self.get_scheme()
            if not scheme and parent_url:
                scheme = UrlParser(parent_url).get_scheme()
        if scheme:
            scheme += "://"
            
        query_sorted_encoded = self.query_sort()
        if len(query_sorted_encoded) > 1:
            query_sorted_encoded = "?" + query_sorted_encoded
        
        complete_url = "{0}{1}{2.path}{3}".format(scheme, domain, self.parseResult, query_sorted_encoded)
        
        if encode:
            return urllib.quote(complete_url, '')
        else:
            return complete_url
        
    
##################
# Extract link
##################
from pyvirtualdisplay import Display # Chrome headless
from selenium import webdriver 
from bs4 import BeautifulSoup
import object_model.url_info
def link_extractor(url_info, html_source=None, dest_folder=None):
    print("Going to link_extractor from url '"+url_info.url+"'.")
    
    if html_source is not None:
        return link_extractor_html(url_info, html_source)
    
    if dest_folder is not None:
        html_file = dest_folder + "/" + UrlParser(url_info.url).encode_url() + ".html"
        if os.path.isfile(html_file):
            with open(html_file, 'r') as file_handler:
                html_source = file_handler.read().decode('ascii','ignore')
                return link_extractor_html(url_info, html_source)

    
    display = Display(visible=0, size=(800, 600))
    display.start()
    
    driver = webdriver.Chrome()
    #driver = webdriver.Firefox()
    driver.get(url_info.url);
            
    # save html source in local file
    html_source = driver.page_source.encode('utf-8')
    
    if dest_folder is not None: 
        with open(html_file, 'w') as html_file_handler:
            html_file_handler.write(html_source)
        
    return link_extractor_html(url_info, html_source)

def link_extractor_html(url_info, html_source):
    
    url = url_info.url
    full_url = UrlParser(url).url_complete_from_parent(url)
    domain = UrlParser(url).GetStripDomain()
    if not domain:
        print("No domain in url '"+url+"'.")
        return [], []
    
    soup = BeautifulSoup(html_source, 'html.parser')
    links = soup.find_all('a')

    internal_links = dict()
    external_links = dict()
    for link in links:
        try:
            href = link.get('href')
            if (href is None) or (href in ["None",  ""] or href.startswith("javascript:") or href.startswith("#")):
                continue 
            
            href = href.encode('utf-8')
    
            link_domain = UrlParser(href).GetStripDomain()
            
            url_info_new = object_model.url_info.UrlInfo({
                                                           "parent_url": url,
                                                           "url": href,
                                                           "type": object_model.url_info.UrlInfoTypeEnum.unknown,
                                                           "initiator_type": object_model.url_info.UrlInfoInitiatorTypeEnum.extracted,
                                                           "initiator_id": url,
                                                           "depth": url_info.depth + 1,
                                                           "depth_max": url_info.depth_max,
                                                           "uuid": [ url_info.uuid ],
                                                           })
            
            if full_url == url_info_new.url:
                # Same link
                continue
            
            if url_info_new.url in external_links or url_info_new.url in internal_links:
                # link already exist
                continue
    
            if (link_domain not in domain) and (domain not in link_domain) and (("http" in href) or ("https" in href)):
                external_links[url_info_new.url] = url_info_new
            else:
                internal_links[url_info_new.url] = url_info_new
                
        except Exception as e: 
            print("Exception: type '",sys.exc_info()[0],"', message '",e,"'")
            traceback.print_exc()
            return [], [] 
        
    internal_links_list = []
    for value in internal_links.itervalues():
        internal_links_list.append(value)
        
    external_links_list = []
    for value in external_links.itervalues():
        external_links_list.append(value)
    
    return internal_links_list, external_links_list
    
##################
# Utilities
##################

import os # Check if folder exists, join paths





#===============================================================================
# Object to dic function 
#===============================================================================
def ExtractDictValue(dic, param, default):
    try:
        return dic[param]
    except Exception: 
        return default

def to_dict(obj, classkey=None):
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = to_dict(v, classkey)
        return data
    elif hasattr(obj, "_ast"):
        return to_dict(obj._ast())
    elif hasattr(obj, "__iter__"):
        return [to_dict(v, classkey) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict([(key, to_dict(value, classkey)) 
            for key, value in obj.__dict__.iteritems() 
            if not callable(value) and not key.startswith('__')])
        if classkey is not None and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    else:
        return obj
    
    
    
    