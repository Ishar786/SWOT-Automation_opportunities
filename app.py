# app.py

import streamlit as st
import google.generativeai as genai
import textwrap
import os
from dotenv import load_dotenv

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SWOT Point Generator",
    page_icon="✍",
    layout="wide"
)

# --- LOAD ENVIRONMENT VARIABLES FOR LOCAL DEVELOPMENT ---
# This line is for running the app locally. It loads the API key from a .env file.
# When deployed on Streamlit Community Cloud, you will set this as a secret.
load_dotenv()

# --- THE STYLE GUIDE (EXAMPLES) ---
# This dictionary holds the perfect example for each SWOT category.
SWOT_EXAMPLES = {
    "Opportunity": [
        textwrap.dedent("""
            in January 2025, Elevance has acquired Indiana University (IU) Health Plans, to enhance its local presence, expanding product offerings. IU Health Plans is a managed care organization created by Indiana University Health which provides Medicare advantage plans to 19,000 people across 36 countries. This acquisition would elevate quality and would expand Elevance's product offerings. This acquisition would strengthen the company’s efforts to cultivate healthier communities and improve health outcomes for those they are privileged to serve. This strategic step is in line with Elevance’s health equity goals and allow it to provide comprehensive access to high-quality care and timely interventions.
        """),
        textwrap.dedent("""
            in September 2024, AT&T has announced its plan to introduce a Wi-Fi 7-capable gateway, to step forward in its commitment to deliver cutting-edge home connectivity. This Wi-Fi would aim to unlock the full potential of AT&T’s multi-gig fiber offerings by improving speed, latency, and the ability to handle next-generation digital services. Through this initiative, the company would be able to solidify its leadership in providing reliable, scalable, and forward-looking broadband solutions for residential users.
        """)
    ],
    "Weakness": [
        textwrap.dedent("""
            BASF has agreed to pay a $700,000 civil penalty, to the U.S. Environmental Protection Agency (EPA) for the violation of the Toxic Substances Control Act (TSCA) related to the group’s chemical reporting obligations. According to EPA findings, BASF did not report required data on hundreds of chemical substances within the mandated timeframe, hindering the agency’s ability to assess potential public health and environmental risks. This settlement reinforces EPA’s commitment to fair but firm enforcement of environmental laws. It also serves as a reminder to the chemical industry of the importance of meeting federal reporting standards.
        """),
        textwrap.dedent("""
            in January 2025, AT&T has faced a lawsuit filed by Cornell University over a wireless fidelity (WI-FI) patent infringement. The lawsuit alleged that AT&T’s smartphones, routers, and other Wi-Fi-enabled products violate two patents related to Wi-Fi 5 and Wi-Fi 6 standards, which were granted to Cornell University in 2010 and 2011. The university seeks monetary damages and injunctive relief to prevent further use of the patented technology. This lawsuit could result in financial and operational consequences for the company if the court finds in favor of Cornell University.
        """)
    ]
}

# --- THE PROMPT LIBRARY (WRITING FORMULAS) ---
# This dictionary holds the unique, step-by-step writing formula for each category.
SWOT_PROMPTS = {
    "Opportunity": """
    You are a business analyst who MUST follow a very specific writing formula to identify an OPPORTUNITY.
    Analyze the provided "Press Release Text" and generate a single paragraph.

    **YOUR TASK IS TO FOLLOW THIS EXACT 5-STEP FORMULA:**
    1.  **The Opening Sentence:** Start with the date, company name, the positive action (e.g., 'has acquired', 'has launched'), the entity involved, and the immediate purpose.
    2.  **The Detail Sentence:** Provide a specific, factual detail about the entity or initiative.
    3.  **The "Would" Benefit Sentence:** Describe the direct benefit using the word "would". Use transitional phrases like "Through this acquisition...".
    4.  **The Strategic Benefit Sentence:** Describe the broader strategic benefit. Use transitional phrases like "Further...".
    5.  **The Concluding Sentence:** Link the action to a larger company mission or goal.
    """,
    "Weakness": """
    You are a business analyst. Your task is to analyze the provided text and write a single paragraph summarizing a company's WEAKNESS, perfectly replicating the user's writing style.

    **YOUR TASK IS TO FOLLOW THIS PRECISE 3-PART STRUCTURE:**

    1.  **The Negative Event:** In the first sentence, state the date, the company, and the core negative event (e.g., "faced a lawsuit," "agreed to pay a penalty," "recalled vehicles").
    2.  **The Problem Details:** In the next sentence, provide the specific details of the problem. Use phrases like "The lawsuit alleged that...", "According to EPA findings...", or "This recall targets..." to explain the core issue.
    3.  **The Impact and Implications:** In the final sentence(s), describe the outcome. This can be the direct negative consequence for the company (e.g., financial penalties, reputational damage) OR the broader implications for the industry.
    """
}

