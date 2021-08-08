import random
import threading
import time
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
import pymysql as pymysql
from tqdm import tqdm
import pyautogui

dbConnect = None
dbCursor = None
driver = None
maxPagingSize = 2
mySearchKeywordList = []

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


def getCategoryList():
    # print("키워드 리스트 가져오기 시작")
    sql = "select `category` from `Category`"
    dbCursor.execute(sql)
    categoryList = ["피트니스"]
    # categoryList = [item[0] for item in dbCursor.fetchall()]
    # print("키워드 리스트 가져오기 끝 : ", keywordList, "\n")
    return categoryList


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
    print("도로명주소 리스트 가져오기 시작")
    sql = "select `road_name` from `RoadName` where region_idx = 1 and idx >= 56"
    dbCursor.execute(sql)
    roadList = [item[0] for item in dbCursor.fetchall()]
    print("도로명주소 리스트 가져오기 끝 : ", roadList, "\n")
    return roadList


""" 크롬드라이버 경로와 옵션 설정 """


def setWebBrowser():
    options = webdriver.ChromeOptions()
    # options.add_argument('headless')
    options.add_argument("--start-maximized")
    # options.add_argument("no-sandbox")
    # options.add_argument("disable-gpu")  # 가속 사용 x
    options.add_argument("lang=ko_KR")  # 가짜 플러그인 탑재
    options.add_argument(
        'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'+str(random.randint(62,80))+'.0.3163.100 Safari/537.36')  # user-agent 이름 설정
    browser = webdriver.Chrome('C:/Users/ehdgn/IdeaProjects/CrawlingGooglePlace/chromedriver.exe', options=options)
    return browser


""" 검색어 입력 후 클릭버튼을 누른다. """


def searchDataInputAndClick(region, roadName, keyword):
    global driver
    driver.find_element_by_id('searchboxinput').clear()
    searchInputData = "{} {} {}".format(region, roadName, keyword)
    driver.find_element_by_id('searchboxinput').send_keys(searchInputData)
    driver.find_element_by_xpath('//*[@id="searchbox-searchbutton"]').click()


""" 콘텐츠를 가장 아래까지 스크롤"""


def contentDownScrolling():
    global driver

    while True:
        try:
            driver.find_element_by_xpath('//*[@id="sb_cb50"]').is_displayed()
            break
        except Exception as e:
            pass

    animation = [pyautogui.easeInQuad, pyautogui.easeInBounce, pyautogui.easeInCubic]

    for i in range(0, 3):
        try:
            pyautogui.moveTo(
                random.randint(50, 400),
                random.randint(300, 800),
                0.1,
                animation[random.randint(0, 2)]
            )
            pyautogui.scroll(-800)
            time.sleep(0.2)
        except:
            pass


def getTitle(region, roadName, curForPostion):
    global driver, mySearchKeywordList

    for i in range(1, 43):
        try:
            title = driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[4]/div[1]/div['+str(i)+']/div/div[2]/div[2]/div[1]/div/div/div/div[1]/div/span').text
            mySearchKeywordList.append("{} {} {}".format(region, roadName, title))
        except:
            try:
                title = driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[4]/div[1]/div['+str(i)+']/div/a').text
                mySearchKeywordList.append("{} {} {}".format(region, roadName, title))
            except:
                pass
            pass
    if curForPostion < maxPagingSize - 1:
        driver.find_element_by_xpath('//*[@id="ppdPk-Ej1Yeb-LgbsSe-tJiF1e"]/img').click()
    time.sleep(0.5)

def insertSearchKeyword():
    global mySearchKeywordList

    for searchKeyword in mySearchKeywordList:
        insertSearchDataSql = "INSERT INTO `SearchData` (search_keyword) VALUES (%s)"
        dbCursor.execute(insertSearchDataSql, (searchKeyword))
        dbConnect.commit()

if __name__ == '__main__':

    dbConnect, dbCursor = connectDB()
    driver = setWebBrowser()

    regionList = getRegionList()
    roadList = getRoadList()
    categoryList = getCategoryList()

    url = "https://www.google.com/maps/search/"
    driver.get(url)

    for region in regionList:
        for roadName in tqdm(roadList):  # 성수동1가, 개봉동 ~~
            for category in categoryList:
                searchDataInputAndClick(region, roadName, category)  # """ 검색어 입력후 클릭 """
                # print("{} {} {}".format(region, roadName, keyword))
                time.sleep(1)
                for i in range(0, maxPagingSize):
                    contentDownScrolling()
                    getTitle(region, roadName, i)
                time.sleep(1)

            insertSearchKeyword()
dbConnect.close()