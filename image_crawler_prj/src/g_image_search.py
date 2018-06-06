'''
Created on Jan 11, 2018

@author: eliad
'''
import json
import logging

from pyvirtualdisplay import Display # Chrome headless
from selenium import webdriver 


# Local lib
import common
from object_model import g_image_details

log = logging.getLogger(__name__)


class GImageSearch(object):
    '''
    classdocs
    '''


    def __init__(self, params = "{}"):
        '''
        Constructor
        '''
        self.stats = common.Stats()
        
        self.driver_headless = False
    
    
    def search(self, search_term = "", g_page_results_max = 20):
        
        if not search_term:
            log.error("search_term is empty !!!")
            return
        
        # Selenium
        url = "https://images.google.com/"
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
                        
        '''
        Load image to google reverse image
        '''
        # Press on camera icon in search row
        element_qbi = driver.find_element_by_id("qbi")
        element_qbi.click()
        
        if image_url:
           
            element_qbui = driver.find_element_by_id("qbui")
            element_qbui.send_keys(image_url)
            
            try:
                element_search_by_image = driver.find_element_by_xpath("//td[@id='qbbtc']/input[1]")
            except Exception as e:
                print "Exception:", e
            
            element_search_by_image.click()
    
        elif image_path:
            # switch to download image path tab
            driver.execute_script("google.qb.ti(true);return false")
            
            element_qbui = driver.find_element_by_id("qbfile")
            element_qbui.send_keys(image_path)
            
            
        g_img_dtl = g_image_details.GImageDetails()
            
        # get Best guess for this image
        try:
            element_best_guess = driver.find_element_by_class_name("_gUb")
            g_img_dtl.best_guess = element_best_guess.text.encode("utf-8")
            print "g_best_guess='{0}'.".format(g_img_dtl.best_guess)
        except Exception as e:
            print "Exception:", e
            
            
        # get results
        g_img_dtl.pages = []
        g_img_dtl.images = []
        try:
            while True:
                results = driver.find_elements_by_class_name("g")
                print "Total results:", len(results), "\n"
                for result in results:
                    
                    # first one is not a link, its the similar images
                    elem_id = result.get_attribute("id")
                    if elem_id and elem_id == "imagebox_bigimages":
                        img_results = result.find_elements_by_tag_name('img')
                        print "Total image results:", len(img_results), "\n"
                        for img_result in img_results:
                            g_image_res = g_image_details.GImageResult()
                            g_image_res.page_src = img_result.get_attribute("title")
                            
                            # Add similar images to object
                            g_img_dtl.images.append(g_image_res)
                            
                        # finished getting images move to next result
                        continue
                    
                    g_page_res = g_image_details.GPageResult()
        
                    try:
                        rc = result.find_element_by_class_name("rc")
                    except Exception as e:  
                        print "Exception:", e
                        continue
                    
                    try:
                        elem_img = result.find_element_by_tag_name("img")
                        g_page_res.img_src = elem_img.get_attribute('src')
                    except Exception as e:  
                        print "Exception:", e
                        # if not image its not a matching image
                        continue
                    
                    elem_a = rc.find_element_by_tag_name('a')
                    g_page_res.href = elem_a.get_attribute('href')
                    g_page_res.title = elem_a.text
                        
                    try:
                        elem_desc = result.find_element_by_class_name("st")
                        g_page_res.desc = elem_desc.text
                    except Exception as e:  
                        print "Exception:", e

                    # Add page result to object
                    g_img_dtl.pages.append(g_page_res)
                    
                if len(g_img_dtl.pages) < g_page_results_max:
                    elem_next = driver.find_element_by_id("pnnext")
                    elem_next.click()
                else:
                    break
    
    
        except Exception as e:
            print "Exception:", e
            
        
        # Release driver
        driver.quit()
        self.stats.TimeEnd("_BrowserDriverTime")
 

        self.g_img_dtl = g_img_dtl
            
            
            
            
if __name__ == "__main__":
    print("Running GReverseImageSearch code example.")            
    g_reverse_image_search = GReverseImageSearch()
    
    g_reverse_image_search.search(image_url = "http://feedbox.com/wp-content/uploads/2018/01/what-you-need-to-do-because-of-flaws-in-computer-chips-1080x675.jpg") 
    print("Statistics '"+json.dumps(g_reverse_image_search.stats.Get(), sort_keys=True, indent=4)+"'.")
    
    g_reverse_image_search.search(image_path = "/home/eliad/Desktop/6hcC4GABvr5azk5enelM.jpg")
    print("Statistics '"+json.dumps(g_reverse_image_search.stats.Get(), sort_keys=True, indent=4)+"'.")         
