import streamlit as st
import pandas as pd

# Set page title
st.set_page_config(page_title="CBB Predictor", page_icon="🏀")
st.title("🏀 CBB 2026 Score Predictor")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('cbb26.csv')
        df.columns = df.columns.str.strip()
        return df, sorted(df['TEAM'].unique())
    except:
        return None, []

df, teams = load_data()

if not teams:
    st.error("Error: 'cbb26.csv' not found in the repository.")
else:
    col1, col2 = st.columns(2)
    with col1:
        team_a = st.selectbox("Away Team", teams, key='a')
    with col2:
        team_b = st.selectbox("Home Team", teams, index=1, key='b')

    if st.button("Predict Score", use_container_width=True):
        t1 = df[df['TEAM'] == team_a].iloc[0]
        t2 = df[df['TEAM'] == team_b].iloc[0]

        pace = (t1['ADJ_T'] + t2['ADJ_T']) / 2
        score_a = (t1['ADJOE'] * t2['ADJDE'] / 100) * (pace / 100)
        score_b = (t2['ADJOE'] * t1['ADJDE'] / 100) * (pace / 100)

        st.divider()
        c1, c2 = st.columns(2)
        c1.metric(team_a, round(score_a))
        c2.metric(team_b, round(score_b))

        winner = team_a if score_a > score_b else team_b
        st.success(f"**Prediction:** {winner} wins!")
