import os
import re
import requests

def send_message(message):
    """디스코드 웹훅을 통해 요약된 기사 메시지를 전송합니다. 쉼표(,)로 구분하면 여러 채널/계정에 동시 전송됩니다."""
    webhook_urls_str = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_urls_str:
        print("[Error] DISCORD_WEBHOOK_URL 환경 변수가 설정되지 않았습니다.")
        return False
        
    # 쉼표(,) 기준으로 분리하여 리스트 생성
    webhook_urls = [url.strip() for url in webhook_urls_str.split(',') if url.strip()]
        
    # --- 스마트 뉴스 블록 분할 로직 ---
    MAX_LEN = 2000
    message_chunks = []
    
    if len(message) <= MAX_LEN:
        message_chunks.append(message)
    else:
        # 1단계: 나머지 뉴스 섹션 위치 파악 (--- 또는 📌 기준)
        remaining_marker = re.search(r'(?m)^---\s*\n?📌', message) or re.search(r'(?m)^📌', message)
        
        main_part = message
        remaining_part = ""
        
        if remaining_marker:
            idx = remaining_marker.start()
            main_part = message[:idx].strip()
            remaining_part = message[idx:].strip()
            
        # 2단계: 메인 뉴스(Top 5) 처리 - 뉴스 블록(###) 단위로 분할
        if len(main_part) <= MAX_LEN:
            message_chunks.append(main_part)
        else:
            # ### 기호를 기준으로 뉴스 블록을 추출 (첫 번째 덩어리는 제목 포함)
            blocks = re.split(r'(?m)(?=^###)', main_part)
            current_chunk = ""
            for block in blocks:
                if not block.strip(): continue
                if len(current_chunk) + len(block) <= MAX_LEN:
                    current_chunk += block
                else:
                    if current_chunk:
                        message_chunks.append(current_chunk.strip())
                    current_chunk = block
            if current_chunk:
                message_chunks.append(current_chunk.strip())
            
        # 3단계: 나머지 뉴스 목록 처리
        if remaining_part:
            if len(remaining_part) <= MAX_LEN:
                message_chunks.append(remaining_part)
            else:
                # 안전장치: 나머지 섹션조차 너무 길면 줄 단위로 분할 (링크 보호)
                lines = remaining_part.split('\n')
                current_chunk = ""
                for line in lines:
                    if len(current_chunk) + len(line) + 1 <= MAX_LEN:
                        current_chunk += line + '\n'
                    else:
                        if current_chunk:
                            message_chunks.append(current_chunk.strip())
                        current_chunk = line + '\n'
                if current_chunk:
                    message_chunks.append(current_chunk.strip())
    # --- 스마트 분할 로직 끝 ---

    all_success = True
    for url in webhook_urls:
        for chunk in message_chunks:
            data = {
                "content": chunk,
                "username": "뉴스 요약 봇",
                "avatar_url": "https://cdn-icons-png.flaticon.com/512/3260/3260838.png"
            }
            try:
                response = requests.post(url, json=data)
                response.raise_for_status()
                print(f"[Success] 웹훅({url[:30]}...) 전송 완료!")
            except Exception as e:
                print(f"[Error] 웹훅 전송 실패 ({url[:30]}...): {e}")
                all_success = False
            
    return all_success
