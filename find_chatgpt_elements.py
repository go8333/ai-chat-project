from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import os

print("ChatGPT 요소 찾기 테스트...")

# 기존 프로필 사용
profile_path = os.path.join(os.getcwd(), "chrome_profile")
options = webdriver.ChromeOptions()
options.add_argument(f"user-data-dir={profile_path}")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

driver.get("https://chatgpt.com")
print("페이지 로딩 대기...")
time.sleep(5)

print("\n=== 입력창 찾기 시작 ===")

# 다양한 방법으로 입력창 찾기
selectors = [
    ("ID", "prompt-textarea"),
    ("CSS", "textarea#prompt-textarea"),
    ("CSS", "textarea[data-id]"),
    ("CSS", "textarea[placeholder]"),
    ("CSS", "textarea"),
    ("CSS", "div[contenteditable='true']"),
    ("TAG", "textarea")
]

found_element = None
for method, selector in selectors:
    try:
        if method == "ID":
            element = driver.find_element(By.ID, selector)
        elif method == "CSS":
            element = driver.find_element(By.CSS_SELECTOR, selector)
        elif method == "TAG":
            element = driver.find_element(By.TAG_NAME, selector)
        
        print(f"✅ 발견! 방법: {method}, 셀렉터: {selector}")
        print(f"   - Tag: {element.tag_name}")
        print(f"   - ID: {element.get_attribute('id')}")
        print(f"   - Class: {element.get_attribute('class')}")
        print(f"   - Placeholder: {element.get_attribute('placeholder')}")
        
        if not found_element:
            found_element = element
            
    except:
        print(f"❌ 실패: {method} - {selector}")

if found_element:
    print("\n테스트 메시지 입력 시도...")
    found_element.clear()
    found_element.send_keys("테스트 메시지입니다!")
    print("✅ 메시지 입력 성공!")
else:
    print("\n❌ 입력창을 찾을 수 없습니다")
    
    # 모든 textarea 요소 출력
    print("\n=== 페이지의 모든 textarea 정보 ===")
    textareas = driver.find_elements(By.TAG_NAME, "textarea")
    for i, ta in enumerate(textareas):
        print(f"Textarea {i+1}:")
        print(f"  - ID: {ta.get_attribute('id')}")
        print(f"  - Class: {ta.get_attribute('class')}")

input("\n엔터를 누르면 종료됩니다...")
driver.quit()