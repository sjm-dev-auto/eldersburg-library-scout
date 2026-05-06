import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

# App Config
st.set_page_config(page_title="Eldersburg Library Scout", page_icon="📚", layout="wide")
st.title("📚 Eldersburg Library & Libby Scout")

# Realistic headers to mimic a modern browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,all;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

def get_library_results(topic):
    # Initialize a session to store cookies
    session = requests.Session()
    session.headers.update(HEADERS)
    
    try:
        # Step 1: "Walk through the front door" to get a Session Cookie
        # This prevents the server from giving us a blank page
        session.get("https://catalog.carr.org/default.aspx", timeout=10)
        
        # Step 2: Use the 'Stable View' URL which is better for deep linking
        # ctx=3.1033.0.0.1 is the code for the Eldersburg branch
        search_url = f"https://catalog.carr.org/search/view.aspx?ctx=3.1033.0.0.1&type=keyword&term={topic.replace(' ', '+')}&limit=AVAIL=1"
        
        response = session.get(search_url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        # Look for the 'lblTitle' span - the most consistent way Polaris identifies titles
        titles = soup.find_all('span', id=lambda x: x and 'lblTitle' in x)
        
        for t in titles:
            text = t.get_text().strip()
            if text and text not in results:
                results.append(text)
        
        return results, search_url
    except Exception as e:
        return [f"Library connection error: {e}"], ""

def get_libby_results(topic):
    url = f"https://maryland.overdrive.com/search?query={topic.replace(' ', '+')}"
    try:
        # Libby is usually less strict about sessions, but we still use the session object
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        # Target the specific links that contain book titles
        items = soup.find_all('a', class_='SearchResult-titleLink')
        for item in items:
            title = item.get_text().strip()
            if title and title not in results:
                results.append(title)
        
        return results, url
    except Exception:
        return ["Libby connection error."], url

# --- UI LOGIC ---
query = st.text_input("What are we looking for?", placeholder="e.g. Atomic Habits")
search_button = st.button("Scout Availability")

if search_button and query:
    with st.spinner(f"Scouting for '{query}'..."):
        col1, col2 = st.columns(2)
        
        # Run library check
        physical, p_url = get_library_results(query)
        # Run Libby check
        digital, d_url = get_libby_results(query)
        
        with col1:
            st.subheader("📍 Eldersburg Branch")
            if physical and not any("error" in str(r).lower() for r in physical):
                for book in physical[:8]:
                    st.success(f"**{book}**")
                st.caption(f"[Open full search results]({p_url})")
            else:
                st.info("No physical matches on the shelf right now.")

        with col2:
            st.subheader("📱 Available on Libby")
            if digital and not any("error" in str(r).lower() for r in digital):
                for book in digital[:8]:
                    st.warning(f"**{book}**")
                st.caption(f"[Open Libby search]({d_url})")
            else:
                st.info("No digital copies ready for download.")
