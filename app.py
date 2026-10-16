from openai import APIStatusError, OpenAIError
import streamlit as st
from cap_931.research import collect_sources
from cap_931.report import generate_report

st.title("Sales Account Brief")
st.caption(
    "Collect public pages first. When you click Generate brief, entered "
    "details and fetched page text are sent to Groq. Usage is subject to "
    "your Groq account limits."
)

with st.form("account_inputs"):
    product_name = st.text_input("Product name")
    company_url = st.text_input("Prospect company URL")
    product_category = st.text_input("Product category")
    competitor_urls = st.text_area("Competitor URLs (one per line)")
    value_proposition = st.text_area(
        "Value proposition",
        help=(
            "Describe the problem your product solves, the benefit it provides, "
            "and what makes it different."
        ),
        placeholder=(
            "Example: Helps managed service providers spot security issues "
            "sooner with 24/7 monitoring and locally hosted support."
        ),
    )
    target_customer = st.text_input("Target customer")
    submitted = st.form_submit_button("Continue")

if submitted:
    st.session_state.pop("source_results", None)
    st.session_state.pop("account_data", None)
    st.session_state.pop("report", None)

    required = {
        "Product name": product_name,
        "Prospect company URL": company_url,
        "Product category": product_category,
        "Value proposition": value_proposition,
        "Target customer": target_customer,
    }
    missing = [label for label, value in required.items() if not value.strip()]

    if missing:
        st.error("Please fill in: " + ", ".join(missing))
    else:
        competitor_url_list = competitor_urls.splitlines()
        nonempty_competitor_urls = [
            url.strip() for url in competitor_url_list if url.strip()
        ]

        if len(nonempty_competitor_urls) > 5:
            st.error("Enter no more than 5 competitor URLs.")
        else:
            sources, failures = collect_sources(
                company_url,
                nonempty_competitor_urls,
            )
            st.session_state["source_results"] = {
                "sources": sources,
                "failures": failures,
            }
            st.session_state["account_data"] = {
                "product_name": product_name.strip(),
                "prospect_url": company_url.strip(),
                "product_category": product_category.strip(),
                "value_proposition": value_proposition.strip(),
                "target_customer": target_customer.strip(),
            }

if "source_results" in st.session_state:
    source_results = st.session_state["source_results"]
    sources = source_results["sources"]
    failures = source_results["failures"]

    if sources:
        st.success(f"Fetched {len(sources)} source(s).")
        for source in sources:
            st.subheader(f"{source['id']} — {source['type'].title()}")
            st.write(f"[{source['title']}]({source['url']})")
            with st.expander(f"View {source['id']} page text"):
                st.write(source["text"])
    else:
        st.warning("No sources could be fetched.")

    if failures:
        st.error("Some URLs could not be fetched:")
        for failure in failures:
            st.write(
                f"{failure['type'].title()} — {failure['url']}: "
                f"{failure['error']}"
            )

    has_prospect_source = any(
        source["type"] == "prospect" for source in sources
    )
    if not has_prospect_source:
        st.warning("Fetch the prospect page successfully before generating a brief.")
    elif st.button("Generate brief", type="primary"):
        with st.spinner("Preparing an evidence-based brief..."):
            try:
                report = generate_report(
                    **st.session_state["account_data"],
                    sources=sources,
                )
            except ValueError as exc:
                st.error(str(exc))
            except APIStatusError as exc:
                details = exc.body
                if not details:
                    details = exc.response.text.strip() or str(exc)
                if not details:
                    details = "Groq did not include an error message in its response."
                st.error(
                    f"The Groq request failed (HTTP {exc.status_code}): "
                    f"{details}"
                )
                if exc.request_id:
                    st.caption(f"Groq request ID: {exc.request_id}")
            except OpenAIError as exc:
                st.error(f"The Groq request failed: {exc}")
            except RuntimeError as exc:
                st.error(f"Could not prepare a valid report: {exc}")
            else:
                st.session_state["report"] = report

if "report" in st.session_state:
    st.subheader("Sales account brief")
    st.markdown(st.session_state["report"])
    st.download_button(
        "Download brief as Markdown",
        data=st.session_state["report"],
        file_name="sales-account-brief.md",
        mime="text/markdown",
    )