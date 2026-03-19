import streamlit as st
import pandas as pd
import numpy as np

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

    # Auto-calculate pace from team data
    t1 = df[df['TEAM'] == team_a].iloc[0]
    t2 = df[df['TEAM'] == team_b].iloc[0]
    auto_pace = round((t1['ADJ_T'] + t2['ADJ_T']) / 2, 1)

    st.divider()
    st.markdown("#### ⏱️ Adjusted Tempo")
    st.caption("""
        **What is Adjusted Tempo?** KenPom's Adjusted Tempo (ADJ_T) estimates how many possessions 
        per 40 minutes a team would play against an average Division I opponent. Unlike raw possessions 
        per game, it removes the influence of opponents — so a slow team that played an unusually fast 
        schedule won't look artificially up-tempo. This gives us a fairer, more accurate picture of 
        each team's true pace of play.
    """)

    p1, p2, p3 = st.columns(3)
    p1.metric(f"{team_a} ADJ_T", f"{t1['ADJ_T']}")
    p2.metric(f"{team_b} ADJ_T", f"{t2['ADJ_T']}")
    p3.metric("Projected Game Tempo", f"{auto_pace}")

    if auto_pace <= 66:
        st.caption("🐢 Slow tempo — expect a grind, defensive battle likely.")
    elif auto_pace <= 70:
        st.caption("🏀 Tournament average — March Madness historically averages 68–69 adjusted tempo.")
    elif auto_pace <= 74:
        st.caption("⚡ Up-tempo — both teams like to push the ball.")
    else:
        st.caption("🚀 High tempo — wide open game, points expected.")

    st.divider()

    if st.button("Predict Score", use_container_width=True):

        pace = auto_pace

        # Tournament calibration factor
        # NCAA Tournament avg combined score ~141 vs model output ~149 = 5.4% overestimate
        tournament_factor = 0.946

        # Base efficiency score
        base_a = (t1['ADJOE'] / 100) * (t2['ADJDE'] / 100) * pace * tournament_factor
        base_b = (t2['ADJOE'] / 100) * (t1['ADJDE'] / 100) * pace * tournament_factor

        # EFG adjustment (shooting efficiency)
        efg_adj_a = (t1['EFG_O'] - t2['EFG_D']) * 0.15
        efg_adj_b = (t2['EFG_O'] - t1['EFG_D']) * 0.15

        # Turnover adjustment (pace scaled)
        pace_ratio = pace / 70
        tor_adj_a = (t2['TORD'] - t1['TOR']) * 0.1 * pace_ratio
        tor_adj_b = (t1['TORD'] - t2['TOR']) * 0.1 * pace_ratio

        # Rebounding adjustment (pace scaled)
        reb_adj_a = (t1['ORB'] - t2['DRB']) * 0.05 * pace_ratio
        reb_adj_b = (t2['ORB'] - t1['DRB']) * 0.05 * pace_ratio

        # Final base scores
        score_a = base_a + efg_adj_a + tor_adj_a + reb_adj_a
        score_b = base_b + efg_adj_b + tor_adj_b + reb_adj_b

        # Monte Carlo simulation (10,000 games)
        simulations = 10000
        std_dev = 7

        sim_a = np.random.normal(score_a, std_dev, simulations)
        sim_b = np.random.normal(score_b, std_dev, simulations)

        win_pct_a = np.mean(sim_a > sim_b) * 100
        win_pct_b = 100 - win_pct_a

        avg_a = np.mean(sim_a)
        avg_b = np.mean(sim_b)
        avg_total = np.mean(sim_a + sim_b)

        winner = team_a if avg_a > avg_b else team_b

        # Main prediction
        c1, c2 = st.columns(2)
        c1.metric(team_a, round(avg_a))
        c2.metric(team_b, round(avg_b))

        st.success(f"🏆 **Prediction:** {winner} wins!")
        st.info(f"📊 **Projected Total:** {round(avg_total)} points")

        st.divider()
        st.markdown("#### 🎲 Monte Carlo Simulation (10,000 games)")
        st.caption("Simulates 10,000 versions of this game using statistical variance to estimate outcomes.")

        m1, m2 = st.columns(2)
        m1.metric(f"{team_a} Win Probability", f"{win_pct_a:.1f}%")
        m2.metric(f"{team_b} Win Probability", f"{win_pct_b:.1f}%")

        st.divider()
        st.markdown("#### 📈 Score Distribution (80% confidence range)")
        st.caption("The range you'd expect the score to land in 8 out of 10 simulated games.")

        st.markdown(f"**{team_a}:** {int(np.percentile(sim_a, 10))} – {int(np.percentile(sim_a, 90))} points")
        st.markdown(f"**{team_b}:** {int(np.percentile(sim_b, 10))} – {int(np.percentile(sim_b, 90))} points")
        st.markdown(f"**Total:** {int(np.percentile(sim_a + sim_b, 10))} – {int(np.percentile(sim_a + sim_b, 90))} points")
