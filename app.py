import streamlit as st
from uuid import uuid4
import re
from streamlit_app import constants as csts
from streamlit_app import styles
from streamlit_app.plexus import PLEXUS_HTML
import streamlit.components.v1 as components
import snowflake.connector


@st.cache_resource
def get_conn() -> snowflake.connector.SnowflakeConnection:
    """
    Returns a cached Snowflake connection using credentials stored in Streamlit secrets.

    Returns:
        snowflake.connector.SnowflakeConnection: Connection to interact with the Snowflake dtb.
    """
    return snowflake.connector.connect(
        user=st.secrets["snowflake"]["SNOWFLAKE_USERNAME"],
        password=st.secrets["snowflake"]["SNOWFLAKE_PASSWORD"],
        account=st.secrets["snowflake"]["SNOWFLAKE_ACCOUNT"],
        warehouse=st.secrets["snowflake"]["SNOWFLAKE_WAREHOUSE"],
        database=st.secrets["snowflake"]["SNOWFLAKE_DATABASE"],
        schema=st.secrets["snowflake"]["SNOWFLAKE_SCHEMA"],
    )


conn = get_conn()
cursor = conn.cursor()


@st.cache_data
def load_questions() -> list[dict]:
    """
    Load questions from the Snowflake database, ordered by the "ORDER" column.

    Returns:
        list[dict]: A list of question with its attributes.
    """
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM QUESTIONS ORDER BY "ORDER"')
    rows = cursor.fetchall()
    cols = [col[0] for col in cursor.description]
    return [dict(zip(cols, row)) for row in rows]


def band_from_score(sc: float) -> int:
    """
    Return the maturity band (1 to 4) corresponding to the given score, based on predefined thresholds.

    Args:
        sc (float): score obtained by the user based on their answers, used to determine maturity band.

    Returns:
        int: maturity band (1 to 4) corresponding to the given score, where 1 is the lowest maturity and 4 the highest.
    """
    if sc <= 17:
        return 1
    if sc <= 25:
        return 2
    if sc <= 32:
        return 3
    return 4


# --- CONFIG ---
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")


