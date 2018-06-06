'''
Created on May 13, 2018

@author: eliad
'''

import os
import logging
from PIL import Image
import shutil

from elasticsearch import Elasticsearch
from image_match.elasticsearch_driver import SignatureES

# https://cloudinary.com/blog/image_optimization_in_python


##################
# Stats
##################
import time # Measure execution time
import json
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
        
    def AddVal(self, key, val):
        if key in self.stats:
            self.stats[key] += val
        else:
            self.stats[key] = val

    def GetVal(self, key):
        return self.stats[key]
    
    def add_stats(self, stats_new, prefix=None):
        stats_dic_new = stats_new.Get()
        if not prefix:
            self.stats.update(stats_dic_new)
        else:
            for key, value in stats_dic_new.iteritems():
                self.Add(prefix + "_" + key, value)
    
    def Print(self, pretty=True):
        stats_str = ""
        if pretty:
            stats_str = json.dumps(self.Get(), sort_keys=True, indent=4)
        else:
            stats_str = json.dumps(self.Get(), sort_keys=True)
        
        return stats_str

#### Tasks
# Check how much space was saved

# logging
LOGGING_FILE_NAME = "myapp.log"
loggingFormat = '%(asctime)-15s|%(levelname)s|%(name)s|%(funcName)s|%(lineno)d|%(message)s'
logging.basicConfig(level=logging.WARNING, format=loggingFormat, filename=LOGGING_FILE_NAME)

log = logging.getLogger(__name__)


# globals
conf_source_folder = "/home/eliad/python/image_crawler/images_sig_db/"
conf_dst_folder = "/home/eliad/python/image_crawler/images_sig_db_comp/"

conf_dst_folder_clear = True
#conf_images_comp_num = 100
#conf_comp_param = {"pil_quality": 0, "pil_resize": (0, 0), "pil_convert_jpg": 0 }


class ImageCompDetails:
    
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst
        
    def is_change_dim(self):
        if self.dst_dim[0] != self.src_dim[0] or self.dst_dim[1] != self.src_dim[1]:
            return True
        
        return False
    
    def is_change_ext(self):
        old_ext = os.path.splitext(self.src)[1]
        new_ext = os.path.splitext(self.dst)[1]
        
        if (old_ext != new_ext):
            return True
        
        return False
    
    
def images_search(img_comp_dtl_arr, stats):
    es = Elasticsearch()
    ses = SignatureES(es)
    
    image_cnt = 0

    for img_comp_dtl in img_comp_dtl_arr:
        
        if (image_cnt % 50) == 0:
            log.warning("image_cnt='%d'.", image_cnt)
        
        #log.warning("img_comp_dtl.src='%s'.", img_comp_dtl.src)
        src_result = ses.search_image(img_comp_dtl.src, all_orientations=True)
        dst_result = ses.search_image(img_comp_dtl.dst, all_orientations=True)
        
        src_res_len = len(src_result)
        dst_res_len = len(dst_result)

        stats.Incr("search_src_res_len_" + str(src_res_len))
        stats.Incr("search_dst_res_len_" + str(dst_res_len))
        if src_res_len != dst_res_len:
            log.warning("src_res_len='%d' != dst_res_len='%d'.", src_res_len, dst_res_len)
            stats.Incr("search_res_diff_len")
            
        if src_res_len == 0 or dst_res_len == 0:
            log.warning("Empty: src_res_len='%d', dst_res_len='%d'. img_comp_dtl.src='%s', img_comp_dtl.dst='%s'", src_res_len, dst_res_len, img_comp_dtl.src, img_comp_dtl.dst)
            stats.Incr("search_res_empty")
        
        if src_res_len > 300 or dst_res_len > 300:
            log.warning("Big: src_res_len='%d', dst_res_len='%d'. img_comp_dtl.src='%s', img_comp_dtl.dst='%s'", src_res_len, dst_res_len, img_comp_dtl.src, img_comp_dtl.dst)
            stats.Incr("search_res_big")
        
        for rec in src_result:
            #print(rec["dist"])
            if rec["dist"] == 0.0:
                found_rec = rec
                break
        if found_rec is None:
            log.error("No match with dist '0'. we have a problem !!! ")
            stats.Incr("search_no_src_match")
        
        dst_result_dict = dict()
        for dst_rec in dst_result:
            dst_result_dict[dst_rec["id"]] = dst_rec
            
        for idx in range(src_res_len):
            src_rec = src_result[idx]
            rec_id = src_rec["id"]
            if rec_id in dst_result_dict:
                stats.Incr("search_found")
                #dist_diff = src_rec["dist"] - dst_result_dict[rec_id]["dist"] 
                #log.warning("dist_diff='%lf'.", dist_diff)
            else:
                stats.Incr("search_not_found")
                
        for idx in range(src_res_len):
            src_rec = src_result[idx]
            rec_id = src_rec["id"]
            if idx < len(dst_result):
                if rec_id != dst_result[idx]["id"]:
                    stats.Incr("search_not_same_oreder")
                    break
                
        image_cnt += 1
                    
