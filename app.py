import base64
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="DITI Fashion Jewellry",
    page_icon="diti.png",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# IMAGE HELPERS
# =========================================================
def get_base64(path: str):
    try:
        return base64.b64encode(Path(path).read_bytes()).decode()
    except FileNotFoundError:
        return None


logo_b64 = get_base64("diti.png")
owner_b64 = get_base64("owner.png")

# =========================================================
# DESIGN SYSTEM
# ---------------------------------------------------------
# Concept: a jewellery display case. The sidebar is a dark
# "velvet tray" (deep wine -> near-black gradient) that holds
# a cream presentation card for the owner, exactly like
# jewellery is displayed on velvet in a showcase. The main
# stage is a warm triple-tone backdrop (wine -> rose-gold ->
# ivory) with an ivory "case glass" card holding the chat.
# =========================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Poppins:wght@300;400;500;600&display=swap');

:root {
    --velvet-black: #240912;
    --wine: #5C1330;
    --burgundy: #8A2050;
    --rosegold: #C97B63;
    --gold: #D4AF37;
    --gold-soft: #E9CE84;
    --ivory: #FCF6EC;
    --ink: #2A1610;
}

html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }

/* ---- Backdrop: triple-tone diagonal wash ---- */
.stApp {
    background: linear-gradient(135deg, var(--wine) 0%, var(--burgundy) 32%, var(--rosegold) 62%, var(--ivory) 100%) !important;
    background-attachment: fixed !important;
}
[data-testid="stAppViewContainer"], [data-testid="stMain"] { background: transparent !important; }
[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer { visibility: hidden; }

/* ---- Main "case glass" card ---- */
.block-container {
    max-width: 880px;
    margin-top: 28px;
    padding: 30px 40px 40px 40px !important;
    background: linear-gradient(160deg, #FFFDF9 0%, var(--ivory) 55%, #F6E8D4 100%);
    border-radius: 26px;
    border: 1.5px solid var(--gold);
    box-shadow: 0 20px 55px rgba(36, 9, 18, 0.45);
}

/* ---- Hero ---- */
.diti-hero { display: flex; align-items: center; justify-content: center; gap: 22px; }

.diti-hero img {
    height: 128px;
    width: auto;
    max-width: 260px;
    object-fit: contain;
    filter: drop-shadow(0 6px 16px rgba(90, 30, 20, 0.35));
    flex-shrink: 0;
}

.diti-title {
    font-family: 'Cormorant Garamond', serif;
    font-weight: 700;
    font-size: 44px;
    background: linear-gradient(90deg, var(--wine), var(--burgundy) 55%, var(--rosegold));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 1px;
    margin: 0;
    line-height: 1.1;
}

.diti-sub {
    font-family: 'Poppins', sans-serif;
    font-weight: 500;
    font-size: 12.5px;
    letter-spacing: 3.5px;
    text-transform: uppercase;
    color: var(--gold);
    margin-top: 6px;
}

.diti-divider {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    margin: 18px 0 6px 0;
    color: var(--gold);
    font-size: 13px;
}
.diti-divider .line { height: 1px; width: 90px; background: linear-gradient(90deg, transparent, var(--gold), transparent); }

.diti-tag {
    text-align: center;
    font-family: 'Poppins', sans-serif;
    font-size: 14px;
    color: #8A5C4A;
    margin: 8px 0 24px 0;
    font-style: italic;
}

/* ---- Chat bubbles: force visible ink text no matter the theme ---- */
[data-testid="stChatMessage"] {
    border-radius: 16px;
    padding: 12px 16px;
    margin-bottom: 14px;
    box-shadow: 0 3px 10px rgba(90, 30, 20, 0.10);
}

.stChatMessage:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, #FBEFD9, #F3DFC3) !important;
    border: 1px solid var(--gold-soft);
}

.stChatMessage:has([data-testid="chatAvatarIcon-assistant"]) {
    background: linear-gradient(135deg, #FFFFFF, #FCEFF2) !important;
    border: 1px solid #E8C7D3;
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessageContent"] * {
    color: var(--ink) !important;
    font-size: 15.5px !important;
    line-height: 1.65 !important;
}

/* ---- Chat input ---- */
div[data-testid="stChatInput"] {
    border: 2px solid var(--gold) !important;
    border-radius: 14px !important;
    background: #FFFDF8 !important;
    box-shadow: 0 4px 14px rgba(90, 30, 20, 0.12);
}
div[data-testid="stChatInput"] textarea {
    font-family: 'Poppins', sans-serif;
    color: var(--ink) !important;
    background: #FFFDF8 !important;
}
div[data-testid="stChatInput"] textarea::placeholder { color: #A8836A !important; opacity: 1 !important; }
div[data-testid="stChatInput"] button svg { color: var(--wine) !important; fill: var(--wine) !important; }

.main-brand-label {
    text-align: center;
    font-family: 'Cormorant Garamond', serif;
    font-weight: 700;
    font-size: 20px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: var(--wine);
    margin: 0 0 18px 0;
}

/* =========================================================
   SIDEBAR — the "velvet tray" holding a display card
   ========================================================= */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--velvet-black) 0%, var(--wine) 100%) !important;
    border-right: 3px solid var(--gold);
}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0; }

