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
    st.markdown("#### ⏱️ Game Pace")

    # Show the breakdown so user understands the logic
    p1, p2, p3 = st.columns(3)
    p1.metric(f"{team_a} Avg Pace", f"{t1['ADJ_T']} poss/g")
    p2.metric(f"{team_b} Avg Pace", f"{t2['ADJ_T']} poss/g")
    p3.metric("Projected Game Pace", f"{auto_pace} poss/g")

    if auto_pace <= 66:
        st.caption("🐢 Slow pace — think Iowa (64.7). Expect a grind, defensive battle likely.")
    elif auto_pace <= 70:
        st.caption("🏀 Tournament average — March Madness historically averages 68–69 possessions per game.")
    elif auto_pace <= 74:
        st.caption("⚡ Up-tempo — both teams like to push the ball.")
    else:
        st.caption("🚀 High pace — think Alabama (78.3). Wide open game, points expected.")

    st.divider()
    st.markdown("#### 🎚️ Manual Pace Override")
    st.caption("Auto-calculated from each team's season average. Adjust below if you expect a different tempo.")

    pace_override = st.slider(
        "Possessions per game",
        min_value=64,
        max_value=79,
        value=int(auto_pace),
        step=1
    )

    if pace_override != int(auto_pace):
        st.caption(f"⚠️ Manually adjusted from {auto_pace} to {pace_override}")

    st.divider()

    if st.button("Predict Score", use_container_width=True):

        pace = pace_override

        # Tournament calibration factors derived from historical data:
        # - NCAA Tournament avg combined score ~141 vs model output ~149 = 5.4% overestimate
        # - Tournament teams score ~4 points fewer per game than regular season efficiency predicts
        tournament_factor = 0.946

        # Base efficiency score
        base_a = (t1['ADJOE'] / 100) * (t2['ADJDE'] / 100) * pace * tournament_factor
        base_b = (t2['ADJOE'] / 100) * (t1['ADJDE'] / 100) * pace * tournament_factor

        # EFG adjustment
        efg_adj_a = (t1['EFG_O'] - t2['EFG_D']) * 0.15
        efg_adj_b = (t2['EFG_O'] - t1['EFG_D']) * 0.15

        # Turnover adjustment
        tor_adj_a = (t2['TORD'] - t1['TOR']) * 0.1
        tor_adj_b = (t1['TORD'] - t2['TOR']) * 0.1

        # Rebounding adjustment
        reb_adj_a = (t1['ORB'] - t2['DRB']) * 0.05
        reb_adj_b = (t2['ORB'] - t1['DRB']) * 0.05

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
