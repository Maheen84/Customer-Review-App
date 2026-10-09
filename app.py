import pandas as pd
import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

THEMES = {
    "size/fit": ["size", "sizing", "fit", "runs", "too big", "too small", "tight", "large", "small", "huge", "massive"],
    "not as pictured": ["pictured", "picture", "photo", "online", "pics", "in person"],
    "fabric/quality": ["fabric", "material", "cheap", "quality", "stiff", "itchy", "thick", "heavy", "see through", "see-through"],
}

st.set_page_config(page_title="Why customers don't recommend", layout="wide")

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

@st.cache_data
def load_data():
    df = pd.read_csv("Womens Clothing E-Commerce Reviews.csv")
    df = df.drop(columns=["Unnamed: 0"], errors="ignore")
    df["Title"] = df["Title"].fillna("")
    df["Review Text"] = df["Review Text"].fillna("")
    df["text"] = (df["Title"] + " " + df["Review Text"]).str.strip()
    df = df[df["text"] != ""]
    return df.dropna(subset=["Department Name"])

df = load_data()
neg = df[df["Recommended IND"] == 0]

st.title("Why don't customers recommend our products?")

dept = st.selectbox("Choose a department", sorted(neg["Department Name"].unique()))
total = df[df["Department Name"] == dept]
sub = neg[neg["Department Name"] == dept]

c1, c2 = st.columns(2)
c1.metric("Reviews in department", len(total))
c2.metric("Not recommended", f"{len(sub)} ({len(sub)/len(total):.0%})")

texts = sub["text"].str.lower()
shares = {name: round(texts.apply(lambda t: any(w in t for w in words)).mean() * 100)
          for name, words in THEMES.items()}

st.subheader("What the complaints mention (approx. %)")
st.bar_chart(pd.Series(shares))
if len(sub) < 100:
    st.warning("Small sample: treat these percentages as a rough signal only.")

st.subheader("Example complaints")
for r in sub["text"].sample(min(3, len(sub)), random_state=1).tolist():
    st.write("•", r[:300])

# AI SUMMARY SECTION WITH GEMINI
st.subheader("🤖 AI Summary")

def build_prompt(dept, reviews):
    joined = "\n".join(f"- {r[:300]}" for r in reviews)
    return f"""You are helping a fashion store owner. Below are customer reviews from the "{dept}" department where the customer did NOT recommend the product.

Reviews:
{joined}

Task:
1. List the top 3-4 complaint themes. Keep fabric quality, flattering fit, and "not as pictured" as separate themes if they appear.
2. For each theme give one exact short quote copied from the reviews above.
3. For each theme give one specific, actionable fix a store owner could do this week.
Do not give counts. Be concise and use only what is in the reviews.
The reviews cover different products, so do not assume one product type."""

sample_reviews = sub["text"].sample(min(40, len(sub)), random_state=42).tolist()

if st.button("🤖 Generate AI Summary with Gemini"):
    with st.spinner("Gemini analyze kar rahi hai..."):
        try:
            if not api_key:
                st.error("❌ GEMINI_API_KEY .env file mein nahi hai!")
            else:
                model = genai.GenerativeModel('gemini-3.5-flash')
                response = model.generate_content(build_prompt(dept, sample_reviews))
                st.success("✅ Summary tayyar!")
                st.write(response.text)
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("Agar Gemini fail ho, toh internet check karo ya API key verify karo.")