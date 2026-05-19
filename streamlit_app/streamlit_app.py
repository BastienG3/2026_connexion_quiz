# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from uuid import uuid4
import re
import time
import constants
import styles
from plexus import PLEXUS_HTML
import streamlit.components.v1 as components

def band_from_score(score):
    if score <= 17:
        return "initial"
    if score <= 25:
        return "build"
    if score <= 32:
        return "advanced"
    return "leader"

# --- CONFIG ---
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

st.markdown(styles.load_fonts(), unsafe_allow_html=True)
st.markdown(styles.GLOBAL_CSS + styles.CANVAS_MARKUP, unsafe_allow_html=True)
components.html(PLEXUS_HTML, height=0, width=0)

################################################
# HEADER 
################################################
if "lang" not in st.session_state:
    st.session_state["lang"] = "FR" # default

_, center_col, _ = st.columns([1, 2, 1])
st.markdown(
        f'<div style="display:flex; justify-content:center;">'
        f'{styles.logo_chip_html(tagline="Data & Digital Shapers")}'
        f'</div>',
        unsafe_allow_html=True,
    )

lang = st.radio(
        label="",
        options=["FR", "EN"],
        horizontal=True,
        index=0 if st.session_state["lang"] == "FR" else 1,
        label_visibility="collapsed",
        key="lang_radio",
    )
st.session_state["lang"] = lang
 
st.markdown('<div style="height:10vh;"></div>', unsafe_allow_html=True)


################################################
# MID 
################################################
if "show_home" not in st.session_state:
    st.session_state["show_home"] = True
if st.session_state["show_home"]:
    home_mid_left, home_mid_right = st.columns([2, 1], gap="large")
    with home_mid_left:
        t = constants.texts[lang]
     
        st.markdown(
            styles.kpc_html(
                eyebrow=constants.texts[lang]['tag'],
                title=constants.texts[lang]['home_page_title'],
                subtitle_html=constants.texts[lang]['home_page_msg'],
                trust_items=[],
            ),
            unsafe_allow_html=True,
        )
     
        if st.button(
            constants.texts[lang]['home_page_start_btn'],
            key="start_btn",
            type="primary"
        ):
            st.session_state["show_home"] = False
            st.rerun()
 
    with home_mid_right:
   
        qr_url = (
            "https://api.qrserver.com/v1/create-qr-code/?size=200x200"
            "&data=https%3A%2F%2Flinktr.ee%2Fgroupekpc"
            "%3Futm_source%3Dlinktree_profile_share"
            "%26ltsid%3Dab18f1ca-e451-4beb-aece-22d5c6279f46"
        )
     
        st.markdown(
            styles.qr_card_html(
                qr_url=qr_url,
                title=constants.texts[lang]['scan_msg'],
                helper=constants.texts[lang]['scan_msg_detail'],
            ),
            unsafe_allow_html=True,
        )

    st.stop()


session = get_active_session()
 
if "prospect_id" not in st.session_state:
    st.session_state["prospect_id"] = str(uuid4())
if "q_index" not in st.session_state:
    st.session_state["q_index"] = 0
if "selected_answers" not in st.session_state:
    # Stores {question_id: answer_value} so we can highlight selected on revisit
    st.session_state["selected_answers"] = {}
 
