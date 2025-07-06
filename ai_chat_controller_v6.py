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
        
        # 딜레이 설정
        self.delays = {
            'typing': 0.01,      # 타이핑 속도
            'after_send': 4,     # 전송 후 대기 (증가)
            'check_interval': 2, # 응답 체크 간격
            'max_wait': 120,     # 최대 대기 시간 (증가)
            'between_exchange': 4,  # 교환 간 대기 (증가)
            'initial_load': 10,  # 초기 로딩 대기
            'between_prompts': 10  # 프롬프트 간 대기
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
        
        # 채팅 페이지로 이동
        print("📍 ChatGPT 페이지 로딩...")
        self.gpt_driver.get("https://chatgpt.com")
        
        print("📍 Claude 페이지 로딩...")
        self.claude_driver.get("https://claude.ai/new")
        
        print(f"⏳ {self.delays['initial_load']}초 대기 중...")
        time.sleep(self.delays['initial_load'])
        
        print("✅ 브라우저 준비 완료\n")
    
    def send_to_gpt(self, message):
        """GPT에 메시지 전송 (수정됨)"""
        try:
            print("📤 GPT에 메시지 전송 시작...")
            
            # 여러 방법으로 입력창 찾기
            input_selectors = [
                (By.ID, "prompt-textarea"),
                (By.CSS_SELECTOR, "textarea[data-id='root']"),
                (By.CSS_SELECTOR, "div[contenteditable='true']")
            ]
            
            input_div = None
            for by, selector in input_selectors:
                try:
                    input_div = WebDriverWait(self.gpt_driver, 5).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    if input_div:
                        print(f"   ✓ 입력창 찾음: {selector}")
                        break
                except:
                    continue
            
            if not input_div:
                print("❌ GPT 입력창을 찾을 수 없습니다")
                return False
            
            # JavaScript로 포커스 및 클리어
            self.gpt_driver.execute_script("""
                var element = arguments[0];
                element.focus();
                element.click();
            """, input_div)
            time.sleep(0.5)
            
            # 기존 텍스트 삭제
            input_div.send_keys(Keys.CONTROL + "a")
            time.sleep(0.2)
            input_div.send_keys(Keys.DELETE)
            time.sleep(0.5)
            
            # 메시지 입력 (클립보드 방식)
            self.gpt_driver.execute_script("""
                navigator.clipboard.writeText(arguments[0]);
            """, message)
            time.sleep(0.5)
            
            input_div.send_keys(Keys.CONTROL + "v")
            time.sleep(1)
            
            # Enter로 전송
            input_div.send_keys(Keys.RETURN)
            
            print(f"✅ GPT 전송 완료!")
            print(f"   메시지: {message[:60]}...")
            time.sleep(self.delays['after_send'])
            return True
            
        except Exception as e:
            print(f"❌ GPT 전송 실패: {e}")
            # 에러 발생시 스크린샷 저장
            self.gpt_driver.save_screenshot("gpt_error.png")
            return False
    
    def send_to_claude(self, message):
        """Claude에 메시지 전송"""
        try:
            print("📤 Claude에 메시지 전송 시작...")
            
            # 입력창 찾기
            input_div = WebDriverWait(self.claude_driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div[contenteditable='true']"))
            )
            
            # 클릭 및 포커스
            input_div.click()
            time.sleep(0.5)
            
            # 기존 텍스트 삭제
            input_div.send_keys(Keys.CONTROL + "a")
            time.sleep(0.2)
            input_div.send_keys(Keys.DELETE)
            time.sleep(0.5)
            
            # 클립보드로 텍스트 복사
            self.claude_driver.execute_script("""
                navigator.clipboard.writeText(arguments[0]);
            """, message)
            time.sleep(0.5)
            
            # 붙여넣기
            input_div.send_keys(Keys.CONTROL + "v")
            time.sleep(1)
            
            # Enter로 전송
            input_div.send_keys(Keys.RETURN)
            
            print(f"✅ Claude 전송 완료!")
            print(f"   메시지: {message[:60]}...")
            time.sleep(self.delays['after_send'])
            return True
            
        except Exception as e:
            print(f"❌ Claude 전송 실패: {e}")
            self.claude_driver.save_screenshot("claude_error.png")
            return False
    
    def wait_for_response_complete(self, driver, platform="GPT"):
        """응답 완료 대기 (통합 함수)"""
        print(f"⏳ {platform} 응답 대기 중...")
        
        # 플랫폼별 셀렉터
        if platform == "GPT":
            selectors = [
                "div[data-message-author-role='assistant']",
                "div.group:has(div.text-token-text-primary)"
            ]
        else:  # Claude
            selectors = [
                "div[data-test-render-count]",
                "div.prose"
            ]
        
        start_time = time.time()
        last_text = ""
        stable_count = 0
        
        while (time.time() - start_time) < self.delays['max_wait']:
            try:
                # 여러 셀렉터 시도
                messages = None
                for selector in selectors:
                    try:
                        messages = driver.find_elements(By.CSS_SELECTOR, selector)
                        if messages:
                            break
                    except:
                        continue
                
                if messages:
                    latest_msg = messages[-1]
                    
                    # JavaScript로 전체 텍스트 가져오기
                    current_text = driver.execute_script("""
                        return arguments[0].innerText || arguments[0].textContent || '';
                    """, latest_msg)
                    
                    current_length = len(current_text) if current_text else 0
                    
                    # 텍스트가 안정화되었는지 확인
                    if current_length > 50 and current_text == last_text:
                        stable_count += 1
                        print(f"   응답 안정화 확인... ({stable_count}/3) - {current_length}자")
                        
                        if stable_count >= 3:
                            print(f"✅ {platform} 응답 완료! (총 {current_length}자)")
                            return current_text
                    else:
                        stable_count = 0
                        last_text = current_text
                        if current_length > 0:
                            print(f"   응답 수신 중... (현재 {current_length}자)")
                
            except Exception as e:
                pass
            
            time.sleep(self.delays['check_interval'])
        
        # 시간 초과시 마지막 텍스트 반환
        if last_text and len(last_text) > 50:
            print(f"⚠️ {platform} 시간 초과, 현재까지 받은 응답 사용 ({len(last_text)}자)")
            return last_text
        
        print(f"❌ {platform} 응답을 받지 못했습니다")
        return None
    
    def run_single_prompt_conversation(self, prompt, prompt_idx):
        """단일 프롬프트로 3회 왕복 대화"""
        print(f"\n{'='*70}")
        print(f"🎯 프롬프트 {prompt_idx + 1}/{len(self.prompts)}")
        print(f"📝 내용: {prompt}")
        print(f"{'='*70}\n")
        
        # 1. GPT에 초기 프롬프트 전송
        print("【1단계】 GPT에 초기 프롬프트 전송")
        if not self.send_to_gpt(prompt):
            return False
        
        # 2. 3회 왕복 대화
        for exchange in range(3):
            print(f"\n{'─'*50}")
            print(f"🔄 왕복 대화 {exchange + 1}/3")
            print(f"{'─'*50}\n")
            
            # GPT 응답 받기
            print("【GPT → Claude】 GPT 응답 대기")
            gpt_response = self.wait_for_response_complete(self.gpt_driver, "GPT")
            if not gpt_response:
                print("❌ GPT 응답 받기 실패")
                return False
            
            print(f"📥 GPT 응답 수신 완료 ({len(gpt_response)}자)")
            
            # 교환 간 대기
            print(f"⏸️ {self.delays['between_exchange']}초 대기...")
            time.sleep(self.delays['between_exchange'])
            
            # Claude에 전달
            print("\n【GPT → Claude】 Claude에 GPT 응답 전달")
            if not self.send_to_claude(gpt_response):
                print("❌ Claude 전달 실패")
                return False
            
            # Claude 응답 받기
            print("【Claude → GPT】 Claude 응답 대기")
            claude_response = self.wait_for_response_complete(self.claude_driver, "Claude")
            if not claude_response:
                print("❌ Claude 응답 받기 실패")
                return False
            
            print(f"📥 Claude 응답 수신 완료 ({len(claude_response)}자)")
            
            # 마지막 교환이면 종료
            if exchange == 2:
                print(f"\n✅ 프롬프트 {prompt_idx + 1} 완료!")
                return True
            
            # 교환 간 대기
            print(f"⏸️ {self.delays['between_exchange']}초 대기...")
            time.sleep(self.delays['between_exchange'])
            
            # GPT에 Claude 응답 전달
            print("\n【Claude → GPT】 GPT에 Claude 응답 전달")
            if not self.send_to_gpt(claude_response):
                print("❌ GPT 전달 실패")
                return False
        
        return True
    
    def run_all_conversations(self):
        """모든 프롬프트 순차 실행"""
        print("\n🚀 자동 대화 시작!")
        print("📋 총 프롬프트 수:", len(self.prompts))
        print("🔄 각 프롬프트당 3회 왕복 대화")
        print("💬 하나의 세션에서 모든 대화 진행\n")
        
        self.is_running = True
        successful_prompts = 0
        
        for idx, prompt in enumerate(self.prompts):
            if not self.is_running:
                break
            
            # 프롬프트 실행
            success = self.run_single_prompt_conversation(prompt, idx)
            
            if success:
                successful_prompts += 1
                print(f"\n✅ 성공: {successful_prompts}/{idx + 1}")
            else:
                print(f"\n⚠️ 실패: 프롬프트 {idx + 1}")
            
            # 다음 프롬프트 전 대기 (마지막 제외)
            if idx < len(self.prompts) - 1:
                print(f"\n⏸️ 다음 프롬프트까지 {self.delays['between_prompts']}초 대기...")
                for i in range(self.delays['between_prompts'], 0, -1):
                    print(f"   {i}초...", end='\r')
                    time.sleep(1)
                print()
        
        print(f"\n{'='*70}")
        print(f"🎊 모든 대화 완료!")
        print(f"📊 결과: {successful_prompts}/{len(self.prompts)} 성공")
        print(f"{'='*70}\n")
        
        # 브라우저는 열어둔 채로 유지
        print("💡 브라우저는 계속 열려있습니다.")
        print("🔚 프로그램을 종료하려면 Ctrl+C를 누르세요.")
    
    def stop(self):
        """프로그램 종료 (브라우저 닫기)"""
        print("\n⏹️ 프로그램 종료 중...")
        self.is_running = False
        
        try:
            if self.gpt_driver:
                self.gpt_driver.quit()
                print("✅ GPT 브라우저 종료")
        except:
            pass
        
        try:
            if self.claude_driver:
                self.claude_driver.quit()
                print("✅ Claude 브라우저 종료")
        except:
            pass
        
        print("👋 프로그램을 종료합니다. 감사합니다!")

# 메인 실행
if __name__ == "__main__":
    controller = AIController()
    
    print("🎮 AI 자동 대화 컨트롤러 v6.0 - 완성 버전")
    print("=" * 60)
    print("✨ v6.0 주요 기능:")
    print("- ✅ GPT ↔ Claude 양방향 메시지 전달")
    print("- ✅ 하나의 세션에서 모든 대화 진행")
    print("- ✅ 프롬프트별 3회 왕복 대화")
    print("- ✅ 브라우저 자동 종료 방지")
    print("- ✅ 상세한 진행 상황 표시")
    print("=" * 60)
    
    try:
        # 브라우저 시작
        controller.start_browsers()
        
        # 준비 확인
        print("\n⚠️ 시작 전 확인사항:")
        print("1. ChatGPT 로그인 상태 확인")
        print("2. Claude 로그인 상태 확인")
        print("3. 두 브라우저 모두 채팅 화면인지 확인")
        print("4. 팝업이나 안내 메시지 닫기")
        
        input("\n✅ 준비가 완료되면 엔터를 눌러주세요...")
        
        # 모든 대화 실행
        controller.run_all_conversations()
        
        # 종료 대기
        input("\n🔚 브라우저를 닫고 종료하려면 엔터를 누르세요...")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자가 중단했습니다 (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()
    finally:
        controller.stop()