# --- THE AI ANALYSIS ENGINE ---
# This function assembles the prompt and calls the AI model.
def generate_swot_point(text: str, swot_category: str, api_key: str) -> str:
    """Generates a SWOT point by calling the Google Generative AI."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        return f"Error configuring the AI model: {e}. Please check your API key."

    prompt_formula = SWOT_PROMPTS.get(swot_category)
    example_list = SWOT_EXAMPLES.get(swot_category)

    if not prompt_formula or not example_list:
        return f"Error: No prompt or examples found for SWOT category '{swot_category}'."

    formatted_examples = "\n\n---\n\n".join(example_list)

    final_prompt = f"""
    {prompt_formula}

    **You must write the entire output as a single, flowing paragraph. The structure instructions are for the content and sequence of ideas within that paragraph.**

    Here are several perfect examples to mimic. Learn the pattern from all of them:
    ---
    {formatted_examples}
    ---

    **Press Release Text:**
    ---
    {text}
    ---
    """

    try:
        response = model.generate_content(final_prompt)
        return response.text.strip()
    except Exception as e:
        return f"An error occurred during AI analysis: {e}"


# --- STREAMLIT USER INTERFACE ---
st.title("SWOT Analysis Point Generator")
st.markdown("This tool uses AI to analyze a press release or article and generate a concise SWOT (Strengths, Weaknesses, Opportunities, Threats) paragraph based on a specific writing formula.")

# --- API Key Handling ---
# Try to get the API key from Streamlit secrets first (for deployed app)
# Then try from environment variables (for local .env file)
# Finally, fall back to a text input for the user to provide it directly
api_key = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY"))

if not api_key:
    st.warning("Google API Key not found. Please enter it below to proceed.")
    api_key = st.text_input("Enter your Google API Key:", type="password", key="api_key_input")

if api_key:
    st.success("API Key loaded successfully!")

    # --- INPUT FIELDS ---
    st.header("1. Enter Your Information")
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("Enter the Company Name:", value="Reliance Industries")
    with col2:
        swot_category = st.selectbox("Select SWOT Category:", options=["Opportunity", "Weakness"])

    st.header("2. Paste the Article Text")
    article_text = st.text_area("Paste the full text of the article or press release below:", height=300)

    # --- GENERATE BUTTON AND OUTPUT ---
    if st.button("Generate SWOT Point", type="primary", use_container_width=True):
        if not company_name.strip():
            st.error("Please enter a company name.")
        elif not article_text.strip():
            st.error("Please paste the article text.")
        else:
            with st.spinner(f"Analyzing text for '{company_name}' to find a potential {swot_category}..."):
                # We don't need the company_name in the function call anymore
                # as the model infers it from the text, but you could add it back
                # to the prompt if needed.
                swot_paragraph = generate_swot_point(article_text, swot_category, api_key)

                st.header("3. Generated Paragraph")
                st.markdown(swot_paragraph)

else:
    st.error("Please provide a Google API Key to use the application.")
