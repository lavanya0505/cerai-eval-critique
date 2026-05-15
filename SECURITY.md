# Security Policy — EvalGuardAI-X

**Framework Version:** 1.0.0  
**Last Updated:** May 2026  
**Maintainer:** Lavanya Madaan  

---

## Scope

This security policy covers the EvalGuardAI-X evaluation framework, including:

- The multi-agent evaluation pipeline (`orchestrator.py`, `*_agent.py`)
- The Streamlit web dashboard (`app.py`)
- The benchmark runner and adversarial test suite
- All JSON benchmark datasets

It does **not** cover the AI systems being *evaluated* by this framework.

---

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | ✅ Active  |
| < 1.0   | ❌ No longer maintained |

---

## Reporting a Vulnerability

**Do not file public GitHub issues for security vulnerabilities.**

If you discover a vulnerability in EvalGuardAI-X, please report it via **private disclosure**:

1. **Email:** Create a GitHub Security Advisory via the repository's Security tab
2. **Response SLA:** We will acknowledge within 48 hours and provide an assessment within 7 days
3. **Disclosure timeline:** We follow a 90-day coordinated disclosure policy

When reporting, please include:

- A description of the vulnerability and its potential impact
- Steps to reproduce (proof of concept if available)
- The affected component(s) and version
- Your assessment of severity (CVSS score if possible)

---

## Security Considerations by Component

### 1. API Key Handling

**Risk:** Groq API keys are passed as environment variables or Streamlit secrets.

**Mitigations in place:**
- Keys are never logged or included in evaluation output JSON
- The dashboard uses `type="password"` for the API key input field
- Keys are read from `.env` via `python-dotenv`, not hardcoded

**Required actions by deployers:**
- Never commit `.env` files to version control
- Use `st.secrets` for Streamlit Cloud deployments
- Rotate API keys if accidentally exposed
- Add `.env` to `.gitignore`

```bash
# .gitignore — required entries
.env
*.env
.env.local
secrets.toml
```

### 2. Query and Response Data

**Risk:** User queries and AI responses may contain sensitive PII (names, Aadhaar numbers, health information).

**Current behaviour:** Evaluation results are stored in memory only during the session. The `run_suite.py` batch runner writes results to `results/` directory.

**Required actions by deployers:**
- **Strip PII** from query and response text before passing to the evaluation pipeline in production
- Do **not** log raw queries containing health information
- If storing results for incident memory, implement data retention limits and access controls
- For healthcare deployments: ensure compliance with the Digital Personal Data Protection Act 2023 (India)

### 3. LLM Judge Security

**Risk:** Adversarially crafted responses could attempt to manipulate the LLM judge into producing false scores (judge manipulation attacks).

**Mitigations in place:**
- System prompt explicitly instructs agents to "respond only in valid JSON"
- JSON schema validation — non-conforming responses fall back to conservative `0.0` scores
- Temperature set to `0.1` to reduce susceptibility to creative jailbreaks in judge responses
- No user-controlled content is inserted into the system prompt

**Known limitations:**
- A sufficiently sophisticated response could still attempt to influence the judge via the user prompt
- Judge model (LLaMA 3.3 70B) inherits any biases of its training data
- This is documented as a known limitation in the MODEL_CARD

### 4. Streamlit Dashboard

**Risk:** The dashboard is a web interface that accepts user-supplied text. Risks include XSS via `st.markdown(..., unsafe_allow_html=True)` and SSRF if endpoint evaluation is added.

**Current mitigations:**
- `unsafe_allow_html=True` is used only for static, developer-controlled strings (UI chrome, badges)
- User-supplied query and response text is **never** rendered as raw HTML — it passes to the Groq API only
- No file upload functionality is exposed
- No outbound HTTP requests to user-specified URLs

**Future risk (if endpoint evaluation is added):**
- Any feature allowing users to specify a URL to evaluate must implement strict URL validation and SSRF protections
- Allowlist permitted domains; block private IP ranges (RFC1918)

### 5. Benchmark Datasets

**Risk:** Benchmark JSON files contain adversarial prompts (prompt injections, jailbreak attempts) that could be misused.

**Context:** These are *test inputs for evaluation purposes*, not executable code. They represent realistic attack vectors in the target deployment context.

**Required actions:**
- Do not expose benchmark JSON files via public API without authentication
- Treat adversarial prompt datasets as sensitive research materials
- Do not use adversarial prompts to actually attack production systems

### 6. Dependencies

**Current dependency surface:**
```
fastapi, uvicorn, groq, python-dotenv, pydantic, requests, streamlit, pandas, plotly
```

**Security practices:**
- Dependencies are pinned in `requirements.txt`
- Run `pip audit` or `safety check` before production deployment
- Groq Python SDK — monitor for security advisories

---

## Threat Model

The primary threats for a framework deployed in Indian public-health evaluation contexts:

| Threat | Likelihood | Impact | Mitigation |
|--------|-----------|--------|-----------|
| API key exposure via public repo | HIGH | HIGH | `.gitignore`, secrets management |
| PII in evaluation logs | HIGH | HIGH | Strip PII before evaluation |
| Judge manipulation via adversarial response | MEDIUM | MEDIUM | JSON validation, conservative fallback |
| Misuse of adversarial dataset | LOW | HIGH | Access control, research context |
| Dependency vulnerability | LOW | MEDIUM | Regular audits |
| XSS via user input | LOW | LOW | No HTML rendering of user input |

---

## Security Audit Status

This framework has not undergone a formal third-party security audit. It is a research
and governance evaluation tool, not a production security system.

Before deploying in a production environment handling sensitive healthcare data:

1. Conduct a dependency audit (`pip audit`)
2. Review all data retention and logging paths
3. Implement authentication if exposing the Streamlit dashboard publicly
4. Review compliance requirements under DPDPA 2023 for healthcare data

---

## Acknowledgements

We thank the security research community for responsible disclosure practices.
Contributors who responsibly disclose vulnerabilities will be acknowledged here.

---

*This policy is reviewed annually or following any significant security incident.*