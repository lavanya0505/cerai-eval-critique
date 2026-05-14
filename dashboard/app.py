# dashboard/app.py

import os
import sys
import base64
import streamlit as st

ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from agents.orchestrator import evaluate
from engines.harm_engine import classify
from engines.readiness_grader import grade
from engines.trust_passport import generate

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="EvalGuardAI-X",
    layout="wide",
    page_icon="🛡️",
)

# =====================================================
# LOAD CSS
# =====================================================

css_path = "dashboard/styles.css"

if os.path.exists(css_path):

    with open(css_path) as f:

        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

# =====================================================
# IMAGE ENCODER
# =====================================================

def img_to_base64(path):

    if not os.path.exists(path):
        return ""

    with open(path, "rb") as img:
        return base64.b64encode(
            img.read()
        ).decode()

# =====================================================
# NAVBAR
# =====================================================

st.markdown(
    """
    <div class="eg-nav">

        <div class="eg-nav-inner">

            <div class="eg-nav-brand">

                <div class="eg-nav-logo">
                    🛡️
                </div>

                <div>

                    <div class="eg-nav-title">
                        EvalGuardAI-X
                    </div>

                    <div class="eg-nav-sub">
                        AI Governance Infrastructure
                    </div>

                </div>

            </div>

            <div class="eg-nav-status">
                ● SYSTEM LIVE
            </div>

        </div>

    </div>
    """,
    unsafe_allow_html=True
)

# =====================================================
# HERO
# =====================================================

hero_img = img_to_base64(
    "dashboard/assets/hero-healthcare.jpg"
)

hero_html = f"""
<section
    class="eg-hero"
    style="
        background-image:
        linear-gradient(
            rgba(5,8,22,0.82),
            rgba(5,8,22,0.92)
        ),
        url('data:image/jpeg;base64,{hero_img}');
    "
>

    <div class="eg-hero-content">

        <div class="eg-label">
            AI GOVERNANCE FRAMEWORK
        </div>

        <div class="eg-hero-title">

            Governing AI Before It
            <span class="eg-accent">
                Harms Real People
            </span>

        </div>

        <div class="eg-hero-sub">

            EvalGuardAI-X evaluates conversational AI
            systems across healthcare, civic-tech,
            multilingual safety, welfare delivery,
            and vulnerable public-service deployment contexts.

        </div>

    </div>

</section>
"""

st.markdown(
    hero_html,
    unsafe_allow_html=True
)

# =====================================================
# STATS
# =====================================================

st.markdown(
    """
    <div class="eg-stats">

        <div class="eg-stat-card">
            <div class="eg-stat-value">128+</div>
            <div class="eg-stat-label">
                Benchmark Cases
            </div>
        </div>

        <div class="eg-stat-card">
            <div class="eg-stat-value">5</div>
            <div class="eg-stat-label">
                Governance Agents
            </div>
        </div>

        <div class="eg-stat-card">
            <div class="eg-stat-value">14</div>
            <div class="eg-stat-label">
                Public Harm Domains
            </div>
        </div>

        <div class="eg-stat-card">
            <div class="eg-stat-value">LIVE</div>
            <div class="eg-stat-label">
                Deployment Status
            </div>
        </div>

    </div>
    """,
    unsafe_allow_html=True
)

# =====================================================
# DOMAINS
# =====================================================

domains = [

    (
        "Healthcare AI",
        "Clinical escalation and false reassurance detection",
        "dashboard/assets/healthcare.jpg"
    ),

    (
        "Women Safety",
        "Domestic violence and vulnerable-user safety evaluation",
        "dashboard/assets/women-safety.jpg"
    ),

    (
        "Agriculture",
        "Farmer-facing AI reliability evaluation",
        "dashboard/assets/agriculture.jpg"
    ),

    (
        "Civic Tech",
        "Welfare schemes and citizen-service governance",
        "dashboard/assets/civic-tech.jpg"
    ),

    (
        "Education",
        "Educational misinformation and accessibility evaluation",
        "dashboard/assets/education.jpg"
    )

]

domain_html = """
<div class="eg-section-title">
    Governance Domains
</div>

<div class="eg-domains-grid">
"""

for title, desc, path in domains:

    img64 = img_to_base64(path)

    domain_html += f"""

    <div class="eg-domain-card">

        <div
            class="eg-domain-image"
            style="
                background-image:
                linear-gradient(
                    rgba(5,8,22,0.25),
                    rgba(5,8,22,0.82)
                ),
                url('data:image/jpeg;base64,{img64}');
            "
        >

            <div class="eg-domain-overlay">

                <div class="eg-domain-title">
                    {title}
                </div>

                <div class="eg-domain-desc">
                    {desc}
                </div>

            </div>

        </div>

    </div>
    """

domain_html += "</div>"

st.markdown(
    domain_html,
    unsafe_allow_html=True
)

# =====================================================
# EVALUATION
# =====================================================

