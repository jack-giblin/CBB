import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="CBB Predictor", page_icon="🏀")
st.title("🏀 CBB 2026 Score Predictor")

st.caption("""
    This program forecasts games using KenPom statistical metrics through statistical analysis. 
    It accounts for team efficiency on both sides of the ball, pace of play, shooting, turnovers, 
    rebounding, and free throws — but does not factor in injuries, sportsbook shading, 
    coaching adjustments, or the chaos that makes March Madness unpredictable. 🚨
""")

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

    t1 = df[df['TEAM'] == team_a].iloc[0]
    t2 = df[df['TEAM'] == team_b].iloc[0]
    auto_pace = round((t1['ADJ_T'] + t2['ADJ_T']) / 2, 1)

    # League averages used to anchor adjustments
    avg_efficiency = df['ADJOE'].mean()
    avg_efg = df['EFG_O'].mean()
    avg_tor = df['TOR'].mean()
    avg_orb = df['ORB'].mean()
    avg_ftr = df['FTR'].mean()
    national_avg_pace = df['ADJ_T'].mean()

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

        # Base efficiency score
        base_a = (t1['ADJOE'] * t2['ADJDE'] / avg_efficiency) * (pace / 100)
        base_b = (t2['ADJOE'] * t1['ADJDE'] / avg_efficiency) * (pace / 100)

        # EFG adjustment
        efg_adj_a = ((t1['EFG_O'] - avg_efg) - (t2['EFG_D'] - avg_efg)) * 0.15
        efg_adj_b = ((t2['EFG_O'] - avg_efg) - (t1['EFG_D'] - avg_efg)) * 0.15

        # Turnover adjustment
        pace_ratio = pace / 70
        tor_adj_a = ((avg_tor - t1['TOR']) + (t2['TORD'] - avg_tor)) * 0.1 * pace_ratio
        tor_adj_b = ((avg_tor - t2['TOR']) + (t1['TORD'] - avg_tor)) * 0.1 * pace_ratio

        # Rebounding adjustment
        reb_adj_a = ((t1['ORB'] - avg_orb) - (t2['DRB'] - avg_orb)) * 0.05 * pace_ratio
        reb_adj_b = ((t2['ORB'] - avg_orb) - (t1['DRB'] - avg_orb)) * 0.05 * pace_ratio

        # Free throw adjustment
        ftr_adj_a = ((t1['FTR'] - avg_ftr) - (t2['FTRD'] - avg_ftr)) * 0.05
        ftr_adj_b = ((t2['FTR'] - avg_ftr) - (t1['FTRD'] - avg_ftr)) * 0.05

        # Final scores
        score_a = base_a + efg_adj_a + tor_adj_a + reb_adj_a + ftr_adj_a
        score_b = base_b + efg_adj_b + tor_adj_b + reb_adj_b + ftr_adj_b

        # Monte Carlo simulation (10,000 games)
        # std_dev is dynamic — faster pace = more possessions = more variance
        # scaled by square root of pace ratio, grounded in probability theory
        simulations = 10000
        base_std = 10.5
        pace_factor = (pace / national_avg_pace)**0.5
        std_dev = base_std * pace_factor

        sim_a = np.random.normal(score_a, std_dev, simulations)
        sim_b = np.random.normal(score_b, std_dev, simulations)

        sim_total = sim_a + sim_b
        median_total = round(np.median(sim_total) * 2) / 2

        avg_a = np.mean(sim_a)
        avg_b = np.mean(sim_b)

        winner = team_a if avg_a > avg_b else team_b

        # Main prediction
        c1, c2 = st.columns(2)
        c1.metric(team_a, round(avg_a))
        c2.metric(team_b, round(avg_b))

        st.success(f"🏆 **Prediction:** {winner} wins!")

        st.divider()
        st.markdown("#### 🎲 Monte Carlo Simulation (10,000 games)")
        st.caption(f"""
            Simulates 10,000 versions of this game using pace-adjusted statistical variance. 
            Projected tempo of {auto_pace} produces a standard deviation of {round(std_dev, 2)} — 
            faster games have more possessions and therefore more room for variance.
        """)

        st.metric("Simulated Total", median_total)

        st.divider()
        st.markdown("#### 📈 Score Distribution (80% confidence range)")
        st.caption("The range you'd expect the score to land in 8 out of 10 simulated games.")

        st.markdown(f"**{team_a}:** {int(np.percentile(sim_a, 10))} – {int(np.percentile(sim_a, 90))} points")
        st.markdown(f"**{team_b}:** {int(np.percentile(sim_b, 10))} – {int(np.percentile(sim_b, 90))} points")
        st.markdown(f"**Total:** {int(np.percentile(sim_total, 10))} – {int(np.percentile(sim_total, 90))} points")
