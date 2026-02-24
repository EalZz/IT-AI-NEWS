import requests
import xml.etree.ElementTree as ET

def get_latest_news():
    """AI타임스에서 최신 기사 3개를 가져옵니다 (RSS 1.0/2.0 기준)."""
    url = "https://www.aitimes.com/rss/allArticle.xml"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    articles = []
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # XML 네임스페이스가 포함된 경우를 고려하여 파싱
        root = ET.fromstring(response.content)
        
        # 주로 channel 하위의 item들을 찾습니다.
        for item in root.findall('.//item')[:3]:
            title_elem = item.find('title')
            link_elem = item.find('link')
            desc_elem = item.find('description')
            
            title = title_elem.text if title_elem is not None else ""
            link = link_elem.text if link_elem is not None else ""
            raw_desc = desc_elem.text if desc_elem is not None else ""
            
            articles.append({
                "source": "AI타임스",
                "title": title.strip(),
                "link": link.strip(),
                "description": raw_desc[:200] + "..." if len(raw_desc) > 200 else raw_desc
            })

    except Exception as e:
        print(f"[Error] AI타임스 크롤링 실패: {e}")
        
    return articles

if __name__ == "__main__":
    # Test execution
    news = get_latest_news()
    for n in news:
        print(n)
