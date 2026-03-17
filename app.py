import streamlit as st
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="CBB +EV Predictor", page_icon="💰")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('cbb26.csv')
        df.columns = df.columns.str.strip()
        return df, sorted(df['TEAM'].unique())
    except:
        return None, []

# --- APP UI ---
st.title("💰 CBB +EV Betting Engine")
st.markdown("Compare model predictions to sportsbook lines to find an edge.")

df, teams = load_data()

if not teams:
    st.error("Missing 'cbb26.csv' in your GitHub repository!")
else:
    # 1. Team Selection
    col1, col2 = st.columns(2)
    with col1:
        team_a = st.selectbox("Away Team", teams, key='a')
    with col2:
        team_b = st.selectbox("Home Team", teams, index=1, key='b')

    # 2. Sportsbook Input
    st.sidebar.header("Current Sportsbook Lines")
    sb_spread = st.sidebar.number_input(f"Spread ({team_b} favored = negative)", value=0.0, step=0.5)
    sb_total = st.sidebar.number_input("Game Total (O/U)", value=145.0, step=0.5)

    if st.button("Analyze for +EV Value", use_container_width=True):
        # Stats & Logic
        t1 = df[df['TEAM'] == team_a].iloc
        t2 = df[df['TEAM'] == team_b].iloc

        LG_EFF, LG_TEMPO = 109.5, 68.3
        match_tempo = (t1['ADJ_T'] * t2['ADJ_T']) / LG_TEMPO
        
        score_a = ((t1['ADJOE'] + t2['ADJDE'] - LG_EFF) * match_tempo) / 100
        score_b = ((t2['ADJOE'] + t1['ADJDE'] - LG_EFF) * match_tempo) / 100
        
        model_total = round(score_a + score_b, 1)
        model_spread = round(score_b - score_a, 1) # Positive = Team B favored

        # --- EV ANALYSIS ---
        st.divider()
        
        # Total Analysis
        total_diff = model_total - sb_total
        if abs(total_diff) >= 2.5: # 2.5 point edge threshold
            verdict_total = f"✅ BET THE {'OVER' if total_diff > 0 else 'UNDER'} ({total_diff:+.1f} point edge)"
        else:
            verdict_total = "❌ NO VALUE ON TOTAL"

        # Spread Analysis (Standardizing to Home Team)
        # If model says -5 and book says -2, model sees value on favorite
        spread_edge = sb_spread - model_spread 
        if abs(spread_edge) >= 1.5: # 1.5 point edge threshold
            bet_on = team_b if spread_edge > 0 else team_a
            verdict_spread = f"✅ BET ON {bet_on} ({abs(spread_edge):.1f} point edge)"
        else:
            verdict_spread = "❌ NO VALUE ON SPREAD"

        # Display Results
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Model Total", model_total)
            st.write(verdict_total)
        with c2:
            st.metric("Model Spread", f"{team_b} -{model_spread}")
            st.write(verdict_spread)

        if "✅" not in verdict_total and "✅" not in verdict_spread:
            st.warning("⚠️ No significant +EV opportunities found. Odds are efficiently priced.")




