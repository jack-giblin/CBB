import streamlit as st
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="CBB March Madness Predictor", page_icon="🏀")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('cbb26.csv')
        df.columns = df.columns.str.strip()
        return df, sorted(df['TEAM'].unique())
    except:
        return None, []

# --- APP UI ---
st.title("🏀 CBB March Madness Predictor")
st.markdown("### Neutral Site Tournament Mode")

df, teams = load_data()

if not teams:
    st.error("Missing 'cbb26.csv' in your GitHub repository!")
else:
    col1, col2 = st.columns(2)
    with col1:
        team_a = st.selectbox("Team 1", teams, key='a')
    with col2:
        team_b = st.selectbox("Team 2", teams, index=1, key='b')

    if st.button("Generate Tournament Prediction", use_container_width=True):
        # 1. Get Stats
        t1 = df[df['TEAM'] == team_a].iloc[0]
        t2 = df[df['TEAM'] == team_b].iloc[0]

        # 2. 2026 League Averages (Estimated for Normalization)
        lg_eff = 105.5
        lg_tempo = 68.5

        # 3. Calculate Matchup Tempo (Possessions)
        # Formula: (T1 Tempo * T2 Tempo) / League Average
        match_tempo = (t1['ADJ_T'] * t2['ADJ_T']) / lg_tempo

        # 4. Calculate Expected Points Per 100 Possessions
        # Formula: (Offense + Defense - League Average)
        t1_eff_v_t2 = t1['ADJOE'] + t2['ADJDE'] - lg_eff
        t2_eff_v_t1 = t2['ADJOE'] + t1['ADJDE'] - lg_eff

        # 5. Final Score Calculation
        score_a = (t1_eff_v_t2 * match_tempo) / 100
        score_b = (t2_eff_v_t1 * match_tempo) / 100

        # --- RESULTS ---
        st.divider()
        res1, res2 = st.columns(2)
        res1.metric(team_a, round(score_a, 1))
        res2.metric(team_b, round(score_b, 1))
        
        total_pts = round(score_a + score_b, 1)
        spread = round(abs(score_a - score_b), 1)
        winner = team_a if score_a > score_b else team_b

        st.subheader(f"📊 Market Analysis")
        st.write(f"**Predicted Winner:** {winner} by {spread}")
        st.write(f"**Predicted Total:** {total_pts}")
        
        st.info("Note: Neutral site settings applied (No Home Court Advantage).")