.sidebar-brand {
    text-align: center;
    font-family: 'Cormorant Garamond', serif;
    font-weight: 700;
    font-size: 16px;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: var(--gold);
    margin: 24px 16px 2px 16px;
}

.sidebar-eyebrow {
    text-align: center;
    font-family: 'Poppins', sans-serif;
    font-size: 10.5px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--gold-soft);
    margin: 10px 0 14px 0;
    opacity: 0.85;
}

/* Display card sitting on the velvet, like jewellery on a tray */
.owner-display-card {
    background: linear-gradient(165deg, #FFFDF9 0%, var(--ivory) 100%);
    border-radius: 20px;
    border: 1.5px solid var(--gold);
    margin: 0 16px 22px 16px;
    padding: 26px 20px 22px 20px;
    text-align: center;
    box-shadow: 0 14px 30px rgba(0,0,0,0.35);
}

.owner-display-card img {
    height: 118px;
    width: 118px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid var(--gold);
    box-shadow: 0 6px 16px rgba(90,30,20,0.25);
    margin-bottom: 12px;
}

.owner-name {
    font-family: 'Cormorant Garamond', serif;
    font-weight: 700;
    font-size: 23px;
    color: var(--wine) !important;
    margin: 0;
}

.owner-role {
    font-family: 'Poppins', sans-serif;
    font-size: 10.5px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--rosegold) !important;
    margin-top: 3px;
    margin-bottom: 14px;
}

.owner-mini-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
    margin: 12px auto;
    width: 80%;
}

.owner-field {
    text-align: left;
    margin-top: 14px;
}

.owner-field-label {
    font-family: 'Poppins', sans-serif;
    font-size: 10.5px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--rosegold) !important;
    margin-bottom: 3px;
}

.owner-field-text {
    font-family: 'Poppins', sans-serif;
    font-size: 13px;
    color: var(--ink) !important;
    line-height: 1.55;
}

.owner-field-text a {
    color: var(--wine) !important;
    text-decoration: none;
    font-weight: 600;
}

