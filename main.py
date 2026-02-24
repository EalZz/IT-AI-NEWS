import os
from scraper.ai_times import get_latest_news as get_aitimes
from scraper.pytorch_kr import get_latest_news as get_pytorchkr
from summarizer.gemini import summarize_articles
from notifier.discord import send_message
from dotenv import load_dotenv

# 로컬(개발환경) 테스트용 환경 변수 로드 (.env 파일이 있을 경우)
load_dotenv()

def main():
    print("--- [시작] 최신 뉴스 크롤링 파이프라인 우주선 발사 ---")
    
    # 1. 분야별 뉴스 데이터 수집
    ai_times_news = get_aitimes()
    pytorch_kr_news = get_pytorchkr()
    
    all_news = ai_times_news + pytorch_kr_news
    
    if not all_news:
        print("[종료] 수집된 새로운 기사가 없어 작업을 중단합니다.")
        return
        
    print(f"--- [성공] 총 {len(all_news)}개의 핫한 기사 수집 완료 ---")
    
    # 2. Gemini API로 요약 텍스트 생성
    print("--- [진행] Gemini가 기사들을 읽고 요약하는 중 ---")
    summary_text = summarize_articles(all_news)
    
    # 에러 혹은 API 키 부재 등의 문제로 요약 실패 시 처리
    if summary_text.startswith("요약 실패"):
        print("[종료] 요약 과정에서 치명적인 오류가 발생하여 메시지를 전송하지 않습니다.")
        return
        
    print("--- [성공] 전문 요약 완료 ---")
    
    # 3. 디스코드 채널로 푸시 전송
    print("--- [진행] 디스코드 채널로 실시간 푸시 전송 중 ---")
    send_message(summary_text)
    print("--- [종료] 오늘 업무 끝! ---")

if __name__ == "__main__":
    main()
