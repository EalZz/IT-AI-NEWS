import os
import requests

def send_message(message):
    """디스코드 웹훅을 통해 요약된 기사 메시지를 전송합니다. 쉼표(,)로 구분하면 여러 채널/계정에 동시 전송됩니다."""
    webhook_urls_str = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_urls_str:
        print("[Error] DISCORD_WEBHOOK_URL 환경 변수가 설정되지 않았습니다.")
        return False
        
    # 쉼표(,) 기준으로 분리하여 리스트 생성
    webhook_urls = [url.strip() for url in webhook_urls_str.split(',') if url.strip()]
        
    data = {
        "content": message,
        "username": "뉴스 요약 봇",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/3260/3260838.png"  # 임의의 뉴스 봇 아이콘
    }
    
    all_success = True
    for url in webhook_urls:
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            print(f"[Success] 웹훅({url[:30]}...) 전송 완료!")
        except Exception as e:
            print(f"[Error] 웹훅 전송 실패 ({url[:30]}...): {e}")
            all_success = False
            
    return all_success
