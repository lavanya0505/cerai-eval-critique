# Contributing to EvalGuardAI-X

Thank you for your interest in contributing to EvalGuardAI-X — an AI governance
evaluation framework for multilingual public-health conversational AI in India.

This is a research project developed for the Gates Foundation AI Fellowship (India 2026).
Contributions that extend the framework's coverage, improve evaluation quality, or
strengthen its deployment in real public-service contexts are especially welcome.

---

## Ways to Contribute

### 1. Extend Benchmark Coverage

The highest-value contributions are new benchmark test cases, particularly:

- **Regional language coverage** — Tamil, Bengali, Telugu, Marathi, Punjabi queries and responses
- **New health domains** — mental health, chronic disease management, elderly care, nutrition
- **Civic services** — new government schemes, welfare programme eligibility queries
- **New adversarial attack types** — attack vectors not currently covered

**Format for new benchmark cases:**
```json
{
  "id": "XX-001",
  "query": "The user query (can be Hindi/Hinglish/English)",
  "response": "The AI response to evaluate (intentionally safe or unsafe)",
  "domain": "healthcare | civic | financial | agriculture | education",
  "expected_verdict": "APPROVED | CONDITIONAL | NOT_RECOMMENDED | BLOCKED",
  "notes": "Why this case is interesting / what failure mode it tests"
}
```

Add cases to the appropriate file in `benchmark/`:
- `benchmark/maternal_health.json`
- `benchmark/child_health.json`
- `benchmark/adversarial_attacks.json`
- `benchmark/trust_calibration.json`
- `benchmark/multilingual_stress.json`
- or create a new domain file

### 2. Improve Evaluation Agents

Agent improvements should:
- Keep the JSON output schema stable (other components depend on it)
- Not remove existing fields (add new ones instead)
- Include at least 3 test cases demonstrating the improvement
- Document the change in the agent's module docstring

**Key areas for agent improvement:**
- `healthcare_agent.py` — extend CLINICAL_SIGNAL_PATTERNS for more languages
- `linguistic_agent.py` — improve handling of Tamil/Bengali script detection
- `hallucination_agent.py` — Indian government scheme knowledge base for fact-checking
- `trust_agent.py` — improve detection of implicit overconfidence

### 3. Add New Agents

If proposing a new evaluation agent:

1. Follow the existing agent interface:
   ```python
   def run(query: str, response: str, domain: str = "civic") -> dict:
       # Returns dict with: agent, score, confidence, passed, weight, reasoning, suggestion
   ```
2. Assign an appropriate weight (justify in the PR)
3. Add the agent to `AGENT_REGISTRY` in `orchestrator.py`
4. Update `TOTAL_WEIGHT` in `orchestrator.py`
5. Add the agent to the README weight table and MODEL_CARD

**Proposed agents for v2:**
- `BiasDetectionAgent` — detect caste, gender, religion bias in responses
- `PrivacyAgent` — detect PII leakage, Aadhaar/PAN number exposure
- `AccessibilityAgent` — evaluate for screen reader / IVR accessibility
- `CitationAgent` — verify that scheme/policy citations are real

### 4. File and Fix Issues

Before filing an issue, search existing issues to avoid duplicates.

**Good issue reports include:**
- Clear title describing the problem
- Steps to reproduce
- Expected vs. actual behaviour
- Example query/response pair that demonstrates the issue
- Your assessment of impact (does this affect governance decisions?)

**Priority issue areas:**
- False negatives in healthcare evaluation (dangerous responses that pass)
- Language detection failures for regional Indian languages
- Agent errors on unusual query types

### 5. Improve Documentation

- README improvements (installation, quickstart, examples)
- MODEL_CARD additions (new limitations discovered, fairness findings)
- Code docstrings for undocumented functions
- Architecture diagrams

---

## Development Setup

```bash
# Clone the repository
git clone https://github.com/lavanya0505/cerai-eval-critique.git
cd cerai-eval-critique

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Add your GROQ_API_KEY to .env

# Run the dashboard locally
streamlit run app.py

# Run a single agent test
python agents/healthcare_agent.py

# Run the orchestrator test
python agents/orchestrator.py
```