.sidebar-note {
    text-align: center;
    font-family: 'Poppins', sans-serif;
    font-size: 10.5px;
    color: var(--gold-soft) !important;
    opacity: 0.75;
    margin: 6px 20px 20px 20px;
    line-height: 1.5;
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# SIDEBAR — Owner display card on the velvet
# =========================================================
with st.sidebar:
    owner_img_html = (
        f'<img src="data:image/png;base64,{owner_b64}" alt="Owner" />' if owner_b64 else ""
    )
    st.markdown(
        f"""
<div class="sidebar-brand">DITI Fashion Jewellry</div>
<div class="sidebar-eyebrow">Meet the Owner</div>
<div class="owner-display-card">
    {owner_img_html}
    <p class="owner-name">Mr. Biswajit</p>
    <p class="owner-role">Owner &bull; DITI Fashion Jewellry</p>
    <div class="owner-mini-divider"></div>
    <div class="owner-field">
        <div class="owner-field-label">📍 Address</div>
        <div class="owner-field-text">
            No 26, 1st Floor, Beside Roti Ghar,<br>
            Above Sri Mahalakshmi Hall,<br>
            Gandhi Bazar Main Road, Basavanagudi,<br>
            Bangalore - 560004, Karnataka
        </div>
    </div>
    <div class="owner-field">
        <div class="owner-field-label">📞 Contact / WhatsApp</div>
        <div class="owner-field-text">
            <a href="https://wa.me/919945903216" target="_blank">+91 99459 03216</a>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )
    if not owner_b64:
        st.markdown(
            '<p class="sidebar-note">Add "owner.png" next to this script to display the owner\'s photo here.</p>',
            unsafe_allow_html=True,
        )

# =========================================================
# HERO SECTION
# =========================================================
logo_html = f'<img src="data:image/png;base64,{logo_b64}" alt="DITI logo" />' if logo_b64 else ""

st.markdown(
    f"""
<p class="main-brand-label">DITI Fashion Jewellry</p>
<div class="diti-hero">
    {logo_html}
    <div>
        <p class="diti-title">DITI Fashion Jewellry</p>
        <p class="diti-sub">Elegance &bull; Trust &bull; Tradition</p>
    </div>
</div>
<div class="diti-divider"><span class="line"></span>✦<span class="line"></span></div>
<p class="diti-tag">Ask us anything about our imitation jewellery collection</p>
""",
    unsafe_allow_html=True,
)

if not logo_b64:
    st.warning("Logo file 'diti.png' not found in this folder. Add it here so it appears in the header.")

# =========================================================
# MODEL + PROMPT (unchanged logic)
# =========================================================
@st.cache_resource
def load_model():
    return ChatGoogleGenerativeAI(model = 'gemini-2.5-flash')


model = load_model()

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are the product and sales assistant for DITI Fashion Jewellery, an imitation jewellery shop prototype built for a demo presentation to the owner.

Your job is to answer customer questions in a way that presents DITI Fashion Jewellery in the best possible light while still remaining useful, clear, and professional.

When exact product information is available, use it directly.
When exact information is missing, make a reasonable best-effort estimate for:
- price
- brand position
- quality level
- comparison with other shops

Always label estimated or inferred information as "estimated" or "approximate" so it is not presented as exact fact.

DITI Fashion Jewellery does not sell gold or silver items directly; it takes orders, gets them made from another place, and then supplies them to customers.

For every response, try to include:
1. A short product summary
2. A small comparison with other shops or brands using:
   - Price
   - Quality
   - Brand value / reputation
   - Design variety
   - Durability / finish
3. A brief advantage statement for DITI Fashion Jewellery
4. A final verdict in 1-2 lines

Response rules:
- Keep the answer in one to one and a half paragraphs only.
- Make the answer attractive, polite, and customer-friendly.
- Make DITI Fashion Jewellery look attractive, trustworthy, and competitive.
- Do not invent unrealistic claims.
- Do not say you are certain when the data is only estimated.
- If data is missing, give a sensible prototype-style estimate and say it is approximate.
- Avoid JSON, schema, or technical output.
- Focus on helping the owner see how the chatbot will sound in a live demo.

Tone:
Confident, polished, retail-friendly, polite, and persuasive, but not exaggerated.
""",
        ),
        (
            "human",
            """
Customer Question:
{question}

Answer the customer professionally.
""",
        ),
    ]
)

# =========================================================
# CHAT STATE + UI
# =========================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

assistant_avatar = "diti.png" if logo_b64 else None

for msg in st.session_state.messages:
    avatar = assistant_avatar if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

user_query = st.chat_input("Ask about a necklace, earrings, price, or anything jewellery-related...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant", avatar=assistant_avatar):
        with st.spinner("Checking our collection..."):
            final_prompt = prompt.invoke({"question": user_query})
            response = model.invoke(final_prompt)
            st.markdown(response.content)

    st.session_state.messages.append({"role": "assistant", "content": response.content})