import streamlit as st
from uuid import uuid4
import re
from streamlit_app import constants as csts
from streamlit_app import styles
from streamlit_app.plexus import PLEXUS_HTML
import streamlit.components.v1 as components
import snowflake.connector

# TODO TO COMMENT -- CLEAR CACHES ON EVERY RUN FOR DEV PURPOSES, REMOVE LATER
# st.cache_data.clear()
# st.cache_resource.clear()


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
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM QUESTIONS ORDER BY "ORDER"')
    rows = cursor.fetchall()
    cols = [col[0] for col in cursor.description]
    return [dict(zip(cols, row)) for row in rows]

@st.cache_data
def load_choices() -> dict[int, list[dict]]:
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT *
        FROM CHOICES
    """)

    rows = cursor.fetchall()
    columns = [col.name if hasattr(col, 'name') else col for col in cursor.description]

    choices_by_question = {}

    for row in rows:
        if isinstance(row, dict):
            choice_dict = {key.name if hasattr(key, 'name') else key: val for key, val in row.items()}
        else:
            choice_dict = dict(zip(columns, row))
        
        q_id = choice_dict['QUESTION_ID']
        
        if q_id not in choices_by_question:
            choices_by_question[q_id] = []
            
        choices_by_question[q_id].append(choice_dict)
        
    return choices_by_question


@st.cache_data
def load_result_bands():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM RESULT_BANDS")
    rows = cursor.fetchall()
    cols = [col[0] for col in cursor.description]
    return [dict(zip(cols, row)) for row in rows]


#@st.cache_data(ttl=60)
def load_prospect_count():
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(1) FROM PROSPECTS WHERE DATE(CREATED_AT) = CURRENT_DATE()"
    )
    return cursor.fetchone()[0]


def band_from_score(sc: float) -> int:
    if sc <= 17:
        return 1
    if sc <= 25:
        return 2
    if sc <= 32:
        return 3
    return 4


def save_all_answers():
    answers = st.session_state["selected_answers"]
    prospect_id = st.session_state["prospect_id"]

    if not answers:
        return

    values_sql = ",".join(
        [f"('{prospect_id}','{q_id}','{val}')" for q_id, val in answers.items()]
    )

    query = f"""
        INSERT INTO RESULTS (PROSPECT_ID, QUESTION_ID, ANSWER_VALUE)
        VALUES {values_sql}
        """

    cursor.execute(query)
    conn.commit()


# --- CONFIG ---
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
st.html(styles.load_fonts())
st.html(styles.GLOBAL_CSS + styles.CANVAS_MARKUP)
components.html(PLEXUS_HTML, height=0, width=0)

# Load questions
questions = load_questions()
choices_db = load_choices()
NB_QUESTIONS = len(questions)

# TODO TO COMMENT -- DEBUG RESULT SCREEN
# if st.button("GO TO RESULT (DEBUG)"):
#     st.session_state["q_index"] = NB_QUESTIONS
#     st.session_state["form_submitted"] = True
#     st.rerun()

with st.container():

    ################################################
    # HEADER - logo + lang switcher
    ################################################
    if "lang" not in st.session_state:
        st.session_state["lang"] = "FR"  # default

    if "show_home" not in st.session_state:
        st.session_state["show_home"] = True

    if "prospect_id" not in st.session_state:
        st.session_state["prospect_id"] = str(uuid4())

    if "q_index" not in st.session_state:
        st.session_state["q_index"] = 0

    if "selected_answers" not in st.session_state:
        # {question_id: answer_value} highlight selected on revisit
        st.session_state["selected_answers"] = {}

    st.markdown(styles.logo_chip_html(), unsafe_allow_html=True)

    lang = st.radio(
        label="Language",
        options=["FR", "EN"],
        horizontal=True,
        index=0 if st.session_state["lang"] == "FR" else 1,
        label_visibility="collapsed",
        key="lang_radio",
    )
    st.session_state["lang"] = lang

    ################################################
    # MID SECTION - home screen with quiz intro + QR code
    ################################################
    if st.session_state["show_home"]:
        with st.container():
            st.markdown('<div class="kpc-fluid-answers-box">', unsafe_allow_html=True)
            home_mid_left, home_mid_right = st.columns([2, 1], gap="large")

            # --- LEFT: Intro text + start button ---
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

                total_registered = load_prospect_count()

                if total_registered > 0:
                    COUNTER_MSG = (
                        f"Déjà {total_registered} participants !"
                        if lang == "FR"
                        else f"Join {total_registered} other participants!"
                    )

                    st.markdown(
                        f"""
                        <div style="color: #888888; font-size: 14px; margin-left:10px; margin-bottom:5px">
                        <i>{COUNTER_MSG}</i>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            # --- RIGHT: QR code ---
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
            st.markdown("</div>", unsafe_allow_html=True)
        st.stop()

    ################################################
    # END SCREEN
    ################################################
    if st.session_state["q_index"] >= NB_QUESTIONS:

        ################################################
        # LEAD GEN FORM
        ################################################
        if not st.session_state.get("form_submitted", False):
            with st.container():
                st.markdown(
                    '<div class="kpc-fluid-answers-box">', unsafe_allow_html=True
                )
                st.markdown(
                    f'<h3 class="kpc-section-title">{csts.texts[lang]["informations_msg"]}</h3>',
                    unsafe_allow_html=True,
                )

                col_a, col_b = st.columns(2)
                with col_a:
                    name = st.text_input(csts.texts[lang]["info_name"], key="user_name")
                    email = st.text_input(
                        csts.texts[lang]["info_email"], key="user_email"
                    )
                with col_b:
                    company = st.text_input(
                        csts.texts[lang]["info_company"], key="user_company"
                    )
                    role = st.text_input(csts.texts[lang]["info_role"], key="user_role")

                consent = st.checkbox(
                    csts.texts[lang]["contact_checkbox"], key="user_consent"
                )
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="kpc-nav-row">', unsafe_allow_html=True)
            if st.button(
                csts.texts[lang]["submit_btn"],
                key="submit_btn",
                type="primary",
                disabled=not consent,
                use_container_width=True,
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
                        INSERT INTO PROSPECTS(
                            PROSPECT_ID, 
                            EMAIL, 
                            NAME, 
                            COMPANY, 
                            ROLE, 
                            CONSENT
                        ) VALUES (
                            '{st.session_state["prospect_id"]}',
                            '{safe_email}',
                            '{safe_name}',
                            '{safe_company}',
                            '{safe_role}',
                            {1 if consent else 0}
                        )
                        """)
                    conn.commit()

                    # st.success(csts.texts[lang]["saved_info_msg"])

                    st.markdown(
                        f"""
                        <div style="
                            background-color: #e6f4ea;
                            border: 1px solid #2e7d32;
                            color: #2e7d32;
                            padding: 12px;
                            border-radius: 8px;
                            font-weight: 500;
                            margin-top: 10px;
                        ">
                            {csts.texts[lang]["saved_info_msg"]}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    if not st.session_state.get("answers_saved", False):
                        save_all_answers()
                        st.session_state["answers_saved"] = True

                    # Flip the state to True and rerun to hide the form and show the results
                    st.session_state["form_submitted"] = True
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
            st.stop()

        ################################################
        # RESULT CARD
        ################################################
        else:

            with st.container():
                st.markdown(
                    '<div class="kpc-fluid-answers-box">', unsafe_allow_html=True
                )
                cursor.execute(f"""
                    SELECT SUM(c.SCORE) AS TOTAL_SCORE
                    FROM RESULTS r
                    JOIN CHOICES c ON c.VALUE = r.ANSWER_VALUE
                    WHERE r.PROSPECT_ID = '{st.session_state["prospect_id"]}'
                """)
                row = cursor.fetchone()
                total_score = row[0] if row[0] is not None else 0
                MATURITY_LEVEL = band_from_score(total_score)

                data = load_result_bands()

                bands_map = {row["MATURITY_LEVEL"]: row for row in data}
                icons_map = {
                    lvl: row["ICON_FILENAME"] for lvl, row in bands_map.items()
                }
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

            st.markdown('<div class="kpc-nav-row">', unsafe_allow_html=True)
            # Allow the user to return home manually after they finish reading
            HOME_BTN_LABEL = csts.texts[lang]["return_home"]

            if st.button(
                HOME_BTN_LABEL,
                key="return_home_btn",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.clear()
                st.session_state["show_home"] = True
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
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
        if st.button(
            csts.texts[lang]["restart_btn"], key="restart_btn", type="tertiary"
        ):
            st.session_state.clear()
            st.session_state["show_home"] = True
            st.rerun()

    # --- PROGRESS BAR ---
    st.markdown(styles.progress_bar_html(progress), unsafe_allow_html=True)
    st.markdown(styles.quiz_meta_html(COUNTER_TEXT), unsafe_allow_html=True)

    # --- QUESTION ---
    st.markdown(
        styles.question_html(question_order, question_body), unsafe_allow_html=True
    )

    # --- LOAD CHOICES ---
    with st.container():
        st.markdown(
            '<div class="kpc-fluid-answers-box kpc-answer-row">', unsafe_allow_html=True
        )

        choices_df = choices_db.get(question_id, [])

        choice_labels = [c["CHOICE_TEXT_" + lang] for c in choices_df]
        choice_values = [c["VALUE"] for c in choices_df]

        # --- ANSWER CARDS (as buttons in a 2-column grid) ---
        # Currently selected answer (from session state, if user has visited this question)
        current_selection = st.session_state["selected_answers"].get(question_id)

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
    st.markdown('<div class="kpc-nav-row">', unsafe_allow_html=True)

    nav_l, nav_spacer, nav_r = st.columns([2, 3, 2])

    with nav_l:
        if st.session_state["q_index"] > 0:
            if st.button(
                csts.texts[lang]["back_btn"],
                key="back_btn",
                type="secondary",
                use_container_width=True,
            ):
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
            use_container_width=True,
        ):

            st.session_state["q_index"] += 1
            st.rerun()

    # Handling for the back or nexr buttons
    components.html("""
    <script>
    (function() {
    let backOriginal = null;
    let nextOriginal = null;

    function fixLayout() {
        const doc = window.parent.document;
        const w = window.parent.innerWidth;

        const backContainer = doc.querySelector('.st-key-back_btn');
        const nextContainer = doc.querySelector('.st-key-next_btn');

        if (backContainer) {
        const p = backContainer.querySelector('p');
        if (p) {
            if (p.textContent !== '←' && p.textContent !== '→') backOriginal = p.textContent;
            p.textContent = w < 480 ? '←' : (backOriginal || p.textContent);
        }
        }

        if (nextContainer) {
        const p = nextContainer.querySelector('p');
        if (p) {
            if (p.textContent !== '←' && p.textContent !== '→') nextOriginal = p.textContent;
            p.textContent = w < 480 ? '→' : (nextOriginal || p.textContent);
        }
        }

        if (backContainer && nextContainer) {
        const backCol = backContainer.closest('[data-testid="stColumn"]');
        const nextCol = nextContainer.closest('[data-testid="stColumn"]');

        if (backCol && nextCol) {
            // Find the shared stHorizontalBlock parent
            const hBlock = backCol.closest('[data-testid="stHorizontalBlock"]');
            if (hBlock) {
            const cols = hBlock.querySelectorAll('[data-testid="stColumn"]');
            if (w < 480) {
                cols.forEach((col, i) => {
                if (col === backCol || col === nextCol) {
                    col.style.setProperty('flex', '1 1 0', 'important');
                    col.style.setProperty('max-width', '50%', 'important');
                    col.style.setProperty('min-width', '0', 'important');
                    const btn = col.querySelector('button');
                    if (btn) btn.style.setProperty('width', '100%', 'important');
                } else {
                    // Handling for the Spacer column
                    col.style.setProperty('display', 'none', 'important');
                    col.style.setProperty('flex', '0', 'important');
                    col.style.setProperty('width', '0', 'important');
                    col.style.setProperty('padding', '0', 'important');
                }
                });
            } else {
                // Restore on wide screens
                cols.forEach(col => {
                col.style.removeProperty('display');
                col.style.removeProperty('flex');
                col.style.removeProperty('max-width');
                col.style.removeProperty('min-width');
                col.style.removeProperty('width');
                col.style.removeProperty('padding');
                const btn = col.querySelector('button');
                if (btn) btn.style.removeProperty('width');
                });
            }
            }
        }
        }
    }

    setInterval(fixLayout, 300);
    window.parent.addEventListener('resize', fixLayout);
    fixLayout();
    })();
    </script>
    """, height=0)
    st.markdown("</div>", unsafe_allow_html=True)
