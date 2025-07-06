from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os

print("Claude 자동화 테스트 시작...")

# Claude용 별도 프로필 생성
profile_path = os.path.join(os.getcwd(), "claude_profile")
if not os.path.exists(profile_path):
    os.makedirs(profile_path)
    print(f"✅ Claude 프로필 폴더 생성: {profile_path}")

# Chrome 옵션 설정
options = webdriver.ChromeOptions()
options.add_argument(f"user-data-dir={profile_path}")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])

# 브라우저 실행
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

print("Claude로 이동 중...")
driver.get("https://claude.ai")

print("\n📌 Claude 로그인:")
print("1. Continue with Google 또는 이메일로 로그인")
print("2. 로그인 완료 후 채팅 화면이 나올 때까지 대기")
print("\n⏰ 시간제한 없습니다!")

input("\n로그인 완료 후 엔터를 눌러주세요...")

# 쿠키 저장
cookies = driver.get_cookies()
print(f"\n✅ 로그인 정보 저장됨 ({len(cookies)}개 쿠키)")

# Claude 입력창 찾기 시도
print("\n=== Claude 입력창 찾기 ===")
selectors = [
    "div[contenteditable='true']",
    "div.ProseMirror",
    "div[data-placeholder]",
    "p[data-placeholder]",
    "div[role='textbox']"
]

found = False
for selector in selectors:
    try:
        element = driver.find_element(By.CSS_SELECTOR, selector)
        print(f"✅ 입력창 발견! 셀렉터: {selector}")
        
        # 테스트 메시지 입력
        element.click()
        element.send_keys("안녕하세요! Claude 자동화 테스트입니다.")
        print("✅ 메시지 입력 성공!")
        found = True
        break
    except:
        print(f"❌ 실패: {selector}")

if not found:
    print("\n❌ 입력창을 찾을 수 없습니다")

print("\n💾 다음 실행부터는 Claude도 자동 로그인됩니다!")
input("\n엔터를 누르면 종료됩니다...")
driver.quit()