import streamlit as st
import requests
from bs4 import BeautifulSoup

# App Config
st.set_page_config(page_title="Eldersburg Library Scout", page_icon="📚")
st.title("📚 Eldersburg Library & Libby Scout")

# Standard Headers to avoid being blocked as a bot
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

def check_eldersburg(topic):
    ctx = "3.1033.0.0.1"
    url = f"https://catalog.carr.org/search/searchresults.aspx?ctx={ctx}&type=Keyword&term={topic.replace(' ', '+')}&limit=AVAIL=1"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # New Polaris 7.x selectors: titles are often in <a> or <span> with 'lblTitle' in the ID
        results = []
        # Look for the new 'result-item' container OR the specific title spans
        items = soup.find_all(['div', 'span'], id=lambda x: x and ('divResultItem' in x or 'lblTitle' in x))
        
        for item in items:
            title_tag = item.find('a') if item.name == 'div' else item
            if title_tag and title_tag.text:
                title = title_tag.text.strip()
                # Ensure we aren't adding the same title twice
                if title and title not in results:
                    results.append(title)
        
        return results[:10] # Return top 10
    except Exception as e:
        return []

def check_libby(topic):
    # This URL targets the 'Available Now' digital search directly
    url = f"https://maryland.overdrive.com/search?query={topic.replace(' ', '+')}&showAll=true"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Libby/Overdrive updated to use 'SearchResult-titleLink' and 'AvailabilityBadge'
        # We also look for the 'title' attribute in the cover images as a fallback
        items = soup.select('a.SearchResult-titleLink')
        
        for item in items:
            title = item.text.strip()
            if title:
                results.append(title)
        
        return results[:10]
    except Exception as e:
        return []

# --- UI LOGIC ---
query = st.text_input("What are we looking for?", placeholder="e.g. Atomic Habits")
search_button = st.button("Search Availability")

if search_button and query:
    with st.spinner(f"Scouting for '{query}'..."):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📍 Eldersburg Branch")
            physical = check_eldersburg(query)
            if physical:
                for book in physical:
                    st.success(f"**{book}**")
            else:
                st.info("No physical matches found.")

        with col2:
            st.subheader("📱 Available on Libby")
            digital = check_libby(query)
            if digital:
                for book in digital:
                    st.warning(f"**{book}**")
            else:
                st.info("No digital matches found.")
