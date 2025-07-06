from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import json
import re

class AIController:
    def __init__(self):
        self.gpt_driver = None
        self.claude_driver = None
        self.is_running = False
        self.current_round = 0
        
        # 프롬프트 저장 파일
        self.prompts_file = "prompts.json"
        self.load_prompts()
        
        # 단계별 딜레이 (초)
        self.delays = {
            1: 2,   # 시작
            2: 5,   # 프롬프트 전달
            3: 30,  # GPT 답변 대기
            4: 5,   # 답변 복사
            5: 5,   # Claude 전달
            6: 30,  # Claude 답변 대기
            7: 5,   # 답변 복사
            8: 5,   # GPT 전달
            9: 3    # 다음 라운드
        }
    
    def load_prompts(self):
        """저장된 프롬프트 불러오기"""
        if os.path.exists(self.prompts_file):
            with open(self.prompts_file, 'r', encoding='utf-8') as f:
                self.prompts = json.load(f)
        else:
            # 기본 프롬프트
            self.prompts = [
                "안녕하세요! 오늘 날씨가 어떤가요?",
                "인공지능의 미래에 대해 어떻게 생각하시나요?",
                "창의적인 이야기를 하나 만들어주세요."
            ]
            self.save_prompts()
    
    def save_prompts(self):
        """프롬프트 저장"""
        with open(self.prompts_file, 'w', encoding='utf-8') as f:
            json.dump(self.prompts, f, ensure_ascii=False, indent=2)
    
    def start_browsers(self):
        """브라우저 시작"""
        print("🚀 브라우저 시작 중...")
        
        # ChatGPT 브라우저
        gpt_options = webdriver.ChromeOptions()
        gpt_options.add_argument(f"user-data-dir={os.path.join(os.getcwd(), 'chrome_profile')}")
        gpt_options.add_argument("--disable-blink-features=AutomationControlled")
        self.gpt_driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=gpt_options
        )
        self.gpt_driver.get("https://chatgpt.com")
        print("✅ ChatGPT 브라우저 시작")
        
        # Claude 브라우저
        claude_options = webdriver.ChromeOptions()
        claude_options.add_argument(f"user-data-dir={os.path.join(os.getcwd(), 'claude_profile')}")
        claude_options.add_argument("--disable-blink-features=AutomationControlled")
        self.claude_driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=claude_options
        )
        self.claude_driver.get("https://claude.ai")
        print("✅ Claude 브라우저 시작")
        
        # 로딩 대기
        time.sleep(5)
        print("✅ 모든 브라우저 준비 완료!\n")
    
    def send_to_gpt(self, message):
        """ChatGPT에 메시지 전송"""
        try:
            # 입력창 찾기
            input_div = self.gpt_driver.find_element(By.ID, "prompt-textarea")
            input_div.click()
            input_div.clear()
            input_div.send_keys(message)
            
            # 전송 버튼 찾기 - 여러 방법 시도
            time.sleep(1)
            
            # 방법 1: 전송 버튼 클릭
            try:
                send_button = self.gpt_driver.find_element(By.CSS_SELECTOR, "button[data-testid='send-button']")
                send_button.click()
            except:
                # 방법 2: Ctrl+Enter
                try:
                    input_div.send_keys(Keys.CONTROL + Keys.RETURN)
                except:
                    # 방법 3: 그냥 Enter
                    input_div.send_keys(Keys.RETURN)
            
            print(f"📤 GPT에 전송: {message[:50]}...")
            return True
        except Exception as e:
            print(f"❌ GPT 전송 실패: {e}")
            return False
    
    def send_to_claude(self, message):
        """Claude에 메시지 전송"""
        try:
            # 이모지 제거 (BMP 오류 방지)
            clean_message = re.sub(r'[^\u0000-\uFFFF]', '', message)
            
            # 입력창 찾기
            input_div = self.claude_driver.find_element(By.CSS_SELECTOR, "div[contenteditable='true']")
            input_div.click()
            input_div.clear()
            input_div.send_keys(clean_message)
            
            # 전송 (Enter)
            time.sleep(1)
            input_div.send_keys(Keys.RETURN)
            
            print(f"📤 Claude에 전송: {clean_message[:50]}...")
            return True
        except Exception as e:
            print(f"❌ Claude 전송 실패: {e}")
            return False
    
    def get_gpt_response(self):
        """GPT 최신 응답 가져오기"""
        try:
            # 응답 대기
            time.sleep(self.delays[3])
            
            # 최신 메시지 찾기
            messages = self.gpt_driver.find_elements(By.CSS_SELECTOR, "div[data-message-author-role='assistant']")
            if messages:
                latest = messages[-1].text
                print(f"📥 GPT 응답: {latest[:100]}...")
                return latest
            return None
        except Exception as e:
            print(f"❌ GPT 응답 가져오기 실패: {e}")
            return None
    
    def get_claude_response(self):
        """Claude 최신 응답 가져오기"""
        try:
            # 응답 대기
            time.sleep(self.delays[6])
            
            # 최신 메시지 찾기
            messages = self.claude_driver.find_elements(By.CSS_SELECTOR, "div[data-test-render-count]")
            if messages:
                latest = messages[-1].text
                print(f"📥 Claude 응답: {latest[:100]}...")
                return latest
            return None
        except Exception as e:
            print(f"❌ Claude 응답 가져오기 실패: {e}")
            return None
    
    def run_auto_mode(self):
        """자동 모드 실행"""
        print("\n🤖 자동 모드 시작!\n")
        self.is_running = True
        
        for round_num, prompt in enumerate(self.prompts):
            if not self.is_running:
                break
                
            print(f"\n═══ 라운드 {round_num + 1}/{len(self.prompts)} 시작 ═══")
            print(f"프롬프트: {prompt}\n")
            
            # 1. 두 AI에게 동시에 프롬프트 전송
            print("단계 1: 프롬프트 전송")
            self.send_to_gpt(prompt)
            self.send_to_claude(prompt)
            time.sleep(self.delays[2])
            
            # 대화 반복 (3회)
            for i in range(3):
                if not self.is_running:
                    break
                    
                print(f"\n--- 대화 {i+1}/3 ---")
                
                # 2. GPT 응답 대기 및 가져오기
                print("단계 2: GPT 응답 대기")
                gpt_response = self.get_gpt_response()
                if not gpt_response:
                    print("⚠️ GPT 응답 없음")
                    continue
                
                # 3. GPT 응답을 Claude에게 전달
                print("단계 3: GPT → Claude")
                self.send_to_claude(gpt_response)
                time.sleep(self.delays[5])
                
                # 4. Claude 응답 대기 및 가져오기
                print("단계 4: Claude 응답 대기")
                claude_response = self.get_claude_response()
                if not claude_response:
                    print("⚠️ Claude 응답 없음")
                    continue
                
                # 5. Claude 응답을 GPT에게 전달
                print("단계 5: Claude → GPT")
                self.send_to_gpt(claude_response)
                time.sleep(self.delays[8])
            
            print(f"\n✅ 라운드 {round_num + 1} 완료!")
            time.sleep(self.delays[9])
        
        print("\n🎉 모든 라운드 완료!")
        self.is_running = False
    
    def stop(self):
        """중지"""
        print("\n⏹️ 중지 중...")
        self.is_running = False
        
        if self.gpt_driver:
            self.gpt_driver.quit()
        if self.claude_driver:
            self.claude_driver.quit()
        
        print("✅ 종료 완료")

# 메인 실행
if __name__ == "__main__":
    controller = AIController()
    
    print("🎮 AI 자동 대화 컨트롤러")
    print("=" * 40)
    
    try:
        # 브라우저 시작
        controller.start_browsers()
        
        # 자동 모드 실행
        input("준비되면 엔터를 눌러 시작하세요...")
        controller.run_auto_mode()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자가 중단했습니다")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
    finally:
        controller.stop()