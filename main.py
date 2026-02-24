import os
from scraper.ai_times import get_latest_news as get_aitimes
from scraper.pytorch_kr import get_latest_news as get_pytorchkr
from summarizer.gemini import summarize_articles
from notifier.discord import send_message
from state_manager.memory import load_sent_articles, save_sent_articles
from dotenv import load_dotenv

# 로컬(개발환경) 테스트용 환경 변수 로드 (.env 파일이 있을 경우)
load_dotenv()

def main():
    print("--- [시작] 최신 뉴스 크롤링 1시간주기 에이전트 가동 ---")
    
    # 1. 분야별 뉴스 데이터 수집
    ai_times_news = get_aitimes()
    pytorch_kr_news = get_pytorchkr()
    all_news = ai_times_news + pytorch_kr_news
    
    # 2. 기억 장소에서 이전에 읽은 뉴스 목록 불러오기
    sent_links = load_sent_articles()
    
    # 아직 읽지 않은(보내지 않은) 새로운 기사만 필터링
    new_articles = [news for news in all_news if news['link'] not in sent_links]
    
    if not new_articles:
        print("[종료] 1시간 동안 새롭게 수집된 기사가 없어 작업을 중단합니다.")
        return
        
    print(f"--- [진행] 총 {len(new_articles)}개의 새로운 기사를 발견했습니다. LLM에게 평가를 요청합니다 ---")
    
    # 3. Gemini API로 중요도 분석 및 요약 텍스트 생성
    summary_text = summarize_articles(new_articles)
    
    # 이번에 읽은 기사의 링크들을 기억소에 추가 (다음에 또 평가하지 않도록)
    sent_links.extend([news['link'] for news in new_articles])
    save_sent_articles(sent_links)
    
    if summary_text.startswith("요약 실패"):
        print(f"[종료] 요약 과정에서 오류가 발생했습니다. 메시지 전송 생략.\n사유: {summary_text}")
        return
        
    if summary_text.strip() == "SKIP":
        print("[종료] AI 에이전트 판단 결과: 이번 시간의 뉴스들은 중요도가 낮아 알림을 보내지 않습니다. (SKIP)")
        return
        
    print("--- [성공] 특급 뉴스 전문 요약 완료. 메시지 전송을 시작합니다 ---")
    
    # 4. 중요한 뉴스가 있다면 디스코드 채널로 푸시 전송
    send_message(summary_text)
    print("--- [종료] 이번 턴 단위 에이전트 업무 끝! ---")

if __name__ == "__main__":
    main()
