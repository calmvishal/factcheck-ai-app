import streamlit as st
import fitz
import requests
from duckduckgo_search import DDGS

st.title("AI Fact Checker & Verification Tool")
st.markdown(
    "Upload a PDF document to automatically extract factual claims and verify them using live web data.")
API_KEY = st.secrets["OPENROUTER_API_KEY"]

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
    {text[:3000]}
    Return only bullet points.
    """
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openai/gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
    )

    result = response.json()

    if "choices" in result:
        claims = result["choices"][0]["message"]["content"]
    else:
        st.error(result)
        st.stop()

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

            results = list(search.text(claim, max_results=1))

            if results:

                snippet = results[0]["body"]

                st.success("Related information found")

                st.caption(snippet)

            else:

                st.warning("No strong evidence found")

        except Exception as e:

            st.error(str(e))
