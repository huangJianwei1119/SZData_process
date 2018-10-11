import os
import time as Time
from math import *
import datetime

utc_format='%Y-%m-%dT%H:%M:%S'
recordID = 0
cardID = 1
tradeType = 2 #tradeType=21/22 means subway on/off, 1 means bus on
time = 3
TrafficLine = 4
station = 5
lon=6
lat=7

def calcDistance(lat1, lon1, lat2, lon2):
    #Calculate the great circle distance between two points  on the earth (specified in decimal degrees)
    EARTH_RADIUS = 6378.137 #单位为KM
    # 将十进制度数转化为弧度
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine公式
    dlon = lon1 - lon2
    dlat = lat1 - lat2
    s = 2 * asin(sqrt(pow(sin(dlat / 2), 2) + cos(lat1) * cos(lat2) * pow(sin(dlon / 2), 2)))
    s = s * EARTH_RADIUS
    #s = round(s * 10000) / 10000;
    return s
def IdentifyBusTrip(Trips):
    line1=Trips[0]
    line2=Trips[1]
    duration = '1800'
    transfer = '0'
    typ = '1'
    start_time = line1[time]
    end_time = line1[time]  # need to caculated
    start_station = line1[station]
    start_lon = line1[lon]
    start_lat = line1[lat]
    end_station = line2[station]
    end_lon = line2[lon]
    end_lat = line2[lat]
    Trip = line[cardID] + ',' + duration + ',' + transfer + ',' + typ + ',' + start_time + ',' + end_time + ',' + start_station + ',' + start_lon + ',' + start_lat + ',' + end_station + ',' + end_lon + ',' + end_lat
    return Trip
def IdentifySubwayTrip(Trips):
    line1=Trips[0]
    line2=Trips[1]
    dt1 = Time.strptime(line1[time][:19], utc_format)
    dt2 = Time.strptime(line2[time][:19], utc_format)
    dt = abs(int(Time.mktime(dt1) - Time.mktime(dt2)))
    duration=str(dt)
    if line1[TrafficLine] != line2[TrafficLine]:
        transfer = '1'
    else:
        transfer = '0'
    typ='0'
    start_time = line1[time]
    end_time = line2[time]
    start_station = line1[station]
    start_lon = line1[lon]
    start_lat = line1[lat]
    end_station = line2[station]
    end_lon = line2[lon]
    end_lat = line2[lat]
    Trip = line[cardID] + ',' + duration + ',' + transfer + ',' + typ + ',' + start_time + ',' + end_time + ',' + start_station + ',' + start_lon + ',' + start_lat + ',' + end_station + ',' + end_lon + ',' + end_lat
    return Trip

def IdentifyTrips(Userdata):
    # TripsResult=[]
    print('Identify trips about user',Userdata[0][cardID])
    Trips=[]

    if len(Userdata)>3:
        T=[]
        L=len(Userdata)
        i=0
        while i<L-1:
            line1=Userdata[i]
            line1TradeType = line1[tradeType]
            T.append(line1)
            if line1TradeType=='21':
                line2=Userdata[i+1]
                line2TradeType=line2[tradeType]
                if line2TradeType=='22':
                    T.append(line2)
                    Trip=IdentifySubwayTrip(T)
                    Trips.append(Trip)
                    T=[]
                    i=i+2
                else:
                    #if Error,drop this user
                    #i=i+1
                    return None
            elif line1TradeType=='1':
                line2=Userdata[i+1]
                T.append(line2)
                Trip=IdentifyBusTrip(T)
                Trips.append(Trip)
                T=[]
                i=i+1
            else:
                #if Error,Drop this user
                #i=i+1
                return None
        return Trips
    else:
        return None

def Loaddata(file,name,mydata):
    try:
        data=open(os.path.join(file,name),'r',encoding='utf-8')
        for line in data.readlines():
            line=line.strip('\n')
            line=line.replace('NA','0')
            line=line.replace('None','1')
            line=line.split(',')
            mydata.append(line)
        data.close()
        return mydata
    except IOError as e:
        print(e)

if __name__ == '__main__':
    #'recordID','cardID','tradeType','time','line','station'
    file=r'E:\SZTransData\SmartCard\Allday\Subway_busAllDay.csv'
    ouputfile=r'E:\SZTransData\SmartCard\TripIdentify'
    ouputname='users_trip_chain_dropError.csv'
    nameList1=[]
    nameList2=[]
    nameList3=[]
    for i in range(0,200):
        if i<10:
            name='part-0000'+str(i)+'-0b6c6f6b-35cd-4d56-9aa8-7aefe52395ae-c000.csv'
            nameList1.append(name)
        elif 10<=i and i<100:
            name='part-000'+str(i)+'-0b6c6f6b-35cd-4d56-9aa8-7aefe52395ae-c000.csv'
            nameList2.append(name)
        else:
            name='part-00'+str(i)+'-0b6c6f6b-35cd-4d56-9aa8-7aefe52395ae-c000.csv'
            nameList3.append(name)

    #defien a trip
    # @cardId is a User
    # @duration is trip duration
    # @transfer means if this trip transfer or not, 0 means not, 1 means yes
    # @frequence means this trip frequnce in dataset
    # @type means trip type, 0 means subway, 1 means bus
    head='cardId,duration,transfer,type,start_time, end_time, start_station, start_lon, start_lat, end_station, end_lon, end_lat'

    UserTData=[]
    txt_file=open(os.path.join(ouputfile,ouputname),'w',encoding='utf-8')
    txt_file.write(head+'\n')

    namelist=nameList1+nameList2+nameList3

    mydata2=[]

    for i in range(0,200):
        mydata=[]
        name=namelist[i]
        mydata=Loaddata(file,name,mydata)
        mydata=mydata2+mydata
        lenth=len(mydata)
        print('Load dataset ',i)
        j=0
        flag=1
        while flag==1:
            #Extract user's trajectory
            line=mydata[j]
            if len(UserTData)==0:
                UserTData.append(line)
                j=j+1
            elif (UserTData[len(UserTData)-1])[cardID]==line[cardID]:
                UserTData.append(line)
                j=j+1
            else:
            #Extract user's Trips
                Trips=IdentifyTrips(UserTData)
                if Trips is not None:
                    print('Writing Trip of user:', UserTData[0][cardID])
                    for Trip in Trips:
                        #Output User's trips
                        txt_file.write(Trip+'\n')
                UserTData=[]
                UserTData.append(line)
                j=j+1
            if (lenth - j) < 100 and i != 200:
                del mydata2
                mydata2 = []
                for k in range(lenth - 100, lenth):
                    line2 = mydata[k]
                    mydata2.append(line2)
                flag = 0
        flag = 1
        del mydata
    txt_file.close()

    print('Finish!')