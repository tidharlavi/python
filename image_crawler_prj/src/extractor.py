'''
Created on Dec 5, 2017

@author: eliad
'''
import os # Check if folder/file exists/sizes
import time # used for unknown name
from datetime import datetime # datetime now
import urllib # url parsing
import urllib2 # Download images
#import json # pretty dump
import re # string parsing: extract url from style

from bs4 import BeautifulSoup # handle html parsing and printing
from bs4.element import Comment

# get exception info
import sys 
import traceback

from binascii import a2b_base64 # decode embedded images
from PIL import Image

from pyvirtualdisplay import Display # Chrome headless
from selenium import webdriver 

import requests

# Local lib
import common
from object_model import image_details

class extractor(object):
    '''
    classdocs
    '''

    def __init__(self, params = "{}"):
        self.stats = common.Stats()
        self.image_details_arr = []
        
        if "dest_folder" in params:
            self.dest_folder = params["dest_folder"]
        else:
            self.dest_folder = "/home/eliad/python/image_crawler/images_db/"
        
        self.driver_headless = True

    def extract_info(self, url_info):
        self.stats.TimeStart("_TotalTime")
        
        self.url_info = url_info
        
        url = url_info.url
        
        # Create relevant folders
        domain = common.UrlParser(url).GetStripDomain()
        self.url_time_folder = self.dest_folder + "/" + domain + "/" + common.UrlParser(url).encode_url() + "/" + time.strftime("%Y_%m_%d-%H")
        for folder in [self.dest_folder + "/" + domain, 
                       self.dest_folder + "/" + domain + "/" + common.UrlParser(url).encode_url(), 
                       self.url_time_folder,
                       self.url_time_folder + "/images",
                       self.url_time_folder + "/images/irr"]:
            if not os.path.exists(folder):
                os.makedirs(folder)

        # Selenium
        self.stats.TimeStart("_BrowserDriverTime")
        if self.driver_headless:
            display = Display(visible=0, size=(1920, 1080))
            display.start()
        
        driver = webdriver.Chrome()
        #driver = webdriver.Firefox()
        print "extract_info(): driver.get({0})".format(url)
        driver.get(url);
        
        window_size =  driver.get_window_size()
        driver.get_screenshot_as_file(self.url_time_folder + "/start_try_1920_1080_actual_"+str(window_size["width"])+"_"+str(window_size["height"])+".png")
        
        driver.set_window_size(1920, 1080)
        #print driver.get_window_size()
        driver.get_screenshot_as_file(self.url_time_folder + "/try_1920_1080_actual_"+str(window_size["width"])+"_"+str(window_size["height"])+".png")
        
        #driver.set_window_size(480, 320)
        #print driver.get_window_size()
        #driver.get_screenshot_as_file(self.url_time_folder + "/480_320.png")
        
        # Exception: 
        #driver.maximize_window()
        #print driver.get_window_size()
        #driver.get_screenshot_as_file(self.url_time_folder + "/maximize.png")
                
        # save html source in local file
        self.html_source = driver.page_source.encode('utf-8')
        html_file = self.url_time_folder + "/" + common.UrlParser(url).encode_url() + ".html"
        if (not os.path.isfile(html_file) and len(html_file) < 500):
            with open(html_file, 'w') as html_file_handler:
                html_file_handler.write(self.html_source)
        
        # temporary array with basic info on images
        img_dtl_arr = []
        
        # Extract images !!!
        print "extract_info(): self.extract_images_from_img_tag()"
        self.extract_images_from_img_tag(url, driver, img_dtl_arr)
        print "extract_info(): self.extract_images_from_style_attribute()"
        self.extract_images_from_style_attribute(url, driver, img_dtl_arr)
        
        # Release driver
        driver.quit()
        self.stats.TimeEnd("_BrowserDriverTime")
        
        # Download images and add more details to img_dtl
        print "extract_info(): self.download_images()"
        self.download_images(img_dtl_arr)
        
        # Extract all links
        print "extract_info(): common.link_extractor()"
        self.internal_links, self.external_links = common.link_extractor(url_info, self.html_source, self.url_time_folder)
        self.stats.Add("internal_links_cnt", len(self.internal_links))
        self.stats.Add("external_links_cnt", len(self.external_links))
        
        # extract information from surrounding html tag
        print "extract_info(): self.extract_info_from_html_tag()"
        self.extract_info_from_html_tag()
        
        # extract information from webpage: tags, keywords, title
        print "extract_info(): self.extract_info_from_html_tag()"
        self.extract_web_page_info(url_info)

        self.stats.TimeEnd("_TotalTime")    
      

    #
    # Internal functions - 
    #
    
    def extract_images_from_style_attribute(self, url, driver, img_dtl_arr):
        # Get all elements and go over them
        elements = driver.find_elements_by_xpath("//*")
        
        for elem in elements:
            try:
                # check if they have 'style' attribute
                style = elem.get_attribute('style')
                if not style:
                    continue
    
                # Check if we have url
                # width: 92px; height: 19px; background: url("/images/searchDropDown.gif") 3px 7px no-repeat rgb(255, 255, 255); position: absolute; left: 1px; z-index: 10; border: 1px solid rgb(216, 218, 221);
                urlRegex = re.compile('.*url\(\"?([^\"]*)\"?\).*')
                m = urlRegex.match(style)
                if not m:
                    continue
                
                # Regex fixes
                src = m.group(1)
                if src[-1:] == '"':
                    src = src[:-1]
                    
                self.stats.Incr("images_from_style_attribute")
                img_dtl = image_details.image_details()
                
                img_dtl.page_src_url = url
                img_dtl.time = datetime.utcnow()
                
                img_dtl.src = src
                
                img_dtl.extract_method = image_details.extract_method.style_attribute
                
                img_dtl.html_tag_id = elem.get_attribute("id")
                if img_dtl.html_tag_id == None or img_dtl.html_tag_id == "" or len(img_dtl.html_tag_id) < 1:
                    self.stats.Incr("fail_to_get_img_html_tag_id")
                    
                img_dtl.window_size = driver.get_window_size()
                
                img_dtl.html_tag_height = elem.get_attribute('height')
                img_dtl.html_tag_width = elem.get_attribute('width')
                img_dtl.browser_location = elem.location
                img_dtl.browser_location_once_scrolled_into_view = elem.location_once_scrolled_into_view  
                img_dtl.browser_width = elem.size["width"]
                img_dtl.browser_height = elem.size["height"]
                
                img_dtl_arr.append(img_dtl)
            except Exception as e:
                print("Exception during extract_images_from_style_attribute() handling. first loop.")
                print("Exception: type '",sys.exc_info()[0],"', message '",e,"'")
                traceback.print_exc()
                self.stats.Incr("exception_extract_images_from_style_attribute")
    
    def extract_images_from_img_tag(self, url, driver, img_dtl_arr):
        images = driver.find_elements_by_tag_name('img')
        #print("'"+str(len(images))+"' images in '"+url+"'")
        
        for img in images:
            try:
                
                self.stats.Incr("images_from_img_tag")
            
                img_dtl = image_details.image_details()
    
                img_dtl.page_src_url = url
                img_dtl.time = datetime.utcnow()
    
                img_dtl.src = img.get_attribute('src')
                img_dtl.alt = img.get_attribute('alt')
                img_dtl.title = img.get_attribute('title')
                
                img_dtl.extract_method = image_details.extract_method.img_tag
                
                img_dtl.html_tag_id = img.get_attribute("id")
                if img_dtl.html_tag_id == None or img_dtl.html_tag_id == "" or len(img_dtl.html_tag_id) < 1:
                    self.stats.Incr("fail_to_get_img_html_tag_id")
                    
                img_dtl.window_size = driver.get_window_size()
                
                img_dtl.html_tag_height = img.get_attribute('height')
                img_dtl.html_tag_width = img.get_attribute('width')
    
                img_dtl.browser_location = img.location
                img_dtl.browser_location_once_scrolled_into_view = img.location_once_scrolled_into_view  
                img_dtl.browser_width = img.size["width"]
                img_dtl.browser_height = img.size["height"]
                img_dtl_arr.append(img_dtl)
            except Exception:
                print("Exception during extract_images_from_img_tag() handling. first loop.")
                exc_type, value, exc_traceback = sys.exc_info()
                print("Global Exception: type '"+str(exc_type)+"', value '"+str(value)+"'")
                traceback.print_exc()
                
    def download_images(self, img_dtl_arr):
        for img_dtl in img_dtl_arr:
            try:
    
                if not img_dtl.src:
                    self.stats.Incr("skip_no_src")
                    continue
                
                file_extension = os.path.splitext(img_dtl.src)[1][1:]
                img_dtl.extension = file_extension.lower()
                
                if img_dtl.extension in ['svg']:
                    self.stats.Incr("skip_svg_file_extension")
                    continue
                
                if img_dtl.extension in ['mp4']:
                    self.stats.Incr("skip_mp4_file_extension")
                    continue
      
                if img_dtl.browser_width < 10 or img_dtl.browser_height < 10:
                    #print("skip_browser_size: height '"+str(img_dtl.browser_height)+"', width '"+str(img_dtl.browser_width)+"' for '"+img_dtl.src+"'.")
                    self.stats.Incr("skip_browser_size")
                    continue
    
                file_name = self.download_image(img_dtl)
                if file_name is None:
                    continue
    
                self.image_details_arr.append(img_dtl)
                self.stats.Incr("append_image")
            except Exception as e: 
                print("======= download_images() Exception: type '",sys.exc_info()[0],"', message '",e,"'")
                print ', '.join("%s: %s" % img_dtl for img_dtl in vars(img_dtl).items())
                traceback.print_exc()
                continue

    def download_image(self, img_dtl):

        src = img_dtl.src
        url = img_dtl.page_src_url

        domain = common.UrlParser(url).GetStripDomain()
        img_dtl.domain = domain
                
        destFolder = self.url_time_folder + "/images"
      
        if "data:image" in src:
            # src="data:image/png;base64,iVBORw0KG .... "
            fileName = self.download_image_embeeded(src, destFolder)
            img_dtl.extract_method = image_details.download_method.embeeded
        else:
            # <img class="lazy" data-original="https://go.ynet.co.il/TipIsraeli/pics/ynetshopsBig/images/assets/product_images/74510_105.jpg" alt="" title="???? 554 ???? " width="105px" height="105px" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC">
            fileName = self.download_image_src(src, domain, destFolder)
            img_dtl.extract_method = image_details.download_method.src_url

        if fileName is None:
            print("Fail to download '"+src+"', fileName '"+fileName+"'.")
            self.stats.Incr("skip_fail_download")
            return None

        # validation
        img_dtl.os_size = os.stat(fileName).st_size
        if img_dtl.os_size == 0:
            #print("Fail to download '"+src+"', fileName '"+fileName+"'. File size is 0.")
            self.stats.Incr("skip_os_file_size")
            return None
        
        img_dtl.path = str(fileName)
        #print("Download: src '"+src+"' to fileName '"+fileName+"'.")

        try:
            with Image.open(fileName) as im:
                # fill img object
                img_dtl.image_height = im.size[1]
                img_dtl.image_width = im.size[0]
                img_dtl.image_format = im.format
                img_dtl.image_format_description = im.format_description
                #img_dtl.image_info = im.info
                img_dtl.image_mode = im.mode
                if hasattr(im, "text"):
                    img_dtl.image_text = im.text
                #img_dtl.image_tile = im.tile

        except Exception as e: 
            print("Fail to Image.open '"+fileName+"'.")
            print("Exception: type '",sys.exc_info()[0],"', message '",e,"'")
            traceback.print_exc()
            self.stats.Incr("skip_fail_image_open")
            return None

        try:
            if (img_dtl.os_size < 2500) or img_dtl.image_width < 100 or img_dtl.image_height < 100 or img_dtl.browser_width < 30 or img_dtl.browser_height < 30:
                self.stats.Incr("skip_irr")
                #print("Irrelevent: '" + ', '.join("%s: %s" % item for item in vars(img_dtl).items()) + "'." )
                #print("skip_irr: os_size '"+str(img_dtl.os_size)+"', browser_height '"+str(img_dtl.browser_height)+"', browser_width '"+str(img_dtl.browser_width)+"', image_height '"+str(img_dtl.image_height)+"', image_width '"+str(img_dtl.image_width)+"' for '"+img_dtl.src+"'.")
                basename = os.path.basename(src)
                if '?' in basename:
                    file_name_with_ext_arr = basename.split('?')[0].split('.')
                    ext = ""
                    if len(file_name_with_ext_arr) > 2:
                        ext = file_name_with_ext_arr[1]
                    encoded_basename = urllib.quote(basename, '')
                    encoded_basename = encoded_basename + '.' + ext
                    filename_move = destFolder + "/irr/" + encoded_basename
                        
                else:
                    filename_move = destFolder + "/irr/" + basename

                if not os.path.exists(filename_move):
                    os.rename(fileName, filename_move)
                else:
                    # Already exist, we can delete it
                    os.remove(fileName)
                    
                return None
                
        except Exception:
            exc_traceback, value, exc_traceback = sys.exc_info()
            print("Global Exception: type '"+str(exc_traceback)+"', value '"+str(value)+"'")
            traceback.print_exc()
            return None

        return fileName

    def download_image_embeeded(self, src, destFolder):
        print("Embeeded image found !!!")

        data = src.split(',')[1]
        binary_data = a2b_base64(data)

        fileext =  src.split(';')[0].split('/')[1]
        if fileext.lower() not in ["png", "jpg", "jpeg", "gif"]:
            return 
        filename = destFolder + "/" + time.strftime("%Y%m%d-%H%M%S") + "." + fileext
        fd = open(filename, 'wb')
        fd.write(binary_data)
        fd.close()

        print("fileName '"+filename+"'.")

        return filename

    def download_image_src(self, src, domain, destFolder):
        # Set up image src
        if src.startswith('http'):
            src_full_path = src
        elif src.startswith('//'):
            src_full_path = "http:" + src
        elif domain in src:
            src_full_path = "http:" + src
        else:
            src_full_path = "http://" + domain + src

        # setup target file name
        basename = os.path.basename(src)

        fileName = destFolder + "/" + basename
        filename_irr = destFolder + "/irr/" + basename
        if '?' in basename:
            print("basename '"+basename+"', src '"+src+"'.")
            file_name_with_ext = basename.split('?')[0]
            if file_name_with_ext is not "":
                file_name_with_ext_arr = file_name_with_ext.split('.')
                if len(file_name_with_ext_arr) > 2:
                    ext = file_name_with_ext_arr[1]
                    encoded_basename = urllib.quote(basename, '')
                    encoded_basename = encoded_basename + '.' + ext
                    fileName = destFolder + "\\" + encoded_basename

        # check if file already exist
        if os.path.exists(fileName):
            #print("src_full_path '"+src_full_path+"', fileName '"+fileName+"'. Exist !!!!")
            self.stats.Incr("image_exist")
            return fileName
        
        if os.path.exists(filename_irr):
            #print("src_full_path '"+src_full_path+"', fileName '"+filename_irr+"'. Exist !!!!")
            self.stats.Incr("image_irr_exist")
            return filename_irr

        #print("Try to download: src_full_path '"+src_full_path+"' to fileName '"+fileName+"'.")

        try:
            # try to get image
            opener = urllib2.build_opener()
            opener.addheaders = [('User-Agent', 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)')]
            response = opener.open(src_full_path)
        except Exception:
            print("Fail to download '"+src_full_path+"'.")
            return None

        # getting content-length
        content_len = 0;
        try:
            content_len_str = response.headers['content-length']
        except Exception:
            content_len_str = "0"
            print("No content len in headers.")
        if content_len_str is not None:
            content_len = float(content_len_str)

        try:
            # try to save image
            with open(fileName, 'wb') as f:
                f.write(response.read())
        except Exception:
            print("Fail to save '"+fileName+"'.")
            return None

        return fileName
                    
    def extract_info_from_html_tag(self, img_dtl_arr = None, depth = 4):
        
        if img_dtl_arr is None:
            img_dtl_arr = self.image_details_arr
            
        soup = BeautifulSoup(self.html_source, 'html.parser')
        
        for img_dtl in img_dtl_arr:
            try:
                if "taboola" in img_dtl.src:
                    img_dtl.adv = image_details.advertisers.taboola
                    self.stats.Incr("found_adv_" + image_details.advertisers.taboola.name)
                    
                if "outbrain" in img_dtl.src:
                    img_dtl.adv = image_details.advertisers.outbrain
                    self.stats.Incr("found_adv_" + image_details.advertisers.outbrain.name)
                
                #print "New image ==========================="
                img_soup_arr = soup.findAll('img', {'src': img_dtl.src})
                if len(img_soup_arr) != 1:
                    self.stats.Incr("same_src_img_"+str(len(img_soup_arr)))
                    #print("Error: len(img_soup_arr)=" + str(len(img_soup_arr)))
                    continue
                    
                img_soup = img_soup_arr[0]
                
                img_soup_p = img_soup.parent
                for i in range(1, depth):
                    #print "depth = " + str(i) + "==="
                    if img_soup_p is None or img_soup_p.name in ["body", "html"]:
                        self.stats.Incr("reached_end")
                        break
                    
                    if img_soup_p.name == 'a' and not hasattr(img_dtl, 'link'):
                        img_dtl.link = img_soup_p.get("href")
                        self.stats.Incr("found_link_in_"+str(i))
                        
                        if "doubleclick" in img_dtl.link:
                            img_dtl.adv = image_details.advertisers.doubleclick
                            self.stats.Incr("found_adv_" + image_details.advertisers.doubleclick.name)
                    
                    text = self.text_from_soup(img_soup_p).strip()
                    if text and not hasattr(img_dtl, 'text'):
                        img_dtl.text = text
                        self.stats.Incr("found_text_in_"+str(i))
                        
                    img_soup_p = img_soup_p.parent
                        
                #print(str(index) + ": " + ', '.join("%s: %s" % item for item in vars(img_dtl).items()) + "'." )
            except Exception as e: 
                print("extract_info_from_html_tag Exception: type '",sys.exc_info()[0],"', message '",e,"'")
                traceback.print_exc()
                continue

    def extract_web_page_info(self, url_info = None):  

        html_source = None
        if hasattr(self, 'html_source'):
            html_source = self.html_source        
        if url_info != None and hasattr(url_info, "url"):
            url = url_info.url
            res = requests.get(url)
            #html_source = res.text
            
            content_type = res.headers['Content-Type'] # figure out what you just fetched
            ctype, charset = content_type.split(';')
            encoding = charset[len(' charset='):] # get the encoding
            #print encoding # ie ISO-8859-1
            utext = res.content.decode(encoding) # now you have unicode
            html_source = utext.encode('utf8', 'ignore')
            
        if html_source == None:
            return
        
        soup = BeautifulSoup(html_source, 'html.parser')
    
        meta_tags = soup.findAll("meta", attrs={"name":"keywords"})
        if len(meta_tags) == 1:
            for meta_tag in meta_tags:
                if "content" in meta_tag.attrs:
                    #print("meta name 'keywords' = " + meta_tag["content"])
                    url_info.metatag_keywords = meta_tag["content"]
                    self.stats.Incr("found_metatag_keywords")
            
        meta_tags = soup.findAll("meta", attrs={"name":"description"})
        if len(meta_tags) == 1:
            for meta_tag in meta_tags:
                if "content" in meta_tag.attrs:
                    #print("meta name 'description' = " + meta_tag["content"])
                    url_info.metatag_desription = meta_tag["content"]
                    self.stats.Incr("found_metatag_desription")
             
        title = soup.title.string
        if title:
            url_info.page_title = title
            self.stats.Incr("found_page_title") 
            
        self.url_info = url_info
        
    #                
    # Utilities
    #          
    def tag_visible(self, element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True
    
    def text_from_soup(self, soup):
        texts = soup.findAll(text=True)
        visible_texts = filter(self.tag_visible, texts)  
        return u" ".join(t.strip() for t in visible_texts)        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    