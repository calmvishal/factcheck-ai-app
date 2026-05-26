import streamlit as st
import fitz
from openai import OpenAI
from duckduckgo_search import DDGS

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"],

    default_headers={
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "AI Fact Checker"
    }
)

st.title("AI Fact Checker & Verification Tool")

st.markdown(
    "Upload a PDF document to automatically extract factual claims and verify them using live web data."
)

uploaded_file = st.file_uploader("Upload PDF", type="pdf")

if uploaded_file:

    pdf_data = uploaded_file.read()

    doc = fitz.open(stream=pdf_data, filetype="pdf")

    text = ""

    for page in doc:
        text += page.get_text()

    st.subheader("Extracted Text")
    st.write(text[:2000])

    prompt = f"""
    Extract important factual claims, statistics, dates, and numerical statements from this text.

    Text:
    {text}

    Return only bullet points.
    """

    response = client.chat.completions.create(
        model="openai/gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    claims = response.choices[0].message.content

    st.subheader("Extracted Claims")
    st.write(claims)

    st.subheader("Fact Check Results")

    search = DDGS()

    claim_list = claims.split("\n")

    for claim in claim_list:

        if claim.strip() == "":
            continue

        st.write("Checking:", claim)

        try:

            results = list(search.text(claim, max_results=3))

            if results:

                snippet = results[0]["body"]

                verify_prompt = f"""
                Claim: {claim}

                Search Result:
                {snippet}

                Tell whether this claim is:
                Verified
                Inaccurate
                False

                Give short reason.
                """

                verification = client.chat.completions.create(
                    model="openai/gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "user",
                            "content": verify_prompt
                        }
                    ]
                )

                answer = verification.choices[0].message.content

                st.success(answer)

            else:
                st.error("No evidence found")

        except Exception as e:
            st.error(str(e))
