'''
Created on Feb 19, 2018

@author: eliad
'''

from PIL import Image

if __name__ == '__main__':
    pass

#image_file_path = "/home/eliad/Downloads/home2-videoLarge.gif"
image_file_path = "/home/eliad/python/image_crawler/images_db/nytimes.com/www.nytimes.com/2018_02_19-00/images/00stagesSS-slide-4CEZ-largeHorizontal375.jpg"

with Image.open(image_file_path) as im:
    try:
        im.seek(1)
    except EOFError:
        isanimated = False
    else:
        isanimated = True
        
        
    is_animated = im.is_animated
    
    
print "END !!!"

