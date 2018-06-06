'''
Created on Dec 5, 2017

@author: eliad
'''
import logging
import os # Check if folder/file exists/sizes
import time # used for unknown name
import urllib # url parsing
import urllib2 # Download images
#import json # pretty dump
import re # string parsing: extract url from style
import operator

from bs4 import BeautifulSoup # handle html parsing and printing
from bs4.element import Comment
import cssutils

# get exception info
import sys 
import traceback

from binascii import a2b_base64 # decode embedded images
from PIL import Image

from pyvirtualdisplay import Display # Chrome headless
from selenium import webdriver 
from selenium.common.exceptions import StaleElementReferenceException

import requests

# Local lib
import common
from object_model import image_details
from object_model import url_info
import extract_keywords

log = logging.getLogger(__name__)

class extractor(object):
    '''
    classdocs
    '''
    
    DRIVER_GET_RETRY_NUM = 3

    def __init__(self, params = "{}"):
        self.stats = common.Stats()
        self.image_details_arr = []
        self.internal_links = []
        self.image_links = []
        
        if "dest_folder" in params:
            self.dest_folder = params["dest_folder"]
        else:
            self.dest_folder = "/home/eliad/python/image_crawler/images_db/"
        
        self.driver_headless = True

    def extract_info(self, url_inf):
        self.stats.TimeStart("_TotalTime")
        
        self.url_info = url_inf
        
        url = url_inf.url
        self.url = url_inf.url
        
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
        
        driver_success = False
        for idx in range(self.DRIVER_GET_RETRY_NUM):
            try:
                if self.driver_headless:
                    display = Display(visible=0, size=(1920, 1080))
                    display.start()
                
                driver = webdriver.Chrome()
                log.info("try '%d': driver.get(%s)", idx, url)
                driver.get(url);
                driver_success = True
                break;
            except:
                log.exception("Exception during try '%d' selenium driver.get(%s).", idx, url)
                if self.driver_headless:
                    display.stop()
                driver.quit()
        
        self.stats.Add("driver_succed_in_try", idx)
                
        if not driver_success:
            log.error("Fail to driver.get(%s).", url)
            self.stats.TimeEnd("_BrowserDriverTime")
            self.stats.TimeEnd("_TotalTime")
            return None
        
        self.window_size =  driver.get_window_size()
        driver.get_screenshot_as_file(self.url_time_folder + "/start_try_1920_1080_actual_"+str(self.window_size["width"])+"_"+str(self.window_size["height"])+".png")
        
        driver.set_window_size(1920, 1080)
        #print driver.get_window_size()
        driver.get_screenshot_as_file(self.url_time_folder + "/try_1920_1080_actual_"+str(self.window_size["width"])+"_"+str(self.window_size["height"])+".png")
        
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
        self.soup = BeautifulSoup(self.html_source, 'html.parser')
        
        # temporary array with basic info on images
        img_dtl_arr = []
        
        # Extract images !!!
        print "extract_info(): self.extract_images_from_img_tag()"
        self.extract_images_from_img_tag(url, driver, img_dtl_arr)
        print "extract_info(): self.extract_images_from_style_attribute()"
        self.extract_images_from_style_attribute(url, driver, img_dtl_arr)
        
        # Release driver
        display.stop()
        driver.quit()
        self.stats.TimeEnd("_BrowserDriverTime")
        
        # Download images and add more details to img_dtl
        print "extract_info(): self.download_images()"
        self.download_images(img_dtl_arr)
        
        # Add information to images - browser area, score according to area size ..
        print "extract_info(): self.process_images()"
        self.process_images()
        
        # extract information from web page: tags, keywords, title
        print "extract_info(): self.extract_website_info()"
        try:
            self.extract_website_info()
        except:
            log.exception("Exception during extract_website_info(), mainly for keywords extraction.")
            
        # Extract all links
        print "extract_info(): common.link_extractor()"
        self.internal_links, self.external_links = common.link_extractor(url_inf, self.html_source, self.url_time_folder)
        self.stats.Add("internal_links_cnt", len(self.internal_links))
        self.stats.Add("external_links_cnt", len(self.external_links))
        
        # extract information from surrounding html tag
        print "extract_info(): self.extract_info_from_html_tag()"
        self.extract_info_from_html_tag()
        
        self.stats.TimeEnd("_TotalTime")    
        
        return True
      

    #
    # Internal functions - 
    #
    
    def extract_images_from_style_attribute(self, url, driver, img_dtl_arr):
        
        if False:
            ### using selenuiom driver
            self.stats.TimeStart("extract_images_from_style_attribute_selenuim_time")
            # Get all elements and go over them
            elements = driver.find_elements_by_xpath("//*")
            self.stats.Add("extract_images_from_style_attribute_selenuim_elem_cnt", len(elements))
            for elem in elements:
                try:
                    self.stats.Incr("extract_images_from_style_attribute_selenuim_url_check")
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
                        
                    self.stats.Incr("extract_images_from_style_attribute_selenuim_url_cnt")
                    img_dtl = image_details.ImageDetails()
                    
                    img_dtl.website_src_url = url
                    
                    img_dtl.src = src
                    
                    img_dtl.extract_method = image_details.ExtractMethodEnum.style_attribute
                    
                    img_dtl.html_tag_id = elem.get_attribute("id")
                    if img_dtl.html_tag_id == None or img_dtl.html_tag_id == "" or len(img_dtl.html_tag_id) < 1:
                        self.stats.Incr("fail_to_get_img_html_tag_id")
                        
                    img_dtl.browser_window_size = self.window_size
                    
                    img_dtl.html_tag_height = elem.get_attribute('height')
                    img_dtl.html_tag_width = elem.get_attribute('width')
                    img_dtl.browser_location = elem.location
                    img_dtl.browser_location_once_scrolled_into_view = elem.location_once_scrolled_into_view  
                    img_dtl.browser_width = elem.size["width"]
                    img_dtl.browser_height = elem.size["height"]
                    
                    #img_dtl_arr.append(img_dtl)
                except StaleElementReferenceException:
                    log.exception("StaleElementReferenceException during extract_images_from_style_attribute() break !!!.")
                    self.stats.Incr("exception_stale_extract_images_from_style_attribute_selenuim")
                    break
                except Exception:
                    log.exception("Exception during extract_images_from_style_attribute() handling. also break !!!")
                    self.stats.Incr("exception_extract_images_from_style_attribute_selenuim")
                    break
                    
            self.stats.TimeEnd("extract_images_from_style_attribute_selenuim_time")
                    
            
        ### using selenuiom driver
        self.stats.TimeStart("extract_images_from_style_attribute_soup_time")
        try:
            styles = self.soup.findAll(style=re.compile("background-image"))
            self.stats.Add("extract_images_from_style_attribute_soup_elem_cnt", len(styles))
            for style in styles:
                img_dtl = image_details.ImageDetails()
                
                div_style = style.get('style')
                style_attr = cssutils.parseStyle(div_style)
                background_image_url = style_attr['background-image']
                
                if background_image_url is None or background_image_url == 'none':
                    self.stats.Incr("extract_images_from_style_attribute_soup_not_valid_url")
                    continue
                
                urlRegex = re.compile('.*url\(\"?([^\"]*)\"?\).*')
                m = urlRegex.match(background_image_url)
                if not m:
                    continue
                
                # Regex fixes
                src = m.group(1)
                if src[-1:] == '"':
                    src = src[:-1]
                    
                img_dtl.website_src_url = background_image_url
                
                img_dtl.src = src
                
                img_dtl.extract_method = image_details.ExtractMethodEnum.style_attribute
                
                html_tag_id = style.get('id')
                if html_tag_id != None:
                    print "html_tag_id=" + ', '.join(html_tag_id)
                    elem = driver.find_element_by_id(html_tag_id)
                    
                    img_dtl.html_tag_height = elem.get_attribute('height')
                    img_dtl.html_tag_width = elem.get_attribute('width')
                    img_dtl.browser_location = elem.location
                    img_dtl.browser_location_once_scrolled_into_view = elem.location_once_scrolled_into_view  
                    img_dtl.browser_width = elem.size["width"]
                    img_dtl.browser_height = elem.size["height"]
        
                else:
                    html_tag_classes = style.get('class')
                    if html_tag_classes != None:
                        log.info("html_tag_classes '%s'", html_tag_classes)
                        
                        for tag_class in html_tag_classes:
                            html_tags = driver.find_elements_by_css_selector(tag_class)
                            log.info("Found '%s' for class '%s'.", len(html_tags), tag_class)
                        
                self.stats.Incr("extract_images_from_style_attribute_soup_url_cnt")
                img_dtl_arr.append(img_dtl)
        except Exception:
                log.exception("Exception during extract_images_from_style_attribute() soup handling.")
                self.stats.Incr("exception_extract_images_from_style_attribute_soup")
        
        self.stats.TimeEnd("extract_images_from_style_attribute_soup_time")       
        
    def extract_images_from_img_tag(self, url, driver, img_dtl_arr):
        images = driver.find_elements_by_tag_name('img')
        #print("'"+str(len(images))+"' images in '"+url+"'")
        
        for img in images:
            try:
                
                self.stats.Incr("images_from_img_tag")
            
                img_dtl = image_details.ImageDetails()
    
                img_dtl.website_src_url = url
    
                img_dtl.src = img.get_attribute('src')
                img_dtl.html_tag_alt = img.get_attribute('alt')
                if img_dtl.html_tag_alt:
                    self.stats.Incr("image_have_alt")
                img_dtl.html_tag_title = img.get_attribute('title')
                if img_dtl.html_tag_title:
                    self.stats.Incr("image_have_title")
                
                img_dtl.extract_method = image_details.ExtractMethodEnum.img_tag
                
                img_dtl.html_tag_id = img.get_attribute("id")
                if img_dtl.html_tag_id == None or img_dtl.html_tag_id == "" or len(img_dtl.html_tag_id) < 1:
                    self.stats.Incr("fail_to_get_img_html_tag_id")
                    
                img_dtl.browser_window_size = self.window_size
                
                img_dtl.html_tag_height = img.get_attribute('height')
                img_dtl.html_tag_width = img.get_attribute('width')
    
                img_dtl.browser_location = img.location
                img_dtl.browser_location_once_scrolled_into_view = img.location_once_scrolled_into_view  
                img_dtl.browser_width = img.size["width"]
                img_dtl.browser_height = img.size["height"]
                img_dtl_arr.append(img_dtl)
            except StaleElementReferenceException:
                log.exception("StaleElementReferenceException during extract_images_from_img_tag() break !!!.")
                self.stats.Incr("exception_stale_extract_images_from_img_tag")
                break
            except Exception:
                log.exception("Exception during extract_images_from_img_tag() handling. first loop.")
                self.stats.Incr("exception_extract_images_from_img_tag")
                
                if self.stats.GetVal("exception_extract_images_from_img_tag") > 2:
                    log.exception("Exception during extract_images_from_img_tag() handling. first loop. too many exceptions - break!!!")
                    break
                
                
    '''
    Download Images functions
    '''
    def download_images(self, img_dtl_arr):
        for img_dtl in img_dtl_arr:
            try:
    
                if not img_dtl.src:
                    self.stats.Incr("skip_no_src")
                    continue
                
                filename_arr = os.path.splitext(common.UrlParser(img_dtl.src).parseResult.path)
                if len(filename_arr) != 2:
                    self.stats.Incr("image_file_no_extension")
                    continue
                
                img_dtl.extension = filename_arr[1][1:].lower()
                
                if img_dtl.extension in ['svg']:
                    self.stats.Incr("skip_svg_file_extension")
                    continue
                
                if img_dtl.extension in ['mp4']:
                    self.stats.Incr("skip_mp4_file_extension")
                    continue
                
                if img_dtl.extension in ['asp']:
                    self.stats.Incr("skip_mp4_file_extension")
                    continue
      
                if img_dtl.browser_width < 10 or img_dtl.browser_height < 10:
                    #print("skip_browser_size: height '"+str(img_dtl.browser_height)+"', width '"+str(img_dtl.browser_width)+"' for '"+img_dtl.src+"'.")
                    self.stats.Incr("skip_browser_size")
                    continue
    
                file_name = self.download_image(img_dtl)
                if file_name is None:
                    continue
                
                img_dtl.crwl = self.url_info.crwl_curr
    
                self.image_details_arr.append(img_dtl)
                self.stats.Incr("append_image")
            except Exception: 
                log.exception("Exception during download_image(). img_dtl '" + ', '.join("%s: %s" % img_dtl for img_dtl in vars(img_dtl).items()) + "'.")
                continue

    def download_image(self, img_dtl):

        src = img_dtl.src
        url = img_dtl.website_src_url

        domain = common.UrlParser(url).GetStripDomain()
        img_dtl.website_domain = domain
                
        destFolder = self.url_time_folder + "/images"
      
        if "data:image" in src:
            # src="data:image/png;base64,iVBORw0KG .... "
            fileName = self.download_image_embeeded(src, destFolder)
            img_dtl.download_method = image_details.DownloadMethodEnum.embeeded
        else:
            # <img class="lazy" data-original="https://go.ynet.co.il/TipIsraeli/pics/ynetshopsBig/images/assets/product_images/74510_105.jpg" alt="" title="???? 554 ???? " width="105px" height="105px" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC">
            fileName = self.download_image_src(src, domain, destFolder)
            img_dtl.download_method = image_details.DownloadMethodEnum.src_url

        if fileName is None:
            log.debug("Fail to download '"+src+".")
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
        img_dtl.id_set()

        try:
            with Image.open(fileName) as im:
                # fill img object
                img_dtl.image_height = im.size[1]
                img_dtl.image_width = im.size[0]
                
                if not img_dtl.extension:
                    img_dtl.extension = im.format.lower()
                
                #img_dtl.image_format_description = im.format_description
                #img_dtl.image_info = im.info
                #img_dtl.image_mode = im.mode
                #if hasattr(im, "text"):
                #    if isinstance(im.text, dict):
                #        img_dtl.image_text_dic = im.text.copy()
                #    else:
                #        log.info("Eliad: PIL im.text is not a dict !!!!")
                #img_dtl.image_tile = im.tile
                
                # check if its animated gif
                if img_dtl.extension in ['gif'] and hasattr(im, "is_animated") and im.is_animated:
                    log.info("Image is animated gif, skip it '%s'.", fileName)
                    self.stats.Incr("skip_animated_gif")
                    return None

        except Exception: 
            log.exception("Fail to PIL Image.open().")
            self.stats.Incr("skip_fail_image_open")
            return None

        try:
            if (img_dtl.os_size < 1300) or img_dtl.image_width < 50 or img_dtl.image_height < 50 or img_dtl.browser_width < 45 or img_dtl.browser_height < 45:
                self.stats.Incr("skip_irr")
                log.info("Irrelevent: '" + ', '.join("%s: %s" % item for item in vars(img_dtl).items()) + "'." )
                #print("skip_irr: os_size '"+str(img_dtl.os_size)+"', browser_height '"+str(img_dtl.browser_height)+"', browser_width '"+str(img_dtl.browser_width)+"', image_height '"+str(img_dtl.image_height)+"', image_width '"+str(img_dtl.image_width)+"' for '"+img_dtl.src+"'.")
                
                basename = os.path.basename(img_dtl.path)
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
        src_parse = common.UrlParser(src)
        src_full_path = src_parse.url_complete_from_parent(self.url, True, False)
        
        image_basename = os.path.basename(src_parse.parseResult.path)
        
        fileName = destFolder + "/" + image_basename
        filename_irr = destFolder + "/irr/" + image_basename

        # check if file already exist
        if os.path.exists(fileName):
            #print("src_full_path '"+src_full_path+"', fileName '"+fileName+"'. Exist !!!!")
            self.stats.Incr("image_exist")
            return fileName
        
        if os.path.exists(filename_irr):
            #print("src_full_path '"+src_full_path+"', fileName '"+filename_irr+"'. Exist !!!!")
            self.stats.Incr("image_irr_exist")
            return filename_irr

        #log.debug("Try to download: src_full_path '"+src_full_path+"' to fileName '"+fileName+"'.")

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
            log.exception("Fail to save '"+fileName+"'.")
            return None

        return fileName
                    
    def process_images(self, img_dtl_arr=None):
        
        if img_dtl_arr is None:
            img_dtl_arr = self.image_details_arr
        
        area_dic = dict()
        
        arr_len = len(img_dtl_arr)
        if arr_len == 0:
            return
        
        for img_dtl in img_dtl_arr:
            img_dtl.website_images_len = arr_len
            
            img_dtl.browser_area = img_dtl.browser_width * img_dtl.browser_height
            area_dic[img_dtl.id] = img_dtl.browser_area

        sorted_areas = sorted(area_dic.items(), key=lambda x: x[1]) # sorted(area_dic.items(), key=operator.itemgetter(1)).reverse() # (id, area)
        
        sorted_area_dic = dict()
        rank = 0
        prev_value = sorted_areas[-1][1]
        for img_area in reversed(sorted_areas):
            if img_area[1] != prev_value:
                rank = rank + 1
            prev_value = img_area[1]
            sorted_area_dic[img_area[0]] = rank
                
        for img_dtl in img_dtl_arr:
            img_dtl.website_image_rank = sorted_area_dic[img_dtl.id] 
              
    def extract_info_from_html_tag(self, img_dtl_arr = None, depth = 4):
        
        if img_dtl_arr is None:
            img_dtl_arr = self.image_details_arr
            
        self.image_links = []
        
        for img_dtl in img_dtl_arr:
            try:
                if "taboola" in img_dtl.src:
                    img_dtl.html_adv = image_details.AdvertisersEnum.taboola
                    self.stats.Incr("found_adv_" + image_details.AdvertisersEnum.taboola.name)
                    
                if "outbrain" in img_dtl.src:
                    img_dtl.html_adv = image_details.AdvertisersEnum.outbrain
                    self.stats.Incr("found_adv_" + image_details.AdvertisersEnum.outbrain.name)
                
                #print "New image ==========================="
                img_soup_arr = self.soup.findAll('img', {'src': img_dtl.src})
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
                    
                    if img_soup_p.name == 'a' and not img_dtl.html_link:
                        self.stats.Incr("found_link_in_" + str(i))
                        
                        href = img_soup_p.get('href')
                        if (href is None) or (href in ["None",  ""] or href.startswith("javascript:") or href.startswith("#")):
                            continue 
                        
                        href = href.encode('utf-8')
                        
                        url_info_new = url_info.UrlInfo({
                                                           "parent_url": self.url,
                                                           "url": href,
                                                           "type": url_info.UrlInfoTypeEnum.unknown,
                                                           "initiator_type": url_info.UrlInfoInitiatorTypeEnum.image,
                                                           "initiator_id": img_dtl.id,
                                                           "depth": 0,
                                                           "depth_max": 1,
                                                           "crwl_curr": self.url_info.crwl_curr,
                                                           })
                        
                        self.image_links.append(url_info_new)
                        
                        img_dtl.html_link = url_info_new.url
                        if "doubleclick" in img_dtl.html_link:
                            img_dtl.html_adv = image_details.AdvertisersEnum.doubleclick
                            self.stats.Incr("found_adv_" + image_details.AdvertisersEnum.doubleclick.name)
                    
                    text = self.text_from_soup(img_soup_p).strip()
                    if text and not hasattr(img_dtl, 'text'):
                        img_dtl.html_text = text
                        self.stats.Incr("found_text_in_"+str(i))
                        
                    img_soup_p = img_soup_p.parent
                        
                #print(str(index) + ": " + ', '.join("%s: %s" % item for item in vars(img_dtl).items()) + "'." )
            except: 
                log.exception("")
                continue

    def extract_website_info(self):
        
        ext_keywords = extract_keywords.ExtractKeywords({})
        ext_keywords.extract_keywords(html_decoded_text = self.html_source)
        
        self.url_info.extract_info = dict()
        self.url_info.extract_info["page_title"] = ext_keywords.page_title.encode('ascii', 'ignore')
        self.url_info.extract_info["metatag_keywords"] = ext_keywords.page_meta_keywords.encode('ascii', 'ignore')
        self.url_info.extract_info["metatag_desription"] = ext_keywords.page_meta_desription.encode('ascii', 'ignore')
        self.url_info.extract_info["page_keywords"] = list(ext_keywords.keywords)
        
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
        if soup != None:
            texts = soup.findAll(text=True)
        else:
            texts = self.soup.findAll(text=True)
        visible_texts = filter(self.tag_visible, texts)  
        return u" ".join(t.strip() for t in visible_texts)        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    