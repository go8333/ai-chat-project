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
            3: 20,  # GPT 답변 대기 (줄임)
            4: 3,   # 답변 복사
            5: 3,   # Claude 전달
            6: 20,  # Claude 답변 대기 (줄임)
            7: 3,   # 답변 복사
            8: 3,   # GPT 전달
            9: 3    # 다음 라운드
        }
    
    def load_prompts(self):
        """저장된 프롬프트 불러오기"""
        # 대화형 프롬프트로 변경
        self.prompts = [
            "안녕하세요! 당신의 이름은 무엇인가요? 그리고 오늘 기분은 어떠신가요?",
            "좋아하는 색깔이 무엇인가요? 그 이유도 알려주세요.",
            "만약 하루 동안 어떤 동물이든 될 수 있다면 무엇이 되고 싶나요?"
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
    
    def start_new_chat_gpt(self):
        """GPT 새 채팅 시작"""
        try:
            # 새 채팅 버튼 찾기 시도
            new_chat_selectors = [
                "a[href='/']",
                "button[aria-label='New chat']",
                "nav a[href='/']"
            ]
            
            for selector in new_chat_selectors:
                try:
                    new_chat = self.gpt_driver.find_element(By.CSS_SELECTOR, selector)
                    new_chat.click()
                    time.sleep(2)
                    print("✅ GPT 새 채팅 시작")
                    return True
                except:
                    continue
                    
            # 못 찾으면 URL로 이동
            self.gpt_driver.get("https://chatgpt.com")
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"⚠️ GPT 새 채팅 시작 실패: {e}")
            return False
    
    def start_new_chat_claude(self):
        """Claude 새 채팅 시작"""
        try:
            # Claude 홈으로 이동 (새 채팅)
            self.claude_driver.get("https://claude.ai/new")
            time.sleep(2)
            print("✅ Claude 새 채팅 시작")
            return True
        except Exception as e:
            print(f"⚠️ Claude 새 채팅 시작 실패: {e}")
            return False
    
    def send_to_gpt(self, message):
        """ChatGPT에 메시지 전송"""
        try:
            # 입력창 찾기
            input_div = WebDriverWait(self.gpt_driver, 10).until(
                EC.presence_of_element_located((By.ID, "prompt-textarea"))
            )
            input_div.click()
            input_div.clear()
            
            # 메시지 입력 (천천히)
            for char in message:
                input_div.send_keys(char)
                time.sleep(0.01)
            
            # 전송
            time.sleep(1)
            input_div.send_keys(Keys.RETURN)
            
            print(f"📤 GPT에 전송: {message[:50]}...")
            return True
        except Exception as e:
            print(f"❌ GPT 전송 실패: {e}")
            return False
    
    def send_to_claude(self, message):
        """Claude에 메시지 전송"""
        try:
            # 이모지 제거
            clean_message = re.sub(r'[^\u0000-\uFFFF]', '', message)
            
            # 입력창 찾기
            input_div = WebDriverWait(self.claude_driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true']"))
            )
            input_div.click()
            input_div.clear()
            
            # 메시지 입력 (천천히)
            for char in clean_message:
                input_div.send_keys(char)
                time.sleep(0.01)
            
            # 전송
            time.sleep(1)
            input_div.send_keys(Keys.RETURN)
            
            print(f"📤 Claude에 전송: {clean_message[:50]}...")
            return True
        except Exception as e:
            print(f"❌ Claude 전송 실패: {e}")
            return False
    
    def wait_for_gpt_response(self):
        """GPT 응답 완료 대기"""
        try:
            # 응답 생성 중 표시가 사라질 때까지 대기
            time.sleep(3)
            
            # 최대 대기 시간
            max_wait = self.delays[3]
            waited = 0
            
            while waited < max_wait:
                # 입력창이 다시 활성화되었는지 확인
                try:
                    input_div = self.gpt_driver.find_element(By.ID, "prompt-textarea")
                    if input_div.is_enabled():
                        time.sleep(2)  # 안정화 대기
                        return True
                except:
                    pass
                
                time.sleep(1)
                waited += 1
            
            return True
        except:
            return True
    
    def wait_for_claude_response(self):
        """Claude 응답 완료 대기"""
        try:
            time.sleep(3)
            
            max_wait = self.delays[6]
            waited = 0
            
            while waited < max_wait:
                try:
                    # 입력창 확인
                    input_div = self.claude_driver.find_element(By.CSS_SELECTOR, "div[contenteditable='true']")
                    if input_div.is_enabled():
                        time.sleep(2)
                        return True
                except:
                    pass
                
                time.sleep(1)
                waited += 1
            
            return True
        except:
            return True
    
    def get_gpt_response(self):
        """GPT 최신 응답 가져오기"""
        try:
            # 응답 완료 대기
            self.wait_for_gpt_response()
            
            # 모든 메시지 가져오기
            messages = self.gpt_driver.find_elements(By.CSS_SELECTOR, "div[data-message-author-role='assistant']")
            if messages:
                # 마지막 메시지의 텍스트 추출
                latest_msg = messages[-1]
                # 코드 블록, 버튼 등 제외하고 순수 텍스트만
                paragraphs = latest_msg.find_elements(By.CSS_SELECTOR, "p, li")
                text = "\n".join([p.text for p in paragraphs if p.text])
                
                if not text:  # p 태그가 없으면 전체 텍스트
                    text = latest_msg.text
                
                print(f"📥 GPT 응답: {text[:100]}...")
                return text
            return None
        except Exception as e:
            print(f"❌ GPT 응답 가져오기 실패: {e}")
            return None
    
    def get_claude_response(self):
        """Claude 최신 응답 가져오기"""
        try:
            # 응답 완료 대기
            self.wait_for_claude_response()
            
            # Claude 응답 찾기
            messages = self.claude_driver.find_elements(By.CSS_SELECTOR, "div[data-test-render-count]")
            if messages:
                latest_msg = messages[-1]
                text = latest_msg.text
                print(f"📥 Claude 응답: {text[:100]}...")
                return text
            return None
        except Exception as e:
            print(f"❌ Claude 응답 가져오기 실패: {e}")
            return None
    
    def run_conversation_round(self, prompt):
        """한 라운드 대화 실행"""
        print(f"\n🔄 프롬프트: {prompt}")
        
        # 1. 새 채팅 시작
        print("\n📝 새 채팅 시작...")
        self.start_new_chat_gpt()
        self.start_new_chat_claude()
        time.sleep(2)
        
        # 2. 초기 프롬프트 전송
        print("\n💬 초기 프롬프트 전송...")
        if not self.send_to_gpt(prompt):
            return False
        time.sleep(2)
        
        # 3. GPT 응답 받기
        print("\n⏳ GPT 응답 대기...")
        gpt_response = self.get_gpt_response()
        if not gpt_response:
            print("⚠️ GPT 응답 없음")
            return False
        
        # 4. GPT 응답을 Claude에게 전달
        print("\n🔀 GPT → Claude 전달...")
        full_message = f"다른 AI가 '{prompt}'라는 질문에 이렇게 답했습니다:\n\n{gpt_response}\n\n당신은 어떻게 생각하시나요?"
        if not self.send_to_claude(full_message):
            return False
        
        # 5. Claude 응답 받기
        print("\n⏳ Claude 응답 대기...")
        claude_response = self.get_claude_response()
        if not claude_response:
            print("⚠️ Claude 응답 없음")
            return False
        
        # 6. 대화 계속 (2회 더)
        for i in range(2):
            print(f"\n🔄 추가 대화 {i+1}/2")
            
            # Claude 응답을 GPT에게
            gpt_message = f"다른 AI가 이렇게 답했습니다:\n\n{claude_response}\n\n당신의 생각은 어떤가요?"
            if not self.send_to_gpt(gpt_message):
                break
            
            gpt_response = self.get_gpt_response()
            if not gpt_response:
                break
            
            # GPT 응답을 다시 Claude에게
            claude_message = f"상대방이 이렇게 답했습니다:\n\n{gpt_response}\n\n추가로 하실 말씀이 있나요?"
            if not self.send_to_claude(claude_message):
                break
            
            claude_response = self.get_claude_response()
            if not claude_response:
                break
        
        print("\n✅ 라운드 완료!")
        return True
    
    def run_auto_mode(self):
        """자동 모드 실행"""
        print("\n🤖 자동 대화 모드 시작!\n")
        self.is_running = True
        
        for round_num, prompt in enumerate(self.prompts):
            if not self.is_running:
                break
            
            print(f"\n{'='*50}")
            print(f"📍 라운드 {round_num + 1}/{len(self.prompts)}")
            print(f"{'='*50}")
            
            success = self.run_conversation_round(prompt)
            
            if not success:
                print("⚠️ 라운드 실패, 다음 라운드로 진행...")
            
            # 다음 라운드 전 대기
            if round_num < len(self.prompts) - 1:
                print(f"\n⏸️ 다음 라운드까지 {self.delays[9]}초 대기...")
                time.sleep(self.delays[9])
        
        print("\n🎉 모든 대화 완료!")
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
    
    print("🎮 AI 자동 대화 컨트롤러 v2.0")
    print("=" * 40)
    print("✨ 개선사항:")
    print("- 각 라운드마다 새 대화 시작")
    print("- 대화 맥락 전달 개선")
    print("- 응답 대기 로직 개선")
    print("=" * 40)
    
    try:
        # 브라우저 시작
        controller.start_browsers()
        
        # 자동 모드 실행
        input("\n준비되면 엔터를 눌러 시작하세요...")
        controller.run_auto_mode()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자가 중단했습니다")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
    finally:
        controller.stop()