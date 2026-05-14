"""
metrics.py
----------
Computes aggregate metrics from evaluation results.
Used by the report generator and the HTML dashboard.
"""

import json


def load_results(path: str = "results/eval_results.json") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_metrics(results_path: str = "results/eval_results.json") -> dict:
    """
    Computes full metrics report from eval_results.json.
    Returns a structured dict ready for HTML rendering or JSON export.
    """
    data = load_results(results_path)
    summary = data["summary"]
    results = data["results"]

    # Per-dimension breakdown
    dimensions = {}
    for r in results:
        dim = r["dimension"]
        score = r["judgment"].get("score", 0)
        passed = r["judgment"].get("pass", False)
        severity = r["severity"]

        if dim not in dimensions:
            dimensions[dim] = {
                "scores": [], "passed": 0, "total": 0,
                "critical_failures": [], "issues_found": []
            }

        dimensions[dim]["scores"].append(score)
        dimensions[dim]["total"] += 1
        if passed:
            dimensions[dim]["passed"] += 1
        if not passed and severity == "critical":
            dimensions[dim]["critical_failures"].append({
                "id": r["id"],
                "prompt": r["prompt"],
                "score": score,
                "reasoning": r["judgment"].get("reasoning", "")
            })
        for issue in r["judgment"].get("issues", []):
            dimensions[dim]["issues_found"].append(issue)

    dim_metrics = {}
    for dim, d in dimensions.items():
        avg = round(sum(d["scores"]) / len(d["scores"]), 2)
        pass_rate = round(d["passed"] / d["total"] * 100, 1)
        dim_metrics[dim] = {
            "average_score": avg,
            "pass_rate_percent": pass_rate,
            "passed": d["passed"],
            "total": d["total"],
            "critical_failures": d["critical_failures"],
            "top_issues": list(set(d["issues_found"]))[:5]
        }

    # Severity breakdown
    severity_breakdown = {}
    for r in results:
        sev = r["severity"]
        if sev not in severity_breakdown:
            severity_breakdown[sev] = {"total": 0, "passed": 0}
        severity_breakdown[sev]["total"] += 1
        if r["judgment"].get("pass", False):
            severity_breakdown[sev]["passed"] += 1

    # Top failures
    failures = [
        {
            "id": r["id"],
            "dimension": r["dimension"],
            "severity": r["severity"],
            "prompt": r["prompt"][:100],
            "score": r["judgment"].get("score", 0),
            "reasoning": r["judgment"].get("reasoning", ""),
            "suggestion": r["judgment"].get("suggestion", "")
        }
        for r in results if not r["judgment"].get("pass", False)
    ]
    failures.sort(key=lambda x: x["score"])

    return {
        "summary": summary,
        "dimension_metrics": dim_metrics,
        "severity_breakdown": severity_breakdown,
        "failures": failures,
        "all_results": results
    }


if __name__ == "__main__":
    metrics = compute_metrics()
    print(json.dumps(metrics["summary"], indent=2))
    print("\nDimension Breakdown:")
    for dim, m in metrics["dimension_metrics"].items():
        print(f"  {dim:35s} avg={m['average_score']:4.1f}  pass={m['pass_rate_percent']}%")