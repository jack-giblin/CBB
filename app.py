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

    t1 = df[df['TEAM'] == team_a].iloc[0]
    t2 = df[df['TEAM'] == team_b].iloc[0]
    auto_pace = round((t1['ADJ_T'] + t2['ADJ_T']) / 2, 1)

    # League averages used to anchor adjustments
    avg_efficiency = df['ADJOE'].mean()
    avg_efg = df['EFG_O'].mean()
    avg_tor = df['TOR'].mean()
    avg_orb = df['ORB'].mean()
    avg_ftr = df['FTR'].mean()

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

    st.divider()
    st.markdown("#### 🚨 Quick Notes")
    st.caption("""
        ** This program is designed to forecast games using KenPom statistical metrics purely through statistical
        analysis. It accounts for a variety of factors including teams efficiency on both sides of the ball, pace of play, shooting, etc -
        but it does not factor in injuries, sportsbook shading, coaching adjustments, or the chaos that is March Madness **
    """)I 

        # Base efficiency score
        # Dividing by avg_efficiency removes double-counting of average
        # since both ADJOE and ADJDE are already measured against average D1
        base_a = (t1['ADJOE'] * t2['ADJDE'] / avg_efficiency) * (pace / 100)
        base_b = (t2['ADJOE'] * t1['ADJDE'] / avg_efficiency) * (pace / 100)

        # EFG adjustment
        # How much better/worse each team shoots vs opponent's defensive EFG
        # Anchored against league average so adjustment is relative not absolute
        efg_adj_a = ((t1['EFG_O'] - avg_efg) - (t2['EFG_D'] - avg_efg)) * 0.15
        efg_adj_b = ((t2['EFG_O'] - avg_efg) - (t1['EFG_D'] - avg_efg)) * 0.15

        # Turnover adjustment
        # TOR = turnovers allowed (offensive turnovers, lower is better offensively)
        # TORD = steals committed (higher means better defensive pressure)
        pace_ratio = pace / 70
        tor_adj_a = ((avg_tor - t1['TOR']) + (t2['TORD'] - avg_tor)) * 0.1 * pace_ratio
        tor_adj_b = ((avg_tor - t2['TOR']) + (t1['TORD'] - avg_tor)) * 0.1 * pace_ratio

        # Rebounding adjustment
        # ORB = offensive rebound rate (higher is better offensively)
        # DRB = offensive rebound rate allowed (lower is better defensively)
        reb_adj_a = ((t1['ORB'] - avg_orb) - (t2['DRB'] - avg_orb)) * 0.05 * pace_ratio
        reb_adj_b = ((t2['ORB'] - avg_orb) - (t1['DRB'] - avg_orb)) * 0.05 * pace_ratio

        # Free throw adjustment
        # FTR = how often team gets to the line (higher is better offensively)
        # FTRD = how often opponent gets to the line (lower is better defensively)
        ftr_adj_a = ((t1['FTR'] - avg_ftr) - (t2['FTRD'] - avg_ftr)) * 0.05
        ftr_adj_b = ((t2['FTR'] - avg_ftr) - (t1['FTRD'] - avg_ftr)) * 0.05

        # Final scores
        score_a = base_a + efg_adj_a + tor_adj_a + reb_adj_a + ftr_adj_a
        score_b = base_b + efg_adj_b + tor_adj_b + reb_adj_b + ftr_adj_b

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
