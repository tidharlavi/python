'''
Created on Dec 3, 2017

@author: eliad
'''

#### basic firefox
#from selenium import webdriver

#browser = webdriver.Firefox()
#browser.get('http://www.ubuntu.com/')


#### headless chrome driver
from pyvirtualdisplay import Display
from selenium import webdriver
import time

from bs4 import BeautifulSoup

print("Start !!!")

start = time.time()
display = Display(visible=0, size=(800, 600))
display.start()
driver = webdriver.Chrome()
#driver = webdriver.Firefox()
#driver.get('http://www.ynet.co.il/home/0,7340,L-8,00.html')
driver.get('https://www.google.co.il/search?client=ubuntu&channel=fs&q=google+images+bitcoin&ie=utf-8&oe=utf-8&gfe_rd=cr&dcr=0&ei=I8cwWrHFDq7L8gfw4r-ABg')
print driver.title
end = time.time()
print(end - start)


images = driver.find_elements_by_tag_name('img')

img = images[5]

for i in range(0,3):
    print "================= depth '"+str(i)+"':"
    print "text = " + img.text
    for attr in ['src', 'id', 'class', 'name', 'innerHTML']:
        try:
            print attr + " = " + img.get_attribute(attr)
        except Exception:
            print "no " + attr
            
    soup = BeautifulSoup(img.get_attribute('innerHTML'), 'html.parser')
    prettyHTML=soup.prettify()
    print  prettyHTML

    img = img.find_element_by_xpath('..')

driver.quit()

print("End !!!")

## chrome 57.1123251915
## chrome headless 38.5014309883
## firefox 92.0616509914
## firefox headless 44.2865440845

