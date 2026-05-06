import streamlit as st
import requests
from bs4 import BeautifulSoup

# App Config
st.set_page_config(page_title="Eldersburg Library Scout", page_icon="📚")
st.title("📚 Eldersburg Library & Libby Scout")

# User Inputs
query = st.text_input("What are we looking for?", placeholder="e.g. Artificial Intelligence")
search_button = st.button("Search Availability")

def check_eldersburg(topic):
    # Context ID for Eldersburg Branch
    ctx = "3.1033.0.0.1"
    url = f"https://catalog.carr.org/search/searchresults.aspx?ctx={ctx}&type=Keyword&term={topic.replace(' ', '+')}&limit=AVAIL=1"
    
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Simplified selector - this may need adjustment based on CCPL's live HTML
        items = soup.find_all('div', class_='result-item-details')
        results = []
        for item in items:
            if "Eldersburg" in item.text:
                title = item.find('a', class_='title-link').text.strip()
                results.append(title)
        return results
    except Exception:
        return []

def check_libby(topic):
    url = f"https://maryland.overdrive.com/search?query={topic.replace(' ', '+')}"
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        # Looks for the 'Available' badge in OverDrive
        items = soup.find_all('div', class_='SearchResult-details')
        for item in items:
            status = item.find('span', class_='AvailabilityBadge-text')
            if status and "Available" in status.text:
                title = item.find('a', class_='SearchResult-titleLink').text.strip()
                results.append(title)
        return results
    except Exception:
        return []

if search_button and query:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📍 At the Eldersburg Branch")
        physical = check_eldersburg(query)
        if physical:
            for book in physical[:5]:
                st.success(f"**{book}**")
        else:
            st.info("No immediate matches on the shelf.")

    with col2:
        st.subheader("📱 Available on Libby")
        digital = check_libby(query)
        if digital:
            for book in digital[:5]:
                st.warning(f"**{book}**")
        else:
            st.info("No digital copies ready for download.")