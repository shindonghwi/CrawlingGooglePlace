import random
import time
from urllib.parse import unquote_plus
from selenium.common.exceptions import NoSuchElementException
import requests
from bs4 import BeautifulSoup
import pymysql as pymysql
from selenium import webdriver
import pymysql as pymysql
import os
from tqdm import tqdm
import pyautogui
from mechanize import Browser
import threading
from selenium.webdriver.common.keys import Keys

dbConnect = None
dbCursor = None
driver = None

""" Database 연결 """


def connectDB():
    print("DB 연결 시작")
    global dbConnect, dbCursor
    # DB 연결
    ip = '115.68.179.37'
    id = 'root'
    pw = 'ehdgnl8940!'
    db = 'Wolf'
    charset = 'utf8'
    dbConnect = pymysql.connect(host=ip, user=id, password=pw, db=db, charset=charset)
    dbCursor = dbConnect.cursor()
    print("DB 연결 끝", "\n")
    return dbConnect, dbCursor


""" 키워드 리스트 가져오기 """


def getKeywordList():
    # print("키워드 리스트 가져오기 시작")
    sql = "select `idx`, `keyword` from `Keyword`"
    dbCursor.execute(sql)
    keywordList = [item for item in dbCursor.fetchall()]
    # print("키워드 리스트 가져오기 끝 : ", keywordList, "\n")
    return keywordList


""" 지역 리스트 가져오기 """


def getRegionList():
    # print("지역 리스트 가져오기 시작")
    sql = "select `region` from `Region`"
    dbCursor.execute(sql)
    regionList = [item[0] for item in dbCursor.fetchall()]
    # print("지역 리스트 가져오기 끝 : ", regionList, "\n")
    return regionList


""" 도로명주소 리스트 가져오기 """


def getRoadList():
    # print("도로명주소 리스트 가져오기 시작")
    sql = "select `region_idx`, `road_name` from `RoadName` where saveComplete = 0"
    dbCursor.execute(sql)
    roadList = [item for item in dbCursor.fetchall()]
    # print("도로명주소 리스트 가져오기 끝 : ", roadList, "\n")
    return roadList


""" 크롬드라이버 경로와 옵션 설정 """


def setWebBrowser():
    options = webdriver.ChromeOptions()
    # options.add_argument('headless')
    options.add_argument("--start-maximized")
    options.add_argument("no-sandbox")
    options.add_argument("disable-gpu")  # 가속 사용 x
    options.add_argument("lang=ko_KR")  # 가짜 플러그인 탑재
    options.add_argument(
        'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')  # user-agent 이름 설정
    browser = webdriver.Chrome('C:/Users/ehdgn/IdeaProjects/CrawlingGooglePlace/chromedriver.exe', options=options)
    return browser


""" 검색어 입력 후 클릭버튼을 누른다. """


def searchDataInputAndClick(region, roadName, keyword):
    global driver
    searchInputData = "{} {} {}".format(region, roadName, keyword)
    driver.find_element_by_id('searchboxinput').send_keys(searchInputData)
    driver.find_element_by_xpath('//*[@id="searchbox-searchbutton"]').click()


""" 콘텐츠를 가장 아래까지 스크롤"""


def contentDownScrolling():
    global driver

    whileTime = 0
    while True:
        if whileTime > 10:
            whileTime = 0
            break
        try:
            time.sleep(0.5)
            whileTime += 0.5
            driver.find_element_by_xpath(
                '//*[@id="pane"]/div/div[1]/div/div/div[2]/div[1]/div/button/span[1]').is_displayed()
            break
        except Exception as e:
            pass

    animation = [pyautogui.easeInQuad, pyautogui.easeInBounce, pyautogui.easeInCubic]
    while True:
        if whileTime > 10:
            whileTime = 0
            break

        pyautogui.moveTo(
            random.randint(50, 400),
            random.randint(300, 800),
            0.2,
            animation[random.randint(0, 2)]
        )
        pyautogui.scroll(-800)
        whileTime += 0.5
        try:
            driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[4]/div[1]/div[39]/div').is_selected()
            break
        except Exception as e:
            pass


def contentClick(contentIdx):
    global driver

    while True:
        try:
            driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[4]/div[1]/div[1]/div/a').is_displayed()
            time.sleep(1)
            break
        except:
            pass
    driver.find_element_by_xpath(
        '//*[@id="pane"]/div/div[1]/div/div/div[4]/div[1]/div[' + str(contentIdx) + ']/div/a').click()


