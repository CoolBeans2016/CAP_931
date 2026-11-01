# CAP 931 Sales Account Brief

## Project summary

This project is a Streamlit application that collects product and account context from a user, fetches public source pages for the prospect and competitors, and generates a concise evidence-based sales brief. The app is intentionally narrow: it only uses supplied URLs, validates them for safety, extracts readable page text, and sends that evidence to Groq for generation.

The goal is to support a sales researcher or account manager who wants a one-page brief grounded in public company information rather than unsupported assumptions.

## What was built

- A Streamlit UI in `app.py` for the required inputs:
  - product name
  - prospect URL
  - product category
  - competitor URLs
  - value proposition
  - target customer
- A research module in `src/cap_931/research.py` that:
  - validates URLs
  - rejects localhost, private IPs, and other unsafe destinations
  - handles redirects safely
  - fetches content with bounded limits
  - strips HTML scripts and styles before extracting readable text
  - tracks which URLs fail and why
- A report module in `src/cap_931/report.py` that:
  - packages source evidence into a structured prompt
  - instructs the model to stay within the supplied text
  - requires citations for factual claims
  - rejects empty or ungrounded outputs
  - appends a source list with links for the final brief

## Setup

1. Open PowerShell in the project root:

   ```powershell
   Set-Location "C:\Users\Lenovo\Documents\CODE\PER_SCHOLAS\CAX_215\MODULE_931\CAP_931"
   ```

2. Use the project virtual environment instead of the system Python:

   ```powershell
   .\.venv\Scripts\python.exe --version
   .\.venv\Scripts\python.exe -m streamlit --version
   ```

3. Set the Groq API key in the current PowerShell session before generating a brief:

   ```powershell
   $env:GROQ_API_KEY = "your_key_here"
   ```

   Do not store the key in source files. This project intentionally keeps secrets out of version-controlled files.

4. Optional: override the model if needed:

   ```powershell
   $env:GROQ_MODEL = "llama-3.3-70b-versatile"
   ```

## Run the app

```powershell
Set-Location "C:\Users\Lenovo\Documents\CODE\PER_SCHOLAS\CAX_215\MODULE_931\CAP_931"
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Then open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

## How the workflow works

1. User enters the required product and company information.
2. The UI validates required fields and ensures no more than five competitor URLs are submitted.
3. The app fetches the prospect page and each competitor page using the safety checks in `research.py`.
4. Retrieved HTML is cleaned to visible text only.
5. The extracted evidence and product context are sent to Groq as structured JSON.
6. The model is instructed to:
   - ground every factual claim in the supplied source material
   - cite sources like `[S1]`
   - separate evidence-backed observations from hypotheses/recommendations
   - avoid inventing facts, leaders, or signals not present in the source pages
7. The report is displayed in the Streamlit app and can be downloaded as Markdown.

## Sample assignment deliverable

A generated account brief for Cohere Cyber Secure, with Dataprise and NinjaOne
included as comparison sources, is available at
[`src/cap_931/sales-account-brief.md`](src/cap_931/sales-account-brief.md).
Sage Hybrid Monitoring is fictional and used as a proposed product concept for
the assignment. The brief separates Sage's intended design from sourced company
claims, distinguishes managed-service providers from software vendors, and
includes conditional fit hypotheses, discovery questions, and citations.

### How to explain the comparison

- **Sage** is the fictional product concept: a proposed cloud-hosted SaaS view
  for MSPs to monitor customer environments across on-premises and cloud
  systems. Treat these as design goals, not verified market claims.
- **Cohere Cyber Secure** is the prospect in this example. Its public page is
  evidence about its stated services, not evidence that it needs Sage.
- **Dataprise** is a managed IT and cybersecurity services provider, so it is a
  service-model comparison rather than a like-for-like software vendor.
- **NinjaOne** is a software-platform comparison. Compare only the capabilities
  described on the supplied NinjaOne page.
- **Fit hypotheses** are conditional questions to investigate, not facts or
  proof that Sage is better. The source citations support company statements;
  Sage's fictional design comes from the project brief.

## Testing and validation

The assignment was validated using the project test suite:

```powershell
Set-Location "C:\Users\Lenovo\Documents\CODE\PER_SCHOLAS\CAX_215\MODULE_931\CAP_931"
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Actual result:

- 18 tests ran
- 18 tests passed
- exit code: 0

Additional runtime verification was also performed by starting the Streamlit app in headless mode and confirming an HTTP 200 response from `http://localhost:8501`.

## Limitations and responsibilities

- The app uses only user-supplied public sources; it does not perform general-purpose web searching.
- The app is designed for a classroom/research prototype and should not be treated as a production-safe public web scraper.
- It blocks private/localhost destinations and validates redirects to reduce common SSRF risks.
- Any real AI generation depends on the presence of a valid Groq API key and the user's billing/account status.
- The model is instructed to state uncertainty where evidence is missing; it will not invent facts.

## Model and provider choice

This version uses the Groq OpenAI-compatible API with the default model:

```text
openai/gpt-oss-120b
```

The implementation uses the OpenAI Python SDK against the Groq endpoint because Groq provides an OpenAI-compatible API surface.

## Deployment considerations

For a classroom or internal prototype:

- keep the app on a trusted local machine or a controlled environment
- store secrets in environment variables, not in code
- keep the fetched pages limited to user-supplied public URLs
- use permissioned or allowlisted access if the app is later expanded beyond the assignment scope

This approach is suitable for a controlled demo but should be reviewed before any public internet deployment.

## Time and project status

This assignment was completed as a working prototype with the required core behavior, validation tests, and a verified app startup. The project is ready for demonstration and explanation in class.
