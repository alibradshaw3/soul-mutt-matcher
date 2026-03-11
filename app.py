import streamlit as st
import pandas as pd
import urllib.parse

# 1. SETUP & DATA LOADING
st.set_page_config(page_title="Soul Dog Matcher 2026", page_icon="🐶")

@st.cache_data
def load_data():
    # Loading your Kaggle file (ensure this filename matches exactly on GitHub)
    df = pd.read_csv("akc-data-latest.csv", index_col=0, encoding='ISO-8859-1')
    return df

df = load_data()

# 2. USER INTERFACE
st.title("🐾 Find Your Perfect Dog")
st.write("Match your lifestyle to the official AKC breed database.")

with st.form("main_quiz"):
    st.subheader("The Dealbreakers")
    
    # Size Filter
    size_pref = st.selectbox("What size dog fits your home?", 
                             ["Any Size", "Small (under 20 lbs)", "Medium (20-60 lbs)", "Large (60+ lbs)"])
    
    # Kid Friendly Toggle
    is_family = st.checkbox("I have children (Prioritize social/friendly breeds)")

    st.subheader("Personality & Maintenance")
    
    # Traits mapped to 0.2 - 1.0 to match your Kaggle data values
    u_energy = st.select_slider("Energy Level", options=[1, 2, 3, 4, 5], value=3) / 5
    u_shed = st.select_slider("Shedding Tolerance (1: Love fur, 5: Must stay clean)", options=[1, 2, 3, 4, 5], value=3) / 5
    u_train = st.select_slider("Importance of Trainability", options=[1, 2, 3, 4, 5], value=3) / 5

    submitted = st.form_submit_button("Find My Match")

# 3. MATCHING LOGIC
if submitted:
    results = df.copy()

    # Apply Kid-Friendly Filter (High demeanor value)
    if is_family:
        results = results[results['demeanor_value'] >= 0.6]

    # Apply Size Filter (Converting kg to lbs)
    if size_pref == "Small (under 20 lbs)":
        results = results[results['max_weight'] * 2.204 < 20]
    elif size_pref == "Medium (20-60 lbs)":
        results = results[(results['max_weight'] * 2.204 >= 20) & (results['max_weight'] * 2.204 < 60)]
    elif size_pref == "Large (60+ lbs)":
        results = results[results['max_weight'] * 2.204 >= 60]

    # Calculate "Compatibility Score"
    if not results.empty:
        results['score'] = (
            abs(results['energy_level_value'] - u_energy) + 
            abs(results['shedding_value'] - u_shed) +
            abs(results['trainability_value'] - u_train)
        )
        
        # Identify the best breed
        best_match = results['score'].idxmin()
        row = results.loc[best_match]
        
        # 4. DISPLAY RESULTS
        st.balloons()
        st.success(f"Your Match: The {best_match}!")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.write(f"**Temperament:** {row['temperament']}")
            st.write(f"**About the breed:** {row['description']}")
        with col2:
            st.metric("Energy", f"{int(row['energy_level_value']*5)}/5")
            st.metric("Trainability", f"{int(row['trainability_value']*5)}/5")

        # Shelter Buttons
        google_query = urllib.parse.quote(f"adopt {best_match} near me")
        st.link_button(f"🏠 Find {best_match}s at local shelters", f"https://www.google.com/search?q={google_query}")
        
    else:

        st.error("No breeds matched those specific criteria. Try loosening your size or family filters!")

