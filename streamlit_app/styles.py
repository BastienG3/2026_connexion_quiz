import os
import base64

def load_font(font_path: str, font_name: str, weight: int = 400) -> str:
    with open(font_path, "rb") as f:
        font_data = base64.b64encode(f.read()).decode("utf-8")
    ext = font_path.split(".")[-1]  # ttf, woff, woff2, otf
    return f"""
    @font-face {{
        font-family: '{font_name}';
        src: url('data:font/{ext};base64,{font_data}') format('{ext}');
        font-weight: {weight};
        font-style: normal;
    }}
    """
    
def load_fonts():
    fonts = load_font("fonts/Exo/Exo-Medium.ttf", "Exo", weight=500)
    fonts += load_font("fonts/Exo/Exo-Regular.ttf", "Exo", weight=400)
    
    return f"<style>{fonts}</style>"
    
GLOBAL_CSS = """
<style>
  :root {
    --kpc-font: 'Exo', 'Segoe UI', system-ui, sans-serif;
    --ink: #0a0814;
    --ink-2: #14101f;
    --ink-3: #1e1730;
    --paper: #f5f1ea;
    --paper-dim: #d8d2c7;
    --paper-mute: rgba(245, 241, 234, 0.55);
    --paper-faint: rgba(245, 241, 234, 0.12);
    --ember: #ff6b1a;
    --ember-soft: #ff8a4c;
    --ember-deep: #d94a00;
    --line: rgba(245, 241, 234, 0.08);
    --line-strong: rgba(245, 241, 234, 0.22);
  }
 
  #MainMenu, footer, header { visibility: hidden; }
 
  .stApp { background: transparent !important; }
  [data-testid="stAppViewContainer"],
  [data-testid="stHeader"],
  [data-testid="stToolbar"],
  [data-testid="stMain"] {
    background: transparent !important;
  }
 
  #plexus-canvas {
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    z-index: -1;
    pointer-events: none;
  }
 
  .block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    max-width: 1100px !important;
  }
 
  /* HOME PAGE STYLES (preserved) */
  .kpc-eyebrow {
    display: inline-block;
    background: rgba(180,140,255,0.12);
    border: 1px solid rgba(180,140,255,0.3);
    color: #d4c5ff;
    font-size: 20px;
    font-weight: 500;
    padding: 6px 14px;
    border-radius: 999px;
    margin-bottom: 24px;
    letter-spacing: 0.5px;
  }
  .kpc-title {
    color: #fff !important;
    font-size: 56px;
    font-weight: 800;
    line-height: 1.05;
    margin: 0 0 16px;
    letter-spacing: -1.5px;
  }
  .kpc-subtitle {
    color: rgba(255,255,255,0.72);
    font-size: 18px;
    line-height: 1.6;
    margin: 0 0 28px;
    max-width: 480px;
  }
  .kpc-subtitle strong { color: #fff; font-weight: 600; }
  .kpc-trust { display: flex; gap: 24px; margin-bottom: 32px; flex-wrap: wrap; }
  .kpc-trust-item {
    display: flex; align-items: center; gap: 8px;
    color: rgba(255,255,255,0.65); font-size: 13px;
  }
  .kpc-trust-item .dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; }
  .kpc-logo-chip img { height: 150px; width: auto; }
 
  /* LANGUAGE PILL */
  div[data-testid="stRadio"] > label,
  div[data-testid="stRadio"] label[data-testid="stWidgetLabel"] {
    display: none !important;
  }
  div[data-testid="stElementContainer"]:has(div[data-testid="stRadio"]) {
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
  }
  div[data-testid="stRadio"] [role="radiogroup"] {
    display: inline-flex !important;
    flex-direction: row !important;
    gap: 4px !important;
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 999px !important;
    padding: 4px !important;
    width: fit-content !important;
  }
  div[data-testid="stRadio"] [role="radiogroup"] > label {
    margin: 0 !important;
    padding: 6px 18px !important;
    border-radius: 999px !important;
    cursor: pointer !important;
    background: transparent !important;
    border: none !important;
    transition: background 0.2s ease !important;
    min-height: unset !important;
    display: inline-flex !important;
    align-items: center !important;
  }
  div[data-testid="stRadio"] [role="radiogroup"] > label:hover {
    background: rgba(255,255,255,0.08) !important;
  }
  div[data-testid="stRadio"] [role="radiogroup"] > label:has(input:checked) {
    background: rgba(255,255,255,0.2) !important;
  }
  div[data-testid="stRadio"] [role="radiogroup"] input[type="radio"],
  div[data-testid="stRadio"] [role="radiogroup"] > label > div:first-child,
  div[data-testid="stRadio"] [role="radiogroup"] [data-baseweb="radio"] > div:first-child {
    display: none !important;
    width: 0 !important; height: 0 !important;
    opacity: 0 !important; margin: 0 !important;
  }
  div[data-testid="stRadio"] [role="radiogroup"] label p,
  div[data-testid="stRadio"] [role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
    color: #fff !important;
    font-size: 16px !important;
    font-weight: 500 !important;
    margin: 0 !important;
    line-height: 1 !important;
    font-family: var(--kpc-font) !important;
  }
 
  /* ==========================
     QUIZ — from HTML mockup
     ========================== */
  .kpc-quiz {
    width: 100%;
    max-width: 880px;
    margin: 0 auto;
    font-family: 'Inter Tight', sans-serif;
    color: var(--paper);
  }
 
  .kpc-quiz-meta {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 28px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--paper-mute);
  }
  .kpc-quiz-meta .counter {
    color: var(--ember-soft);
    font-weight: 500;
    white-space: nowrap;
  }
  .kpc-quiz-meta .divider {
    flex: 1;
    height: 1px;
    background: var(--line-strong);
  }
 
  .kpc-progress { margin-bottom: 48px; }
  .kpc-progress-track {
    height: 2px;
    background: var(--line-strong);
    position: relative;
    border-radius: 2px;
  }
  .kpc-progress-fill {
    position: absolute;
    top: 0; left: 0;
    height: 100%;
    background: linear-gradient(90deg, var(--ember-deep), var(--ember), var(--ember-soft));
    border-radius: 2px;
    transition: width 0.6s cubic-bezier(0.65, 0, 0.35, 1);
  }
  .kpc-progress-fill::after {
    content: '';
    position: absolute;
    right: -2px; top: -3px;
    width: 8px; height: 8px;
    background: var(--ember-soft);
    border-radius: 50%;
    box-shadow: 0 0 14px var(--ember);
  }
  div[data-testid="stProgress"] { display: none !important; }
 
  .kpc-question {
    font-family: 'Fraunces', serif;
    font-weight: 400;
    font-size: clamp(32px, 4.2vw, 52px);
    line-height: 1.05;
    letter-spacing: -0.025em;
    margin: 0 0 40px;
    color: var(--paper) !important;
  }
  .kpc-question .qnum {
    color: var(--ember-soft);
    font-weight: 300;
    font-style: italic;
    margin-right: 12px;
  }
 
  /* =====================================================================
     BUTTONS — by kind attribute
     primary   = orange CTA (Next / Submit / Start) + SELECTED answer
     secondary = ghost (Back / Restart) + UNSELECTED answer
     ===================================================================== */
  div[data-testid="stButton"] > button {
    transition: all 0.25s ease !important;
    font-family: 'Inter Tight', sans-serif !important;
  }
 
  /* PRIMARY = orange CTA */
  div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #ff8c42, #ff5722) !important;
    color: #fff !important;
    border: none !important;
    padding: 14px 32px !important;
    border-radius: 999px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    box-shadow: 0 8px 24px rgba(255,87,34,0.35) !important;
  }
  div[data-testid="stButton"] > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 32px rgba(255,87,34,0.5) !important;
  }
 
  /* SECONDARY = ghost */
  div[data-testid="stButton"] > button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid var(--line-strong) !important;
    color: var(--paper-dim) !important;
    padding: 12px 22px !important;
    border-radius: 999px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    box-shadow: none !important;
  }
  div[data-testid="stButton"] > button[kind="secondary"]:hover {
    border-color: var(--paper) !important;
    color: var(--paper) !important;
    background: rgba(245, 241, 234, 0.04) !important;
    box-shadow: none !important;
    transform: none !important;
  }
 
  /* TERTIARY = small Restart */
  div[data-testid="stButton"] > button[kind="tertiary"] {
    background: transparent !important;
    border: 1px solid var(--line-strong) !important;
    color: var(--paper-dim) !important;
    padding: 6px 14px !important;
    border-radius: 999px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    font-weight: 500 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    box-shadow: none !important;
    min-height: unset !important;
    height: auto !important;
  }
  div[data-testid="stButton"] > button[kind="tertiary"]:hover {
    border-color: var(--paper) !important;
    color: var(--paper) !important;
    background: rgba(245, 241, 234, 0.04) !important;
    box-shadow: none !important;
  }
 
  /* ANSWER CARDS — both kinds restyled inside .kpc-answer-row */
  .kpc-answer-row [data-testid="stHorizontalBlock"] {
    gap: 14px !important;
  }
  .kpc-answer-row { margin-bottom: 48px; }
 
  /* Unselected answer (kind=secondary inside answer row) */
  .kpc-answer-row div[data-testid="stButton"] > button[kind="secondary"] {
    width: 100% !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 22px 26px !important;
    border-radius: 4px !important;
    min-height: 88px !important;
    height: 100% !important;
    font-size: 15px !important;
    font-weight: 400 !important;
    color: var(--paper) !important;
    background: rgba(20, 16, 31, 0.5) !important;
    border: 1px solid var(--line-strong) !important;
    letter-spacing: -0.005em !important;
    line-height: 1.4 !important;
    white-space: normal !important;
    display: flex !important;
    align-items: center !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
  }
  .kpc-answer-row div[data-testid="stButton"] > button[kind="secondary"]:hover {
    border-color: rgba(245, 241, 234, 0.35) !important;
    background: rgba(20, 16, 31, 0.7) !important;
    transform: translateY(-2px) !important;
  }
 
  /* Selected answer (kind=primary inside answer row) */
  .kpc-answer-row div[data-testid="stButton"] > button[kind="primary"] {
    width: 100% !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 22px 26px !important;
    border-radius: 4px !important;
    min-height: 88px !important;
    height: 100% !important;
    font-size: 15px !important;
    font-weight: 400 !important;
    color: var(--paper) !important;
    background: rgba(255, 107, 26, 0.10) !important;
    border: 1px solid var(--ember) !important;
    letter-spacing: -0.005em !important;
    line-height: 1.4 !important;
    white-space: normal !important;
    display: flex !important;
    align-items: center !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    box-shadow: 0 0 24px rgba(255, 107, 26, 0.15) !important;
  }
  .kpc-answer-row div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: rgba(255, 107, 26, 0.14) !important;
    border-color: var(--ember-soft) !important;
    transform: translateY(-2px) !important;
  }
 
  /* Result card */
  .kpc-result-card {
    background: rgba(20, 16, 31, 0.55);
    border: 1px solid var(--line-strong);
    border-radius: 12px;
    padding: 40px 44px;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
  }
  .kpc-result-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 3px;
    background: linear-gradient(90deg, var(--ember-deep), var(--ember), var(--ember-soft));
  }
  .kpc-result-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--ember-soft);
    margin-bottom: 12px;
  }
  .kpc-result-band {
    font-family: 'Fraunces', serif;
    color: #fff;
    font-size: 48px;
    font-weight: 500;
    letter-spacing: -1px;
    line-height: 1.1;
    margin: 0 0 20px;
  }
  .kpc-result-text {
    color: var(--paper-dim);
    font-size: 16px;
    line-height: 1.6;
    margin: 0 0 24px;
  }
  .kpc-result-pitch {
    background: rgba(255, 107, 26, 0.08);
    border: 1px solid rgba(255, 107, 26, 0.3);
    border-radius: 8px;
    padding: 18px 22px;
    color: #fff;
    font-size: 15px;
    line-height: 1.55;
  }
 
  .kpc-section-title {
    font-family: 'Fraunces', serif;
    color: #fff !important;
    font-size: 28px;
    font-weight: 400;
    margin: 32px 0 20px;
    letter-spacing: -0.5px;
  }
 
  div[data-testid="stTextInput"] label,
  div[data-testid="stTextInput"] label p {
    color: var(--paper-dim) !important;
    font-family: 'Inter Tight', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
  }
  div[data-testid="stTextInput"] input {
    background: rgba(20, 16, 31, 0.5) !important;
    border: 1px solid var(--line-strong) !important;
    color: #fff !important;
    border-radius: 6px !important;
    padding: 12px 16px !important;
    font-family: 'Inter Tight', sans-serif !important;
    font-size: 15px !important;
  }
  div[data-testid="stTextInput"] input:focus {
    border-color: var(--ember) !important;
    box-shadow: 0 0 0 3px rgba(255, 107, 26, 0.15) !important;
    outline: none !important;
  }
 
  div[data-testid="stCheckbox"] label p {
    color: var(--paper-dim) !important;
    font-size: 14px !important;
    font-family: 'Inter Tight', sans-serif !important;
  }
 
  div[data-testid="stAlertContentSuccess"] {
    background: rgba(255, 107, 26, 0.08) !important;
    border: 1px solid rgba(255, 107, 26, 0.3) !important;
    color: #fff !important;
  }
 
  /* QR card preserved */
  .kpc-qr-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 20px;
    padding: 20px;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    text-align: center;
    width: 100%;
    max-width: 320px;
    margin: 0 auto;
    font-family: var(--kpc-font);
    box-shadow: 0 8px 32px rgba(0,0,0,0.25);
    box-sizing: border-box;
  }
  .kpc-qr-img {
    width: 100%;
    height: auto;
    display: block;
    border-radius: 10px;
    background: #fff;
    padding: 10px;
    box-sizing: border-box;
    margin-bottom: 14px;
  }
  .kpc-qr-title { color: #fff; font-size: 26px; font-weight: 500; margin-bottom: 4px; }
  .kpc-qr-help { color: rgba(255,255,255,0.5); font-size: 22px; }
 
  .kpc-fade-in {
    opacity: 0;
    transform: translateY(8px);
    animation: kpcFadeIn 0.5s cubic-bezier(0.2, 0, 0.2, 1) forwards;
  }
  @keyframes kpcFadeIn {
    to { opacity: 1; transform: translateY(0); }
  }
</style>
"""