st.markdown(
    """
    <div class="eg-section-title">
        Live Governance Evaluation
    </div>
    """,
    unsafe_allow_html=True
)

query = st.text_area(
    "User Query",
    height=150
)

response = st.text_area(
    "AI Response",
    height=180
)

domain = st.selectbox(
    "Domain",
    [
        "healthcare",
        "mental_health",
        "women_safety",
        "financial",
        "civic",
        "welfare"
    ]
)

# =====================================================
# RUN EVALUATION
# =====================================================

if st.button("Run Governance Evaluation"):

    with st.spinner(
        "Running multi-agent governance..."
    ):

        result = evaluate(
            query=query,
            response=response,
            domain=domain
        )

        harm = classify(result)

        readiness = grade(
            result,
            harm
        )

        passport = generate(
            result,
            harm,
            "EvalGuardAI-X"
        )

        consensus_data = result.get(
            "consensus",
            {}
        )

        if isinstance(consensus_data, dict):

            consensus = float(
                consensus_data.get(
                    "score",
                    0
                )
            )

        else:

            consensus = float(consensus_data)

        verdict = passport["verdict"][
            "deployment_status"
        ]

        risk = passport["verdict"][
            "risk_level"
        ]

        grade_letter = passport["verdict"][
            "grade"
        ]

        agents_data = result.get(
            "agents",
            {}
        )

        if isinstance(agents_data, dict):
            agents_list = list(
                agents_data.values()
            )
        else:
            agents_list = agents_data

        passed_count = sum(
            1
            for a in agents_list
            if isinstance(a, dict)
            and a.get("passed")
        )

        verdict_class = {
            "BLOCKED":
            "eg-blocked",

            "APPROVED":
            "eg-approved",

            "CONDITIONAL":
            "eg-conditional"
        }.get(
            verdict,
            "eg-conditional"
        )

        st.markdown(
            f"""
            <div class="eg-verdict {verdict_class}">

                <div>

                    <div class="eg-verdict-title">
                        {verdict}
                    </div>

                    <div class="eg-verdict-risk">
                        Public Harm Risk:
                        {risk}
                    </div>

                </div>

                <div class="eg-verdict-score">
                    {round(consensus * 100, 1)}%
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        # =====================================================
        # AGENTS
        # =====================================================

        st.markdown(
            """
            <div class="eg-section-title">
                Multi-Agent Consensus
            </div>
            """,
            unsafe_allow_html=True
        )

        agent_html = """
        <div class="eg-agent-grid">
        """

        for agent in agents_list:

            if not isinstance(agent, dict):
                continue

            score = round(
                float(agent.get(
                    "score",
                    0
                )) * 100,
                1
            )

            passed = agent.get(
                "passed",
                False
            )

            name = agent.get(
                "agent",
                "Unknown"
            )

            reasoning = agent.get(
                "reasoning",
                "No reasoning available."
            )

            badge_class = (
                "eg-pass"
                if passed else
                "eg-fail"
            )

            color = (
                "#10B981"
                if passed else
                "#EF4444"
            )

            status = (
                "PASSED"
                if passed else
                "FAILED"
            )

            card_fail = (
                ""
                if passed else
                "eg-agent-card-fail"
            )

            agent_html += f"""

            <div class="eg-agent-card {card_fail}">

                <div class="eg-agent-header">

                    <div class="eg-agent-name">
                        {name}
                    </div>

                    <div class="eg-agent-badge {badge_class}">
                        {status}
                    </div>

                </div>

                <div
                    class="eg-agent-score"
                    style="color:{color}"
                >
                    {score}%
                </div>

                <div class="eg-progress">

                    <div
                        class="eg-progress-fill"
                        style="
                            width:{score}%;
                            background:{color};
                        "
                    ></div>

                </div>

                <div class="eg-agent-reason">
                    {reasoning[:220]}
                </div>

            </div>
            """

        agent_html += "</div>"

        st.markdown(
            agent_html,
            unsafe_allow_html=True
        )

        # =====================================================
        # FINDINGS
        # =====================================================

        findings = []

        for agent in agents_list:

            if not isinstance(agent, dict):
                continue

            if "flags" in agent:
                findings.extend(
                    agent["flags"]
                )

            if "red_flags_detected" in agent:
                findings.extend(
                    agent["red_flags_detected"]
                )

        findings = list(set(findings))

        if findings:

            st.markdown(
                """
                <div class="eg-section-title">
                    Governance Findings
                </div>
                """,
                unsafe_allow_html=True
            )

            for item in findings:

                st.markdown(
                    f"""
                    <div class="eg-finding">
                        ⚠️ {item}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with st.expander(
            "Deployment Readiness"
        ):
            st.json(readiness)

        with st.expander(
            "AI Trust Passport"
        ):
            st.json(passport)

        with st.expander(
            "Raw Evaluation"
        ):
            st.json(result)