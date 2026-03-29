# 🏀 CBB 2026 Score Predictor

A March Madness score predictor built in Python using Streamlit and KenPom statistical metrics. 
Built as a personal project to apply data analytics concepts to sports — no computer science 
background, just curiosity and a lot of iteration.

## 🔗 Live App
[cbbgiblin.streamlit.app](https://cbbgiblin.streamlit.app)

## 📊 How It Works

The model uses KenPom efficiency metrics to predict game outcomes for the 2026 NCAA Tournament.

### Core Formula
Each team's projected score is calculated by averaging their offensive efficiency against 
the opponent's defensive efficiency, scaled by the game's adjusted tempo:
```python
score_a = ((ADJOE_a / 100) + (ADJDE_b / 100)) / 1.92 * pace
```

### Key Stats Used
- **ADJOE** — Adjusted Offensive Efficiency (points scored per 100 possessions vs average D1 defense)
- **ADJDE** — Adjusted Defensive Efficiency (points allowed per 100 possessions vs average D1 offense)
- **ADJ_T** — Adjusted Tempo (possessions per 40 minutes vs average D1 opponent)
- **BARTHAG** — Power Rating (probability of beating an average D1 team) — used for win probability

### Monte Carlo Simulation
The model runs 10,000 simulations of each game using a pace-adjusted standard deviation:
```python
pace_factor = (pace / national_avg_pace) ** 0.5
std_dev = 7 * pace_factor
```

Faster games have more possessions and therefore more variance. This is grounded in 
probability theory — variance scales with the square root of possessions.

The simulation outputs an 80% confidence range for each team's score and the combined total.

## 📈 Results Tracker
The app tracks predicted winners vs actual winners throughout the tournament, 
updating the win/loss record in real time as games are played.

## 🛠️ Built With
- Python
- Streamlit
- Pandas
- NumPy
- KenPom data (cbb26.csv)

## ⚠️ Limitations
This model does not account for:
- Player injuries or absences
- Sportsbook line shading
- Coaching adjustments and game-specific strategy
- Tournament experience and momentum
- In-game factors like foul trouble

Even the most sophisticated models can't predict everything that makes March Madness great.

## 👤 About
Built by Jack Giblin — Supply Chain & Operations Management graduate applying 
data analytics to sports. Background in SQL, Python, and Tableau.