CANVAS_MARKUP = '<canvas id="plexus-canvas"></canvas>'
LOGO_URL = "images/KPC23-Logotype-baseline-sans-fond-01_cropped.png" #"https://kpcgroup.fr/wp-content/uploads/2023/10/KPC23-Logo-seul-color.png.webp"

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()
 
def logo_chip_html(tagline: str = "Data & Digital Shapers") -> str:
    if not os.path.exists(LOGO_URL):
        return f"<p style='color:red;'>Error: Logo not found at {LOGO_URL}</p>"
    img_base64 = get_base64_of_bin_file(LOGO_URL)
    img_src = f"data:image/png;base64,{img_base64}"
    return f'<img src="{img_src}" alt="KPC" />'
 
def kpc_html(eyebrow, title, subtitle_html, trust_items):
    trust_blocks = "".join(
        f'<div class="kpc-trust-item"><span class="dot" style="background:{color};"></span>{label}</div>'
        for color, label in trust_items
    )
    return f"""
    <div class="kpc-eyebrow">{eyebrow}</div>
    <h1 class="kpc-title">{title}</h1>
    <p class="kpc-subtitle">{subtitle_html}</p>
    <div class="kpc-trust">{trust_blocks}</div>
    """
 
def qr_card_html(qr_url, title, helper):
    return f"""
    <div class="kpc-qr-card">
      <img class="kpc-qr-img" src="{qr_url}" alt="QR code" />
      <div class="kpc-qr-title">{title}</div>
      <div class="kpc-qr-help">{helper}</div>
    </div>
    """
 
