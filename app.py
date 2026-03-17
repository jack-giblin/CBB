import streamlit as st
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="CBB 2026 March Madness Predictor", page_icon="🏀")

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
st.markdown("### 2026 Tournament Edition (Neutral Site)")

df, teams = load_data()

if not teams:
    st.error("Missing 'cbb26.csv' in your GitHub repository!")
else:
    col1, col2 = st.columns(2)
    with col1:
        team_a = st.selectbox("Away Team", teams, key='a')
    with col2:
        team_b = st.selectbox("Home Team", teams, index=1, key='b')

    if st.button("Predict Score", use_container_width=True):
        # 1. Get Team Stats
        t1 = df[df['TEAM'] == team_a].iloc[0]
        t2 = df[df['TEAM'] == team_b].iloc[0]

        # 2. 2026 Tournament-Level Averages
        # Adjusting to 109.5 accounts for the higher efficiency of power teams
        LG_EFF = 109.5  
        LG_TEMPO = 68.3 

        # 3. Calculate Matchup Tempo (Possessions)
        # (T1 Tempo * T2 Tempo) / League Average
        match_tempo = (t1['ADJ_T'] * t2['ADJ_T']) / LG_TEMPO

        # 4. Professional Additive Efficiency Formula
        # This prevents "double-counting" elite offenses
        t1_eff = t1['ADJOE'] + t2['ADJDE'] - LG_EFF
        t2_eff = t2['ADJOE'] + t1['ADJDE'] - LG_EFF

        # 5. Final Score Calculation
        score_a = (t1_eff * match_tempo) / 100
        score_b = (t2_eff * match_tempo) / 100

        # --- DISPLAY RESULTS ---
        st.divider()
        res1, res2 = st.columns(2)
        res1.metric(team_a, round(score_a, 1))
        res2.metric(team_b, round(score_b, 1))
        
        total_pts = round(score_a + score_b, 1)
        spread_val = round(score_b - score_a, 1) # Positive means Team B (Home) is favored
        
        st.subheader(f"📊 Market Comparison")
        st.write(f"**Predicted Total:** {total_pts}")
        
        if spread_val > 0:
            st.write(f"**Predicted Line:** {team_b} -{abs(spread_val)}")
        else:
            st.write(f"**Predicted Line:** {team_a} -{abs(spread_val)}")
        
        st.info("Tournament Mode: Using 2026 power-conference normalization (LG_EFF: 109.5).")



