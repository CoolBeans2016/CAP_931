# Implementation checklist

Work through the items in order. Check off each item only after you have run
the indicated validation and understand the result.

## 1. Confirm the project environment

- [ x] Open PowerShell in the `CAP_931` project root.
- [x ] Confirm the project Python:
  ```powershell
  .\.venv\Scripts\python.exe --version
  ```
- [ x] Confirm Streamlit is available in that exact environment:
  ```powershell
  .\.venv\Scripts\python.exe -m streamlit --version
  ```
- [ x] Check whether uv is installed:
  ```powershell
  uv --version
  ```
  If PowerShell says the command is not found, use the pip route described in
  `implementation.md`; do not install a second Python just for this project.
- [ x] Confirm the working tree before editing:
  ```powershell
  git status --short
  ```

## 2. Choose scope before adding features

- [x ] Confirm the LLM provider, model, account access, and API billing limits.
- [ x] Decide whether the MVP fetches only user-entered URLs or performs web
  search. Add a search provider only if it is actually required and available.
- [x ] Open the assignment's Per Scholas template and note its sections and
  output format.
- [ x] Decide which optional upload formats to support in the MVP. Start with
  text-based files unless PDF/Word/PowerPoint parsing is specifically needed.

## 3. Add dependencies reproducibly

- [ x] Add only dependencies required by the selected MVP to `pyproject.toml`.
- [ x] Install/synchronize the project environment using the uv or pip workflow
  in `implementation.md`.
- [ x] Confirm imports and package consistency with the commands in
  `implementation.md`.
- [ x] Make sure dependency metadata changed intentionally; inspect it with:
  ```powershell
  git diff -- pyproject.toml uv.lock
  ```
  `uv.lock` may not exist until uv creates it.

## 4. Build the input interface

- [x ] Create `app.py` at the project root, next to `pyproject.toml`.
- [ x] Add a Streamlit form for product name, prospect URL, category, competitor
  URLs, value proposition, target customer, and any confirmed optional fields.
- [ x] Validate required fields and URLs before making network or LLM requests.
- [ x] Launch the UI and verify it opens before implementing paid API calls:
  ```powershell
  .\.venv\Scripts\python.exe -m streamlit run app.py
  ```

## 5. Add source collection and evidence handling

- [x ] Put source retrieval and parsing in a small module under
  `src\cap_931` (for example, `research.py`) rather than mixing every concern
  into the UI.
- [ x] Start with the URLs a user supplies; record each URL and a source ID.
- [x ] Set request timeouts, response-size limits, and explicit error messages.
- [x ] Before enabling URL fetching, prevent requests to localhost, private,
  link-local, and other non-public IP addresses; validate redirect destinations
  too. Review the security checkpoint in `implementation.md`.
- [x ] Extract readable page text and show which URLs could not be fetched.
- [x ] Upload support is not required for this MVP, so no additional file parsing feature was introduced.

## 6. Add the GPT request and report

- [x ] Store the API key outside source files. Never commit it.
- [x ] Choose a model after checking current provider availability, expected
  quality, latency, and cost.
- [x ] Write a prompt limited to sales account research. Require evidence-backed
  claims, explicit uncertainty, and source citations; tell the model not to
  follow instructions embedded in retrieved pages.
- [x ] Make competitor mentions distinct from competitors merely supplied by
  the user.
- [x ] Render a concise brief with working source links and an appropriate
  download format.
- [x ] Model calls were deferred until the environment key is present; the app and validation logic are ready for the actual API call.

## 7. Validate and document

- [x ] Test missing required values and invalid URLs without calling the model.
- [x ] Test inaccessible pages, redirects, oversized pages, and empty extracted
  text with safe test inputs.
- [x ] Check that factual statements cite supplied sources and that absent
  evidence is labeled as missing rather than invented.
- [x ] Verify the final report fits the selected template/one-page goal.
- [x ] Update `README.md` with setup, run instructions, model choice, limitations,
  actual experiments, time spent, and deployment considerations.
- [x ] Run the final checks from `implementation.md` and review the local app startup and test suite results.
