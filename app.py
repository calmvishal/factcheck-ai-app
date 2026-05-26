import streamlit as st
import fitz
import requests
st.markdown(
    "<h1 style='color:#1565C0;'>AI Fact Checker & Verification Tool</h1>",
    unsafe_allow_html=True)
st.markdown(
    "Upload a PDF document to automatically extract factual claims and verify them using AI.")
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
    claim_list = claims.split("\n")
    for claim in claim_list:
        if claim.strip() == "":
            continue
        st.write("Checking:", claim)
        verify_prompt = f"""
        Verify this claim and tell whether it is:
        - Verified
        - Inaccurate
        - False
        Claim:
        {claim}
        Give a short reason in one line.
        """
        verify_response = requests.post(
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
                        "content": verify_prompt
                    }
                ]
            }
        )

        verify_result = verify_response.json()
        if "choices" in verify_result:
            verdict = verify_result["choices"][0]["message"]["content"]
            if "Verified" in verdict:
                st.success(verdict)
            elif "Inaccurate" in verdict:
                st.warning(verdict)
            else:
                st.error(verdict)

        else:
            st.error("Verification failed")
