'''
Created on Apr 7, 2018

@author: eliad
'''

class ImageRecord(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
        self.src = []
        
        self.path_sig_db = ""
        
        self.html_tag_title = []
        self.html_tag_alt = []
        self.html_text = []
        self.html_link = []
        
        self.keywords = []
        
        # Image count (include recurring inside image details)
        self.cnt = 0
        
        # Image details Array
        self.details_cnt = 0
        self.details = []
        
    def image_details_add(self, img_dtl):
        
        self.cnt = self.cnt + 1
        
        self.details.append(img_dtl)
        self.details_cnt = len(self.details)
        
        # Update this info only on first add
        if self.details_cnt == 1:
            self.path_sig_db = img_dtl.path_sig_db
        
        if img_dtl.src and img_dtl.src not in self.src:
            self.src.append(img_dtl.src)
        if img_dtl.html_tag_title and img_dtl.html_tag_title not in self.html_tag_title:
            self.html_tag_title.append(img_dtl.html_tag_title)
        if img_dtl.html_tag_alt and img_dtl.html_tag_alt not in self.html_tag_alt:
            self.html_tag_alt.append(img_dtl.html_tag_alt)
        if img_dtl.html_text and img_dtl.html_text not in self.html_text:
            self.html_text.append(img_dtl.html_text)
        if img_dtl.html_link and img_dtl.html_link not in self.html_link:
            self.html_link.append(img_dtl.html_link)
        