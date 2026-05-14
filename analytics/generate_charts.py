import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import os

os.makedirs("analytics/outputs", exist_ok=True)

# =====================================================
# SAMPLE GOVERNANCE DATA
# =====================================================

agents = {
    "Safety": 0.92,
    "Hallucination": 0.84,
    "Trust": 0.67,
    "Healthcare": 0.95,
    "Linguistic": 0.72
}

# =====================================================
# BAR CHART
# =====================================================

plt.figure(figsize=(10,6))

plt.bar(
    agents.keys(),
    [v * 100 for v in agents.values()]
)

plt.title(
    "Governance Agent Scores",
    fontsize=18
)

plt.ylabel("Score (%)")

plt.ylim(0,100)

plt.savefig(
    "analytics/outputs/bar_chart.png"
)

plt.close()

# =====================================================
# RADAR CHART
# =====================================================

labels = list(agents.keys())

values = list(agents.values())

values += values[:1]

angles = np.linspace(
    0,
    2*np.pi,
    len(labels),
    endpoint=False
).tolist()

angles += angles[:1]

fig = plt.figure(figsize=(8,8))

ax = plt.subplot(111, polar=True)

ax.plot(
    angles,
    values,
    linewidth=2
)

ax.fill(
    angles,
    values,
    alpha=0.25
)

ax.set_thetagrids(
    np.degrees(angles[:-1]),
    labels
)

plt.title(
    "Governance Radar Analysis",
    fontsize=18
)

plt.savefig(
    "analytics/outputs/radar.png"
)

plt.close()

# =====================================================
# HEATMAP
# =====================================================

heatmap_data = pd.DataFrame({

    "Healthcare":[92,88,75],
    "WomenSafety":[84,90,68],
    "Civic":[70,82,61],
    "Finance":[76,80,73]

},

index=[
    "GPT-4",
    "Claude",
    "Gemini"
])

plt.figure(figsize=(10,6))

sns.heatmap(
    heatmap_data,
    annot=True,
    cmap="coolwarm"
)

plt.title(
    "AI Governance Heatmap"
)

plt.savefig(
    "analytics/outputs/heatmap.png"
)

plt.close()

# =====================================================
# RISK DISTRIBUTION PIE
# =====================================================

risk_labels = [

    "Healthcare Harm",
    "Hallucination",
    "Trust Erosion",
    "Escalation Failure"

]

risk_values = [35,25,20,20]

plt.figure(figsize=(8,8))

plt.pie(
    risk_values,
    labels=risk_labels,
    autopct="%1.1f%%"
)

plt.title(
    "Public Harm Distribution"
)

plt.savefig(
    "analytics/outputs/risk_distribution.png"
)

plt.close()

# =====================================================
# CONSENSUS TREND
# =====================================================

x = [1,2,3,4,5]

y = [42,58,63,71,89]

plt.figure(figsize=(10,6))

plt.plot(
    x,
    y,
    marker="o"
)

plt.title(
    "Consensus Score Improvement"
)

plt.xlabel("Evaluation Runs")

plt.ylabel("Consensus Score")

plt.savefig(
    "analytics/outputs/consensus_trend.png"
)

plt.close()

# =====================================================
# BENCHMARK LEADERBOARD
# =====================================================

models = [
    "GPT-4",
    "Claude",
    "Gemini",
    "Llama"
]

scores = [91,88,82,74]

plt.figure(figsize=(10,6))

sns.barplot(
    x=models,
    y=scores
)

plt.title(
    "Governance Benchmark Leaderboard"
)

plt.ylabel("Governance Score")

plt.savefig(
    "analytics/outputs/benchmark_scores.png"
)

plt.close()

print(
    "All charts generated successfully."
)