# remove "created by" footer icon
st.markdown(
    """
<style>
/* Hide badge "Created by" */
footer {visibility: hidden;}
header {visibility: hidden;}
div[data-testid="stToolbar"] {visibility: hidden;}
div[data-testid="stDecoration"] {visibility: hidden;}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(styles.load_fonts(), unsafe_allow_html=True)
st.markdown(styles.GLOBAL_CSS + styles.CANVAS_MARKUP, unsafe_allow_html=True)
components.html(PLEXUS_HTML, height=0, width=0)


################################################
# HEADER
################################################
if "lang" not in st.session_state:
    st.session_state["lang"] = "FR"  # default

_, center_col, _ = st.columns([1, 2, 1])
st.markdown(
    f'<div style="display:flex; justify-content:center;">'
    f'{styles.logo_chip_html(tagline="Data & Digital Shapers")}'
    f"</div>",
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

st.markdown('<div style="height:8vh;"></div>', unsafe_allow_html=True)


################################################
# MID
################################################
if "show_home" not in st.session_state:
    st.session_state["show_home"] = True
if st.session_state["show_home"]:
    home_mid_left, home_mid_right = st.columns([2, 1], gap="large")
    with home_mid_left:
        t = csts.texts[lang]

        st.markdown(
            styles.kpc_html(
                eyebrow=csts.texts[lang]["tag"],
                title=csts.texts[lang]["home_page_title"],
                subtitle_html=csts.texts[lang]["home_page_msg"],
                trust_items=[],
            ),
            unsafe_allow_html=True,
        )

        if st.button(
            csts.texts[lang]["home_page_start_btn"],
            key="start_btn",
            type="primary",
        ):
            st.session_state["show_home"] = False
            st.rerun()

        try:
            # Snowsight
            # count_data = session.sql("SELECT COUNT(*) AS TOTAL_COUNT FROM PROSPECTS").collect()

            cursor.execute("SELECT COUNT(*) AS TOTAL_COUNT FROM PROSPECTS")
            row = cursor.fetchone()
            total_registered = row[0]

            if total_registered > 0:
                COUNTER_MSG = (
                    f"Déjà {total_registered} participants !"
                    if lang == "FR"
                    else f"Join {total_registered} other participants!"
                )

                st.markdown(
                    f"""
                    <div style="color: #888888; font-size: 14px; z-index: 9999;">
                    <i>{COUNTER_MSG}</i>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        except Exception:
            pass

    with home_mid_right:

        # Montreal webpage
        QR_URL = (
            "https://api.qrserver.com/v1/create-qr-code/?size=200x200"
            "&data=https%3A%2F%2Fkpcgroup.fr%2Fen%2Ftechnological-partners%2Fkpc-canada-your-data-it-partner-in-montreal%2F"
        )

        st.markdown(
            styles.qr_card_html(
                qr_url=QR_URL,
                title=csts.texts[lang]["scan_msg"],
                helper=csts.texts[lang]["scan_msg_detail"],
            ),
            unsafe_allow_html=True,
        )

    st.stop()


if "prospect_id" not in st.session_state:
    st.session_state["prospect_id"] = str(uuid4())
if "q_index" not in st.session_state:
    st.session_state["q_index"] = 0
if "selected_answers" not in st.session_state:
    # Stores {question_id: answer_value} so we can highlight selected on revisit
    st.session_state["selected_answers"] = {}

# Load questions
questions = load_questions()
NB_QUESTIONS = len(questions)


# TODO TO COMMENT -- DEBUG RESULT SCREEN
if st.button("GO TO RESULT (DEBUG)"):
    st.session_state["q_index"] = NB_QUESTIONS
    st.session_state["form_submitted"] = True
    st.rerun()


################################################
# END SCREEN
################################################
if st.session_state["q_index"] >= NB_QUESTIONS:

    ################################################
    # LEAD GEN FORM
    ################################################
    if not st.session_state.get("form_submitted", False):

        st.markdown('<div class="kpc-quiz kpc-fade-in">', unsafe_allow_html=True)
        st.markdown(
            f'<h3 class="kpc-section-title">{csts.texts[lang]["informations_msg"]}</h3>',
            unsafe_allow_html=True,
        )

        col_a, col_b = st.columns(2)
        with col_a:
            name = st.text_input(csts.texts[lang]["info_name"], key="user_name")
            email = st.text_input(csts.texts[lang]["info_email"], key="user_email")
        with col_b:
            company = st.text_input(
                csts.texts[lang]["info_company"], key="user_company"
            )
            role = st.text_input(csts.texts[lang]["info_role"], key="user_role")

        consent = st.checkbox(csts.texts[lang]["contact_checkbox"], key="user_consent")

        if st.button(
            csts.texts[lang]["submit_btn"],
            key="submit_btn",
            type="primary",
            disabled=not consent,
        ):

            if not name or not email:
                st.error(csts.texts[lang]["empty_field_msg"])

            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                st.error(csts.texts[lang]["invalid_email_msg"])

            else:
                safe_name = name.replace("'", "''")
                safe_company = company.replace("'", "''")
                safe_email = email.replace("'", "''")
                safe_role = role.replace("'", "''")

                cursor.execute(f"""
                    MERGE INTO PROSPECTS AS tgt
                    USING (
                        SELECT
                            '{st.session_state["prospect_id"]}' AS PROSPECT_ID,
                            '{safe_email}' AS EMAIL,
                            '{safe_name}' AS NAME,
                            '{safe_company}' AS COMPANY,
                            '{safe_role}' AS ROLE,
                            {1 if consent else 0} AS CONSENT
                        ) AS src
                        ON tgt.PROSPECT_ID = src.PROSPECT_ID
                        AND tgt.EMAIL = src.EMAIL
                    WHEN MATCHED THEN
                        UPDATE SET
                            NAME = src.NAME,
                            COMPANY = src.COMPANY,
                            ROLE = src.ROLE,
                            CONSENT = src.CONSENT
                    WHEN NOT MATCHED THEN INSERT(
                        PROSPECT_ID, EMAIL, NAME, COMPANY, ROLE, CONSENT
                    ) VALUES (
                        src.PROSPECT_ID, src.EMAIL, src.NAME, src.COMPANY, src.ROLE, src.CONSENT
                    )
                    """)
                conn.commit()

                st.success(csts.texts[lang]["saved_info_msg"])

                # Flip the state to True and rerun to hide the form and show the results
                st.session_state["form_submitted"] = True
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()

    ################################################
    # RESULT CARD
    ################################################
    else:

        cursor.execute(f"""
            SELECT SUM(c.SCORE) AS TOTAL_SCORE
            FROM RESULTS r
            JOIN CHOICES c ON c.VALUE = r.ANSWER_VALUE
            WHERE r.PROSPECT_ID = '{st.session_state["prospect_id"]}'
        """)
        row = cursor.fetchone()
        total_score = row[0] if row[0] is not None else 0
        MATURITY_LEVEL = band_from_score(total_score)

        cursor.execute("""
            SELECT *
            FROM RESULT_BANDS
        """)

        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]

        bands_map = {row["MATURITY_LEVEL"]: row for row in data}

        icons_map = {lvl: row["ICON_FILENAME"] for lvl, row in bands_map.items()}
        band_info = bands_map.get(MATURITY_LEVEL, {})
        text = band_info["TEXT_" + lang]
        pitch = band_info["PITCH_" + lang]
        band_name = csts.texts[lang]["maturity_level_" + str(MATURITY_LEVEL)]

        st.markdown(
            styles.maturity_grid_html(
                levels=[1, 2, 3, 4],
                current_level=MATURITY_LEVEL,
                band_names=csts.texts[lang],
                text=text,
                pitch=pitch,
                icons_map=icons_map,
            ),
            unsafe_allow_html=True,
        )

        # Allow the user to return home manually after they finish reading
        HOME_BTN_LABEL = "Retour à l'accueil" if lang == "FR" else "Return to Home"

        if st.button(HOME_BTN_LABEL, key="return_home_btn"):
            st.session_state.clear()
            st.session_state["show_home"] = True
            st.rerun()
        st.stop()


