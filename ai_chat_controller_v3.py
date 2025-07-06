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
        
        # 단계별 딜레이 (초) - 조정됨
        self.delays = {
            'typing': 0.05,      # 타이핑 속도
            'after_send': 2,     # 전송 후 대기
            'check_interval': 1, # 응답 체크 간격
            'max_wait': 60,      # 최대 대기 시간
            'between_rounds': 5  # 라운드 간 대기
        }
    
    def load_prompts(self):
        """저장된 프롬프트 불러오기"""
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
        gpt_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        gpt_options.add_experimental_option('useAutomationExtension', False)
        
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
        claude_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        claude_options.add_experimental_option('useAutomationExtension', False)
        
        self.claude_driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=claude_options
        )
        self.claude_driver.get("https://claude.ai/new")
        print("✅ Claude 브라우저 시작")
        
        # 로딩 대기
        time.sleep(5)
        print("✅ 모든 브라우저 준비 완료!\n")
    
    def send_to_gpt(self, message):
        """ChatGPT에 메시지 전송"""
        try:
            # 입력창 찾기
            input_div = WebDriverWait(self.gpt_driver, 10).until(
                EC.presence_of_element_located((By.ID, "prompt-textarea"))
            )
            
            # 기존 텍스트 클리어
            input_div.click()
            time.sleep(0.5)
            input_div.clear()
            time.sleep(0.5)
            
            # 메시지 입력 (천천히)
            for char in message:
                input_div.send_keys(char)
                time.sleep(self.delays['typing'])
            
            # 잠시 대기 후 전송
            time.sleep(1)
            input_div.send_keys(Keys.RETURN)
            
            print(f"📤 GPT에 전송 완료")
            print(f"   메시지: {message[:50]}...")
            time.sleep(self.delays['after_send'])
            return True
            
        except Exception as e:
            print(f"❌ GPT 전송 실패: {e}")
            return False
    
    def send_to_claude(self, message):
        """Claude에 메시지 전송"""
        try:
            # 이모지 및 특수문자 정리
            clean_message = message.encode('utf-8', 'ignore').decode('utf-8')
            
            # 입력창 찾기
            input_div = WebDriverWait(self.claude_driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true']"))
            )
            
            # 기존 텍스트 클리어
            input_div.click()
            time.sleep(0.5)
            input_div.clear()
            time.sleep(0.5)
            
            # 메시지 입력 (천천히)
            for char in clean_message:
                input_div.send_keys(char)
                time.sleep(self.delays['typing'])
            
            # 잠시 대기 후 전송
            time.sleep(1)
            input_div.send_keys(Keys.RETURN)
            
            print(f"📤 Claude에 전송 완료")
            print(f"   메시지: {clean_message[:50]}...")
            time.sleep(self.delays['after_send'])
            return True
            
        except Exception as e:
            print(f"❌ Claude 전송 실패: {e}")
            return False
    
    def wait_for_gpt_response(self):
        """GPT 응답 완료 대기 (개선된 버전)"""
        print("⏳ GPT 응답 대기 중...")
        try:
            waited = 0
            last_text = ""
            stable_count = 0
            
            while waited < self.delays['max_wait']:
                try:
                    # 현재 응답 텍스트 가져오기
                    messages = self.gpt_driver.find_elements(By.CSS_SELECTOR, "div[data-message-author-role='assistant']")
                    
                    if messages:
                        current_text = messages[-1].text
                        
                        # 텍스트가 변경되지 않으면 stable_count 증가
                        if current_text == last_text and len(current_text) > 10:
                            stable_count += 1
                            print(f"   응답 안정화 중... ({stable_count}/3)")
                            
                            # 3초 동안 변화 없으면 완료로 판단
                            if stable_count >= 3:
                                print("✅ GPT 응답 완료!")
                                return True
                        else:
                            stable_count = 0
                            last_text = current_text
                    
                    # 입력창이 활성화되었는지도 확인
                    try:
                        input_div = self.gpt_driver.find_element(By.ID, "prompt-textarea")
                        if input_div.is_enabled() and messages and len(messages[-1].text) > 10:
                            time.sleep(1)  # 안정화 대기
                            print("✅ GPT 입력창 활성화 확인!")
                            return True
                    except:
                        pass
                    
                except Exception as e:
                    print(f"   대기 중... ({waited}초)")
                
                time.sleep(self.delays['check_interval'])
                waited += self.delays['check_interval']
            
            print("⚠️ 최대 대기 시간 초과")
            return True
            
        except Exception as e:
            print(f"❌ 응답 대기 중 오류: {e}")
            return False
    
    def wait_for_claude_response(self):
        """Claude 응답 완료 대기 (개선된 버전)"""
        print("⏳ Claude 응답 대기 중...")
        try:
            waited = 0
            last_text = ""
            stable_count = 0
            
            while waited < self.delays['max_wait']:
                try:
                    # 현재 응답 텍스트 가져오기
                    messages = self.claude_driver.find_elements(By.CSS_SELECTOR, "div[data-test-render-count]")
                    
                    if messages:
                        current_text = messages[-1].text
                        
                        # 텍스트가 변경되지 않으면 stable_count 증가
                        if current_text == last_text and len(current_text) > 10:
                            stable_count += 1
                            print(f"   응답 안정화 중... ({stable_count}/3)")
                            
                            # 3초 동안 변화 없으면 완료로 판단
                            if stable_count >= 3:
                                print("✅ Claude 응답 완료!")
                                return True
                        else:
                            stable_count = 0
                            last_text = current_text
                    
                    # 입력창 활성화 확인
                    try:
                        input_div = self.claude_driver.find_element(By.CSS_SELECTOR, "div[contenteditable='true']")
                        if input_div.is_enabled() and messages and len(messages[-1].text) > 10:
                            time.sleep(1)
                            print("✅ Claude 입력창 활성화 확인!")
                            return True
                    except:
                        pass
                    
                except Exception as e:
                    print(f"   대기 중... ({waited}초)")
                
                time.sleep(self.delays['check_interval'])
                waited += self.delays['check_interval']
            
            print("⚠️ 최대 대기 시간 초과")
            return True
            
        except Exception as e:
            print(f"❌ 응답 대기 중 오류: {e}")
            return False
    
    def get_gpt_response(self):
        """GPT 최신 응답 가져오기"""
        try:
            # 응답 완료 대기
            if not self.wait_for_gpt_response():
                return None
            
            # 모든 메시지 가져오기
            messages = self.gpt_driver.find_elements(By.CSS_SELECTOR, "div[data-message-author-role='assistant']")
            if messages:
                # 마지막 메시지의 텍스트 추출
                latest_msg = messages[-1]
                
                # 코드 블록과 일반 텍스트 모두 포함
                text_elements = latest_msg.find_elements(By.CSS_SELECTOR, "p, li, code, pre")
                text_parts = []
                
                for elem in text_elements:
                    if elem.text and elem.text.strip():
                        text_parts.append(elem.text.strip())
                
                full_text = "\n".join(text_parts)
                
                # 텍스트가 없으면 전체 텍스트 시도
                if not full_text:
                    full_text = latest_msg.text
                
                print(f"📥 GPT 응답 수신: {full_text[:100]}...")
                return full_text
            
            return None
            
        except Exception as e:
            print(f"❌ GPT 응답 가져오기 실패: {e}")
            return None
    
    def get_claude_response(self):
        """Claude 최신 응답 가져오기"""
        try:
            # 응답 완료 대기
            if not self.wait_for_claude_response():
                return None
            
            # Claude 응답 찾기
            messages = self.claude_driver.find_elements(By.CSS_SELECTOR, "div[data-test-render-count]")
            if messages:
                latest_msg = messages[-1]
                text = latest_msg.text
                print(f"📥 Claude 응답 수신: {text[:100]}...")
                return text
            
            return None
            
        except Exception as e:
            print(f"❌ Claude 응답 가져오기 실패: {e}")
            return None
    
    def run_conversation_round(self, prompt, round_num):
        """한 라운드 대화 실행 (수정됨 - 새 채팅 시작 제거)"""
        print(f"\n{'='*60}")
        print(f"🔄 라운드 {round_num + 1}: {prompt}")
        print(f"{'='*60}\n")
        
        # 첫 라운드에만 프롬프트 전송
        if round_num == 0:
            print("💬 초기 프롬프트를 GPT에 전송...")
            if not self.send_to_gpt(prompt):
                return False
        
        # 대화 루프 (3회 왕복)
        for exchange in range(3):
            print(f"\n🔀 교환 {exchange + 1}/3")
            
            # 1. GPT 응답 받기
            gpt_response = self.get_gpt_response()
            if not gpt_response:
                print("⚠️ GPT 응답을 받지 못했습니다.")
                return False
            
            # 2. GPT 응답을 Claude에게 전달
            if exchange == 0 and round_num == 0:
                # 첫 번째 교환에서는 컨텍스트 포함
                claude_message = f"ChatGPT가 '{prompt}'라는 질문에 이렇게 답했습니다:\n\n{gpt_response}\n\n당신의 생각은 어떤가요?"
            else:
                # 이후 교환에서는 간단히
                claude_message = f"상대방의 답변:\n{gpt_response}\n\n이에 대한 당신의 의견은?"
            
            print("\n📨 Claude에게 전달 중...")
            if not self.send_to_claude(claude_message):
                return False
            
            # 3. Claude 응답 받기
            claude_response = self.get_claude_response()
            if not claude_response:
                print("⚠️ Claude 응답을 받지 못했습니다.")
                return False
            
            # 마지막 교환이면 종료
            if exchange == 2:
                print("\n✅ 라운드 완료!")
                break
            
            # 4. Claude 응답을 GPT에게 전달
            gpt_message = f"상대방의 답변:\n{claude_response}\n\n이에 대한 당신의 생각은?"
            
            print("\n📨 GPT에게 전달 중...")
            if not self.send_to_gpt(gpt_message):
                return False
        
        return True
    
    def run_auto_mode(self):
        """자동 모드 실행 (수정됨)"""
        print("\n🤖 자동 대화 모드 시작!\n")
        print("💡 각 프롬프트로 3회 왕복 대화를 진행합니다.\n")
        self.is_running = True
        
        # 각 프롬프트에 대해 새로운 대화 시작
        for round_num, prompt in enumerate(self.prompts):
            if not self.is_running:
                break
            
            # 새 대화 시작 (각 프롬프트마다)
            print(f"\n🆕 새로운 주제로 대화 시작...")
            self.gpt_driver.get("https://chatgpt.com")
            self.claude_driver.get("https://claude.ai/new")
            time.sleep(3)
            
            # 대화 진행
            success = self.run_conversation_round(prompt, round_num)
            
            if not success:
                print("⚠️ 라운드 실패, 다음 라운드로 진행...")
            
            # 다음 라운드 전 대기
            if round_num < len(self.prompts) - 1:
                print(f"\n⏸️ 다음 라운드까지 {self.delays['between_rounds']}초 대기...")
                time.sleep(self.delays['between_rounds'])
        
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
    
    print("🎮 AI 자동 대화 컨트롤러 v3.0")
    print("=" * 50)
    print("✨ v3.0 개선사항:")
    print("- 응답 완료 동적 감지 (텍스트 안정화 확인)")
    print("- 새로고침 문제 해결")
    print("- 메시지 전달 로직 개선")
    print("- 더 안정적인 대기 시스템")
    print("=" * 50)
    
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