def image_comp(image_source_file_path, image_dst_file_path, comp_param):
    
    try:
        img_comp_dtl = ImageCompDetails(image_source_file_path, image_dst_file_path, )
        
        img_comp_dtl.src_size = os.stat(img_comp_dtl.src).st_size
    
        time_start = time.time()
        
        img = Image.open(img_comp_dtl.src)
        img_comp_dtl.src_dim = img.size
        
        if comp_param["pil_resize"][0] == 0 and comp_param["pil_convert_jpg"] == 0 and comp_param["pil_quality"] == 0:
            shutil.copyfile(img_comp_dtl.src, img_comp_dtl.dst)
        else:
            
            
            pil_resize = comp_param["pil_resize"]
            if pil_resize[0] != 0:
                img.thumbnail(pil_resize, Image.ANTIALIAS)
                
            if comp_param["pil_convert_jpg"] != 0:
                img_comp_dtl.dst = os.path.splitext(img_comp_dtl.dst)[0] + '.jpg'
                rgb_img = img.convert('RGB')
                img = rgb_img 
            
            #set quality= to the preferred quality.
            #I found that 85 has no difference in my 6-10mb files and that 65 is the lowest reasonable number
            if comp_param["pil_quality"] != 0:
                img.save(img_comp_dtl.dst, optimize=True, quality=comp_param["pil_quality"])
            else:
                img.save(img_comp_dtl.dst)
                
            
            
        img_comp_dtl.comp_time = time.time() - time_start
            
        img_comp_dtl.dst_size = os.stat(img_comp_dtl.dst).st_size
        img_comp_dtl.dst_dim = img.size
        
        
    except:
        log.exception("image_source_file_path='%s', image_dst_file_path='%s'.", image_source_file_path, image_dst_file_path)
        return None
        
        
    return img_comp_dtl
        
        
def images_folder_comp(src_fl, dst_fl, images_comp_num = None, dst_folder_clear = True, comp_param = None):
    if not src_fl or not os.path.exists(src_fl):
        log.error("No src_fl '{0}'.", src_fl)
        return None
    
    if dst_folder_clear:
        shutil.rmtree(dst_fl)
    
    if not os.path.exists(dst_fl):
        try:
            os.makedirs(dst_fl)
        except:
            log.exception("Fail to create dst_fl {0}.", dst_fl)
            return None
    
    img_comp_dtl_arr = []    
    image_cnt = 0
    
    for image_filename in os.listdir(src_fl):
        
        if images_comp_num and image_cnt >= images_comp_num:
            break
        
        if (image_cnt % 50) == 0:
            log.warning("image_cnt='%d'.", image_cnt)
            
        
        image_source_file_path = src_fl + image_filename
        image_dst_file_path = dst_fl + "comp_" + image_filename
        #log.warning("image_cnt='%3d', image_source_file_path='%s'.", image_cnt, image_source_file_path)
        img_comp_dtl = image_comp(image_source_file_path, image_dst_file_path, comp_param)
        if img_comp_dtl:
            img_comp_dtl_arr.append(img_comp_dtl)
    
        image_cnt += 1
        
    return img_comp_dtl_arr