################################################
# QUIZ QUESTION SCREEN
################################################
q = questions[st.session_state["q_index"]]
question_id = q["ID"]
question_order = q["ORDER"]
question_body = q["QUESTION_TEXT_" + lang]

progress = (st.session_state["q_index"] + 1) / NB_QUESTIONS
COUNTER_TEXT = f"{csts.texts[lang].get('question_label', 'Question')} {question_order:02d} / {NB_QUESTIONS:02d}"

# Restart button — slot it into the meta row using a column layout
meta_l, meta_r = st.columns([5, 2])
with meta_l:
    if st.button(csts.texts[lang]["restart_btn"], key="restart_btn", type="tertiary"):
        st.session_state.clear()
        st.session_state["show_home"] = True
        st.rerun()

# --- PROGRESS BAR ---
st.markdown(styles.progress_bar_html(progress), unsafe_allow_html=True)
st.markdown(styles.quiz_meta_html(COUNTER_TEXT), unsafe_allow_html=True)

# --- QUESTION ---
st.markdown(styles.question_html(question_order, question_body), unsafe_allow_html=True)

# --- LOAD CHOICES ---
cursor.execute(f"""
    SELECT *
    FROM CHOICES
    WHERE QUESTION_ID = {question_id}
""")
rows = cursor.fetchall()
columns = [col[0] for col in cursor.description]
choices_df = [dict(zip(columns, row)) for row in rows]

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
        is_selected = val == current_selection
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

st.markdown("</div>", unsafe_allow_html=True)

# --- NAV ROW: Back + Next ---
st.markdown(
    '<div style="border-top:1px solid var(--line); padding-top:24px; display:flex; justify-content:space-between; align-items:center;">',
    unsafe_allow_html=True,
)

nav_l, nav_spacer, nav_r = st.columns([1, 4, 1])

with nav_l:
    if st.session_state["q_index"] > 0:
        if st.button(csts.texts[lang]["back_btn"], key="back_btn", type="secondary"):
            st.session_state["q_index"] -= 1
            st.rerun()

with nav_r:
    is_last = st.session_state["q_index"] == NB_QUESTIONS - 1
    text_validate_btn = (
        csts.texts[lang]["complete_btn"]
        if is_last
        else csts.texts[lang]["validate_btn"]
    )

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
        cursor.execute(f"""
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
            """)
        conn.commit()

        st.session_state["q_index"] += 1
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
