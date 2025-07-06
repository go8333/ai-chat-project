from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

print("Chrome 브라우저를 시작합니다...")

# Chrome 드라이버 자동 설치 및 실행
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

print("구글 홈페이지로 이동합니다...")
driver.get("https://www.google.com")

print("5초 대기...")
time.sleep(5)

print("브라우저를 종료합니다...")
driver.quit()

print("테스트 완료!")