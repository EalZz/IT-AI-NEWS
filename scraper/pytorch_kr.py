import requests
import xml.etree.ElementTree as ET

def get_latest_news():
    """PyTorch KR 뉴스(Discourse)에서 최신 글 3개를 가져옵니다 (RSS 기준)."""
    # PyTorch KR 커뮤니티 뉴스는 Discourse 기반이므로 RSS 피드가 가장 안정적입니다.
    url = "https://discuss.pytorch.kr/latest.rss"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    articles = []
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        
        # RSS <channel> 안의 <item> 속성 파싱
        for item in root.findall('./channel/item')[:3]:
            title = item.find('title').text
            link = item.find('link').text
            # HTML 태그가 섞여 있을 수 있으므로 앞부분만 사용
            raw_desc = item.find('description').text or ""
            
            articles.append({
                "source": "PyTorch KR",
                "title": title.strip(),
                "link": link.strip(),
                "description": raw_desc[:200] + "..." if len(raw_desc) > 200 else raw_desc
            })

    except Exception as e:
        print(f"[Error] PyTorch KR 크롤링 실패: {e}")
        
    return articles

if __name__ == "__main__":
    # Test execution
    news = get_latest_news()
    for n in news:
        print(n)
