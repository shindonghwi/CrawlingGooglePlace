import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
options = Options()
# 새창을 열지않고 실행하는 옵션 정보
options.headless = False

# 크롬드라이버 경로와 옵션 설정
browser = webdriver.Chrome('C:/Users/ehdgn/IdeaProjects/PlaceCrawling/chromedriver.exe',options=options)

url = "https://www.google.com/search?q=%EC%84%B1%EC%88%98%EB%8F%991%EA%B0%80+%EB%B2%A0%EC%8A%A4%ED%8A%B8%ED%83%9C%EA%B6%8C%EB%8F%84&oq=%EC%84%B1%EC%88%98%EB%8F%991%EA%B0%80+%EB%B2%A0%EC%8A%A4%ED%8A%B8%ED%83%9C%EA%B6%8C%EB%8F%84&aqs=chrome..69i57j69i61l2.1278j0j4&sourceid=chrome&ie=UTF-8"
browser.get(url)

browser.find_element_by_xpath('//*[@id="lu_map"]').click()

gpsInfo = str(browser.current_url).split('/')[6].replace("@","").split(",")
latitude = gpsInfo[0]
longitude = gpsInfo[1]
print(latitude, longitude)