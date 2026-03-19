import streamlit as st
import pandas as pd

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

    st.divider()

    st.markdown("#### ⏱️ Game Pace Adjustment")
    st.caption("Pace = estimated possessions per game. Tournament games trend slower than regular season.")

    pace_override = st.slider(
        "Possessions per game",
        min_value=64,
        max_value=79,
        value=70,
        step=1
    )

    if pace_override <= 66:
        st.caption("🐢 Slow pace — think Iowa (64.7). Expect a grind, defensive battle likely.")
    elif pace_override <= 70:
        st.caption("🏀 Average pace — most tournament teams fall around 70 possessions per game.")
    elif pace_override <= 74:
        st.caption("⚡ Up-tempo — both teams like to push the ball.")
    else:
        st.caption("🚀 High pace — think Alabama (78.3). Wide open game, points expected.")

    st.divider()

    if st.button("Predict Score", use_container_width=True):
        t1 = df[df['TEAM'] == team_a].iloc[0]
        t2 = df[df['TEAM'] == team_b].iloc[0]

        pace = pace_override

        # Base efficiency score
        base_a = (t1['ADJOE'] / 100) * (t2['ADJDE'] / 100) * pace
        base_b = (t2['ADJOE'] / 100) * (t1['ADJDE'] / 100) * pace

        # EFG adjustment
        efg_factor_a = (t1['EFG_O'] / t2['EFG_D'])
        efg_factor_b = (t2['EFG_O'] / t1['EFG_D'])

        # Turnover adjustment
        tor_factor_a = 1 - ((t1['TOR'] - t2['TORD']) / 200)
        tor_factor_b = 1 - ((t2['TOR'] - t1['TORD']) / 200)

        # Rebounding adjustment
        reb_factor_a = 1 + ((t1['ORB'] - t2['DRB']) / 200)
        reb_factor_b = 1 + ((t2['ORB'] - t1['DRB']) / 200)

        # Final scores
        score_a = base_a * efg_factor_a * tor_factor_a * reb_factor_a
        score_b = base_b * efg_factor_b * tor_factor_b * reb_factor_b

        c1, c2 = st.columns(2)
        c1.metric(team_a, round(score_a))
        c2.metric(team_b, round(score_b))

        total = round(score_a + score_b)
        winner = team_a if score_a > score_b else team_b
        st.success(f"🏆 **Prediction:** {winner} wins!")
        st.info(f"📊 **Projected Total:** {total} points")





