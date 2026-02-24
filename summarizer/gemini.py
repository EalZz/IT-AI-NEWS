import os
import google.generativeai as genai

def summarize_articles(articles):
    """주어진 기사 목록을 Gemini API를 통해 요약합니다.
    기능 구현 시 무료 티어인 gemini-1.5-flash 모델을 활용합니다.
    """
    if not articles:
        return "새로운 기사가 없습니다."
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[Error] GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
        return "요약 실패: GEMINI_API_KEY 누락"

    genai.configure(api_key=api_key)
    # gemini-1.5-flash 모델을 사용하여 빠르고 저렴(무료)하게 요약
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # 프롬프트 구성
    prompt = "다음은 오늘 수집된 주요 AI 관련 뉴스입니다. 매일 아침 전문가가 브리핑해주듯 각 기사의 핵심만 2~3줄 이내로 매우 직관적으로 요약해주세요.\n\n"
    
    for idx, article in enumerate(articles, 1):
        prompt += f"## {idx}. [{article['source']}] {article['title']}\n"
        prompt += f"- 내용: {article['description']}...\n- 원문 링크: {article['link']}\n\n"
        
    prompt += "---\n결과물은 디스코드 채널로 전송될 것입니다. 가독성이 좋도록 이모지(🌟, 📰 등)를 활용하며, 불필요한 서문 없이 본론만 마크다운 포맷으로 깔끔하게 작성해주세요."
    prompt += "기사별 원문 링크는 반드시 포함되어야 합니다."
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"[Error] Gemini API 호출 중 오류 발생: {e}")
        return "요약 실패: API 오류 발생"
