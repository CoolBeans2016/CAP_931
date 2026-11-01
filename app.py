from openai import APIStatusError, OpenAIError
import streamlit as st
from cap_931.research import collect_sources
from cap_931.report import generate_report
st.set_page_config(
    page_title="Sales Account Brief",
    page_icon="📊",
    layout="centered",
)

st.markdown(
    """
    <style>
    :root {
        --ink: #172554;
        --muted: #52627a;
        --blue: #2563eb;
        --teal: #0f766e;
        --line: #dbe5f1;
    }

    .stApp {
        background:
            radial-gradient(ellipse at 8% 2%, #dbeafe 0, transparent 31rem),
            #f5f8fc;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stMain"] > div {
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    .hero {
        position: relative;
        overflow: hidden;
        margin: 0 0 1.5rem;
        padding: 2rem 2.25rem;
        border: 1px solid #264577;
        border-radius: 22px;
        background: linear-gradient(120deg, #142a50 0%, #1e3a68 62%, #155e75 100%);
        box-shadow: 0 18px 40px rgba(23, 37, 84, 0.16);
        color: #fff;
    }

    .hero::after {
        position: absolute;
        top: -5rem;
        right: -3rem;
        width: 15rem;
        height: 15rem;
        border: 1px solid rgba(255, 255, 255, 0.13);
        border-radius: 50%;
        box-shadow: 0 0 0 2rem rgba(255, 255, 255, 0.04),
                    0 0 0 4rem rgba(255, 255, 255, 0.03);
        content: "";
        pointer-events: none;
    }

    .hero-kicker {
        margin-bottom: 0.6rem;
        color: #a5f3fc;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }

    .hero h1 {
        margin: 0;
        color: #fff;
        font-size: clamp(2rem, 5vw, 2.8rem);
        letter-spacing: -0.04em;
        line-height: 1.1;
    }

    .hero-copy {
        max-width: 39rem;
        margin: 0.8rem 0 1.4rem;
        color: #dbeafe;
        font-size: 1rem;
        line-height: 1.65;
    }

    .hero-steps {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
    }

    .hero-steps span {
        padding: 0.4rem 0.7rem;
        border: 1px solid rgba(255, 255, 255, 0.22);
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.08);
        color: #f0f9ff;
        font-size: 0.78rem;
        font-weight: 600;
    }

    [data-testid="stForm"] {
        padding: 1.5rem;
        border: 1px solid var(--line);
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.92);
        box-shadow: 0 8px 26px rgba(23, 37, 84, 0.06);
    }

    [data-testid="stForm"] h3 {
        color: var(--ink);
    }

    [data-testid="stWidgetLabel"] p {
        color: #263b5b;
        font-weight: 600;
    }

    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        border-color: #cbd8e8;
        border-radius: 10px;
        background: #fbfdff;
    }

    [data-testid="stTextInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {
        border-color: var(--blue);
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
    }

    [data-testid="stFormSubmitButton"] button,
    [data-testid="stButton"] button[kind="primary"] {
        min-height: 2.8rem;
        border: 0;
        border-radius: 10px;
        background: linear-gradient(100deg, #2563eb, #0f766e);
        color: #fff !important;
        -webkit-text-fill-color: #fff;
        font-weight: 700;
        transition: filter 120ms ease, transform 120ms ease;
    }

    [data-testid="stFormSubmitButton"] button *,
    [data-testid="stButton"] button[kind="primary"] * {
        color: #fff !important;
        -webkit-text-fill-color: #fff;
    }

    [data-testid="stFormSubmitButton"] button:hover,
    [data-testid="stButton"] button[kind="primary"]:hover {
        filter: brightness(1.08);
        transform: translateY(-1px);
    }

    [data-testid="stAlert"] {
        border-radius: 12px;
    }

    @media (max-width: 640px) {
        [data-testid="stMain"] > div {
            padding: 1rem 1rem 3rem;
        }

        .hero {
            padding: 1.5rem;
            border-radius: 16px;
        }

        [data-testid="stForm"] {
            padding: 1rem;
        }
    }
    </style>
    <div class="hero">
        <div class="hero-kicker">Account intelligence workspace</div>
        <h1>Sales account brief</h1>
        <p class="hero-copy">
            Turn public company research into a focused, evidence-backed
            conversation plan for your next customer meeting.
        </p>
        <div class="hero-steps">
            <span>01 &nbsp; Add context</span>
            <span>02 &nbsp; Review sources</span>
            <span>03 &nbsp; Build your brief</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("account_inputs"):
    st.markdown("### Account and product details")
    st.caption(
        "Start with your product and prospect. Public-page research is "
        "collected before the brief is generated."
    )
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
    submitted = st.form_submit_button("Continue", type="primary")

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