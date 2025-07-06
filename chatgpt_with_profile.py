from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import os

print("독립된 Chrome 프로필로 ChatGPT 접속...")

# 독립 프로필 폴더 생성
profile_path = os.path.join(os.getcwd(), "chrome_profile")
if not os.path.exists(profile_path):
    os.makedirs(profile_path)
    print(f"✅ 프로필 폴더 생성: {profile_path}")

# Chrome 옵션 설정
options = webdriver.ChromeOptions()
options.add_argument(f"user-data-dir={profile_path}")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])

# 브라우저 실행
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

print("ChatGPT로 이동 중...")
driver.get("https://chatgpt.com")

print("\n📌 수동 로그인 단계:")
print("1. 로그인 버튼 클릭")
print("2. 이메일/비밀번호 입력")
print("3. 사람 확인 통과")
print("4. 채팅 화면이 나올 때까지 대기")
print("\n⏰ 시간제한 없습니다. 천천히 진행하세요!")

input("\n로그인 완료 후 엔터를 눌러주세요...")

# 쿠키 저장
cookies = driver.get_cookies()
print(f"\n✅ 로그인 정보 저장됨 ({len(cookies)}개 쿠키)")

# 입력창 테스트
try:
    textarea = driver.find_element(By.CSS_SELECTOR, "textarea[data-id='root']")
    print("✅ 입력창 발견!")
    textarea.send_keys("안녕하세요! 자동화 테스트 성공!")
    print("✅ 메시지 입력 완료!")
except:
    print("❌ 입력창을 찾을 수 없습니다")

print("\n💾 다음 실행부터는 자동 로그인됩니다!")
input("엔터를 누르면 종료됩니다...")
driver.quit()