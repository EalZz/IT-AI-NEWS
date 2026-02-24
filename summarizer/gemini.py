import os
from google import genai

def summarize_articles(articles):
    """주어진 기사 목록을 Gemini API를 통해 요약합니다.
    최신 google-genai 라이브러리와 gemini-2.0-flash 모델을 사용합니다.
    """
    if not articles:
        return "새로운 기사가 없습니다."
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[Error] GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
        return "요약 실패: GEMINI_API_KEY 누락"

    # 프롬프트 구성
    prompt = "다음은 오늘 수집된 주요 AI 관련 뉴스입니다. 매일 아침 전문가가 브리핑해주듯 각 기사의 핵심만 2~3줄 이내로 매우 직관적으로 요약해주세요.\n\n"
    for idx, article in enumerate(articles, 1):
        prompt += f"## {idx}. [{article['source']}] {article['title']}\n"
        prompt += f"- 내용: {article['description']}...\n- 원문 링크: {article['link']}\n\n"
        
    prompt += "---\n결과물은 디스코드 채널로 전송될 것입니다. 가독성이 좋도록 이모지(🌟, 📰 등)를 활용하며, 불필요한 서문 없이 본론만 마크다운 포맷으로 깔끔하게 작성해주세요."
    prompt += "기사별 원문 링크는 반드시 포함되어야 합니다."
    
    try:
        client = genai.Client(api_key=api_key)
        
        # 1. API 키로 접근 가능한 실제 모델 목록을 동적으로 조회
        available_models = []
        for m in client.models.list():
            available_models.append(m.name)
            
        print("[디버그] 사용 가능한 모델 목록:", available_models)
        
        # 2. 'flash'가 포함된 가장 안정적인 무료 모델 자동 선택
        target_model = 'gemini-1.5-flash'
        
        # 만약 기본 모델이 안 보인다면, 목록에 있는 첫 번째 flash 모델이나 기본 모델 선택
        flash_models = [m for m in available_models if 'flash' in m.lower()]
        if flash_models:
            target_model = flash_models[0]
        elif available_models:
            target_model = available_models[0] # 임의의 가능한 모델 선택
            
        # 모델 이름 앞의 'models/' 제거 (SDK가 자동으로 붙이므로 중복 방지)
        if target_model.startswith('models/'):
            target_model = target_model.replace('models/', '')
            
        print(f"[진행] 선택된 모델명: {target_model}")
        
        # 3. 요약 수행
        response = client.models.generate_content(
            model=target_model,
            contents=prompt,
        )
        
        if not response.text:
            return "요약 실패: 결과 텍스트 없음"
            
        return response.text
        
    except Exception as e:
        error_msg = str(e)
        print(f"[Error] Gemini API 호출 중 오류 발생: {error_msg}")
        
        # 429 Limit 0 에러 감지 시 원인 안내
        if '429' in error_msg and 'limit: 0' in error_msg.lower():
            print("\n========================================================")
            print("[중요] Google Gemini API의 무료 티어(Free Tier) 국가 제한에 걸렸습니다!")
            print("현재 GitHub Actions 서버가 구글 무료 API 사용이 금지된 지역(예: 유럽 등)에 배정되었기 때문입니다.")
            print("해결 방법: 구글 클라우드 콘솔에서 API 키 프로젝트에 '결제 수단(신용카드)'을 등록하여 한도를 푸셔야 합니다. (소량 사용 시 요금은 청구되지 않습니다.)")
            print("========================================================\n")
            
        return f"요약 실패: API 오류 발생 ({target_model})"
