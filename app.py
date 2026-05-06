import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

# App Config
st.set_page_config(page_title="Eldersburg Library Scout", page_icon="📚", layout="wide")
st.title("📚 Eldersburg Library & Libby Scout")

# Robust Headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

def check_eldersburg(topic):
    # We'll use the standard search URL but focus on a wider net for selectors
    url = f"https://catalog.carr.org/search/searchresults.aspx?ctx=3.1033.0.0.1&type=Keyword&term={topic.replace(' ', '+')}&limit=AVAIL=1"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # METHOD 1: Look for any link that contains 'Title' in its ID (The Polaris Standard)
        titles = soup.find_all(['a', 'span'], id=re.compile(r'lblTitle|title|ResultItem', re.I))
        
        # METHOD 2: Look for links that look like bibliographic records
        if not titles:
            titles = soup.find_all('a', href=re.compile(r'description\.aspx\?bib=', re.I))
            
        for item in titles:
            t_text = item.get_text().strip()
            if len(t_text) > 3 and t_text not in results:
                results.append(t_text)
                
        return results, url
    except Exception as e:
        return [f"Connection Error: {str(e)}"], url

def check_libby(topic):
    # Libby search for Maryland Digital Library
    url = f"https://maryland.overdrive.com/search?query={topic.replace(' ', '+')}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Libby uses specific class names for their search result titles
        items = soup.find_all('a', class_=re.compile(r'titleLink|title-link', re.I))
        
        # If classes fail, look for any link with 'media' or 'library' in the parent
        if not items:
            items = soup.find_all('a', href=re.compile(r'/media/', re.I))
            
        for item in items:
            t_text = item.get_text().strip()
            if len(t_text) > 2 and t_text not in results:
                results.append(t_text)
                
        return results, url
    except Exception as e:
        return [f"Connection Error: {str(e)}"], url

# --- UI LOGIC ---
query = st.text_input("What are we looking for?", placeholder="e.g. Atomic Habits")
search_button = st.button("Scout Availability")

if search_button and query:
    with st.spinner(f"Scouting for '{query}'..."):
        col1, col2 = st.columns(2)
        
        physical, p_url = check_eldersburg(query)
        digital, d_url = check_libby(query)
        
        with col1:
            st.subheader("📍 Eldersburg Branch")
            st.caption(f"[View Search Results Directly]({p_url})")
            if any("Error" in str(r) for r in physical):
                st.error(physical[0])
            elif not physical or "No physical matches" in str(physical[0]):
                st.info("No matches on the shelf. Check the link above to verify.")
            else:
                for res in physical[:8]:
                    st.success(f"**{res}**")

        with col2:
            st.subheader("📱 Available on Libby")
            st.caption(f"[View Libby Results Directly]({d_url})")
            if any("Error" in str(r) for r in digital):
                st.error(digital[0])
            elif not digital:
                st.info("No digital matches found.")
            else:
                for res in digital[:8]:
                    st.warning(f"**{res}**")

# --- TECHNICAL LOGS ---
with st.expander("Show Technical Logs"):
    if query:
        st.write(f"Last Query: {query}")
        st.write("Eldersburg Branch Context: 3.1033.0.0.1")
        st.write("Anti-Bot Headers: Active")