# Load questions
questions = session.table('QUESTIONS').order_by('ORDER').collect()
nb_questions = len(questions)
 
 
################################################
# END SCREEN 
################################################
if st.session_state["q_index"] >= nb_questions:
 
    score = session.sql(f"""
        SELECT SUM(c.SCORE) AS TOTAL_SCORE
        FROM RESULTS r
        JOIN CHOICES c ON c.VALUE = r.ANSWER_VALUE
        WHERE r.PROSPECT_ID = '{st.session_state["prospect_id"]}'
    """).collect()
 
    band = band_from_score(score[0]['TOTAL_SCORE'])
    band_info = session.table("RESULT_BANDS").filter(f"BAND = '{band}'").collect()[0]
    text = band_info["TEXT_" + lang]
    pitch = band_info["PITCH_" + lang]
 
    st.markdown(
        styles.result_card_html(
            eyebrow=constants.texts[lang]['maturity_msg'],
            band_name=band.capitalize(),
            text=text,
            pitch=pitch,
        ),
        unsafe_allow_html=True,
    )
 
    st.markdown('<div class="kpc-quiz kpc-fade-in">', unsafe_allow_html=True)
    st.markdown(
        f'<h3 class="kpc-section-title">{constants.texts[lang]["informations_msg"]}</h3>',
        unsafe_allow_html=True,
    )
 
    col_a, col_b = st.columns(2)
    with col_a:
        name = st.text_input(constants.texts[lang]['info_name'])
    with col_b:
        company = st.text_input(constants.texts[lang]['info_company'])
    email = st.text_input(constants.texts[lang]['info_email'])
 
    if not name or not email:
        st.error("Merci de remplir les champs obligatoires." if lang == "FR" else "Please fill the required fields.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        st.error("Email invalide" if lang == "FR" else "Invalid email")
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()
 
    consent = st.checkbox(constants.texts[lang]['contact_checkbox'])
 
    if st.button(constants.texts[lang]['submit_btn'], key="submit_btn", type="primary"):
        safe_name = name.replace("'", "''")
        safe_company = company.replace("'", "''")
        safe_email = email.replace("'", "''")
 
        session.sql(f"""
            MERGE INTO PROSPECTS AS tgt
            USING (
                SELECT
                    '{st.session_state["prospect_id"]}' AS PROSPECT_ID,
                    '{safe_name}' AS NAME,
                    '{safe_company}' AS COMPANY,
                    '{safe_email}' AS EMAIL,
                    {1 if consent else 0} AS CONSENT
                ) AS src
                ON tgt.PROSPECT_ID = src.PROSPECT_ID
                AND tgt.EMAIL = src.EMAIL
            WHEN MATCHED THEN
                UPDATE SET
                    NAME = src.NAME,
                    COMPANY = src.COMPANY,
                    CONSENT = src.CONSENT
            WHEN NOT MATCHED THEN INSERT(
                PROSPECT_ID, NAME, COMPANY, EMAIL, CONSENT
            ) VALUES (
                src.PROSPECT_ID, src.NAME, src.COMPANY, src.EMAIL, src.CONSENT
            )
            """).collect()
 
        st.success(constants.texts[lang]['saved_info_msg'])
        time.sleep(5)
        st.session_state.clear()
        st.session_state["show_home"] = True
        st.rerun()
 
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()
 
 
################################################
# QUIZ QUESTION SCREEN
################################################
q = questions[st.session_state["q_index"]]
question_id = q["ID"]
question_order = q["ORDER"]
question_body = q["QUESTION_TEXT_" + lang]
 
progress = (st.session_state['q_index'] + 1) / nb_questions
counter_text = f"{constants.texts[lang].get('question_label', 'Question')} {question_order:02d} / {nb_questions:02d}"
 
# Restart button — slot it into the meta row using a column layout
meta_l, meta_r = st.columns([5, 2])
with meta_l:
    if st.button(constants.texts[lang]['restart_btn'], key="restart_btn", type="tertiary"):
        st.session_state.clear()
        st.session_state["show_home"] = True
        st.rerun()
 
# --- PROGRESS BAR ---
st.markdown(styles.progress_bar_html(progress), unsafe_allow_html=True)
st.markdown(styles.quiz_meta_html(counter_text), unsafe_allow_html=True)
 
# --- QUESTION ---
st.markdown(styles.question_html(question_order, question_body), unsafe_allow_html=True)
 
# --- LOAD CHOICES ---
choices_df = session.table("CHOICES").filter(f"QUESTION_ID = {question_id}").collect()
choice_labels = [c["CHOICE_TEXT_" + lang] for c in choices_df]
choice_values = [c["VALUE"] for c in choices_df]
 
# --- ANSWER CARDS (as buttons in a 2-column grid) ---
# Currently selected answer (from session state, if user has visited this question)
current_selection = st.session_state["selected_answers"].get(question_id)
 
st.markdown('<div class="kpc-answer-row">', unsafe_allow_html=True)
 
# Render in pairs (2 columns per row)
for i in range(0, len(choice_values), 2):
    col1, col2 = st.columns(2)
    columns_pair = [col1, col2]
 
    for j, col in enumerate(columns_pair):
        idx = i + j
        if idx >= len(choice_values):
            continue
        val = choice_values[idx]
        label = choice_labels[idx]
        is_selected = (val == current_selection)
        btn_type = "primary" if is_selected else "secondary"
 
        with col:
            if st.button(
                label,
                key=f"ans_{question_id}_{idx}",
                type=btn_type,
                use_container_width=True,
            ):
                st.session_state["selected_answers"][question_id] = val
                st.rerun()
 
st.markdown('</div>', unsafe_allow_html=True)
 
# --- NAV ROW: Back + Next ---
st.markdown('<div style="border-top:1px solid var(--line); padding-top:24px; display:flex; justify-content:space-between; align-items:center;">', unsafe_allow_html=True)
 
nav_l, nav_spacer, nav_r = st.columns([1, 4, 1])
 
with nav_l:
    if st.session_state["q_index"] > 0:
        if st.button(constants.texts[lang]['back_btn'], key="back_btn", type="secondary"):
            st.session_state["q_index"] -= 1
            st.rerun()
 
with nav_r:
    is_last = st.session_state['q_index'] == nb_questions - 1
    text_validate_btn = constants.texts[lang]['complete_btn'] if is_last else constants.texts[lang]['validate_btn']
 
    # Disable Next if no answer selected yet
    has_selection = current_selection is not None
 
    if st.button(
        text_validate_btn,
        key="next_btn",
        type="primary",
        disabled=not has_selection,
    ):
        selected = current_selection
        # Save answer to Snowflake
        session.sql(f"""
            MERGE INTO RESULTS AS tgt
            USING (
                SELECT
                    '{st.session_state["prospect_id"]}' AS PROSPECT_ID,
                    '{question_id}' AS QUESTION_ID,
                    '{selected}' AS ANSWER_VALUE
                ) AS src
                ON tgt.PROSPECT_ID = src.PROSPECT_ID
                AND tgt.QUESTION_ID = src.QUESTION_ID
            WHEN MATCHED THEN
                UPDATE SET ANSWER_VALUE = src.ANSWER_VALUE
            WHEN NOT MATCHED THEN INSERT(
                PROSPECT_ID, QUESTION_ID, ANSWER_VALUE
            ) VALUES (
                src.PROSPECT_ID, src.QUESTION_ID, src.ANSWER_VALUE
            )
            """
        ).collect()
 
        st.session_state["q_index"] += 1
        st.rerun()
 
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)