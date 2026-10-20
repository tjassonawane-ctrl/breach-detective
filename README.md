# 🕵️ Breach Detective

A cyber-security anomaly-spotting game powered by a statistics engine written from scratch in pure Python.

**Play it live:** [https://YOUR-APP-LINK.streamlit.app](https://breach-detective-8qkmbgf95sjrtkmkrvucwx.streamlit.app)
*(Best viewed in Chrome or Firefox.)*

## How it works
You play a security analyst. Each of the 5 rounds shows a chart of simulated network activity (failed logins, data uploads, VPN traffic and so on). A few points are suspicious. Flag them, submit your report, and the engine reveals what it found, then scores you.

- Rounds get harder: outliers get subtler and some start to hide each other.
- After each round, a short stats lesson shows how outliers drag the **mean** around while the **median** barely moves.
- Final rank runs from Script Kiddie to Threat Hunter.

## Scoring
+10 per anomaly caught, -5 per false alarm, -5 per miss, +10 bonus for a perfect report.

## The engine (`stats_engine.py`)
Everything is built without numpy or the statistics module:
merge sort, mean, median, mode, variance, standard deviation (Newton's method square root), quartiles, IQR outlier detection and Pearson correlation.

The game uses the engine as the judge: data is generated randomly, then the IQR rule decides what counts as an outlier.

## Run it locally
```
pip install streamlit plotly
streamlit run app.py
```

## Tech
Python, Streamlit, Plotly.

## Files
- `app.py`: the game
- `stats_engine.py`: the statistics engine
- `requirements.txt`: dependencies
- `.streamlit/config.toml`: dark theme
