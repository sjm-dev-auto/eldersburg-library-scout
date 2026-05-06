import streamlit as st
import requests
from bs4 import BeautifulSoup

# App Config
st.set_page_config(page_title="Eldersburg Library Scout", page_icon="📚")
st.title("📚 The "No-Bouncer" Library Scout")

# We use the DuckDuckGo "Lite" version - it's text-only and bot-friendly
DDG_LITE_URL = "https://duckduckgo.com/lite/"

def scout_via_proxy(topic):
    """Uses DuckDuckGo to see what the library has indexed recently."""
    # We build a very specific search query for Google/DDG to find
    search_query = f'site:catalog.carr.org "Eldersburg" "Available" {topic}'
    
    try:
        # We send a POST request to DDG Lite (it's faster and cleaner)
        response = requests.post(DDG_LITE_URL, data={"q": search_query}, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # We look for the search results
        links = soup.find_all('a', class_='result-link')
        
        results = []
        for link in links:
            title = link.get_text().strip()
            # We filter for titles that actually look like books (avoiding 'Help', 'Search', etc)
            if len(title) > 5 and not any(x in title.lower() for x in ["catalog", "search", "carroll"]):
                results.append(title)
        
        return results if results else []
    except Exception as e:
        return [f"Search Error: {e}"]

# --- UI LOGIC ---
st.info("This version uses DuckDuckGo to bypass library firewalls. No API key needed!")

query = st.text_input("What book are we scouting for?", placeholder="e.g. We Are as Gods")
if st.button("Run Scout") and query:
    with st.spinner(f"Asking DuckDuckGo to check the Eldersburg shelves..."):
        hits = scout_via_proxy(query)
        
        if hits:
            st.subheader(f"📍 Possible Matches at Eldersburg")
            for hit in hits[:5]:
                st.success(f"**{hit}**")
            st.caption("Note: If these results look old, the library might have updated their shelf since the last search engine crawl.")
        else:
            st.warning("No immediate matches found in the search index. Try a broader search (e.g., just the author's last name).")

# --- ALTERNATIVE FOR LIBBY ---
st.markdown("---")
st.subheader("📱 Looking for Libby?")
st.write("Since Libby/Overdrive is a 'Live' database, it's harder to search via DuckDuckGo. To get Libby working for free, the best bet is a free **Apify** account (they give you $5 of credit every month for free, which is about 2,000 searches).")
