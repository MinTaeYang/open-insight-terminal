import re
import urllib.parse
from urllib.parse import urlparse
from difflib import SequenceMatcher
from typing import List, Dict

import feedparser
import streamlit as st
import streamlit.components.v1 as components

# ----------------------------
# 1. Page Configuration & AdSense Verification (Best-effort on Streamlit)
# ----------------------------
st.set_page_config(
    page_title="OPEN INSIGHT",
    page_icon="🗞️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ✅ [중요] AdSense 소유권 확인 메타 태그 (Streamlit에서 가능한 최선의 방식)
# Streamlit Community Cloud는 index.html <head>를 직접 수정할 수 없어서,
# JS로 document.head에 meta를 실제 삽입하는 방식으로 "최대한" 맞춥니다.
components.html(
    """
    <script>
      (function () {
        try {
          var existing = document.querySelector('head meta[name="google-adsense-account"]');
          if (!existing) {
            var meta = document.createElement('meta');
            meta.setAttribute('name', 'google-adsense-account');
            meta.setAttribute('content', 'ca-pub-5334002072937874');
            document.head.appendChild(meta);
          }
        } catch (e) {
          // ignore
        }
      })();
    </script>
    """,
    height=0,
)

# ----------------------------
# 2. UI Style (minimal, list)
# ----------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;700&display=swap');
* { font-family: 'Pretendard', sans-serif; }

.stApp { background-color: #0D1117; color: #E6EDF3; }

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
/* ✅ header는 숨기지 않음: 좌측 상단 사이드바 토글(☰/>)이 필요 */

.block-container {
  padding-top: 56px;
  padding-bottom: 48px;
  max-width: 980px;
}

.hero-title {
  font-size: 40px;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin: 0 0 10px 0;
}
.hero-subtitle {
  color: #94A3B8;
  font-size: 15px;
  margin: 0 0 16px 0;
}

.stTextInput > div > div > input {
  background-color: #0B1220;
  color: #E6EDF3;
  border-radius: 14px;
  border: 1px solid #1F2A3A;
  padding: 12px 14px;
}
.stTextInput > div > div > input:focus {
  border-color: #2B3B52;
  box-shadow: none;
}

.stButton > button {
  background: #E6EDF3;
  color: #0D1117;
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: 12px;
  padding: 10px 14px;
}
.stButton > button:hover {
  background: #FFFFFF;
  border-color: rgba(148, 163, 184, 0.35);
}

.news-item {
  padding: 14px 2px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.14);
}
.news-link {
  color: #E6EDF3;
  text-decoration: none;
  font-size: 18px;
  font-weight: 650;
  line-height: 1.35;
}
.news-link:hover { text-decoration: underline; }

.news-meta {
  margin-top: 6px;
  color: #94A3B8;
  font-size: 13px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.meta-pill {
  border: 1px solid rgba(148, 163, 184, 0.18);
  color: #94A3B8;
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 12px;
}

.small-footer {
  color: rgba(148, 163, 184, 0.7);
  font-size: 12px;
  margin-top: 22px;
  line-height: 1.55;
}
.small-footer a {
  color: rgba(148, 163, 184, 0.9);
  text-decoration: none;
}
.small-footer a:hover { text-decoration: underline; }

.small-footer .note {
  display: block;
  margin-top: 6px;
  color: rgba(148, 163, 184, 0.65);
}
</style>
""",
    unsafe_allow_html=True,
)

# ----------------------------
# 3. Constants & Helpers
# ----------------------------
DEFAULT_QUERY = "오늘의 경제"

if "run_search" not in st.session_state:
    st.session_state.run_search = True
if "query" not in st.session_state:
    st.session_state.query = ""
if "last_keyword" not in st.session_state:
    st.session_state.last_keyword = ""
if "feed_entries" not in st.session_state:
    st.session_state.feed_entries = []
if "recent_keywords" not in st.session_state:
    st.session_state.recent_keywords = []
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "limit" not in st.session_state:
    st.session_state.limit = 25
if "pick_recent" not in st.session_state:
    st.session_state.pick_recent = ""
if "pick_fav" not in st.session_state:
    st.session_state.pick_fav = ""


def trigger_search():
    st.session_state.run_search = True


def set_query_and_search(q: str):
    st.session_state.query = (q or "").strip()
    st.session_state.run_search = True


def push_recent(q: str, max_n: int = 8):
    q = q.strip()
    if not q:
        return
    rec = [x for x in st.session_state.recent_keywords if x != q]
    rec.insert(0, q)
    st.session_state.recent_keywords = rec[:max_n]


def clear_recent():
    st.session_state.recent_keywords = []
    st.session_state.pick_recent = ""


def toggle_favorite(q: str):
    q = q.strip()
    if not q:
        return
    fav = st.session_state.favorites
    if q in fav:
        st.session_state.favorites = [x for x in fav if x != q]
    else:
        st.session_state.favorites = [q] + fav


def is_favorite(q: str) -> bool:
    return q.strip() in st.session_state.favorites


def normalize_title(title: str) -> str:
    t = title.strip()
    t = re.sub(r"\s+-\s+[^-]{2,}$", "", t).strip()
    t = re.sub(r"[\u200b\u200c\u200d]+", "", t)
    t = re.sub(r"[^\w\s가-힣]", " ", t)
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t


def similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def dedupe_entries(entries: List[Dict], title_sim_threshold: float = 0.90) -> List[Dict]:
    seen_links = set()
    kept_titles = []
    out = []
    for e in entries:
        link = (e.get("link") or "").strip()
        title = (e.get("title") or "").strip()

        if link:
            try:
                p = urlparse(link)
                canonical = p._replace(query="", fragment="").geturl()
            except Exception:
                canonical = link
            if canonical in seen_links:
                continue
            seen_links.add(canonical)

        nt = normalize_title(title)
        if nt:
            if any(similar(nt, kt) >= title_sim_threshold for kt in kept_titles):
                continue
            kept_titles.append(nt)

        out.append(e)
    return out


@st.cache_data(ttl=300, show_spinner=False)
def fetch_entries(keyword: str) -> List[Dict]:
    encoded = urllib.parse.quote(keyword)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(url)
    items = []
    for entry in getattr(feed, "entries", []) or []:
        items.append(
            {
                "title": getattr(entry, "title", ""),
                "link": getattr(entry, "link", ""),
                "published": getattr(entry, "published", ""),
            }
        )
    return items


def on_pick_recent():
    val = (st.session_state.pick_recent or "").strip()
    if val:
        st.session_state.pick_recent = ""
        set_query_and_search(val)


def on_pick_fav():
    val = (st.session_state.pick_fav or "").strip()
    if val:
        st.session_state.pick_fav = ""
        set_query_and_search(val)


# ----------------------------
# ✅ AdSense 정책 안전 패치: "콘텐츠 없는 화면" 방지
# ----------------------------
if (
    not (st.session_state.query or "").strip()
    and not (st.session_state.last_keyword or "").strip()
    and not st.session_state.feed_entries
):
    st.session_state.query = DEFAULT_QUERY
    st.session_state.run_search = True


# ----------------------------
# 4. Sidebar & Layout
# ----------------------------
with st.sidebar:
    # ✅ [추가] 정책 링크/면책/문의 (승인/신뢰도 보강용)
    st.markdown("### Open Insight")
    st.markdown("- 홈: https://mintaeyang.github.io/")
    st.markdown("- 개인정보: https://mintaeyang.github.io/privacy.html")
    st.markdown("- 이용약관: https://mintaeyang.github.io/terms.html")
    st.markdown("- 문의: openinsight.contact@gmail.com")
    st.caption("※ 본 서비스는 투자 자문/권유가 아니며, 제공 정보의 최종 판단과 책임은 사용자에게 있습니다.")
    st.caption("※ 헤드라인/링크는 Google News RSS 기반이며, 기사 저작권은 각 언론사에 있습니다.")
    st.markdown("---")

    st.markdown("### 옵션")
    dedupe_on = st.toggle("중복 제거", value=True)
    st.caption("Google News RSS 기반")
    st.markdown("---")

    st.markdown("### 즐겨찾기")
    if st.session_state.favorites:
        st.selectbox(
            "즐겨찾기 선택",
            options=[""] + st.session_state.favorites[:20],
            key="pick_fav",
            on_change=on_pick_fav,
            label_visibility="collapsed",
        )
    else:
        st.caption("아직 없습니다.")
    st.markdown("---")

    st.markdown("### 최근 검색")
    if st.session_state.recent_keywords:
        st.selectbox(
            "최근 선택",
            options=[""] + st.session_state.recent_keywords[:20],
            key="pick_recent",
            on_change=on_pick_recent,
            label_visibility="collapsed",
        )
        if st.button("기록 삭제", use_container_width=True):
            clear_recent()
            st.rerun()
    else:
        st.caption("아직 없습니다.")

st.markdown('<div class="hero-title">Open Insight</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">키워드를 입력하면 최신 헤드라인을 정리해 보여줍니다.</div>',
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns([6, 1, 1], vertical_alignment="bottom")
with c1:
    st.text_input(
        "분석할 마켓 키워드를 입력하세요",
        placeholder="예: 반도체 수출, 연준 금리 결정",
        key="query",
        on_change=trigger_search,
    )
with c2:
    if st.button("검색", use_container_width=True):
        st.session_state.run_search = True
with c3:
    current_for_star = (st.session_state.query or "").strip() or (
        st.session_state.last_keyword or ""
    ).strip()
    star_label = (
        "★ 저장" if current_for_star and not is_favorite(current_for_star) else "★ 해제"
    )
    if st.button(star_label, use_container_width=True, disabled=not bool(current_for_star)):
        toggle_favorite(current_for_star)
        st.rerun()

keyword = (st.session_state.query or "").strip() or DEFAULT_QUERY

if st.session_state.run_search:
    with st.spinner("뉴스 불러오는 중..."):
        entries = fetch_entries(keyword)
    if dedupe_on:
        entries = dedupe_entries(entries)
    st.session_state.last_keyword = keyword
    st.session_state.feed_entries = entries
    push_recent(keyword)
    st.session_state.run_search = False

entries = st.session_state.feed_entries
active_keyword = st.session_state.last_keyword or keyword

if not entries:
    st.info(
        "현재 키워드에 대한 헤드라인을 가져오지 못했어요. "
        "다른 키워드(예: 반도체, 환율, 미국 금리, ETF, 비트코인)로 다시 검색해보세요."
    )
    st.caption(f"현재 키워드: {active_keyword}")
else:
    st.caption(f"키워드: {active_keyword} · 결과: {len(entries)}")

    limit = st.slider("표시 개수", 10, 50, st.session_state.limit, 5, key="limit_slider")
    st.session_state.limit = limit

    for entry in entries[:limit]:
        title, link, published = (
            entry.get("title", ""),
            entry.get("link", "#"),
            entry.get("published", ""),
        )
        source = urlparse(link).netloc.replace("www.", "") if link else ""
        st.markdown(
            f"""
            <div class="news-item">
              <a href="{link}" target="_blank" rel="noopener noreferrer" class="news-link">{title}</a>
              <div class="news-meta">
                {f'<span class="meta-pill">{source}</span>' if source else ''}
                <span>{published}</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ✅ 하단(푸터)에도 정책 링크 + 면책을 노출 (사이드바가 닫혀 있어도 보이게)
st.markdown(
    """
<div class="small-footer">
  <div>
    © 2026 Open Insight ·
    <a href="https://mintaeyang.github.io/" target="_blank" rel="noopener">홈</a> ·
    <a href="https://mintaeyang.github.io/privacy.html" target="_blank" rel="noopener">개인정보처리방침</a> ·
    <a href="https://mintaeyang.github.io/terms.html" target="_blank" rel="noopener">이용약관</a> ·
    <a href="mailto:openinsight.contact@gmail.com" rel="noopener">문의</a>
  </div>
  <span class="note">※ 본 서비스는 투자 자문/권유가 아니며, 제공 정보의 최종 판단과 책임은 사용자에게 있습니다.</span>
  <span class="note">※ 헤드라인/링크는 Google News RSS 기반이며, 기사 저작권은 각 언론사에 있습니다.</span>
</div>
""",
    unsafe_allow_html=True,
)