def footer_html(copyright_text, link_text):
    return f"""
    <div class="kpc-footer">
      <div>{copyright_text}</div>
      <div>{link_text}</div>
    </div>
    """
 
################################################
# QUIZ HELPERS
################################################
 
def quiz_meta_html(counter_text):
    return f"""
    <div class="kpc-quiz kpc-fade-in">
      <div class="kpc-quiz-meta">
        <span class="counter">{counter_text}</span>
      </div>
    """
 
def progress_bar_html(progress):
    pct = max(0, min(100, progress * 100))
    return f"""
    <div class="kpc-progress kpc-fade-in">
      <div class="kpc-progress-track">
        <div class="kpc-progress-fill" style="width: {pct}%;"></div>
      </div>
    </div>
    """
 
def question_html(question_num, question_body):
    return f"""
    <h2 class="kpc-question kpc-fade-in"><span class="qnum">{question_num:02d}</span>{question_body}</h2>
    """
 
def result_card_html(eyebrow, band_name, text, pitch):
    return f"""
    <div class="kpc-quiz kpc-fade-in">
      <div class="kpc-result-card">
        <div class="kpc-result-eyebrow">— {eyebrow}</div>
        <h2 class="kpc-result-band">{band_name}</h2>
        <p class="kpc-result-text">{text}</p>
        <div class="kpc-result-pitch">{pitch}</div>
      </div>
    </div>
    """
 