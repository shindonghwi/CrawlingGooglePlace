import random
import time

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

myTimer = 0
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


""" 키워드 리스트 가져오기 """


def getKeywordList():
    # print("키워드 리스트 가져오기 시작")
    sql = "select `keyword` from `Keyword`"
    dbCursor.execute(sql)
    keywordList = [item[0] for item in dbCursor.fetchall()]
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
    sql = "select `region_idx`, `road_name` from `RoadName`"
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


def searchDataInputAndClick():
    global driver
    searchInputData = "{} {} {}".format(region, roadName, keyword)
    driver.find_element_by_id('searchboxinput').send_keys(searchInputData)
    driver.find_element_by_xpath('//*[@id="searchbox-searchbutton"]').click()

def myTimerFuntion():
    global myTimer
    myTimer += 1
    timer = threading.Timer(1, myTimerFuntion)
    timer.start()

    if myTimer == 5:
        timer.cancel()

""" 콘텐츠를 가장 아래까지 스크롤"""


def contentDownScrolling():
    global driver, myTimer

    myTimerFuntion()
    while True:
        if myTimer == 5:
            myTimer = 0
            break

        try:
            driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[2]/div[1]/div/button/span[1]').is_displayed()
            time.sleep(0.5)
            break
        except Exception as e:
            pass

    animation = [pyautogui.easeInQuad, pyautogui.easeInBounce, pyautogui.easeInCubic]
    while True:
        pyautogui.moveTo(
            random.randint(50, 400),
            random.randint(300, 800),
            0.2,
            animation[random.randint(0, 2)]
        )
        pyautogui.scroll(-800)

        try:
            driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[4]/div[1]/div[39]/div').is_selected()
            break
        except Exception as e:
            pass


def contentClick(contentIdx):
    global driver
    driver.find_element_by_xpath(
        '//*[@id="pane"]/div/div[1]/div/div/div[4]/div[1]/div[' + str(contentIdx) + ']/div/a').click()


def getPlaceInfo():
    global driver

    while True:
        try:
            driver.find_element_by_xpath(
                '//*[@id="pane"]/div/div[1]/div/div/div[2]/div[1]/div[1]/div[1]/h1/span[1]').is_displayed()
            break
        except:
            pass

    name = driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[2]/div[1]/div[1]/div[1]/h1/span[1]')
    print(name.text)

    sub_name = driver.find_element_by_xpath(
        '//*[@id="pane"]/div/div[1]/div/div/div[2]/div[1]/div[1]/div[2]/div/div[2]/span[1]/span[1]/button')
    print(sub_name.text)

    address = driver.find_element_by_xpath(
        '//*[@id="pane"]/div/div[1]/div/div/div[7]/div[1]/button/div[1]/div[2]/div[1]').text
    print(address)

    # 장소 place_gm_blue_24dp
    # 시간 schedule_gm_blue_24dp
    # 사이트 public_gm_blue_24dp
    # 번호 phone_gm_blue_24dp

    try:
        for i in range(2, 5):
            try:
                imageType = driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[7]/div[' + str(
                    i) + ']/button/div[1]/div[1]/div/img').get_attribute('src')
            except:
                imageType = driver.find_element_by_xpath(
                    '//*[@id="pane"]/div/div[1]/div/div/div[7]/div[' + str(i) + ']/div[1]/img').get_attribute('src')

            print(imageType)

            if "place_gm_blue_24dp" in imageType:
                # 장소
                pass
            # 시간
            elif "schedule_gm_blue_24dp" in imageType:
                driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[7]/div['+str(i)+']/div[1]/div/div[1]/span[2]').click()
                timeInfo = driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[7]/div[' + str(i) + ']/div[2]')
                print(timeInfo.text)
            elif "public_gm_blue_24dp" in imageType:
                # 시간
                pass
            elif "phone_gm_blue_24dp" in imageType:
                # 시간
                pass

    except NoSuchElementException as e:
        pass

    driver.find_element_by_xpath('//*[@id="omnibox-singlebox"]/div[1]/div[4]/div/div[1]/div/div/button/span').click()
    time.sleep(2)


if __name__ == '__main__':
    connectDB()
    regionList = getRegionList()
    roadList = getRoadList()
    keywordList = getKeywordList()

    driver = setWebBrowser()

    # 구글 지도
    url = "https://www.google.com/maps/search/"
    driver.get(url)

    for region in regionList:  # 서울특별시, 경기도 ~~

        for roadNameTuple in roadList:  # 성수동1가, 개봉동 ~~
            regionIdx = roadNameTuple[0]  # 1, 2 ~~ 지역 인덱스
            roadName = roadNameTuple[1]  # 도로명 주소 - ex) 성수동1가

            for keyword in keywordList:  # 필라테스, 태권도 ~~

                searchDataInputAndClick()  # """ 검색어 입력후 클릭 """
                contentDownScrolling()  # """ 콘텐츠를 가장 아래쪽까지 스크롤 """

                for contentIdx in range(1, 40, 2):
                    print(contentIdx)
                    if contentIdx >= 13:
                        contentDownScrolling()

                    contentClick(contentIdx)  # 콘텐츠 클릭
                    getPlaceInfo()  # 콘텐츠 정보 수집

                exit()
