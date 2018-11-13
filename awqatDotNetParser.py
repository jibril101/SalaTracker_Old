#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat Aug  4 18:12:02 2018

@author: admin
"""

import requests
from bs4 import BeautifulSoup
import json
import datetime

site = "http://awqat.net"
sites = []

excludedMsjds = ['British Columbia - Surrey Jamea Masjid', 'British Columbia - Amir Hamza Musalla']

def GetMsjdName(soup):
    allHeadTitle = soup.find_all('head')
    name = str(allHeadTitle[0].text).rstrip().replace('\n', '')
    return name


timeToSleep = 60*60*24

# while(True):
'''
now = datetime.datetime.now()
secAfterMidnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()

if secAfterMidnight > 1:
    sleep(timeToSleep - secAfterMidnight)
'''

try:
    req = requests.get(site)
    soup = BeautifulSoup(req.content, 'html.parser')
    allOption = soup.find_all('option')

    # update db with todays time -------------
    # load the json file into a var
    with open('./db.json', 'r') as db:
        dataBase = json.load(db)
        
    # each msjd page url
    msjdsPagesURL = []
    for option in allOption[1:]:
        proxy = str(option['value']).replace('\\', '/')
        msjdsPagesURL.append(f'{site}{proxy}')
        print(f'{site}{proxy}')

    # get times for each msjd
    for msjdPageURL in msjdsPagesURL:
        msjdPageResponse = requests.get(msjdPageURL)
        soup = BeautifulSoup(msjdPageResponse.content, 'lxml')
        alltr = soup.find_all('tr')

        msjdName = GetMsjdName(soup)

        # remove tmrw's times
        pos = 0
        for tr in alltr:
            if 'Prayer' in tr.text:
                break
            pos = pos + 1

        # todays times
        print(msjdName)
        if msjdName in excludedMsjds:
            print(f'Note: {msjdName} is excluded msjd')
            continue

        for tr in alltr[pos+1:]:
            temp = str(tr.text).split()
            dic = {temp[0]: temp[1:]}
            # print(dic)

            # update Times

            iqamaHour24FormatStr = ''
            for salahName, azanIqamaList in dic.items():
                if salahName in ['Fajr', 'Duhr', 'Asr', 'Maghrib', 'Isha']:
                    if (':' in azanIqamaList[0]) and (':' in azanIqamaList[1]):
                        
                        azanList = azanIqamaList[0].split(':')
                        iqamaList = azanIqamaList[1].split(':')
                        azanHour12Format = int(azanList[0])
                        azanMin12Format = int(azanList[1])
                        iqamaHour12Format = int(iqamaList[0])
                        iqamaMin12Format = int(iqamaList[1])

                        #convert to 24 format
                        if salahName != 'Fajr':
                            # Azan hour
                            if azanHour12Format != 12:
                                azanHour24FormatStr = str(azanHour12Format + 12)
                            else :
                                azanHour24FormatStr = str(azanHour12Format )
                            #Azan min
                            azanMin24FormatStr = str(azanMin12Format)
                            #Iqama hour
                            if iqamaHour12Format != 12:
                                iqamaHour24FormatStr = str(iqamaHour12Format + 12)
                            else :
                                iqamaHour24FormatStr = str(iqamaHour12Format )
                            #Iqama min
                            iqamaMin24FormatStr = str(iqamaMin12Format )
                        else:
                            # Azan hour
                            azanHour24FormatStr = str(azanHour12Format )
                            #Azan min
                            azanMin24FormatStr = str(azanMin12Format)
                            #Iqama hour
                            iqamaHour24FormatStr = str(iqamaHour12Format )
                            #Iqama min
                            iqamaMin24FormatStr = str(iqamaMin12Format )
                            
                        dataBase[msjdName][salahName]['azan'] = f'{azanHour24FormatStr}:{azanMin24FormatStr}'

                        dataBase[msjdName][salahName]['iqama'] = f'{iqamaHour24FormatStr}:{iqamaMin24FormatStr}'
                        print(
                            f'{salahName :<{10}}', dataBase[msjdName][salahName]['azan'], dataBase[msjdName][salahName]['iqama'])


    # write updates to db
    db = open('db.json', 'w')
    db.write(json.dumps(dataBase))
    db.close()

    print('all good')
except Exception as e:
    print(e)
