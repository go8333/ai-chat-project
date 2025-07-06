from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

print("ChatGPT 테스트 시작...")

# Chrome 옵션 설정 (봇 감지 회피)
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# 브라우저 실행
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# 봇 감지 회피 추가 설정
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

print("ChatGPT 페이지로 이동...")
driver.get("https://chatgpt.com")

print("\n⏰ 로그인해주세요! (시간제한 없음)")
print("로그인 완료 후 채팅 화면이 나타나면 엔터를 눌러주세요...")
input("준비되면 엔터 >>> ")

# 다양한 셀렉터로 입력창 찾기
selectors = [
    "textarea[data-id='root']",
    "textarea#prompt-textarea",
    "textarea[placeholder*='Message']",
    "div[contenteditable='true']",
    "textarea[rows]"
]

found = False
for selector in selectors:
    try:
        print(f"시도 중: {selector}")
        element = driver.find_element(By.CSS_SELECTOR, selector)
        if element:
            print(f"✅ 입력창 찾기 성공! (셀렉터: {selector})")
            found = True
            
            # 테스트 메시지 입력
            element.send_keys("안녕하세요! 이것은 자동화 테스트입니다.")
            print("✅ 테스트 메시지 입력 성공!")
            break
    except:
        continue

if not found:
    print("❌ 입력창을 찾을 수 없습니다")
    print("현재 페이지 URL:", driver.current_url)

input("\n엔터를 누르면 브라우저가 종료됩니다...")
driver.quit()