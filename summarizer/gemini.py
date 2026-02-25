import os
from google import genai

def summarize_articles(articles, mode="hourly"):
    """주어진 기사 목록을 Gemini API를 통해 요약합니다.
    """
    if not articles:
        return "새로운 기사가 없습니다."
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[Error] GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
        return "요약 실패: GEMINI_API_KEY 누락"

    if mode == "daily":
        prompt = """다음은 어제부터 밤사이 수집된 최신 AI 주요 뉴스들입니다.
독자들을 위해 '오전 8시 정기 뉴스 브리핑'을 작성해주세요. 

조건:
1. 전체 기사들 중에서 가장 중요한 핵심 뉴스 딱 5개만 엄선하여, 그 중요도 순서대로 나열해주세요.
2. 최상단에 `## 🌅 오늘 아침 AI 뉴스 브리핑` 이라는 제목을 달아주세요.
3. 선별된 5개의 기사는 아래의 [Top 5 출력 양식]을 정확히 지켜서 작성해주세요.
4. Top 5에 들지 못한 나머지 탈락한 기사들은 요약 없이 맨 아래에 [나머지 기사 양식]으로 제목과 링크만 나열해주세요.
5. 가독성이 좋도록 이모지(🌟, 📰 등)를 적절히 활용하세요.

[Top 5 출력 양식]
### 📰 (기사 제목)
(기사 핵심 요약 내용 2~3줄)
🔗 [원문 바로가기](실제 기사 URL)

[나머지 기사 양식]
---
📌 그 외 오늘 수집된 AI 뉴스들:
- [(기사 제목)](실제 기사 URL)
- [(기사 제목)](실제 기사 URL)

\n\n"""
    else:
        prompt = """다음은 1시간 동안 새롭게 수집된 AI 관련 뉴스입니다.
이 뉴스들 중에서 '인공지능 업계에 큰 파장을 부를 만한 특급/급상승 뉴스'나 '실무자에게 매우 유용한 핵심 정보'라고 판단되는 매우 중요한 기사가 있는지 심사하세요.

조건:
1. 매우 중요한 기사가 있다면, 최상단에 `## 🔥 실시간 급상승 AI 속보` 라는 제목을 달아주세요.
2. 중요한 기사를 선별했다면 아래의 [출력 양식]을 정확히 지켜서 작성해주세요.
3. 만약 모든 기사가 단순한 동향이거나 중요도가 낮다고 판단된다면, 어떠한 부연 설명도 없이 오직 대문자로 "SKIP" 이라고만 답변해 주세요.

[출력 양식]
### 🚨 (기사 제목)
(기사 핵심 요약 내용 2~3줄)
🔗 [원문 바로가기](실제 기사 URL)

\n\n"""
    for idx, article in enumerate(articles, 1):
        prompt += f"## {idx}. [{article['source']}] {article['title']}\n"
        prompt += f"- 내용: {article['description']}...\n- 원문 링크: {article['link']}\n\n"
        

    
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