def getPlaceInfo():
    global driver

    responseData = {}
    responseData['name'] = ''
    responseData['sub_name'] = ''
    responseData['phone'] = ''
    responseData['address'] = ''
    responseData['open_time'] = ''
    responseData['time1'] = ''
    responseData['time2'] = ''
    responseData['time3'] = ''
    responseData['time4'] = ''
    responseData['time5'] = ''
    responseData['time6'] = ''
    responseData['time7'] = ''
    responseData['latitude'] = ''
    responseData['longitude'] = ''
    responseData['image_list'] = ''
    responseData['website'] = ''

    while True:
        try:
            driver.find_element_by_xpath(
                '//*[@id="pane"]/div/div[1]/div/div/div[2]/div[1]/div[1]/div[1]/h1/span[1]').is_displayed()
            break
        except:
            pass

    name = driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[2]/div[1]/div[1]/div[1]/h1/span[1]')
    responseData['name'] = name.text

    sub_name = driver.find_element_by_xpath(
        '//*[@id="pane"]/div/div[1]/div/div/div[2]/div[1]/div[1]/div[2]/div/div[2]/span[1]/span[1]/button')
    responseData['sub_name'] = sub_name.text

    try:
        address = driver.find_element_by_xpath(
            '//*[@id="pane"]/div/div[1]/div/div/div[7]/div[1]/button/div[1]/div[2]/div[1]')
    except:
        address = driver.find_element_by_xpath(
            '//*[@id="pane"]/div/div[1]/div/div/div[9]/div[1]/button/div[1]/div[2]/div[1]')

    responseData['address'] = address.text

    # 장소 place_gm_blue_24dp
    # 시간 schedule_gm_blue_24dp
    # 사이트 public_gm_blue_24dp
    # 번호 phone_gm_blue_24dp

    try:
        for i in range(2, 6):
            imageType = ""
            try:
                imageType = driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[7]/div[' + str(
                    i) + ']/button/div[1]/div[1]/div/img').get_attribute('src')
            except:
                imageType = driver.find_element_by_xpath(
                    '//*[@id="pane"]/div/div[1]/div/div/div[7]/div[' + str(i) + ']/div[1]/img').get_attribute('src')

            # 시간
            if "schedule_gm_blue_24dp" in imageType:
                driver.find_element_by_xpath(
                    '//*[@id="pane"]/div/div[1]/div/div/div[7]/div[' + str(i) + ']/div[1]/div/div[1]/span[2]').click()
                timeText = driver.find_element_by_xpath(
                    '//*[@id="pane"]/div/div[1]/div/div/div[7]/div[' + str(i) + ']/div[2]')
                timeText = str(timeText.text).replace("수정 제안하기", "")
                responseData["saturday"] = timeText.split("\n")[1]
                responseData["sunday"] = timeText.split("\n")[3]
                responseData["monday"] = timeText.split("\n")[5]
                responseData["tuesday"] = timeText.split("\n")[7]
                responseData["wednesday"] = timeText.split("\n")[9]
                responseData["thursday"] = timeText.split("\n")[11]
                responseData["friday"] = timeText.split("\n")[13]
            # 사이트
            elif "public_gm_blue_24dp" in imageType:
                website = driver.find_element_by_xpath(
                    '//*[@id="pane"]/div/div[1]/div/div/div[7]/div[' + str(i) + ']/button/div[1]/div[2]/div[1]')
                responseData['website'] = "www.{}".format(website.text)

            # 번호
            elif "phone_gm_blue_24dp" in imageType:
                phone = driver.find_element_by_xpath(
                    '//*[@id="pane"]/div/div[1]/div/div/div[7]/div[' + str(i) + ']/button/div[1]/div[2]/div[1]')
                responseData['phone'] = phone.text

    except NoSuchElementException as e:
        pass

    responseData = getImageUrlsAndGPS(responseData)

    while True:
        try:
            driver.find_element_by_xpath(
                '//*[@id="omnibox-singlebox"]/div[1]/div[4]/div/div[1]/div/div/button/span').click()
            time.sleep(2)
            break
        except:
            pass

    return responseData