---

## Code Style

- **Python:** Follow PEP 8. Use `black` for formatting.
- **Docstrings:** All public functions should have docstrings explaining purpose,
  args, and return format.
- **Comments:** Explain *why*, not *what*. The code shows what; comments explain intent.
- **JSON schemas:** Keep agent output schemas stable across contributions.
- **Error handling:** All agent `run()` functions must handle exceptions and return
  a valid (conservative) result on failure. Never let an agent crash the orchestrator.

```python
# Good error handling pattern (follow this)
except Exception as e:
    logger.error(f"AgentName error: {e}")
    return {
        "agent": "AgentName",
        "score": 0.0,
        "confidence": 0.0,
        "passed": False,
        "weight": WEIGHT,
        "reasoning": f"Agent error: {e}",
        "suggestion": "Re-run evaluation",
        "error": str(e)
    }
```

---

## Testing

Before submitting a PR:

1. Run the agent you modified in standalone mode:
   ```bash
   python agents/your_agent.py
   ```
2. Run the orchestrator with at least one test case:
   ```bash
   python agents/orchestrator.py
   ```
3. Test your benchmark cases against the evaluation pipeline
4. Confirm the Streamlit dashboard still loads: `streamlit run app.py`

There is currently no automated test suite. PRs that add `pytest` tests are very welcome.

---

## Clinical Content Review

**Important:** Any contribution that modifies clinical evaluation criteria
(healthcare agent, clinical signal patterns, risk taxonomy) should ideally be
reviewed by a qualified health professional before merging.

If you don't have access to clinical review:
- Clearly note in the PR that clinical review is pending
- Reference the specific clinical guidelines you're drawing from
- Tag the PR with `needs-clinical-review`

This is especially important for:
- Changes to escalation criteria
- New clinical signal patterns
- Modifications to risk taxonomy weights
- New pediatric/obstetric/emergency signal detection

---

## Multilingual Contributions

If contributing Hindi, Hinglish, or regional language content:

- Provide a translation/explanation for non-Hindi speakers in PR description
- Note the regional variant (formal Hindi, Hinglish, Bundeli, etc.)
- Indicate the literacy level the query represents (urban educated / rural low-literacy)
- Flag if the query uses a dialect-specific term that may not be recognized

---

## Pull Request Process

1. Fork the repository and create a feature branch:
   ```bash
   git checkout -b feature/my-contribution
   ```

2. Make your changes with clear, descriptive commits:
   ```bash
   git commit -m "feat(healthcare): add POSTPARTUM signal pattern"
   git commit -m "bench: add 5 Tamil maternal health test cases"
   ```

3. Update documentation as needed (README, MODEL_CARD, docstrings)

4. Open a PR with:
   - Clear description of what changed and why
   - Examples demonstrating the improvement
   - Note of any limitations or things not done

5. PRs will be reviewed within 7 days. Feedback will be provided in comments.

---

## Governance and Sensitive Domains

This framework is used to make decisions about AI systems deployed to vulnerable
populations. Please keep this in mind:

- **Don't contribute benchmark cases that trivialise health emergencies.** Test
  cases should reflect realistic failures that could occur in real deployments.
- **Don't add attack templates targeting real individuals, organisations, or
  specific communities** by name in adversarial prompts.
- **Do flag genuine safety concerns immediately** — if you discover that the
  framework is producing dangerous false negatives (unsafe responses passing),
  file an issue immediately regardless of PR status.

---

## Recognition

Contributors will be acknowledged in the repository README.
Significant contributions (new agents, language extensions, clinical review)
will be credited in the MODEL_CARD.

---

## Questions

Open a GitHub Discussion for questions about the framework's design, evaluation
methodology, or how to contribute. Issues are for bugs and feature requests;
Discussions are for everything else.

---

*EvalGuardAI-X — Gates Foundation AI Fellowship, India 2026*