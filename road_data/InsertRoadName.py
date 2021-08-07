import pymysql as pymysql
import os
from tqdm import tqdm

def connectDB():
    print("DB 연결 시작")
    # DB 연결
    ip = '115.68.179.37'
    id = 'root'
    pw = 'ehdgnl8940!'
    db = 'Wolf'
    charset = 'utf8'
    db_connect=pymysql.connect(host=ip,user=id,password=pw,db=db,charset=charset)
    db_cursor=db_connect.cursor()
    print("DB 연결 끝")
    return db_connect, db_cursor

# def getRegionData():
#     print("지역 데이터 로드 시작")
#     regionDataList = []
#     for file in tqdm(os.listdir('road_data')):
#         if 'txt' in file:
#             regionDataList.append(str(file).replace(".txt",""))
#     print("지역 데이터 로드 끝")
#     return regionDataList
#
# def insertRegionData(dbCursor, regionDataList):
#     print("데이터 추가 시작")
#     for regionData in tqdm(regionDataList):
#         sql = "INSERT INTO `Region` (region) VALUES (%s);"
#         dbCursor.execute(sql,(regionData))
#     dbConnect.commit()
#     print("데이터 추가 끝")

# def selectRegionData(dbCursor):
#     sql = "select region from `Region`"
#     dbCursor.execute(sql)
#     regionDataList = [item[0] for item in dbCursor.fetchall()]
#     return regionDataList

def insertRoadNameData(dbCursor):
    print("도로명 주소 추가시작")

    for file in tqdm(os.listdir('road_data')):
        if 'txt' in file:

            region = str(file).replace(".txt","")
            print(region)
            sql = "select `idx` from `Region` where region = %s"
            dbCursor.execute(sql, (region))
            regionIdx = dbCursor.fetchone()[0]

            roadNameList: list = []
            f = open("road_data/" + file, 'r')
            while True:
                line = f.readline()
                if not line:
                    break
                roadNameList.append(str(line).split('|')[5])

            new_list: list = []
            for v in roadNameList:
                if v not in new_list:
                    new_list.append(v)

            for roadName in new_list:
                sql = "INSERT INTO `RoadName` (region_idx, road_name) VALUES (%s, %s);"
                dbCursor.execute(sql,(regionIdx, roadName))
            dbConnect.commit()

    print("도로명 주소 추가끝")

if __name__ == '__main__':
    dbConnect, dbCursor = connectDB()
    insertRoadNameData(dbCursor)
    dbConnect.close()


