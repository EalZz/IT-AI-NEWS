import os
import datetime
from scraper.ai_times import get_latest_news as get_aitimes
from scraper.pytorch_kr import get_latest_news as get_pytorchkr
from summarizer.gemini import summarize_articles
from notifier.discord import send_message
from state_manager.memory import load_sent_articles, save_sent_articles
from dotenv import load_dotenv

# 로컬(개발환경) 테스트용 환경 변수 로드 (.env 파일이 있을 경우)
load_dotenv()

def main():
    # 현재 시간 확인 (UTC 22시는 KST 07시 10분 실행 시점)
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    is_morning_briefing = (now_utc.hour == 22)
    
    if is_morning_briefing:
        print("--- [시작] 오전 7시 10분 정기 뉴스 브리핑 모드 ---")
    else:
        print("--- [시작] 실시간 급상승 뉴스 에이전트 모드 (1시간 주기) ---")
        
    all_news = get_aitimes() + get_pytorchkr()
    
    # 상태 파일 로드
    hourly_sent_links = load_sent_articles("sent_articles.json")
    daily_sent_links = load_sent_articles("daily_sent_articles.json")
    
    if is_morning_briefing:
        new_articles = [news for news in all_news if news['link'] not in daily_sent_links]
        
        if not new_articles:
            print("[종료] 어제 아침 이후 새롭게 수집된 기사가 없어 브리핑을 중단합니다.")
            return
            
        print(f"--- [진행] 총 {len(new_articles)}개의 최신 뉴스에 대해 🌅아침 브리핑 요약을 요청합니다 ---")
        summary_text = summarize_articles(new_articles, mode="daily")
        
        # 데일리 메모리 업데이트
        daily_sent_links.extend([news['link'] for news in new_articles])
        save_sent_articles(daily_sent_links, "daily_sent_articles.json")
        
        # 오전 8시에 읽은 기사들은 9시에 중복으로 속보 취급되지 않도록 hourly 메모리에도 추가
        hourly_new = [news['link'] for news in new_articles if news['link'] not in hourly_sent_links]
        if hourly_new:
            hourly_sent_links.extend(hourly_new)
            save_sent_articles(hourly_sent_links, "sent_articles.json")
            
        if summary_text.startswith("요약 실패"):
            print(f"[종료] 요약 과정에서 오류가 발생했습니다. 메시지 전송 생략.\n사유: {summary_text}")
            return
            
        print("--- [성공] 아침 브리핑 생성 완료. 전송합니다 ---")
        send_message(summary_text)

    else:
        new_articles = [news for news in all_news if news['link'] not in hourly_sent_links]
        
        if not new_articles:
            print("[종료] 1시간 동안 새롭게 수집된 기사가 없어 작업을 중단합니다.")
            return
            
        print(f"--- [진행] 총 {len(new_articles)}개의 새로운 기사를 발견했습니다. 에이전트에게 🔥중요도 평가를 요청합니다 ---")
        summary_text = summarize_articles(new_articles, mode="hourly")
        
        # 시간당 메모리 업데이트
        hourly_sent_links.extend([news['link'] for news in new_articles])
        save_sent_articles(hourly_sent_links, "sent_articles.json")
        
        if summary_text.startswith("요약 실패"):
            print(f"[종료] 요약 과정에서 오류가 발생했습니다. 메시지 전송 생략.\n사유: {summary_text}")
            return
            
        if summary_text.strip() == "SKIP":
            print("[종료] AI 에이전트 판단 결과: 이번 기사들은 중요도가 낮아 알림을 보내지 않습니다. (SKIP)")
            return
            
        print("--- [성공] 특급 속보 요약 완료. 메시지 전송을 시작합니다 ---")
        send_message(summary_text)

    print("--- [종료] 에이전트 워크플로우 끝! ---")

if __name__ == "__main__":
    main()
