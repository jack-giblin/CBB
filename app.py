import streamlit as st
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="CBB +EV Totals Engine", page_icon="🏀")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('cbb26.csv')
        df.columns = df.columns.str.strip()
        return df, sorted(df['TEAM'].unique())
    except Exception as e:
        return None, []

# --- APP UI ---
st.title("🏀 CBB +EV Totals Predictor")
st.markdown("Enter the sportsbook total to find an edge on the Over/Under.")

df, teams = load_data()

if not teams:
    st.error("Missing 'cbb26.csv' in your GitHub repository!")
else:
    # 1. Team Selection
    col1, col2 = st.columns(2)
    with col1:
        team_a = st.selectbox("Team 1 (Away)", teams, key='a')
    with col2:
        team_b = st.selectbox("Team 2 (Home)", teams, index=1, key='b')

    # 2. Sportsbook Input
    st.divider()
    sb_total = st.number_input("Enter Sportsbook Total (O/U)", value=158.5, step=0.5)

    if st.button("Calculate +EV Edge", use_container_width=True):
        # Stats & Logic
        t1 = df[df['TEAM'] == team_a].iloc[0]
        t2 = df[df['TEAM'] == team_b].iloc[0]

        # 2026 Normalization Constants (Power Conference Baseline)
        LG_EFF, LG_TEMPO = 109.5, 68.3
        
        # Calculate Matchup Tempo
        match_tempo = (t1['ADJ_T'] * t2['ADJ_T']) / LG_TEMPO
        
        # Calculate Predicted Team Scores
        score_a = ((t1['ADJOE'] + t2['ADJDE'] - LG_EFF) * match_tempo) / 100
        score_b = ((t2['ADJOE'] + t1['ADJDE'] - LG_EFF) * match_tempo) / 100
        
        model_total = round(score_a + score_b, 1)

        # --- RESULTS & EV ANALYSIS ---
        st.divider()
        
        # Individual Team Scores
        c1, c2 = st.columns(2)
        c1.metric(f"{team_a} Predicted Score", round(score_a, 1))
        c2.metric(f"{team_b} Predicted Score", round(score_b, 1))

        # Total Analysis
        st.subheader(f"Total Prediction: {model_total}")
        
        total_diff = model_total - sb_total
        # Edge Threshold: 2.5 points difference is usually considered +EV
        if abs(total_diff) >= 2.5:
            verdict = f"✅ BET THE {'OVER' if total_diff > 0 else 'UNDER'}"
            edge_text = f"Edge: {abs(total_diff):.1f} points"
            st.success(f"**{verdict}** ({edge_text})")
        else:
            st.warning("⚠️ NO GOOD BET: Line is too close to model prediction.")

        st.info(f"Model uses neutral site settings with 109.5 power-conference efficiency baseline.")





