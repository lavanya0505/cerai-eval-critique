"""
api/main.py
-----------
EvalGuardAI-X FastAPI Backend

Endpoints:
  GET  /health              → Health check
  GET  /metrics             → Aggregate metrics from last run
  POST /evaluate            → Full multi-agent evaluation
  POST /generate_attacks    → Adversarial prompt generator
  GET  /incidents           → List all filed incident reports
  GET  /incidents/{id}      → Get specific incident report
"""

import os
import json
import glob
import time
import logging
from typing import Optional
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agents.orchestrator import evaluate as orchestrate
from engines.harm_engine import classify as classify_harm
from engines.trust_passport import generate as generate_passport
from engines.readiness_grader import grade as grade_readiness
from engines.incident_reporter import generate_report as generate_incident

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="EvalGuardAI-X",
    description="Agentic AI Governance & Trustworthiness Evaluation Platform for Public-Impact Conversational Systems",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request / Response Models ──────────────────────────────

class EvaluateRequest(BaseModel):
    query: str = Field(..., description="The user query sent to the AI system")
    response: str = Field(..., description="The AI system's response to evaluate")
    domain: str = Field(default="civic", description="Domain: healthcare, civic, financial, agriculture, education")
    system_name: Optional[str] = Field(default="Evaluated AI System", description="Name of the system being evaluated")

class AttackRequest(BaseModel):
    base_prompt: str = Field(..., description="The base prompt to generate adversarial variants of")
    domain: str = Field(default="healthcare", description="Domain context for attack generation")
    attack_types: list[str] = Field(
        default=["jailbreak", "emotional_manipulation", "prompt_injection", "authority_spoofing"],
        description="Types of adversarial attacks to generate"
    )

# ── Endpoints ──────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "framework": "EvalGuardAI-X",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agents": ["SafetyAgent", "HallucinationAgent", "LinguisticRobustnessAgent", "HealthcareRiskAgent", "TrustCalibrationAgent"],
        "engines": ["PublicHarmEngine", "TrustPassportGenerator", "DeploymentReadinessGrader", "AIIncidentReporter"]
    }


@app.post("/evaluate")
async def evaluate(req: EvaluateRequest):
    """
    Full multi-agent evaluation pipeline.
    Runs all 5 agents in parallel, then passes results through
    all 4 engines to produce a complete governance artifact.
    """
    start = time.time()
    logger.info(f"Evaluation request: domain={req.domain}, system={req.system_name}")

    try:
        # Step 1: Multi-agent orchestration
        orch_result = orchestrate(
            query=req.query,
            response=req.response,
            domain=req.domain
        )

        # Step 2: Public harm classification
        harm_result = classify_harm(orch_result)

        # Step 3: Trust passport
        passport = generate_passport(
            orchestrator_result=orch_result,
            harm_result=harm_result,
            system_name=req.system_name
        )

        # Step 4: Readiness grade
        readiness = grade_readiness(orch_result, harm_result)

        # Step 5: Auto-file incident if warranted
        incident = None
        verdict = orch_result["consensus"]["deployment_verdict"]
        if verdict in ["BLOCKED", "NOT_RECOMMENDED"] or harm_result["risk_level"] in ["CRITICAL", "HIGH"]:
            incident = generate_incident(orch_result, harm_result, passport, req.system_name)

        total_ms = round((time.time() - start) * 1000)

        return {
            "request": {
                "query": req.query,
                "response": req.response,
                "domain": req.domain,
                "system_name": req.system_name
            },
            "evaluation": orch_result,
            "harm": harm_result,
            "passport": passport,
            "readiness": readiness,
            "incident": incident,
            "meta": {
                "total_latency_ms": total_ms,
                "pipeline": "orchestrate → harm → passport → readiness → incident"
            }
        }

    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate_attacks")
async def generate_attacks(req: AttackRequest):
    """
    Generates adversarial prompt variants for red-teaming.
    Uses the benchmark adversarial generator.
    """
    try:
        from benchmark.adversarial import generate as gen_attacks
        attacks = gen_attacks(
            base_prompt=req.base_prompt,
            domain=req.domain,
            attack_types=req.attack_types
        )
        return {
            "base_prompt": req.base_prompt,
            "domain": req.domain,
            "attacks_generated": len(attacks),
            "attacks": attacks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics():
    """Returns aggregate metrics from the last evaluation run."""
    try:
        results_path = "results/eval_results.json"
        if not os.path.exists(results_path):
            raise HTTPException(status_code=404, detail="No evaluation results found. Run an evaluation first.")

        with open(results_path, "r") as f:
            data = json.load(f)

        summary = data.get("summary", {})
        results = data.get("results", [])

        dim_breakdown = {}
        for r in results:
            dim = r.get("dimension", "unknown")
            score = r.get("judgment", {}).get("score", 0)
            if dim not in dim_breakdown:
                dim_breakdown[dim] = {"scores": [], "passed": 0, "total": 0}
            dim_breakdown[dim]["scores"].append(score)
            dim_breakdown[dim]["total"] += 1
            if r.get("judgment", {}).get("pass", False):
                dim_breakdown[dim]["passed"] += 1

        return {
            "summary": summary,
            "dimension_breakdown": {
                dim: {
                    "average_score": round(sum(v["scores"]) / len(v["scores"]), 2),
                    "pass_rate": round(v["passed"] / v["total"] * 100, 1),
                    "passed": v["passed"],
                    "total": v["total"]
                }
                for dim, v in dim_breakdown.items()
            },
            "total_results": len(results)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/incidents")
async def list_incidents():
    """Lists all filed AI incident reports."""
    incident_files = glob.glob("results/incidents/INC-*.json")
    incidents = []
    for f in sorted(incident_files, reverse=True):
        try:
            with open(f) as fp:
                data = json.load(fp)
            incidents.append({
                "incident_id": data.get("incident_id"),
                "filed_at": data.get("filed_at"),
                "system": data.get("system", {}).get("name"),
                "domain": data.get("system", {}).get("domain"),
                "severity": data.get("incident", {}).get("severity_label"),
                "risk_level": data.get("incident", {}).get("risk_level"),
                "grade": data.get("incident", {}).get("grade"),
                "status": data.get("status"),
            })
        except Exception:
            continue
    return {"total": len(incidents), "incidents": incidents}


@app.get("/incidents/{incident_id}")
async def get_incident(incident_id: str):
    """Returns a specific incident report by ID."""
    path = f"results/incidents/{incident_id}.json"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    with open(path) as f:
        return json.load(f)