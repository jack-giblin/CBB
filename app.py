import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="CBB Predictor", page_icon="🏀")
st.title("🏀 CBB 2026 Score Predictor")

st.caption("""
    This program forecasts games using KenPom statistical metrics. 
    It does not factor in injuries, sportsbook shading, coaching adjustments, 
    or the chaos that makes March Madness unpredictable. 🚨
""")

# --- Add real results here after each game ---
results = [
    {
        "team_a": "TCU",
        "team_b": "Ohio State",
        "predicted_total": 150.5,
        "sportsbook_total": 146.5,
        "actual_score_a": 67,
        "actual_score_b": 63,
    },
    {
        "team_a": "High Point",
        "team_b": "Wisconsin",
        "predicted_total": 164.0,
        "sportsbook_total": 162.5,
        "actual_score_a": 76,
        "actual_score_b": 89,
    },
    {
        "team_a": "South Florida",
        "team_b": "Louisville",
        "predicted_total": 158.5,
        "sportsbook_total": 163.5,
        "actual_score_a": 74,
        "actual_score_b": 88,
    },
    {
        "team_a": "Troy",
        "team_b": "Nebraska",
        "predicted_total": 142.5,
        "sportsbook_total": 138.5,
        "actual_score_a": 55,
        "actual_score_b": 68,
    },
    {
        "team_a": "Duke",
        "team_b": "Siena",
        "predicted_total": 145.5,
        "sportsbook_total": 137.5,
        "actual_score_a": 78,
        "actual_score_b": 58,
    },
    {
        "team_a": "McNeese",
        "team_b": "Vanderbilt",
        "predicted_total": 153.0,
        "sportsbook_total": 148.5,
        "actual_score_a": 68,
        "actual_score_b": 78,
    },
]

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

        # Score prediction using ADJOE directly
        score_a = (t1['ADJOE'] / 100) * pace
        score_b = (t2['ADJOE'] / 100) * pace

        # Win probability from BARTHAG
        barthag_a = t1['BARTHAG']
        barthag_b = t2['BARTHAG']
        win_prob_a = barthag_a / (barthag_a + barthag_b) * 100
        win_prob_b = 100 - win_prob_a

        winner = team_a if win_prob_a > win_prob_b else team_b

        # Monte Carlo simulation (10,000 games)
        simulations = 10000
        std_dev = 5

        sim_a = np.random.normal(score_a, std_dev, simulations)
        sim_b = np.random.normal(score_b, std_dev, simulations)
        sim_total = sim_a + sim_b
        median_total = round(np.mean(sim_total) * 2) / 2

        # Main prediction
        c1, c2 = st.columns(2)
        c1.metric(team_a, round(score_a))
        c2.metric(team_b, round(score_b))

        st.success(f"🏆 **Prediction:** {winner} wins!")
        st.info(f"📊 **Win Probability:** {team_a} {win_prob_a:.1f}% | {team_b} {win_prob_b:.1f}%")

        st.divider()
        st.markdown("#### 📈 Score Distribution (80% confidence range)")
        st.caption("The range you'd expect the score to land in 8 out of 10 simulated games.")

        st.markdown(f"**{team_a}:** {int(np.percentile(sim_a, 10))} – {int(np.percentile(sim_a, 90))} points")
        st.markdown(f"**{team_b}:** {int(np.percentile(sim_b, 10))} – {int(np.percentile(sim_b, 90))} points")
        st.markdown(f"**Total:** {int(np.percentile(sim_total, 10))} – {int(np.percentile(sim_total, 90))} points")
        st.metric("Simulated Total", median_total)

    # --- Real Results Section ---
    st.divider()

    if results:
        total_bets = 0
        total_wins = 0
        table_rows = []

        for r in results:
            actual_total = r["actual_score_a"] + r["actual_score_b"]
            model_side = "OVER" if r["predicted_total"] > r["sportsbook_total"] else "UNDER"
            if model_side == "OVER":
                total_win = actual_total > r["sportsbook_total"]
            else:
                total_win = actual_total < r["sportsbook_total"]

            total_bets += 1
            if total_win:
                total_wins += 1

            table_rows.append({
                "Game": f"{r['team_a']} vs {r['team_b']}",
                "Our Total": r["predicted_total"],
                "Book": r["sportsbook_total"],
                "Actual": actual_total,
                "Side": model_side,
                "Result": "✅ WIN" if total_win else "❌ LOSS"
            })

        results_df = pd.DataFrame(table_rows)

        st.markdown(f"**📊 Totals Record: {total_wins}-{total_bets - total_wins}**")

        with st.expander("📋 View Results Table"):
            st.dataframe(results_df, use_container_width=True, hide_index=True)
    else:
        with st.expander("📋 Real Results vs Predictions"):
            st.caption("No results yet — check back after games are played.")
