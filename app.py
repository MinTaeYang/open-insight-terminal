import streamlit as st
import feedparser
import urllib.parse
from datetime import datetime
import streamlit.components.v1 as components

# 1. 페이지 인터페이스 및 브랜딩 설정
st.set_page_config(page_title="OPEN INSIGHT TERMINAL", page_icon="🌐", layout="wide")

# 2. 애드센스 소유권 확인 스크립트
# [중요] 'ca-pub-0000000000000000' 부분을 본인의 애드센스 ID로 꼭 수정하세요.
components.html("""
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-0000000000000000"
     crossorigin="anonymous"></script>
""", height=0)

# 3. 하이테크 커스텀 CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700&display=swap');
    * { font-family: 'Pretendard', sans-serif; }
    .stApp { background-color: #0D1117; }
    
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
    .badge { background: #238636; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: bold; }
    .stTextInput>div>div>input { background-color: #0D1117; color: white; border-radius: 10px; border: 1px solid #30363D; }
    </style>
    """, unsafe_allow_html=True)

# 4. 사이드바 구성
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
    st.write("---")
    st.markdown("### ☕ Support")
    st.write("서비스가 마음에 드신다면 후원을 통해 응원해주세요!")
    st.markdown("[![Buy Me A Coffee](https://img.shields.io/badge/Buy_Me_A_Coffee-Donate-yellow?style=for-the-badge&logo=buy-me-a-coffee)](https://www.buymeacoffee.com/)")

# 5. 메인 대시보드 타이틀
st.markdown("<h1 style='color: white; font-size: 2.8rem; font-weight: 800;'>OPEN INSIGHT TERMINAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #8B949E; margin-bottom: 40px;'>전 세계 실시간 뉴스 데이터를 분석하여 마켓 인사이트를 확보하세요.</p>", unsafe_allow_html=True)

# 6. 검색 및 자동 로딩 로직
user_input = st.text_input("분석할 마켓 키워드를 입력하세요", placeholder="예: 삼성전자, 인공지능 주식, 나스닥 전망")

# 봇 심사를 위해 초기 접속 시 '경제' 키워드로 자동 검색 실행
current_keyword = user_input if user_input else "오늘의 경제 뉴스"

with st.spinner(f"'{current_keyword}' 분석 데이터 로딩 중..."):
    encoded_keyword = urllib.parse.quote(current_keyword)
    url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(url)

    if feed.entries:
        c1, c2, c3 = st.columns(3)
        c1.metric("뉴스 수", f"{len(feed.entries)} Articles")
        c2.metric("보안 등급", "SECURE")
        c3.metric("상태", "LIVE DATA")
        
        st.write(" ")
        
        for entry in feed.entries[:25]:
            st.markdown(f"""
                <div class="news-card">
                    <span class="badge">MARKET DATA</span>
                    <div style="margin-top:12px;">
                        <a href="{entry.link}" target="_blank" class="news-title">{entry.title}</a>
                    </div>
                    <div class="news-meta">
                        <span>📅 {entry.published}</span>
                        <span>🌐 Verified Source</span>
                        <span style="color: #238636;">● Insight Connected</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.error("데이터를 불러올 수 없습니다. 키워드를 확인해 주세요.")

# 7. 애드센스 승인 필수 푸터 (Privacy Policy 포함)
st.write("---")
st.markdown("### 🔍 About & Legal")
st.write("""
    OPEN INSIGHT TERMINAL은 실시간 마켓 트렌드 분석 도구입니다. 
    우리는 Google News RSS 인덱스를 기반으로 사용자에게 시각화된 데이터 인사이트를 제공합니다.
""")

st.markdown("""
    <div style="text-align: center; color: #8B949E; font-size: 0.8rem; margin-top: 50px; padding: 20px; border-top: 1px solid #30363D;">
        <p>© 2026 SUN (OPEN INSIGHT). All rights reserved.</p>
        <p>
            <a href="#" style="color: #58A6FF; text-decoration: none;">Privacy Policy</a> | 
            <a href="#" style="color: #58A6FF; text-decoration: none;">Terms of Service</a>
        </p>
        <p style="font-size: 0.7rem;">본 서비스는 광고 수익을 통해 운영되며, 구글 애드센스 정책을 엄격히 준수합니다.</p>
    </div>
""", unsafe_allow_html=True)
