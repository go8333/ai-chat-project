from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
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
        
        # 딜레이 설정
        self.delays = {
            'typing': 0.02,      # 타이핑 속도
            'after_send': 3,     # 전송 후 대기
            'check_interval': 2, # 응답 체크 간격
            'max_wait': 60,      # 최대 대기 시간
            'between_exchange': 2  # 교환 간 대기
        }
        
        # 대화 기록
        self.conversation_history = []
    
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
        """브라우저 시작"""
        print("🚀 브라우저 시작 중...")
        
        # ChatGPT 브라우저
        gpt_options = webdriver.ChromeOptions()
        gpt_options.add_argument(f"user-data-dir={os.path.join(os.getcwd(), 'chrome_profile')}")
        gpt_options.add_argument("--disable-blink-features=AutomationControlled")
        gpt_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        self.gpt_driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=gpt_options
        )
        
        # Claude 브라우저
        claude_options = webdriver.ChromeOptions()
        claude_options.add_argument(f"user-data-dir={os.path.join(os.getcwd(), 'claude_profile')}")
        claude_options.add_argument("--disable-blink-features=AutomationControlled")
        claude_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        self.claude_driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=claude_options
        )
        
        print("✅ 브라우저 시작 완료\n")
    
    def start_new_chat(self, prompt_index):
        """각 프롬프트마다 새 채팅 시작"""
        print(f"\n🆕 프롬프트 {prompt_index + 1}을 위한 새 채팅 시작...")
        
        # GPT 새 채팅
        self.gpt_driver.get("https://chatgpt.com")
        time.sleep(3)
        
        # Claude 새 채팅
        self.claude_driver.get("https://claude.ai/new")
        time.sleep(3)
        
        # 대화 기록 초기화
        self.conversation_history = []
        
        print("✅ 새 채팅 준비 완료\n")
    
    def send_message(self, driver, message, platform="GPT"):
        """메시지 전송 (플랫폼 구분)"""
        try:
            if platform == "GPT":
                # GPT 입력창
                input_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "prompt-textarea"))
                )
            else:  # Claude
                # Claude 입력창
                input_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true']"))
                )
            
            # 클릭하고 기존 텍스트 삭제
            input_element.click()
            time.sleep(0.5)
            
            # 전체 선택 후 삭제
            input_element.send_keys(Keys.CONTROL + "a")
            time.sleep(0.2)
            input_element.send_keys(Keys.DELETE)
            time.sleep(0.5)
            
            # 메시지 입력
            for char in message:
                input_element.send_keys(char)
                time.sleep(self.delays['typing'])
            
            # 잠시 대기 후 전송
            time.sleep(1)
            input_element.send_keys(Keys.RETURN)
            
            print(f"📤 {platform}에 메시지 전송 완료")
            print(f"   내용: {message[:80]}...")
            
            # 전송 후 대기
            time.sleep(self.delays['after_send'])
            return True
            
        except Exception as e:
            print(f"❌ {platform} 메시지 전송 실패: {e}")
            return False
    
    def get_latest_response(self, driver, platform="GPT"):
        """최신 응답 가져오기 (개선된 버전)"""
        print(f"⏳ {platform} 응답 대기 중...")
        
        try:
            start_time = time.time()
            last_text = ""
            stable_count = 0
            
            while (time.time() - start_time) < self.delays['max_wait']:
                try:
                    if platform == "GPT":
                        # GPT 응답 찾기
                        responses = driver.find_elements(By.CSS_SELECTOR, "div[data-message-author-role='assistant']")
                    else:  # Claude
                        # Claude 응답 찾기
                        responses = driver.find_elements(By.CSS_SELECTOR, "div[data-test-render-count]")
                    
                    if responses:
                        # 가장 최근 응답
                        latest_response = responses[-1]
                        current_text = latest_response.text
                        
                        # 텍스트가 충분히 길고 변화가 없으면
                        if len(current_text) > 20 and current_text == last_text:
                            stable_count += 1
                            
                            if stable_count >= 3:
                                print(f"✅ {platform} 응답 완료!")
                                return current_text
                        else:
                            stable_count = 0
                            last_text = current_text
                    
                except Exception as e:
                    pass
                
                time.sleep(self.delays['check_interval'])
            
            # 시간 초과시 마지막 텍스트 반환
            if last_text and len(last_text) > 20:
                print(f"⚠️ {platform} 시간 초과, 마지막 응답 사용")
                return last_text
            
            print(f"❌ {platform} 응답을 가져올 수 없습니다")
            return None
            
        except Exception as e:
            print(f"❌ {platform} 응답 가져오기 오류: {e}")
            return None
    
    def run_single_prompt(self, prompt, prompt_index):
        """단일 프롬프트로 대화 실행"""
        print(f"\n{'='*60}")
        print(f"📌 프롬프트 {prompt_index + 1}: {prompt}")
        print(f"{'='*60}\n")
        
        # 새 채팅 시작
        self.start_new_chat(prompt_index)
        
        # 1. 초기 프롬프트를 GPT에 전송
        print("🔹 단계 1: GPT에 초기 프롬프트 전송")
        if not self.send_message(self.gpt_driver, prompt, "GPT"):
            return False
        
        # 2. 3회 왕복 대화
        for exchange in range(3):
            print(f"\n🔄 교환 {exchange + 1}/3")
            
            # GPT 응답 받기
            print("\n🔹 GPT 응답 가져오기")
            gpt_response = self.get_latest_response(self.gpt_driver, "GPT")
            if not gpt_response:
                print("❌ GPT 응답 실패")
                return False
            
            print(f"📥 GPT 응답: {gpt_response[:100]}...")
            self.conversation_history.append(("GPT", gpt_response))
            
            # 교환 간 대기
            time.sleep(self.delays['between_exchange'])
            
            # Claude에 GPT 응답만 전달 (불필요한 설명 없이)
            print("\n🔹 Claude에 GPT 응답 전달")
            if not self.send_message(self.claude_driver, gpt_response, "Claude"):
                return False
            
            # Claude 응답 받기
            print("\n🔹 Claude 응답 가져오기")
            claude_response = self.get_latest_response(self.claude_driver, "Claude")
            if not claude_response:
                print("❌ Claude 응답 실패")
                return False
            
            print(f"📥 Claude 응답: {claude_response[:100]}...")
            self.conversation_history.append(("Claude", claude_response))
            
            # 마지막 교환이면 종료
            if exchange == 2:
                print("\n✅ 프롬프트 대화 완료!")
                break
            
            # 교환 간 대기
            time.sleep(self.delays['between_exchange'])
            
            # GPT에 Claude 응답 전달
            print("\n🔹 GPT에 Claude 응답 전달")
            if not self.send_message(self.gpt_driver, claude_response, "GPT"):
                return False
        
        return True
    
    def save_conversation(self, prompt_index):
        """대화 내용 저장"""
        filename = f"conversation_prompt_{prompt_index + 1}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"프롬프트: {self.prompts[prompt_index]}\n")
            f.write("=" * 60 + "\n\n")
            
            for speaker, text in self.conversation_history:
                f.write(f"{speaker}:\n{text}\n\n")
                f.write("-" * 40 + "\n\n")
        
        print(f"💾 대화 내용이 {filename}에 저장되었습니다.")
    
    def run_auto_mode(self):
        """자동 모드 실행"""
        print("\n🤖 자동 대화 모드 시작!")
        print("💡 각 프롬프트별로 새 대화를 시작하고 3회 왕복합니다.\n")
        
        self.is_running = True
        
        for i, prompt in enumerate(self.prompts):
            if not self.is_running:
                break
            
            success = self.run_single_prompt(prompt, i)
            
            if success:
                self.save_conversation(i)
            else:
                print(f"⚠️ 프롬프트 {i + 1} 실패")
            
            # 다음 프롬프트 전 대기 (마지막 제외)
            if i < len(self.prompts) - 1:
                print(f"\n⏸️ 10초 후 다음 프롬프트 시작...")
                time.sleep(10)
        
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
    
    print("🎮 AI 자동 대화 컨트롤러 v4.0 - 최종 안정화")
    print("=" * 50)
    print("✨ v4.0 핵심 개선사항:")
    print("- 각 프롬프트마다 새 채팅 (3개만)")
    print("- GPT 응답 → Claude 전달 (설명 없이)")
    print("- Claude 응답 → GPT 전달")
    print("- 안정적인 응답 감지")
    print("- 대화 내용 자동 저장")
    print("=" * 50)
    
    try:
        # 브라우저 시작
        controller.start_browsers()
        
        # 수동으로 로그인 확인
        input("\n두 브라우저에서 로그인을 확인하고 엔터를 눌러주세요...")
        
        # 자동 모드 실행
        controller.run_auto_mode()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자가 중단했습니다")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        controller.stop()