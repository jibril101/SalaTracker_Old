from math import sin, cos, sqrt, atan2, radians
import json
import sys
import datetime as dt 

# approximate radius of earth in km
R = 6373.0

# from https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude
def distanceBtweenTwoGpsPoints(lat1, lon1, lat2, lon2):

    lat1 = radians(float(lat1))
    lon1 = radians(float(lon1))
    lat2 = radians(float(lat2))
    lon2 = radians(float(lon2))

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance

# returns msjd info from db
def FindTheClosestMsjdToThisGpsPoint(deviceGps):

    minDis = 999999999
    closestMsjd = ''

    # make array of names and gps from db
    db = open('./db.json','r')
    dataBase = json.load(db)
    db.close()

    # compare the device gps to each msjd gps points
    for msjdName in dataBase.keys():
        #msjd gps
        lat1 = dataBase[msjdName]['gpsCord']['lat']
        lon1 = dataBase[msjdName]['gpsCord']['log']
        
        #devce gps
        curr_lat = deviceGps['lat'] 
        curr_lon = deviceGps['lon']

        #find distance
        distance = distanceBtweenTwoGpsPoints(lat1 , lon1, curr_lat , curr_lon )
        
        # get min distance and the name of sjd with min distance 
        minDis = min(distance, minDis)
        if minDis == distance:
            closestMsjd = msjdName

    return  dataBase[closestMsjd] 

def GetDeviceCurrentTime():
    #get local time ; later will be UCT time of device
    timeNow = dt.datetime.now()
    return int(timeNow.hour), int(timeNow.minute)
    
def FindTheNextIqamaTimeFroThisMsjd(msjdInfoJson):
    newMsjdInfo = ''
    # get current device time from gps points
    currHour , currMin = GetDeviceCurrentTime() # format is "hh:mm"
    
    # compare times
    newMsjdInfo = msjdInfoJson.copy()
    newMsjdInfo['nextIqama'] = ''
    for prayerName in list(msjdInfoJson)[3:]: 
        # get time to compare against
        iqama = newMsjdInfo[prayerName]['iqama']
        iqamaList = str(iqama).split(':')
        iqamaHour = int(iqamaList[0])
        iqamaMin =  int(iqamaList[1])
        # compare time to msgd iqama times to get the next time
        if (currHour < iqamaHour) or ((currHour == iqamaHour) and (currMin < iqamaMin)):
            newMsjdInfo['nextIqama'] =  f'{iqamaHour}:{iqamaMin}'
            #print(f'{currHour}:{currMin}  <', newMsjdInfo['nextIqama'] , prayerName)
            break
    
    #case of after Isha times assigne fajr time of the same day
    # need to improve by checking if fajr is changing next day or not
    if newMsjdInfo['nextIqama'] == '':
        newMsjdInfo['nextIqama'] = newMsjdInfo['Fajr']['iqama']
        #print(f'{currHour}:{currMin}  <', newMsjdInfo['nextIqama'] , 'Fajr')
    
    # return next iqama time
    return newMsjdInfo


#Begin ============================================================
deviceGpsJsonFromat = {"lat" : sys.argv[1] , "lon" : sys.argv[2]}
closestMsjdInfo = FindTheClosestMsjdToThisGpsPoint(deviceGpsJsonFromat)
closestMsjdInfoWithNextPrayer = FindTheNextIqamaTimeFroThisMsjd(closestMsjdInfo)
print(closestMsjdInfoWithNextPrayer)
