#add async
BASE_URL = 'https://ia800907.us.archive.org/24/items/video_annotations_test/' #'https://ia800901.us.archive.org/13/items/Jopik_YT_Annotation_Collection/' #update this to the actual item to be used
LAST_UPDATE_TIME = -1

if BASE_URL.endswith('/'):
    BASE_URL = BASE_URL[:-1]

import requests
dlsession = requests.session()

from requests_xml import XMLSession
session = XMLSession()

retrieval_url =  BASE_URL + '/' + BASE_URL.split('/')[-1] + '_files.xml'

r = session.get(retrieval_url)
item = r.xml.xpath('//files//file', first=False)

iteminfo = []
MTIME_LIST = []

from filehash import FileHash

for element in item:
    try:
        mtime = int(element.xpath('//mtime', first=True).text)
    except:
        mtime = 0
    try:
        crc32 = str(element.xpath('//crc32', first=True).text).upper().lstrip('0') #try to match the format returned by FileHash
    except:
        crc32 = None
    MTIME_LIST.append(mtime)
    iteminfo.append({'name': element.attrs['name'], 'mtime': mtime, 'crc32': crc32})

for itemdata in iteminfo:
    if itemdata['mtime'] > LAST_UPDATE_TIME:
        #https://stackoverflow.com/questions/12517451/automatically-creating-directories-with-file-output
        import os
        import errno
        if not (os.path.exists(os.path.dirname(itemdata['name'])) or os.path.dirname!=''):
            try:
                os.makedirs(os.path.dirname(itemdata['name']))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        #end SO code
        with open(itemdata['name'], 'wb') as f:
            f.write(dlsession.get(BASE_URL + '/' + itemdata['name']).content)
        #verification, exclude the index file as no crc32 is provided
        if str(FileHash('crc32').hash_file(itemdata['name'])) != str(itemdata['crc32']) and itemdata['name'] != BASE_URL.split('/')[-1] + '_files.xml':
            print(itemdata['name']+' failed verification.') #add redownload?
            #print(itemdata['crc32'], FileHash('crc32').hash_file(itemdata['name']))


LAST_UPDATE_TIME = max(MTIME_LIST) #save this in a config file
