import json
import os

def load_sent_articles(filename="sent_articles.json"):
    """지금까지 알림을 보냈거나 확인한 기사들의 링크 목록을 불러옵니다."""
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Warning] 상태 파일 읽기 실패. 빈 목록으로 시작: {e}")
            return []
    return []

def save_sent_articles(articles, filename="sent_articles.json"):
    """확인완료된 기사 목록을 JSON 파일에 저장합니다. 무한정 커지는 것을 막기 위해 최근 100개만 유지합니다."""
    # 최대 100개까지만 유지 (메모리 최적화)
    articles_to_save = articles[-100:] if len(articles) > 100 else articles
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(articles_to_save, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"[Error] 상태 파일 저장 실패: {e}")
