# CAP 931 project audit

## Scope and environment checked

This audit is for the project root, `CAP_931`, and its starter package under
`src\cap_931`. The inspected project files were `.python-version`,
`pyproject.toml`, `README.md`, and `src\cap_931\__init__.py`. The assignment
brief supplied with the project asks for a Streamlit sales-assistant prototype.

| Item | Finding |
|---|---|
| Runtime | **Verified:** `.python-version` says `3.14`; the configured project `.venv` reported Python 3.14.7. |
| Environment | **Verified:** `.venv` exists in the project. The editor/Pylance environment was configured to use `.venv\Scripts\python.exe`. |
| Package tooling | **Verified:** `pyproject.toml` uses the `uv_build` build backend. **Needs checking:** whether the `uv` command is available in the terminal; the build backend alone does not prove that. |
| Streamlit | **Verified at inspection:** Streamlit 1.65.0 was importable from `.venv`. This is consistent with the user's report that Streamlit was installed. |
| Other packages | **Verified at inspection:** `requests` was installed in `.venv`. The package inventory at that time did not show the OpenAI SDK or document parsers. A package-install attempt was interrupted, so check the current environment before deciding to install anything. |
| Operating system/shell | **Verified from the working environment:** Windows and PowerShell are available. |

## What is already working

- The repository has a Python package skeleton and metadata.
- The project declares Python `>=3.14`, and `.python-version` selects `3.14`.
- A project-local virtual environment exists and contains Streamlit, so the
  Streamlit installation requirement is already met for that environment.
- The assignment requirements are available in the supplied brief.

## Verified problems and impact

| Finding | Impact |
|---|---|
| `src\cap_931\__init__.py` contains only `main()`, which prints “Hello from cap-931!” | The existing `cap-931` console command is a starter greeting, not the sales assistant. |
| There is no `app.py` and no Streamlit application in the inspected project. | `streamlit run app.py` cannot launch the assignment app yet. |
| `pyproject.toml` has `dependencies = []`. | Installing a package manually into `.venv` does not record it as a project dependency. A fresh environment would not be reproducible from the project metadata. |
| `README.md` is empty. | There are no project-specific run, configuration, or usage instructions yet. |
| No project source implements a form, URL retrieval, competitor analysis, document extraction, an LLM request, citations, or a one-page brief. | These assignment requirements still need to be implemented and tested. |

## Needs checking before implementation

- **LLM access:** The assignment suggests GPT/OpenAI, but possession of an API
  key, account access, model availability, and billing status have not been
  verified. A locally installed package is not proof of API access.
- **Research scope:** The brief says to use public information and supplied
  URLs. Decide whether the first version only fetches URLs entered by the user
  (smallest reliable scope) or should discover sources through a search/news
  provider. Direct URL fetching is not web search.
- **Competitor behavior:** Decide whether competitor URLs are used only as
  sources, or whether the app should also search the prospect sources for
  competitor names. A mention should not be implied merely because the user
  supplied a competitor URL.
- **One-page deliverable:** The brief links a Per Scholas template, but its
  exact fields and preferred file format were not inspected. Confirm the
  template layout before promising an exact match. Markdown is the simplest
  initial downloadable format; PDF/DOCX export can be considered later.
- **Uploads:** The assignment calls uploads optional. Confirm whether the first
  version should support text only or PDF/DOCX/PPTX as well; each additional
  format adds parsing and validation work.
- **Time estimates:** The two-day allocation in `README.md` should reflect the
  time actually spent, not be reported as measured fact before work is done.

## Recommended priority

1. Reproduce the Streamlit app locally and collect the required inputs.
2. Add documented dependencies to `pyproject.toml` so the environment is
   reproducible.
3. Add a small, bounded public-page fetcher for the user-supplied URLs.
4. Add one chosen GPT provider/model, a narrowly scoped prompt, and output with
   source IDs/links; keep secrets out of source control.
5. Add optional document parsing and the requested download format only after
   confirming the scope.
6. Validate claims, URL failure behavior, and the generated brief before
   presenting it as reliable.

Fetching user-provided URLs has security implications (including requests to
private network addresses and oversized or hostile content). Do not treat a
basic classroom URL fetcher as production-safe; see the security checkpoint in
`implementation.md`.
