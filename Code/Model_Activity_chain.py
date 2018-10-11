import os
import time as Time
from math import *
import datetime

utc_format='%Y-%m-%dT%H:%M:%S'
cardID = 0
duration=1
transfer = 2 #tradeType=21/22 means subway on/off, 1 means bus on
mode=3
start_time = 4
end_time = 5
start_station=6
start_lon=7
start_lat=8
end_station=9
end_lon=10
end_lat=11


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

def IdentifyActivity(Last_Trip,Next_Trip):
    type_num='4'
    dt1=Time.strptime(Last_Trip[end_time][0:19],utc_format)
    dt2=Time.strptime(Next_Trip[start_time][0:19],utc_format)
    Last_day=dt1[2]
    Next_day=dt2[2]
    dt = abs(int(Time.mktime(dt1) - Time.mktime(dt2)))
    Acty_duration=dt
    Last_duration=Last_Trip[duration]
    Next_duration=Next_Trip[duration]
    Acty_distance=calcDistance(float(Last_Trip[end_lat]),float(Last_Trip[end_lon]),float(Next_Trip[start_lat]),float(Next_Trip[start_lon]))
    if Acty_duration >= 28800 and Acty_duration<=57600 and Last_day != Next_day and Acty_distance<1:
        type_num='2'
    elif Acty_duration>=28800 and Acty_duration<57600 and Last_day==Next_day and Acty_distance<1:
        type_num='1'
    elif Acty_duration<=2400 and Acty_distance<1:
        type_num='3'

    Activity=Last_Trip[cardID]+','+str(Acty_duration)+','+str(Acty_distance)+','+Last_duration+','+Next_duration+','+Last_Trip[end_time]+','+Next_Trip[start_time]+','+Last_Trip[end_station]+','+Last_Trip[end_lon]+','+Last_Trip[end_lat]+','+Next_Trip[start_station]+','+Next_Trip[start_lon]+','+Next_Trip[start_lat]+','+type_num
    return Activity

def IdentifyActivitys(UserTData):
    Activitys = []
    if len(UserTData)==1:
        return None
    else:
        # print('Identify Activitys about user', UserData[0][cardID])
        L=len(UserTData)
        i=0
        while i<L-1:
            Last_Trip=UserTData[i]
            Next_Trip=UserTData[i+1]
            Activity=IdentifyActivity(Last_Trip,Next_Trip)
            Activitys.append(Activity)
            i=i+2
        return Activitys


def Loaddata(data,mydata,number):
    for i in range(0,number):
        line =data.readline()
        line=line.strip('\n')
        line=line.split(',')
        mydata.append(line)
    return mydata

if __name__ == '__main__':
    #'cardId,duration,transfer,type,start_time, end_time, start_station, start_lon, start_lat, end_station, end_lon, end_lat'
    file=r'E:\SZTransData\SmartCard\TripIdentify\users_trip_chain_dropError.csv'
    ouputfile=r'E:\SZTransData\SmartCard\TripIdentify\Users_trip_activity_chain'
    ouputname='users_activity_chain.csv'


    head='cardID,Acty_duration,Acty_distance,Last_duration,next_duration,start_time,end_time,start_station,start_lon,start_lat,end_station,end_lon,end_lat,Acty_type'

    data = open(os.path.join(file), 'r', encoding='utf-8')
    header=data.readline()
    txt_file=open(os.path.join(ouputfile,ouputname),'w',encoding='utf-8')
    txt_file.write(head+'\n')
    number=[]
    Lastnumber=11172078
    number1=1000000

    for i in range(0,100):
        number.append(number1)
    number.append(Lastnumber)
    UserTData = []
    mydata2=[]
    for i in range(0,len(number)):
        mydata=[]
        mydata=Loaddata(data,mydata,number[i])
        mydata=mydata2+mydata
        lenth=len(mydata)
        print('Load dataset part', i)
        j=0
        flag=1
        while flag==1:
            line=mydata[j]
            if len(UserTData)==0:
                UserTData.append(line)
                j=j+1
            elif (UserTData[len(UserTData)-1])[cardID]==line[cardID]:
                UserTData.append(line)
                j=j+1
            else:
                Activitys=IdentifyActivitys(UserTData)
                if Activitys is not None:
                    # print('Writing Activitys of users', UserTData[0][cardID])
                    for Activity in Activitys:
                        txt_file.write(Activity+'\n')
                UserTData=[]

            if (lenth-j)<100 and i!=len(number):
                del mydata2
                mydata2=[]
                for k in range(lenth-100,lenth):
                    line2=mydata[k]
                    mydata2.append(line2)
                flag=0
        flag=1
        del mydata

    data.close()
    txt_file.close()
    print("Finish!")
