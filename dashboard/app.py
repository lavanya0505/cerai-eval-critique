import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import time

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EvalGuardAI-X | Governance Console",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: #050a14;
    color: #e2e8f0;
}

.stApp { background: linear-gradient(135deg, #050a14 0%, #0a1628 50%, #060d1f 100%); }

/* glassmorphism card */
.glass-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(99,179,237,0.15);
    border-radius: 16px;
    padding: 24px;
    margin: 10px 0;
    backdrop-filter: blur(20px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.06);
}

.hero-title {
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(135deg, #63b3ed, #9f7aea, #ed64a6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 4px;
}

.hero-sub {
    text-align: center;
    color: #718096;
    font-size: 0.95rem;
    margin-bottom: 24px;
}

.metric-card {
    background: rgba(99,179,237,0.07);
    border: 1px solid rgba(99,179,237,0.2);
    border-radius: 12px;
    padding: 18px 20px;
    text-align: center;
}

.metric-label { font-size: 0.75rem; color: #718096; text-transform: uppercase; letter-spacing: 1px; }
.metric-value { font-size: 1.9rem; font-weight: 700; color: #63b3ed; margin-top: 4px; }

.status-approved {
    background: linear-gradient(135deg, rgba(72,187,120,0.2), rgba(72,187,120,0.05));
    border: 1px solid #48bb78;
    color: #48bb78;
    border-radius: 8px; padding: 6px 14px; font-weight: 600; font-size: 0.85rem;
    display: inline-block;
}
.status-conditional {
    background: linear-gradient(135deg, rgba(237,137,54,0.2), rgba(237,137,54,0.05));
    border: 1px solid #ed8936;
    color: #ed8936;
    border-radius: 8px; padding: 6px 14px; font-weight: 600; font-size: 0.85rem;
    display: inline-block;
}
.status-blocked {
    background: linear-gradient(135deg, rgba(245,101,101,0.2), rgba(245,101,101,0.05));
    border: 1px solid #f56565;
    color: #f56565;
    border-radius: 8px; padding: 6px 14px; font-weight: 600; font-size: 0.85rem;
    display: inline-block;
}

.agent-card {
    background: rgba(159,122,234,0.07);
    border: 1px solid rgba(159,122,234,0.25);
    border-radius: 12px;
    padding: 16px;
    margin: 8px 0;
}

.finding-flag {
    background: rgba(245,101,101,0.08);
    border-left: 3px solid #f56565;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    margin: 6px 0;
    font-size: 0.88rem;
    color: #fed7d7;
}

.timeline-step {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0;
    border-left: 2px solid rgba(99,179,237,0.3);
    padding-left: 18px;
    margin-left: 8px;
    position: relative;
}

.timeline-dot {
    width: 10px; height: 10px;
    background: #63b3ed;
    border-radius: 50%;
    position: absolute;
    left: -6px;
    box-shadow: 0 0 8px #63b3ed;
}

.section-header {
    font-size: 1.05rem;
    font-weight: 600;
    color: #a0aec0;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin: 20px 0 12px 0;
    padding-bottom: 6px;
    border-bottom: 1px solid rgba(99,179,237,0.15);
}

.stButton > button {
    background: linear-gradient(135deg, #2b6cb0, #553c9a);
    color: white; border: none; border-radius: 10px;
    padding: 10px 28px; font-weight: 600; font-size: 0.95rem;
    width: 100%; cursor: pointer;
    transition: all 0.2s;
}
.stButton > button:hover { opacity: 0.88; transform: translateY(-1px); }

.stTextArea textarea, .stSelectbox select {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(99,179,237,0.2) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}

div[data-testid="stExpander"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(99,179,237,0.12);
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

BACKEND_URL = "https://cerai-eval-critique.onrender.com/evaluate"
DOMAINS = ["Healthcare", "Women Safety", "Civic Tech", "Education", "Welfare", "Financial Risk"]
AGENTS_ORDER = ["SafetyAgent", "HallucinationAgent", "HealthcareRiskAgent", "TrustCalibrationAgent", "LinguisticRobustnessAgent"]

# ── Helpers ────────────────────────────────────────────────────────────────────

def safe_get(obj, *keys, default=None):
    for k in keys:
        if not isinstance(obj, dict):
            return default
        obj = obj.get(k, default)
        if obj is None:
            return default
    return obj


def call_backend(query: str, response: str, domain: str) -> dict | None:
    payload = {"query": query, "response": response, "domain": domain, "system_name": "EvalGuardAI-X"}
    try:
        r = requests.post(BACKEND_URL, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.Timeout:
        st.error("⏳ Backend timed out. The evaluation server may be cold-starting — try again in 30s.")
    except requests.exceptions.ConnectionError:
        st.error("🔌 Cannot reach the governance backend. Check your network or Render service status.")
    except requests.exceptions.HTTPError as e:
        st.error(f"🚨 Backend returned HTTP {e.response.status_code}: {e.response.text[:300]}")
    except json.JSONDecodeError:
        st.error("⚠️ Backend returned non-JSON response.")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)[:200]}")
    return None


def parse_agents(raw_agents) -> list[dict]:
    """Return list of normalised agent dicts with at least {name, score}."""
    if not raw_agents:
        return []
    if isinstance(raw_agents, dict):
        raw_agents = list(raw_agents.values())
    out = []
    for a in raw_agents:
        if isinstance(a, str):
            try:
                a = json.loads(a)
            except Exception:
                continue
        if not isinstance(a, dict):
            continue
        score = a.get("score") or a.get("weighted_score") or a.get("governance_score")
        try:
            score = float(score)
        except (TypeError, ValueError):
            score = None
        name = a.get("agent_name") or a.get("name") or a.get("agent") or "UnknownAgent"
        out.append({**a, "_name": str(name), "_score": score})
    return out


def deployment_badge(status: str) -> str:
    s = str(status).upper().strip()
    if "APPROVE" in s:
        return '<span class="status-approved">✅ APPROVED</span>'
    if "CONDITION" in s:
        return '<span class="status-conditional">⚠️ CONDITIONAL</span>'
    if "BLOCK" in s or "DENY" in s or "REJECT" in s:
        return '<span class="status-blocked">🚫 BLOCKED</span>'
    return f'<span class="status-conditional">{s}</span>'

# ── Charts ─────────────────────────────────────────────────────────────────────

def radar_chart(agents: list[dict]) -> go.Figure:
    rows = [{"Agent": a["_name"].replace("Agent", ""), "Score": a["_score"]}
            for a in agents if a["_score"] is not None]
    if not rows:
        rows = [{"Agent": "NoData", "Score": 0}]
    df = pd.DataFrame(rows)
    fig = go.Figure(go.Scatterpolar(
        r=df["Score"].tolist() + [df["Score"].tolist()[0]],
        theta=df["Agent"].tolist() + [df["Agent"].tolist()[0]],
        fill="toself",
        fillcolor="rgba(99,179,237,0.15)",
        line=dict(color="#63b3ed", width=2),
        marker=dict(color="#9f7aea", size=7),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100], color="#4a5568", gridcolor="rgba(99,179,237,0.1)"),
            angularaxis=dict(color="#a0aec0"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0", family="Inter"),
        margin=dict(t=20, b=20, l=30, r=30),
        showlegend=False,
    )
    return fig


def bar_chart(agents: list[dict]) -> go.Figure:
    rows = [{"Agent": a["_name"].replace("Agent", ""), "Score": a["_score"]}
            for a in agents if a["_score"] is not None]
    if not rows:
        rows = [{"Agent": "NoData", "Score": 0}]
    df = pd.DataFrame(rows).sort_values("Score", ascending=True)
    colors = ["#f56565" if s < 40 else "#ed8936" if s < 70 else "#48bb78" for s in df["Score"]]
    fig = go.Figure(go.Bar(
        x=df["Score"], y=df["Agent"], orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=df["Score"].round(1), textposition="outside",
        textfont=dict(color="#e2e8f0"),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(range=[0, 110], color="#4a5568", gridcolor="rgba(99,179,237,0.08)"),
        yaxis=dict(color="#a0aec0"),
        font=dict(color="#e2e8f0", family="Inter"),
        margin=dict(t=10, b=10, l=10, r=40),
    )
    return fig


def consensus_gauge(score) -> go.Figure:
    try:
        score = float(score)
    except (TypeError, ValueError):
        score = 0
    color = "#48bb78" if score >= 70 else "#ed8936" if score >= 40 else "#f56565"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number=dict(font=dict(color=color, size=36), suffix="/100"),
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor="#4a5568"),
            bar=dict(color=color, thickness=0.25),
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(0,0,0,0)",
            steps=[
                dict(range=[0, 40], color="rgba(245,101,101,0.12)"),
                dict(range=[40, 70], color="rgba(237,137,54,0.12)"),
                dict(range=[70, 100], color="rgba(72,187,120,0.12)"),
            ],
        ),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0", family="Inter"),
        height=200, margin=dict(t=20, b=10, l=20, r=20),
    )
    return fig


def risk_pie(harm_data: dict) -> go.Figure:
    labels, values, clrs = [], [], []
    palette = ["#f56565", "#ed8936", "#ecc94b", "#48bb78", "#63b3ed", "#9f7aea"]
    for i, (k, v) in enumerate(harm_data.items()):
        try:
            labels.append(str(k)); values.append(float(v)); clrs.append(palette[i % len(palette)])
        except (TypeError, ValueError):
            pass
    if not values:
        labels, values, clrs = ["No Risk Data"], [1], ["#4a5568"]
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        marker=dict(colors=clrs, line=dict(color="#050a14", width=2)),
        textfont=dict(color="#e2e8f0"), hole=0.42,
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0", family="Inter"),
        margin=dict(t=10, b=10, l=10, r=10),
        showlegend=True,
        legend=dict(font=dict(color="#a0aec0"), bgcolor="rgba(0,0,0,0)"),
    )
    return fig

# ── Sections ───────────────────────────────────────────────────────────────────

def render_timeline():
    st.markdown('<div class="section-header">⚡ Governance Execution Timeline</div>', unsafe_allow_html=True)
    steps = [
        ("SafetyAgent", "Public harm & safety signal detection"),
        ("HallucinationAgent", "Factual accuracy & confabulation scoring"),
        ("HealthcareRiskAgent", "Medical escalation & clinical risk flags"),
        ("TrustCalibrationAgent", "Confidence vs. epistemic honesty alignment"),
        ("LinguisticRobustnessAgent", "Multilingual drift & adversarial robustness"),
    ]
    cols = st.columns(len(steps))
    for col, (name, desc) in zip(cols, steps):
        with col:
            st.markdown(f"""
            <div style="text-align:center; padding:12px 8px;">
                <div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#2b6cb0,#553c9a);
                    margin:0 auto 8px; display:flex;align-items:center;justify-content:center;
                    box-shadow:0 0 12px rgba(99,179,237,0.4); font-size:14px;">⚙</div>
                <div style="font-size:0.72rem;font-weight:600;color:#63b3ed;">{name.replace('Agent','')}</div>
                <div style="font-size:0.65rem;color:#718096;margin-top:4px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)


def render_deployment_status(deployment: dict):
    st.markdown('<div class="section-header">🚦 Deployment Verdict</div>', unsafe_allow_html=True)
    status = safe_get(deployment, "deployment_status") or safe_get(deployment, "status") or "UNKNOWN"
    grade = safe_get(deployment, "grade") or safe_get(deployment, "deployment_grade") or "—"
    reason = safe_get(deployment, "reason") or safe_get(deployment, "rationale") or "No rationale provided."
    st.markdown(f"""
    <div class="glass-card">
        <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap;">
            {deployment_badge(status)}
            <span style="font-size:1.1rem;font-weight:700;color:#9f7aea;">Grade: {grade}</span>
        </div>
        <p style="margin:12px 0 0;color:#a0aec0;font-size:0.88rem;">{reason}</p>
    </div>
    """, unsafe_allow_html=True)


def render_findings(data: dict):
    st.markdown('<div class="section-header">🔍 Governance Findings & Flags</div>', unsafe_allow_html=True)
    findings = (
        safe_get(data, "findings") or
        safe_get(data, "flags") or
        safe_get(data, "governance_findings") or
        []
    )
    flag_map = {
        "escalation": ("🆘", "Escalation failure detected"),
        "reassurance": ("💬", "False reassurance pattern"),
        "hallucination": ("🌀", "Hallucination risk flagged"),
        "harm": ("⚠️", "Harmful advice detected"),
        "trust": ("🔒", "Trust calibration failure"),
    }
    shown = 0
    if isinstance(findings, list):
        for f in findings:
            label = str(f).lower()
            icon, title = "🚩", str(f)
            for k, (i, t) in flag_map.items():
                if k in label:
                    icon, title = i, t
                    break
            st.markdown(f'<div class="finding-flag">{icon} {title}</div>', unsafe_allow_html=True)
            shown += 1
    elif isinstance(findings, dict):
        for k, v in findings.items():
            if v:
                icon = "🚩"
                for fk, (i, _) in flag_map.items():
                    if fk in str(k).lower():
                        icon = i; break
                st.markdown(f'<div class="finding-flag">{icon} {k}: {v}</div>', unsafe_allow_html=True)
                shown += 1
    if shown == 0:
        st.markdown('<div class="finding-flag" style="border-left-color:#48bb78;color:#c6f6d5;">✅ No critical governance flags raised.</div>', unsafe_allow_html=True)


def render_agent_cards(agents: list[dict]):
    st.markdown('<div class="section-header">🤖 Agent Evaluation Cards</div>', unsafe_allow_html=True)
    if not agents:
        st.info("No agent data returned from backend.")
        return
    cols = st.columns(min(len(agents), 3))
    for i, a in enumerate(agents):
        score = a.get("_score")
        name = a.get("_name", "Agent")
        verdict = a.get("verdict") or a.get("decision") or "—"
        reason = a.get("reasoning") or a.get("reason") or a.get("analysis") or "—"
        score_color = "#48bb78" if (score or 0) >= 70 else "#ed8936" if (score or 0) >= 40 else "#f56565"
        with cols[i % len(cols)]:
            st.markdown(f"""
            <div class="agent-card">
                <div style="font-weight:600;color:#9f7aea;font-size:0.88rem;">{name}</div>
                <div style="font-size:1.6rem;font-weight:700;color:{score_color};margin:6px 0;">
                    {f"{score:.0f}" if score is not None else "N/A"}
                </div>
                <div style="font-size:0.75rem;color:#718096;">Verdict: <span style="color:#e2e8f0">{verdict}</span></div>
                <div style="font-size:0.72rem;color:#718096;margin-top:6px;line-height:1.4;">{str(reason)[:180]}</div>
            </div>
            """, unsafe_allow_html=True)

# ── Main App ───────────────────────────────────────────────────────────────────

def main():
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:16px 0 24px;">
            <div style="font-size:2rem;">🛡️</div>
            <div style="font-weight:700;font-size:1.05rem;color:#63b3ed;">EvalGuardAI-X</div>
            <div style="font-size:0.72rem;color:#718096;">Governance Console v1.0</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("**⚙️ Evaluation Config**")
        domain = st.selectbox("Domain", DOMAINS)
        st.markdown("---")
        st.markdown("""
        <div style="font-size:0.72rem;color:#4a5568;padding:8px 0;">
            <div>Backend: <span style="color:#48bb78">● Live</span></div>
            <div style="margin-top:4px;">Agents: 5 active</div>
            <div style="margin-top:4px;">Mode: API-only</div>
        </div>
        """, unsafe_allow_html=True)

    # Hero
    st.markdown('<div class="hero-title">🛡️ EvalGuardAI-X</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Multi-Agent AI Governance & Deployment Evaluation Console</div>', unsafe_allow_html=True)

    # Input section
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        query = st.text_area("📝 AI Query / Prompt", height=130, placeholder="Enter the user query sent to the AI system...")
    with c2:
        response = st.text_area("🤖 AI System Response", height=130, placeholder="Enter the AI response to be evaluated...")
    st.markdown('</div>', unsafe_allow_html=True)

    run = st.button("⚡ Run Governance Evaluation", use_container_width=True)

    if run:
        if not query.strip() or not response.strip():
            st.warning("Please enter both a query and a response before evaluating.")
            return

        render_timeline()

        with st.spinner("🔬 Running multi-agent governance pipeline..."):
            progress = st.progress(0)
            for i, _ in enumerate(AGENTS_ORDER):
                time.sleep(0.3)
                progress.progress((i + 1) / len(AGENTS_ORDER))
            data = call_backend(query, response, domain)
            progress.empty()

        if data is None:
            st.error("Governance evaluation could not complete. See error above.")
            return

        # ── Top metrics ──
        consensus_score = (
            safe_get(data, "consensus", "final_score") or
            safe_get(data, "consensus", "score") or
            safe_get(data, "consensus_score") or 0
        )
        harm_level = (
            safe_get(data, "harm", "harm_level") or
            safe_get(data, "harm_level") or "Unknown"
        )
        deploy_status = (
            safe_get(data, "deployment", "deployment_status") or
            safe_get(data, "deployment_status") or "Unknown"
        )
        incident_id = (
            safe_get(data, "incident", "incident_id") or
            safe_get(data, "incident_id") or "N/A"
        )

        m1, m2, m3, m4 = st.columns(4)
        for col, label, value in [
            (m1, "Consensus Score", f"{float(consensus_score):.1f}" if consensus_score else "—"),
            (m2, "Harm Level", str(harm_level)),
            (m3, "Deployment", str(deploy_status)),
            (m4, "Incident ID", str(incident_id)[:12]),
        ]:
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Deployment verdict ──
        deploy_data = safe_get(data, "deployment") or {}
        render_deployment_status(deploy_data if isinstance(deploy_data, dict) else {})

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Agents ──
        raw_agents = safe_get(data, "agents") or []
        agents = parse_agents(raw_agents)
        render_agent_cards(agents)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Charts ──
        ch1, ch2 = st.columns(2)
        with ch1:
            st.markdown('<div class="section-header">📡 Agent Radar</div>', unsafe_allow_html=True)
            st.plotly_chart(radar_chart(agents), use_container_width=True, config={"displayModeBar": False})
        with ch2:
            st.markdown('<div class="section-header">📊 Score Distribution</div>', unsafe_allow_html=True)
            st.plotly_chart(bar_chart(agents), use_container_width=True, config={"displayModeBar": False})

        ch3, ch4 = st.columns(2)
        with ch3:
            st.markdown('<div class="section-header">🎯 Consensus Gauge</div>', unsafe_allow_html=True)
            st.plotly_chart(consensus_gauge(consensus_score), use_container_width=True, config={"displayModeBar": False})
        with ch4:
            harm_dict = safe_get(data, "harm") or {}
            if isinstance(harm_dict, dict) and len(harm_dict) > 1:
                st.markdown('<div class="section-header">⚠️ Risk Distribution</div>', unsafe_allow_html=True)
                numeric_harm = {k: v for k, v in harm_dict.items() if isinstance(v, (int, float))}
                if numeric_harm:
                    st.plotly_chart(risk_pie(numeric_harm), use_container_width=True, config={"displayModeBar": False})

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Findings ──
        render_findings(data)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── JSON expanders ──
        st.markdown('<div class="section-header">📂 Governance Artefacts</div>', unsafe_allow_html=True)

        passport = safe_get(data, "passport")
        if passport:
            with st.expander("🪪 AI Trust Passport"):
                st.json(passport if isinstance(passport, dict) else {"raw": str(passport)})

        deploy_exp = safe_get(data, "deployment")
        if deploy_exp:
            with st.expander("🚦 Deployment Report"):
                st.json(deploy_exp if isinstance(deploy_exp, dict) else {"raw": str(deploy_exp)})

        incident = safe_get(data, "incident")
        if incident:
            with st.expander("🚨 Incident Report"):
                st.json(incident if isinstance(incident, dict) else {"raw": str(incident)})

        with st.expander("🗃️ Raw Backend Response"):
            st.json(data)


if __name__ == "__main__":
    main()