def getImageUrlsAndGPS(responseData):
    gpsInfo = str(driver.current_url).split('/')[6].replace("@", "").split(",")
    responseData['latitude'] = gpsInfo[0]
    responseData['longitude'] = gpsInfo[1]

    imageIsEmpty = False

    while True:
        try:
            if 'default_geocode-2x' in driver.find_element_by_xpath(
                    '//*[@id="pane"]/div/div[1]/div/div/div[1]/div[1]/button/img').get_attribute('src'):
                imageIsEmpty = True
                break

            driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[1]/div[1]/button/img').click()
            time.sleep(0.5)
            break
        except Exception as e:
            # print("getImageUrls 1, ", e)
            pass

    if not imageIsEmpty:
        while True:
            try:
                driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[1]/button[1]/div').is_displayed()
                time.sleep(0.5)
                break
            except Exception as e:
                # print("getImageUrls 2, ", e)
                pass

        imageList = []

        for idx in range(1, 10):
            for j in range(1, 5):
                try:
                    bgImage = driver.find_element_by_xpath(
                        '//*[@id="pane"]/div/div[1]/div/div/div[3]/div[1]/div[' + str(idx) + ']/div/a/div[' + str(
                            j) + ']').get_attribute('style')
                    if "http" in bgImage:
                        imaegUrl = str(bgImage).split('url("')[1].split('");')[0]
                        imageList.append(imaegUrl)
                except Exception as e:
                    # print("getImageUrls 3, ", e)
                    pass

        responseData['image_list'] = ','.join(imageList)

        while True:
            try:
                driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[1]/button[1]/div').click()
                break
            except Exception as e:
                # print("getImageUrls 4, ", e)
                pass

    while True:
        try:
            driver.find_element_by_xpath(
                '//*[@id="omnibox-singlebox"]/div[1]/div[4]/div/div[1]/div/div/button/span').is_displayed()
            break
        except Exception as e:
            # print("getImageUrls 5, ", e)
            pass
    return responseData


if __name__ == '__main__':

    dbConnect, dbCursor = connectDB()
    regionList = getRegionList()
    roadList = getRoadList()
    keywordList = getKeywordList()

    driver = setWebBrowser()

    # 구글 지도
    url = "https://www.google.com/maps/search/"
    driver.get(url)

    for region in tqdm(regionList):  # 서울특별시, 경기도 ~~

        for roadNameTuple in roadList:  # 성수동1가, 개봉동 ~~
            regionIdx = roadNameTuple[0]  # 1, 2 ~~ 지역 인덱스
            roadName = roadNameTuple[1]  # 도로명 주소 - ex) 성수동1가

            for keywordTuple in keywordList:  # 필라테스, 태권도 ~~
                keywordIdx = keywordTuple[0]
                keyword = keywordTuple[1]

                searchDataInputAndClick(region, roadName, keyword)  # """ 검색어 입력후 클릭 """
                contentDownScrolling()  # """ 콘텐츠를 가장 아래쪽까지 스크롤 """

                responseDataList = []
                for contentIdx in tqdm(range(1, 40, 2)):
                    if contentIdx >= 13:
                        contentDownScrolling()

                    contentClick(contentIdx)  # 콘텐츠 클릭
                    responseData = getPlaceInfo()  # 콘텐츠 정보 수집
                    responseDataList.append(responseData)

                for inputData in responseDataList:
                    insertSql = "INSERT INTO `Place` " \
                          "(category_idx, name, sub_name, phone, address," \
                          "time1, time2, time3, time4, time5, time6, time7," \
                          "latitude, longitude, image_list, website) VALUES " \
                          "(%s, %s, %s, %s, %s, " \
                          "%s, %s, %s, %s, %s, %s, %s, " \
                          "%s, %s, %s, %s);"

                    val = (
                        keywordIdx, inputData['name'], inputData['sub_name'],inputData['phone'],inputData['address'],
                        inputData['monday'], inputData['tuesday'],inputData['wednesday'],inputData['thursday'],inputData['friday'],inputData['saturday'],inputData['sunday'],
                        inputData['monday'], inputData['tuesday'],inputData['wednesday'],inputData['thursday']
                    )

                    dbCursor.execute(insertSql, val)
                    dbConnect.commit()

                    updateSql = "UPDATE `ROADNAME` set saveComplete=1 where region_idx = %s"
                    dbCursor.execute(updateSql, regionIdx)
                    dbConnect.commit()
dbConnect.close()