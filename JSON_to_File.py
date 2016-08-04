# -*- coding: utf-8 -*-
"""
Created on Wed Aug 03 18:03:41 2016

@author: YuJia
"""

import json
from urllib import urlretrieve
pic_name = 1 
    
# find yourself a picture on an internet web page you like
# (right click on the picture, look under properties and copy the address)
	

with open("gossip.json") as json_file:
    json_data = json.load(json_file)
   
    
for i in json_data:
    if not i=={}:
        url = i["incontent_url"]
        url_type = i["incontent_url_type"]
        filename = str(pic_name)+url_type
        pic_name+=1
        urlretrieve(url, filename)
    else:
        continue
    
    
  