def images_stats(img_comp_dtl_arr, comp_param, stats):
    
    stats.AddVal("_conf_comp_param_pil_resize_w", comp_param["pil_resize"][0])
    stats.AddVal("_conf_comp_param_pil_resize_h", comp_param["pil_resize"][1])
    stats.AddVal("_conf_comp_param_pil_convert_jpg", comp_param["pil_convert_jpg"])
    stats.AddVal("_conf_comp_param_pil_quality", comp_param["pil_quality"])

    for img_comp_dtl in img_comp_dtl_arr:
        stats.AddVal("_src_size_aggr", img_comp_dtl.src_size)
        stats.AddVal("_dst_size_aggr", img_comp_dtl.dst_size)
        stats.AddVal("_comp_time_aggr", img_comp_dtl.comp_time)
        
        if img_comp_dtl.is_change_dim():
            stats.Incr("_change_dim")
            
        if img_comp_dtl.is_change_ext():
            stats.Incr("_change_ext")
            
    img_comp_dtl_arr_len = len(img_comp_dtl_arr)
    size_diff_percent = ((stats.GetVal("_src_size_aggr") - stats.GetVal("_dst_size_aggr")) /  float(stats.GetVal("_src_size_aggr"))) * 100
        
    stats.AddVal("_img_comp_dtl_arr", img_comp_dtl_arr_len)
    stats.AddVal("_size_diff_percent", size_diff_percent)

            
if __name__ == '__main__':
    
    log.warning("Start.")
    
    img_comp_dtl_arr = []
    
    if False:
        pil_quality = 0
        pil_resize = (200, 200)
        pil_convert_jpg = 1
        comp_param = {"pil_quality": pil_quality, "pil_resize": pil_resize, "pil_convert_jpg": pil_convert_jpg }
        
        image_filename = "image_f3dc0d20-55e5-44a3-b7cc-3ded17c7061d.png"
        image_source_file_path = conf_source_folder + image_filename
        image_dst_file_path = conf_dst_folder + "comp_" + image_filename
        
        img_comp_dtl = image_comp(image_source_file_path, image_dst_file_path, comp_param)
        
    
    if True:
        images_comp_num = 50000
        for pil_quality in [0, 50, 70, 90]:
            for pil_resize in [(0, 0), (200, 200), (400, 400), (600, 600)]:
                for pil_convert_jpg in [0, 1]:
                    
                    if pil_quality == 0 and pil_resize[0] == 0 and pil_resize[1] == 0 and pil_convert_jpg == 0:
                        continue
                    if pil_quality == 0 and pil_resize[0] == 0 and pil_resize[1] == 0 and pil_convert_jpg == 1:
                        continue
                    if pil_quality == 0 and pil_resize[0] == 200 and pil_resize[1] == 200 and pil_convert_jpg == 0:
                        continue
                    
                    source_folder = "/home/eliad/python/image_crawler/images_sig_db/"
                    dst_folder = "/home/eliad/python/image_crawler/images_sig_db_comp/"

                    comp_param = {"pil_quality": pil_quality, "pil_resize": pil_resize, "pil_convert_jpg": pil_convert_jpg }
                    img_comp_dtl_arr = images_folder_comp(source_folder, dst_folder, images_comp_num, conf_dst_folder_clear, comp_param)
        
                    stats = Stats()                    
                        
                    # Search images
                    log.warning("Search images.")
                    images_search(img_comp_dtl_arr, stats)
                    
                    # Summarize stats 
                    images_stats(img_comp_dtl_arr, comp_param, stats)
                    log.warning(stats.Print())
                    
    log.warning("End.")
    
    
    # check all png, gif
    # Add ES
    # check on 10000 images
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    