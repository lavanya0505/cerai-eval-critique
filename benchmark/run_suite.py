import json
import glob
import os
import time

from agents.orchestrator import evaluate
from engines.harm_engine import classify
from engines.trust_passport import generate
from engines.readiness_grader import grade
from engines.incident_reporter import generate_report

RESULTS_DIR = "results/benchmark_runs"
os.makedirs(RESULTS_DIR, exist_ok=True)

benchmark_files = glob.glob("benchmark/generated/*.json")

print("\n===================================================")
print("      EvalGuardAI-X Benchmark Runner")
print("===================================================\n")

print(f"Found {len(benchmark_files)} benchmark files\n")

total_tests = 0
blocked_tests = 0
all_results = []

# ---------------------------------------------------
# RUN ONLY SMALL SAMPLE FOR DEMO
# ---------------------------------------------------

for benchmark_file in benchmark_files[:1]:

    print(f"\nRunning benchmark: {benchmark_file}")

    with open(benchmark_file, "r") as f:
        tests = json.load(f)

    benchmark_results = []

    # only first 5 tests
    for test in tests[:5]:

        total_tests += 1

        print(f"\n→ {test['id']}")
        print(f"  Query: {test['query']}")

        start = time.time()

        # VERY IMPORTANT
        time.sleep(10)

        # -------------------------------
        # MULTI-AGENT EVALUATION
        # -------------------------------

        orchestrator_result = evaluate(
            query=test["query"],
            response=test["response"],
            domain=test["domain"]
        )

        # -------------------------------
        # HARM ANALYSIS
        # -------------------------------

        harm_result = classify(orchestrator_result)

        # -------------------------------
        # TRUST PASSPORT
        # -------------------------------

        passport_result = generate(
            orchestrator_result,
            harm_result,
            "EvalGuardAI-X"
        )

        # -------------------------------
        # READINESS
        # -------------------------------

        readiness_result = grade(
            orchestrator_result,
            harm_result
        )

        # -------------------------------
        # INCIDENT REPORT
        # -------------------------------

        incident_result = generate_report(
            orchestrator_result,
            harm_result,
            passport_result,
            system_name="EvalGuardAI-X"
        )

        deployment_status = (
            passport_result["verdict"]["deployment_status"]
        )

        if deployment_status == "BLOCKED":
            blocked_tests += 1

        elapsed = round(time.time() - start, 2)

        print(f"  Status : {deployment_status}")
        print(f"  Risk   : {harm_result['risk_level']}")
        print(f"  Time   : {elapsed}s")

        result = {
            "test": test,
            "consensus": orchestrator_result["consensus"],
            "risk_level": harm_result["risk_level"],
            "passport": passport_result,
            "readiness": readiness_result,
            "incident": incident_result
        }

        benchmark_results.append(result)
        all_results.append(result)

    output_path = (
        f"{RESULTS_DIR}/"
        f"{os.path.basename(benchmark_file)}"
    )

    with open(output_path, "w") as out:
        json.dump(benchmark_results, out, indent=2)

    print(f"\nSaved → {output_path}")

# ---------------------------------------------------
# FINAL SUMMARY
# ---------------------------------------------------

pass_rate = (
    ((total_tests - blocked_tests) / total_tests) * 100
    if total_tests > 0 else 0
)

print("\n===================================================")
print("FINAL SUMMARY")
print("===================================================\n")

print(f"Total Tests      : {total_tests}")
print(f"Blocked          : {blocked_tests}")
print(f"Pass Rate        : {pass_rate:.1f}%")

with open(f"{RESULTS_DIR}/all_results.json", "w") as f:
    json.dump(all_results, f, indent=2)

print("\nResults saved successfully.")