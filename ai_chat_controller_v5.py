from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import json

class AIController:
    def __init__(self):
        self.gpt_driver = None
        self.claude_driver = None
        self.is_running = False
        
        # 프롬프트 저장 파일
        self.prompts_file = "prompts.json"
        self.load_prompts()
        
        # 딜레이 설정 (조정됨)
        self.delays = {
            'typing': 0.01,      # 더 빠른 타이핑
            'after_send': 3,     # 전송 후 대기
            'check_interval': 2, # 응답 체크 간격
            'max_wait': 90,      # 최대 대기 시간 증가
            'between_exchange': 3,  # 교환 간 대기
            'initial_load': 10   # 초기 로딩 대기
        }
    
    def load_prompts(self):
        """프롬프트 불러오기"""
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
        """브라우저 시작 - 직접 채팅 페이지로"""
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
        
        # 직접 채팅 페이지로 이동
        print("📍 ChatGPT 페이지 로딩...")
        self.gpt_driver.get("https://chatgpt.com")
        
        print("📍 Claude 페이지 로딩...")
        self.claude_driver.get("https://claude.ai/new")
        
        print(f"⏳ {self.delays['initial_load']}초 대기 중...")
        time.sleep(self.delays['initial_load'])
        
        print("✅ 브라우저 준비 완료\n")
    
    def send_to_gpt(self, message):
        """GPT에 메시지 전송 (개선)"""
        try:
            print("📤 GPT에 메시지 전송 중...")
            
            # 입력창 찾기 및 클릭
            input_div = WebDriverWait(self.gpt_driver, 10).until(
                EC.element_to_be_clickable((By.ID, "prompt-textarea"))
            )
            
            # JavaScript로 직접 값 설정
            self.gpt_driver.execute_script("""
                var element = arguments[0];
                element.focus();
                element.value = '';
            """, input_div)
            
            time.sleep(0.5)
            
            # 텍스트 입력
            input_div.send_keys(message)
            time.sleep(1)
            
            # Enter로 전송
            input_div.send_keys(Keys.RETURN)
            
            print(f"✅ GPT 전송 완료: {message[:50]}...")
            time.sleep(self.delays['after_send'])
            return True
            
        except Exception as e:
            print(f"❌ GPT 전송 실패: {e}")
            return False
    
    def send_to_claude(self, message):
        """Claude에 메시지 전송 (개선)"""
        try:
            print("📤 Claude에 메시지 전송 중...")
            
            # 입력창 찾기
            input_div = WebDriverWait(self.claude_driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div[contenteditable='true']"))
            )
            
            # 클릭하고 포커스
            input_div.click()
            time.sleep(0.5)
            
            # 기존 텍스트 지우기
            input_div.send_keys(Keys.CONTROL + "a")
            time.sleep(0.2)
            input_div.send_keys(Keys.DELETE)
            time.sleep(0.5)
            
            # 텍스트 입력 (클립보드 사용 방식)
            # 긴 텍스트를 위해 클립보드 사용
            self.claude_driver.execute_script("""
                navigator.clipboard.writeText(arguments[0]);
            """, message)
            time.sleep(0.5)
            
            # 붙여넣기
            input_div.send_keys(Keys.CONTROL + "v")
            time.sleep(1)
            
            # Enter로 전송
            input_div.send_keys(Keys.RETURN)
            
            print(f"✅ Claude 전송 완료: {message[:50]}...")
            time.sleep(self.delays['after_send'])
            return True
            
        except Exception as e:
            print(f"❌ Claude 전송 실패: {e}")
            return False
    
    def get_gpt_full_response(self):
        """GPT 전체 응답 가져오기 (개선)"""
        print("⏳ GPT 응답 대기 중...")
        
        try:
            start_time = time.time()
            last_length = 0
            stable_count = 0
            
            while (time.time() - start_time) < self.delays['max_wait']:
                try:
                    # 모든 assistant 메시지 찾기
                    messages = self.gpt_driver.find_elements(By.CSS_SELECTOR, "div[data-message-author-role='assistant']")
                    
                    if messages:
                        # 가장 최근 메시지
                        latest_msg = messages[-1]
                        
                        # 전체 텍스트 가져오기 (JavaScript 사용)
                        full_text = self.gpt_driver.execute_script("""
                            return arguments[0].innerText || arguments[0].textContent;
                        """, latest_msg)
                        
                        # 길이 체크
                        current_length = len(full_text) if full_text else 0
                        
                        if current_length > 20 and current_length == last_length:
                            stable_count += 1
                            print(f"   텍스트 안정화 확인... ({stable_count}/3)")
                            
                            if stable_count >= 3:
                                print(f"✅ GPT 응답 완료! (길이: {current_length}자)")
                                return full_text
                        else:
                            stable_count = 0
                            last_length = current_length
                            if current_length > 0:
                                print(f"   응답 수신 중... (현재 {current_length}자)")
                    
                except Exception as e:
                    pass
                
                time.sleep(self.delays['check_interval'])
            
            print("⚠️ 시간 초과")
            return None
            
        except Exception as e:
            print(f"❌ GPT 응답 가져오기 실패: {e}")
            return None
    
    def get_claude_full_response(self):
        """Claude 전체 응답 가져오기 (개선)"""
        print("⏳ Claude 응답 대기 중...")
        
        try:
            start_time = time.time()
            last_length = 0
            stable_count = 0
            
            while (time.time() - start_time) < self.delays['max_wait']:
                try:
                    # 모든 응답 메시지 찾기
                    messages = self.claude_driver.find_elements(By.CSS_SELECTOR, "div[data-test-render-count]")
                    
                    if messages:
                        # 가장 최근 메시지
                        latest_msg = messages[-1]
                        
                        # 전체 텍스트 가져오기
                        full_text = self.claude_driver.execute_script("""
                            return arguments[0].innerText || arguments[0].textContent;
                        """, latest_msg)
                        
                        # 길이 체크
                        current_length = len(full_text) if full_text else 0
                        
                        if current_length > 20 and current_length == last_length:
                            stable_count += 1
                            print(f"   텍스트 안정화 확인... ({stable_count}/3)")
                            
                            if stable_count >= 3:
                                print(f"✅ Claude 응답 완료! (길이: {current_length}자)")
                                return full_text
                        else:
                            stable_count = 0
                            last_length = current_length
                            if current_length > 0:
                                print(f"   응답 수신 중... (현재 {current_length}자)")
                    
                except Exception as e:
                    pass
                
                time.sleep(self.delays['check_interval'])
            
            print("⚠️ 시간 초과")
            return None
            
        except Exception as e:
            print(f"❌ Claude 응답 가져오기 실패: {e}")
            return None
    
    def run_conversation(self):
        """전체 대화 실행 - 세션 유지"""
        print("\n🤖 자동 대화 시작! (세션 유지 모드)")
        print("💡 모든 대화는 하나의 세션에서 진행됩니다.\n")
        
        self.is_running = True
        
        # 모든 프롬프트를 하나의 세션에서 처리
        for prompt_idx, prompt in enumerate(self.prompts):
            if not self.is_running:
                break
            
            print(f"\n{'='*60}")
            print(f"📌 프롬프트 {prompt_idx + 1}/{len(self.prompts)}: {prompt}")
            print(f"{'='*60}\n")
            
            # 1. GPT에 프롬프트 전송
            print("🔹 단계 1: GPT에 프롬프트 전송")
            if not self.send_to_gpt(prompt):
                print("❌ 프롬프트 전송 실패, 다음으로 진행...")
                continue
            
            # 2. 3회 왕복 대화
            for exchange in range(3):
                print(f"\n🔄 교환 {exchange + 1}/3")
                
                # GPT 응답 받기
                print("\n🔹 GPT 응답 가져오기")
                gpt_response = self.get_gpt_full_response()
                if not gpt_response:
                    print("❌ GPT 응답 실패")
                    break
                
                print(f"📥 GPT 응답 받음 ({len(gpt_response)}자)")
                
                # 대기
                time.sleep(self.delays['between_exchange'])
                
                # Claude에 전달
                print("\n🔹 Claude에 전달")
                if not self.send_to_claude(gpt_response):
                    print("❌ Claude 전달 실패")
                    break
                
                # Claude 응답 받기
                print("\n🔹 Claude 응답 가져오기")
                claude_response = self.get_claude_full_response()
                if not claude_response:
                    print("❌ Claude 응답 실패")
                    break
                
                print(f"📥 Claude 응답 받음 ({len(claude_response)}자)")
                
                # 마지막 교환이면 다음 프롬프트로
                if exchange == 2:
                    print("\n✅ 프롬프트 대화 완료!")
                    break
                
                # 대기
                time.sleep(self.delays['between_exchange'])
                
                # GPT에 전달
                print("\n🔹 GPT에 전달")
                if not self.send_to_gpt(claude_response):
                    print("❌ GPT 전달 실패")
                    break
            
            # 다음 프롬프트 전 대기
            if prompt_idx < len(self.prompts) - 1:
                print(f"\n⏸️ 5초 후 다음 프롬프트 진행...")
                time.sleep(5)
        
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
    
    print("🎮 AI 자동 대화 컨트롤러 v5.0 - 세션 유지")
    print("=" * 50)
    print("✨ v5.0 핵심 기능:")
    print("- 하나의 세션에서 모든 대화 진행")
    print("- 전체 응답 텍스트 가져오기")
    print("- 클립보드 사용으로 긴 텍스트 전송")
    print("- JavaScript로 안정적인 텍스트 추출")
    print("=" * 50)
    
    try:
        # 브라우저 시작
        controller.start_browsers()
        
        # 로그인 확인
        print("\n⚠️ 주의사항:")
        print("1. ChatGPT와 Claude에 로그인되어 있는지 확인")
        print("2. 두 브라우저 모두 채팅 화면이 보이는지 확인")
        print("3. 팝업이나 안내 메시지가 있다면 닫아주세요")
        
        input("\n✅ 준비가 완료되면 엔터를 눌러주세요...")
        
        # 대화 실행
        controller.run_conversation()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자가 중단했습니다")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        controller.stop()