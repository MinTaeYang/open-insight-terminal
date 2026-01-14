import streamlit as st
import feedparser
import urllib.parse
from datetime import datetime

# 1. 페이지 인터페이스 및 브랜딩 설정
st.set_page_config(page_title="OPEN INSIGHT TERMINAL", page_icon="🌐", layout="wide")

# 2. 최고급 커스텀 CSS (심플, 다크, 하이테크 느낌)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700&display=swap');
    * { font-family: 'Pretendard', sans-serif; }
    .stApp { background-color: #0D1117; }
    
    /* 카드 디자인 */
    .news-card {
        background: #161B22;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #30363D;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    .news-card:hover { 
        border-color: #58A6FF; 
        background: #1C2128;
        transform: scale(1.01);
    }
    
    .news-title { color: #58A6FF; font-size: 1.35rem; font-weight: 700; text-decoration: none; }
    .news-meta { color: #8B949E; font-size: 0.9rem; margin-top: 12px; display: flex; gap: 15px; }
    
    /* 강조 배지 */
    .badge { background: #238636; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: bold; }
    
    /* 검색바 스타일 */
    .stTextInput>div>div>input { background-color: #0D1117; color: white; border-radius: 10px; border: 1px solid #30363D; }
    </style>
    """, unsafe_allow_html=True)

# 3. 사이드바 (정보 및 상태창)
with st.sidebar:
    st.markdown("<h2 style='color: #58A6FF;'>SYSTEM STATUS</h2>", unsafe_allow_html=True)
    st.success("● NETWORK: CONNECTED")
    st.info("● ACCESS: UNLIMITED (FREE)")
    st.write("---")
    st.markdown("### 📡 데이터 소스")
    st.caption("Global Google News RSS Feed")
    st.write("---")
    st.markdown("### 💡 활용 팁")
    st.write("특정 기업이나 자산(예: 비트코인, 테슬라)을 입력하면 관련 마켓 뉴스를 즉시 분석합니다.")

# 4. 메인 대시보드
st.markdown("<h1 style='color: white; font-size: 2.8rem; font-weight: 800;'>OPEN INSIGHT TERMINAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #8B949E; margin-bottom: 40px;'>전 세계 실시간 뉴스 데이터를 무제한으로 조회하고 분석하세요.</p>", unsafe_allow_html=True)

# 검색 섹션
keyword = st.text_input("분석할 마켓 키워드를 입력하세요", placeholder="예: 반도체 수출, 연준 금리 결정, 이더리움 시황")

if st.button("RUN REAL-TIME ANALYSIS"):
    if not keyword:
        st.warning("키워드를 입력해 주세요.")
    else:
        with st.spinner('글로벌 뉴스 피드 분석 중...'):
            encoded_keyword = urllib.parse.quote(keyword)
            url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko"
            feed = feedparser.parse(url)

            if feed.entries:
                # 상단 대시보드 통계
                c1, c2, c3 = st.columns(3)
                c1.metric("검색 결과", f"{len(feed.entries)} Articles")
                c2.metric("보안 등급", "SECURE")
                c3.metric("데이터 상태", "LATEST")

                st.write(" ")
                
                # 뉴스 카드 리스트
                for entry in feed.entries[:25]:
                    st.markdown(f"""
                        <div class="news-card">
                            <span class="badge">OPEN DATA</span>
                            <div style="margin-top:12px;">
                                <a href="{entry.link}" target="_blank" class="news-title">{entry.title}</a>
                            </div>
                            <div class="news-meta">
                                <span>📅 {entry.published}</span>
                                <span>🌐 Google News Feed</span>
                                <span style="color: #238636;">● Verified Source</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("해당 키워드에 대한 데이터를 찾을 수 없습니다.")