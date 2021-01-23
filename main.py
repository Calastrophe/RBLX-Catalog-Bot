from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
from tqdm import tqdm
from urllib.parse import urljoin
import urllib.request
import time
import requests
import json
import re
import urllib3
## declare libraries

## Made by Calastrophe#5752 // github.com/Calastrophe


def get_all_images(imagelist): ## This is used to retrieve all of the images on the page of each library page - in turn giving us the image URL to the template.
    templateurls = []
    try:
        for imageurl in imagelist:
            soup = bs(requests.get(imageurl).content, 'html.parser') ## Parse the content on the page for images

            for img in tqdm(soup.find_all('img'), 'Extracting images'): ## Extract images
                img_url = img.attrs.get('src')

                if not img_url: ## Useless defintion? Required?
                    continue

                img_url = urljoin(imageurl, img_url) ## Join URLs together
                if '.gif' not in img_url: ## The templates are not .gif
                    templateurls.append(img_url)
    except Exception as e:
        print(e)

    return templateurls

def retrieveimage(templateurls): ## Used to retrieve the image and save it from the URL that is inputted.
    global count
    u_templateurls = []

    for templateurl in templateurls:

        if templateurl not in u_templateurls:
            u_templateurls.append(templateurl)
            count += 1
            counter = str(count)
            urllib.request.urlretrieve(templateurl, counter + '.png') ## Saves each one with a number, some might not save due to deletion.


def next_page(driver): ## Used to navigate to the next page
    try:

        driver.find_element_by_class_name('icon-next').click()
        driver.implicity_wait(10)

    except:

        pass

def down_and_up(assetids): ## Using the AssetDelivery API - we can obtain the XML file to locate the image.
    xmllist = []
    try:
        for assetid in assetids:
            r = requests.get('https://assetdelivery.roblox.com/v1/assetId/' + assetid)
            xml = json.loads(r.text)
            xmllist.append(xml['location'])
    except:
        pass
    return xmllist

def XMLtoURL(xmllist): # Using that XML file - we can parse it and find the library URL for the image.
    imageids = []
    imgcount = 0

    for xml in xmllist:
        
        try:
            imgcount += 1
            r = urllib3.PoolManager().request('GET', xml) ## Obtain URL For parsing
            data = str(r.data)
            start = '<url>' ## To navigate the XML file to where we need to be
            end = '</url>'
            s = data
            imgurl = (s.split(start))[1].split(end)[0] ## Grab just the URL
            imgid = str(''.join(filter(str.isdigit, imgurl))) ## Grab just the digits
            imgidurl = 'https://www.roblox.com/library/' + imgid ## Attach digits to the URL we need
            imageids.append(imgidurl) 
        except Exception as e:
            print(e)

    return imageids



def setup(driver): ## Website we are targetting

    driver.get("https://www.roblox.com/catalog?Category=3&Subcategory=12")
    time.sleep(3)

    return driver

def web_driver(): ## Simple set up

    options_driver = Options()
    options_driver.add_argument("--log-level=3")

    driver = webdriver.Chrome(executable_path="chromedriver.exe", options=options_driver)

    return driver


number = int(input("How many pages do you want copied: "))
count = 0 ## Image name
u_links = [] ## To not reuse
assetids = [] ## To make streamline
driver = web_driver()
driver = setup(driver)

for _ in range(number):
    try:
        links = driver.find_elements_by_xpath("//a[@href]") #grab all the links

        for link in links:
            try:
                link = link.get_attribute('href')

                if "roblox.com/catalog/" in link and link not in u_links: ## needs to have catalog in link
                    u_links.append(link)
                    assetid = re.findall('\d+', link) #retrieves the assetids
                    if assetid[0] != '1':
                        assetids.extend(assetid)

            except Exception as e:
                print(e)
                
                pass

    except Exception as e:
        print(e)

        pass
    
    xmllist = down_and_up(assetids) ## grab XML
    print('got the xml')

    imagelist = XMLtoURL(xmllist) ## parse XML
    print('got the image url')

    templateimages = get_all_images(imagelist) ## get images from URL
    print('got all the images')

    retrieveimage(templateimages) ## download images
    print('images recieved...')

    assetids = [] ## to complete the loop
    
    next_page(driver)
    time.sleep(4) ## loading the page



