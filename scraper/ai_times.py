import requests
from bs4 import BeautifulSoup

def get_latest_news():
    """AI타임스에서 최신 기사 3개를 가져옵니다."""
    url = "https://www.aitimes.com/news/articleList.html?sc_section_code=S1N10&view_type=sm"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    articles = []
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # AI타임스의 리스트 블록 탐색 (.list-block 또는 #user-container 하위 요소)
        items = soup.select('.list-block')
        
        for item in items[:3]: # 상위 3개 기사만 추출
            title_tag = item.select_one('.list-titles a')
            if not title_tag:
                continue
                
            title = title_tag.text.strip()
            link = title_tag['href']
            if not link.startswith('http'):
                link = "https://www.aitimes.com" + link
                
            desc_tag = item.select_one('.list-summary')
            desc = desc_tag.text.strip() if desc_tag else ""
            
            articles.append({
                "source": "AI타임스",
                "title": title,
                "link": link,
                "description": desc
            })
            
    except Exception as e:
        print(f"[Error] AI타임스 크롤링 실패: {e}")
        
    return articles

if __name__ == "__main__":
    # Test execution
    news = get_latest_news()
    for n in news:
        print(n)
