import os
import io
import json
import requests
from datetime import datetime, date, time
from PIL import Image
import streamlit as st

from frontend.styles import TRACE_CSS

# Configure Streamlit page
st.set_page_config(
    page_title="TRACE | AI Reunification & Claim Verification",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply TRACE custom CSS
st.markdown(TRACE_CSS, unsafe_allow_html=True)

API_URL = os.getenv("TRACE_API_URL", "http://127.0.0.1:8000")

# Initialize session state variables
if "current_screen" not in st.session_state:
    st.session_state.current_screen = "📝 Screen 1: Log Found Item"
if "active_item_id" not in st.session_state:
    st.session_state.active_item_id = 1
if "active_challenge_id" not in st.session_state:
    st.session_state.active_challenge_id = None
if "active_challenge_question" not in st.session_state:
    st.session_state.active_challenge_question = ""
if "last_claim_result" not in st.session_state:
    st.session_state.last_claim_result = None
if "preset_description" not in st.session_state:
    st.session_state.preset_description = "Navy blue canvas backpack with leather bottom and padded shoulder straps"
if "preset_location" not in st.session_state:
    st.session_state.preset_location = "Platform 4"
if "preset_hidden" not in st.session_state:
    st.session_state.preset_hidden = "small tear on the left strap with yellow lining inside front pocket"
if "preset_photo_path" not in st.session_state:
    st.session_state.preset_photo_path = "data/seed/images/found_navy_backpack.jpg"
if "claim_answer_input" not in st.session_state:
    st.session_state.claim_answer_input = ""
if "is_released" not in st.session_state:
    st.session_state.is_released = False


def get_queue():
    try:
        res = requests.get(f"{API_URL}/dashboard/queue", timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return []


def get_item_matches(item_id: int):
    try:
        res = requests.get(f"{API_URL}/found-items/{item_id}/matches", timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        st.error(f"Error fetching matches: {e}")
    return []


def create_challenge(item_id: int):
    try:
        res = requests.post(f"{API_URL}/found-items/{item_id}/challenge", timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        st.error(f"Error generating challenge question: {e}")
    return None


def submit_answer(challenge_id: int, answer: str):
    try:
        res = requests.post(
            f"{API_URL}/challenges/{challenge_id}/answer",
            json={"answer": answer},
            timeout=5,
        )
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        st.error(f"Error evaluating claim answer: {e}")
    return None


# ==========================================
# HEADER & BRANDING
# ==========================================
st.markdown(
    """
    <div class="trace-header">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <h1 style="margin: 0; font-size: 2.1rem; letter-spacing: -0.5px; color: #F2EFE9;">
                    <span style="color: #C98A2C;">T R A C E</span>
                </h1>
                <p style="margin: 4px 0 0 0; font-size: 1rem; color: #D6D2CA; font-weight: 500;">
                    An AI reunification engine — built to find the match, and prove it belongs to the right person.
                </p>
            </div>
            <div style="text-align: right;">
                <span class="trace-badge-amber">Staff Decision-Support Desk</span>
                <p style="margin: 5px 0 0 0; font-size: 0.8rem; color: #8F8C84;">
                    Team Grey Matter (Niviya Albert, Adithyan M J, Diya Paramanand)
                </p>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Render Workflow Step Progress Banner
step1_class = "active" if st.session_state.current_screen == "📝 Screen 1: Log Found Item" else ("completed" if st.session_state.active_item_id else "")
step2_class = "active" if st.session_state.current_screen == "🎯 Screen 2: Ranked Matches" else ("completed" if st.session_state.active_challenge_id else "")
step3_class = "active" if st.session_state.current_screen == "🛡️ Screen 3: Claim Verification" else ("completed" if st.session_state.last_claim_result and st.session_state.last_claim_result.get("is_match") else "")

st.markdown(
    f"""
    <div class="step-banner">
        <div class="step-item {step1_class}">
            <span class="step-num {step1_class}">1</span>
            <span>1. Intake & Vault Hidden Detail</span>
        </div>
        <div style="color: #555;">➔</div>
        <div class="step-item {step2_class}">
            <span class="step-num {step2_class}">2</span>
            <span>2. Multi-Modal Fusion Ranking</span>
        </div>
        <div style="color: #555;">➔</div>
        <div class="step-item {step3_class}">
            <span class="step-num {step3_class}">3</span>
            <span>3. Anti-Fraud Challenge & Release</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar Navigation
with st.sidebar:
    st.markdown("### 🧭 Navigation")
    screens = [
        "📝 Screen 1: Log Found Item",
        "🎯 Screen 2: Ranked Matches",
        "🛡️ Screen 3: Claim Verification",
        "📋 Staff Queue Overview",
        "➕ Log Lost Report",
    ]
    current_idx = screens.index(st.session_state.current_screen) if st.session_state.current_screen in screens else 0
    selected_screen = st.radio("Select Screen", screens, index=current_idx, label_visibility="collapsed")
    if selected_screen != st.session_state.current_screen:
        st.session_state.current_screen = selected_screen
        st.rerun()

    st.markdown("---")
    st.markdown("### ⚡ 60s Demo Scenarios")
    st.caption("1-click presets for live pitch demonstration:")

    if st.button("🎒 Demo 1: Mismatched Wording", use_container_width=True):
        st.session_state.preset_description = "Navy blue canvas backpack with leather bottom and padded shoulder straps"
        st.session_state.preset_location = "Platform 4"
        st.session_state.preset_hidden = "small tear on the left strap with yellow lining inside front pocket"
        st.session_state.preset_photo_path = "data/seed/images/found_navy_backpack.jpg"
        st.session_state.current_screen = "📝 Screen 1: Log Found Item"
        st.session_state.is_released = False
        st.rerun()

    if st.button("⌚ Demo 2: Missing Photo Re-norm", use_container_width=True):
        st.session_state.preset_description = "Gold wrist chronograph with black leather strap and white dial"
        st.session_state.preset_location = "Near Ticket Counter"
        st.session_state.preset_hidden = "engraved anniversary date 14-02-2018 on rear case plate"
        st.session_state.preset_photo_path = "data/seed/images/found_gold_watch.jpg"
        st.session_state.current_screen = "📝 Screen 1: Log Found Item"
        st.session_state.is_released = False
        st.rerun()

    if st.button("🧳 Demo 3: False Claim vs Genuine", use_container_width=True):
        st.session_state.preset_description = "Blue hard-shell rolling suitcase with 4 spinner wheels and retractable handle"
        st.session_state.preset_location = "Main Concourse"
        st.session_state.preset_hidden = "airline baggage tag with initials R.S. on top handle"
        st.session_state.preset_photo_path = "data/seed/images/found_blue_suitcase.jpg"
        st.session_state.current_screen = "📝 Screen 1: Log Found Item"
        st.session_state.is_released = False
        st.rerun()

    st.markdown("---")
    st.markdown("### ⚙️ Engine Health")
    queue_data = get_queue()
    st.markdown(f"**Open Items in Queue:** `{len(queue_data)}`")
    st.markdown("**Visual Model:** `CLIP ViT-B/32`")
    st.markdown("**Text Model:** `MiniLM-L6-v2`")
    st.markdown("**Verification:** `Deterministic Keyword Check`")


# ==========================================
# SCREEN 1: LOG FOUND ITEM
# ==========================================
if st.session_state.current_screen == "📝 Screen 1: Log Found Item":
    st.markdown("## 📝 Screen 1 — Log a Found Item")
    st.caption("Staff inputs physical item details and vaults one non-public hidden attribute before system ranking.")

    col1, col2 = st.columns([1.2, 1])

    with col1:
        with st.form("log_found_item_form"):
            desc_val = st.session_state.preset_description
            description = st.text_area(
                "Public Item Description",
                value=desc_val,
                height=85,
                help="Free text description of the physical item found.",
            )

            c_loc, c_date = st.columns(2)
            with c_loc:
                locations_list = [
                    "Platform 4", "Platform 1", "Platform 2", "Platform 3", "Platform 5",
                    "Near Ticket Counter", "Waiting Hall", "Main Concourse",
                    "Food Court", "Coach B4", "Parking Lot", "Enquiry Counter"
                ]
                preset_loc_idx = locations_list.index(st.session_state.preset_location) if st.session_state.preset_location in locations_list else 0
                location = st.selectbox("Intake Location", locations_list, index=preset_loc_idx)
            
            with c_date:
                found_d = st.date_input("Found Date", value=date.today())
                found_t = st.time_input("Found Time", value=time(hour=14, minute=30))

            hidden_val = st.session_state.preset_hidden
            hidden_attribute = st.text_area(
                "🔒 Internal Hidden Attribute (Never Shown Publicly)",
                value=hidden_val,
                height=75,
                help="Used strictly for anti-fraud claim verification challenge question.",
            )

            st.caption("🔒 **Staff Vault:** This hidden detail is never revealed to claimants or public search.")

            uploaded_photo = st.file_uploader("Upload Item Photo", type=["jpg", "jpeg", "png"])

            submit_btn = st.form_submit_button("🚀 Log Item & Search Open Lost Reports", use_container_width=True)

            if submit_btn:
                found_dt_str = datetime.combine(found_d, found_t).isoformat()
                files = {}
                data = {
                    "description": description,
                    "location": location,
                    "hidden_attribute": hidden_attribute,
                    "found_at": found_dt_str,
                }

                if uploaded_photo is not None:
                    files["photo"] = (uploaded_photo.name, uploaded_photo.getvalue(), uploaded_photo.type)
                elif st.session_state.preset_photo_path and os.path.exists(st.session_state.preset_photo_path):
                    data["photo_preset_path"] = st.session_state.preset_photo_path
                else:
                    data["photo_preset_path"] = "data/seed/images/found_navy_backpack.jpg"

                with st.spinner("Embedding visual & semantic features and logging item..."):
                    try:
                        res = requests.post(f"{API_URL}/found-items", data=data, files=files if files else None)
                        if res.status_code in (200, 201):
                            new_item = res.json()
                            st.session_state.active_item_id = new_item["id"]
                            st.session_state.active_challenge_id = None
                            st.session_state.active_challenge_question = ""
                            st.session_state.last_claim_result = None
                            st.session_state.is_released = False
                            st.session_state.current_screen = "🎯 Screen 2: Ranked Matches"
                            st.rerun()
                        else:
                            st.error(f"Failed to log item: {res.text}")
                    except Exception as ex:
                        st.error(f"Error: {ex}")

    with col2:
        st.markdown("#### Intake Photo Preview")
        preview_img = None
        if uploaded_photo:
            preview_img = Image.open(uploaded_photo)
        elif st.session_state.preset_photo_path and os.path.exists(st.session_state.preset_photo_path):
            preview_img = Image.open(st.session_state.preset_photo_path)
        else:
            default_path = "data/seed/images/found_navy_backpack.jpg"
            if os.path.exists(default_path):
                preview_img = Image.open(default_path)

        if preview_img:
            st.image(preview_img, caption="Intake Item Photo", use_column_width=True)

        st.info(
            "💡 **Why TRACE works:** When passenger lost reports use different terminology (e.g. 'black rucksack' instead of 'navy backpack'), TRACE's multi-modal CLIP + MiniLM fusion still surfaces the correct match."
        )


# ==========================================
# SCREEN 2: RANKED MATCHES
# ==========================================
elif st.session_state.current_screen == "🎯 Screen 2: Ranked Matches":
    st.markdown("## 🎯 Screen 2 — Multi-Modal Ranked Matches")
    st.caption("Real-time fusion scoring combining Visual (40%), Text (30%), Location (15%), and Time (15%).")

    if not st.session_state.active_item_id and queue_data:
        st.session_state.active_item_id = queue_data[0]["found_item"]["id"]

    if not st.session_state.active_item_id:
        st.info("No item currently selected. Please log a found item in Screen 1 or pick one from the Staff Queue.")
    else:
        matches = get_item_matches(st.session_state.active_item_id)
        curr_item = next((q["found_item"] for q in queue_data if q["found_item"]["id"] == st.session_state.active_item_id), None)
        
        if curr_item:
            with st.expander(f"📦 Active Found Item #{curr_item['id']} — {curr_item['description'][:65]}...", expanded=True):
                c_img, c_info = st.columns([1, 3])
                with c_img:
                    if os.path.exists(curr_item["photo_path"]):
                        st.image(curr_item["photo_path"], width=130)
                with c_info:
                    st.markdown(f"**Description:** {curr_item['description']}")
                    st.markdown(f"**Location:** `{curr_item['location']}` | **Found Time:** `{curr_item['found_at'][:16].replace('T', ' ')}` | **Status:** `{curr_item['status'].upper()}`")
                    st.markdown(f"🔒 **Vaulted Hidden Detail:** `{curr_item['hidden_attribute']}`")

        if not matches:
            st.info("No open lost reports found for matching.")
        else:
            top_match = matches[0]
            
            st.markdown("---")
            st.markdown("### 🌟 Top-Ranked Candidate Match")

            card_col1, card_col2 = st.columns([1.1, 2])
            
            with card_col1:
                st.markdown(
                    f"""
                    <div class="trace-card-highlight">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span class="trace-badge-amber">Lost Report #{top_match['lost_report_id']}</span>
                            <span class="trace-badge-green" style="font-size: 1.05rem;">Fused: {int(top_match['fused_score'] * 100)}%</span>
                        </div>
                        <h4 style="margin: 6px 0; color: #F2EFE9;">{top_match['lost_report']['description']}</h4>
                        <p style="margin: 4px 0; font-size: 0.9rem; color: #BBB7AE;">
                            📍 <b>Location:</b> {top_match['lost_report']['location']}<br>
                            🕒 <b>Lost Time:</b> {top_match['lost_report']['lost_at'][:16].replace('T', ' ')}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if top_match["lost_report"]["photo_path"] and os.path.exists(top_match["lost_report"]["photo_path"]):
                    st.image(top_match["lost_report"]["photo_path"], caption="Lost Report Photo", use_column_width=True)
                else:
                    st.info("📷 *No photo provided on this lost report (weight auto-renormalized to 50% Text, 25% Loc, 25% Time).*")

                if st.button("🛡️ Proceed to Claim Verification", key="btn_verify_top", use_container_width=True):
                    ch = create_challenge(top_match["found_item_id"])
                    if ch:
                        st.session_state.active_challenge_id = ch["id"]
                        st.session_state.active_challenge_question = ch["question_text"]
                        st.session_state.last_claim_result = None
                        st.session_state.current_screen = "🛡️ Screen 3: Claim Verification"
                        st.rerun()

            with card_col2:
                st.markdown("#### 🔬 Multi-Modal Score Breakdown")
                st.caption(top_match["explanation"])

                # Visual Score Bar
                v_score = top_match["visual_score"]
                st.markdown(f"**Visual Embedding Similarity (CLIP ViT-B/32):** `{int(v_score * 100)}%`")
                st.markdown(f'<div class="score-bar-bg"><div class="score-bar-fill-amber" style="width: {int(v_score * 100)}%;"></div></div>', unsafe_allow_html=True)

                # Text Score Bar
                t_score = top_match["text_score"]
                st.markdown(f"**Semantic Text Similarity (Sentence-Transformers MiniLM):** `{int(t_score * 100)}%`")
                st.markdown(f'<div class="score-bar-bg"><div class="score-bar-fill-blue" style="width: {int(t_score * 100)}%;"></div></div>', unsafe_allow_html=True)

                # Location Score Bar
                l_score = top_match["location_score"]
                st.markdown(f"**Station Zone Adjacency Score:** `{int(l_score * 100)}%`")
                st.markdown(f'<div class="score-bar-bg"><div class="score-bar-fill-green" style="width: {int(l_score * 100)}%;"></div></div>', unsafe_allow_html=True)

                # Time Decay Score Bar
                tm_score = top_match["time_score"]
                st.markdown(f"**Time Proximity (14-day Linear Decay):** `{int(tm_score * 100)}%`")
                st.markdown(f'<div class="score-bar-bg"><div class="score-bar-fill-purple" style="width: {int(tm_score * 100)}%;"></div></div>', unsafe_allow_html=True)

                st.markdown(
                    f"""
                    <div style="background-color: #242424; padding: 12px 16px; border-radius: 8px; border: 1px solid #383838; margin-top: 12px;">
                        <span style="font-weight: 700; color: #E5A84B;">Overall Multi-Modal Fused Score:</span>
                        <span style="font-size: 1.35rem; font-weight: 800; color: #56D364; float: right;">{int(top_match['fused_score'] * 100)}%</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Other candidate matches
            if len(matches) > 1:
                st.markdown("---")
                st.markdown("#### Other Candidate Lost Reports")
                for other in matches[1:]:
                    with st.container():
                        st.markdown(
                            f"""
                            <div class="trace-card">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>
                                        <b>Lost Report #{other['lost_report_id']}</b>: {other['lost_report']['description']}
                                        <div style="font-size: 0.85rem; color: #8F8C84; margin-top: 4px;">
                                            📍 {other['lost_report']['location']} | Visual: {int(other['visual_score']*100)}% | Text: {int(other['text_score']*100)}% | Loc: {int(other['location_score']*100)}% | Time: {int(other['time_score']*100)}%
                                        </div>
                                    </div>
                                    <div>
                                        <span class="trace-badge-amber">Fused: {int(other['fused_score']*100)}%</span>
                                    </div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )


# ==========================================
# SCREEN 3: CLAIM VERIFICATION
# ==========================================
elif st.session_state.current_screen == "🛡️ Screen 3: Claim Verification":
    st.markdown("## 🛡️ Screen 3 — Anti-Fraud Claim Verification")
    st.caption("Deterministic challenge question verifies claimant answers against the vaulted hidden detail before physical handoff.")

    if not st.session_state.active_item_id:
        st.info("No active item selected for verification. Please select an item from Screen 1 or the Staff Queue.")
    else:
        curr_item = next((q["found_item"] for q in queue_data if q["found_item"]["id"] == st.session_state.active_item_id), None)
        
        c_ver1, c_ver2 = st.columns([1.2, 1])

        with c_ver1:
            st.markdown("#### 1. Auto-Generated Challenge Question")
            
            if not st.session_state.active_challenge_id:
                if st.button("⚡ Generate Challenge Question", use_container_width=True):
                    ch = create_challenge(st.session_state.active_item_id)
                    if ch:
                        st.session_state.active_challenge_id = ch["id"]
                        st.session_state.active_challenge_question = ch["question_text"]
                        st.session_state.last_claim_result = None
                        st.rerun()

            if st.session_state.active_challenge_id:
                st.markdown(
                    f"""
                    <div style="background-color: #24221D; border-left: 4px solid #C98A2C; padding: 14px; border-radius: 6px; margin: 10px 0;">
                        <span style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; color: #C98A2C; font-weight: 700;">Challenge Question (Presented to Claimant)</span>
                        <h4 style="margin: 6px 0 0 0; color: #F2EFE9;">"{st.session_state.active_challenge_question}"</h4>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown("#### 2. Claimant Response")
                
                st.caption("Demo 1-Click Fillers:")
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("✅ Load Genuine Answer", use_container_width=True):
                        if curr_item:
                            st.session_state.claim_answer_input = f"It has a {curr_item['hidden_attribute']}."
                        st.rerun()
                with b2:
                    if st.button("❌ Load Fraudulent Answer", use_container_width=True):
                        st.session_state.claim_answer_input = "There is a standard blue ribbon tied around the handle."
                        st.rerun()

                claimant_answer = st.text_area(
                    "Typed Claimant Answer",
                    value=st.session_state.claim_answer_input,
                    height=90,
                    placeholder="Enter what the claimant stated or typed...",
                )

                if st.button("🔍 Evaluate Claim Answer", use_container_width=True):
                    if not claimant_answer.strip():
                        st.warning("Please type or paste a claimant answer first.")
                    else:
                        with st.spinner("Evaluating keyword presence against vaulted detail..."):
                            result = submit_answer(st.session_state.active_challenge_id, claimant_answer)
                            if result:
                                st.session_state.last_claim_result = result
                                st.rerun()

        with c_ver2:
            st.markdown("#### 3. Verification Decision")
            
            if st.session_state.last_claim_result:
                res = st.session_state.last_claim_result
                if res["is_match"]:
                    st.markdown(
                        f"""
                        <div style="background-color: #1A281E; border: 2px solid #2EA043; padding: 18px; border-radius: 10px;">
                            <span class="trace-badge-green" style="font-size: 1rem;">✅ CLAIM VERIFIED — MATCH CONFIRMED</span>
                            <h4 style="color: #56D364; margin: 10px 0 6px 0;">Safe for Physical Handover</h4>
                            <p style="color: #D6D2CA; font-size: 0.95rem; margin-bottom: 8px;">
                                {res['message']}
                            </p>
                            <div style="background-color: rgba(46, 160, 67, 0.15); padding: 8px 12px; border-radius: 6px; font-size: 0.85rem; color: #56D364;">
                                <b>Matched Vaulted Terms:</b> {', '.join(res['matched_keywords']) if res['matched_keywords'] else 'All'}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    # Handover Release Certificate Action
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    if not st.session_state.is_released:
                        if st.button("📦 Authorize & Confirm Physical Release", use_container_width=True):
                            st.session_state.is_released = True
                            st.rerun()
                    else:
                        st.markdown(
                            f"""
                            <div class="audit-box">
                                <div style="color: #56D364; font-weight: bold; border-bottom: 1px solid #2E5C3B; padding-bottom: 4px; margin-bottom: 8px;">
                                    🧾 OFFICIAL TRACE HANDOVER RECEIPT
                                </div>
                                <b>Item Reference:</b> Found Item #{curr_item['id'] if curr_item else 'N/A'}<br>
                                <b>Verification Status:</b> VERIFIED & AUTHORIZED<br>
                                <b>Matched Key Terms:</b> {', '.join(res['matched_keywords'])}<br>
                                <b>Released Timestamp:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}<br>
                                <b>Authorized By:</b> Desk Officer (Duty Station 04)<br>
                                <b>Audit Signature:</b> TRACE-SEC-OK-{''.join([c[0] for c in res['matched_keywords']]).upper()}8821
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                else:
                    st.markdown(
                        f"""
                        <div style="background-color: #2D1A1A; border: 2px solid #DA3633; padding: 18px; border-radius: 10px;">
                            <span class="trace-badge-red" style="font-size: 1rem;">❌ FLAGGED FOR STAFF REVIEW</span>
                            <h4 style="color: #F85149; margin: 10px 0 6px 0;">Detail Mismatch — Potential Fraud</h4>
                            <p style="color: #D6D2CA; font-size: 0.95rem; margin-bottom: 8px;">
                                {res['message']}
                            </p>
                            <div style="background-color: rgba(248, 81, 73, 0.15); padding: 8px 12px; border-radius: 6px; font-size: 0.85rem; color: #F85149;">
                                <b>Expected Distinctive Details:</b> {', '.join(res['expected_keywords'])}<br>
                                <b>Matched Terms:</b> None
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("Submit claimant answer to view verification decision.")

            if curr_item:
                st.markdown("---")
                st.markdown("##### 🔒 Vaulted Reference (Staff Only)")
                st.caption(f"**Item ID:** #{curr_item['id']}")
                st.caption(f"**Vaulted Attribute:** `{curr_item['hidden_attribute']}`")


# ==========================================
# STAFF QUEUE OVERVIEW
# ==========================================
elif st.session_state.current_screen == "📋 Staff Queue Overview":
    st.markdown("## 📋 Staff Lost Property Queue")
    st.caption("Live decision-support queue showing all open intake items and top matched candidate reports.")

    if not queue_data:
        st.info("Queue is currently empty.")
    else:
        for row in queue_data:
            f_item = row["found_item"]
            top_m = row["top_match"]
            
            with st.container():
                st.markdown(
                    f"""
                    <div class="trace-card">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px;">
                            <div>
                                <span class="trace-badge-amber">Found Item #{f_item['id']}</span>
                                <span style="font-size: 0.85rem; color: #8F8C84; margin-left: 8px;">📍 {f_item['location']} | 🕒 {f_item['found_at'][:16].replace('T', ' ')}</span>
                                <h4 style="margin: 6px 0; color: #F2EFE9;">{f_item['description']}</h4>
                                <p style="margin: 4px 0; font-size: 0.85rem; color: #BBB7AE;">
                                    🔒 Hidden Detail: <i>{f_item['hidden_attribute']}</i>
                                </p>
                            </div>
                            <div style="text-align: right;">
                                {"<span class='trace-badge-green'>Top Match: " + str(int(top_m['fused_score'] * 100)) + "%</span>" if top_m else "<span class='trace-badge-amber'>No Matches</span>"}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                
                c_btn1, c_btn2 = st.columns([1, 4])
                with c_btn1:
                    if st.button(f"Inspect Matches #{f_item['id']}", key=f"inspect_{f_item['id']}"):
                        st.session_state.active_item_id = f_item["id"]
                        st.session_state.active_challenge_id = None
                        st.session_state.active_challenge_question = ""
                        st.session_state.last_claim_result = None
                        st.session_state.is_released = False
                        st.session_state.current_screen = "🎯 Screen 2: Ranked Matches"
                        st.rerun()


# ==========================================
# LOG LOST REPORT
# ==========================================
elif st.session_state.current_screen == "➕ Log Lost Report":
    st.markdown("## ➕ Register Passenger Lost Report")
    st.caption("Log a report filed by a passenger searching for their lost property.")

    with st.form("log_lost_report_form"):
        lr_desc = st.text_area("Lost Item Description", "Black travel rucksack with side water bottle mesh", height=85)
        
        c1, c2 = st.columns(2)
        with c1:
            lr_loc = st.selectbox("Approximate Location", [
                "Near Ticket Counter", "Platform 4", "Platform 1", "Platform 2", "Platform 3",
                "Waiting Hall", "Main Concourse", "Food Court", "Coach B4", "Parking Lot"
            ])
        with c2:
            lr_date = st.date_input("Date Lost", value=date.today())

        has_photo_choice = st.checkbox("Include reference photo from passenger", value=True)
        photo_path_val = "data/seed/images/lost_black_rucksack.jpg" if has_photo_choice else None

        submit_lr = st.form_submit_button("📝 Register Lost Report", use_container_width=True)

        if submit_lr:
            payload = {
                "description": lr_desc,
                "location": lr_loc,
                "photo_path": photo_path_val,
                "lost_at": datetime.combine(lr_date, time(12, 0)).isoformat(),
            }
            try:
                r = requests.post(f"{API_URL}/lost-reports", json=payload, timeout=5)
                if r.status_code in (200, 201):
                    st.success(f"Lost Report #{r.json()['id']} registered successfully! Open items will now be re-ranked against this report.")
                else:
                    st.error(f"Error: {r.text}")
            except Exception as e:
                st.error(f"Failed to connect to backend: {e}")
