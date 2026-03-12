import streamlit as st
import os
import json
import pandas as pd
from PIL import Image
from generate_demo import generate_assets

OUTPUT_DIR = "output"
FRAMES_DIR = os.path.join(OUTPUT_DIR, "frames")
METADATA_DIR = os.path.join(OUTPUT_DIR, "metadata")

st.set_page_config(page_title="Chrono-Auth Demo", page_icon="🔐", layout="wide")

st.markdown("""
<style>
.stApp {
    background-color: #0b1120;
    color: #e5e7eb;
}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 1.5rem;
    max-width: 1400px;
}
h1, h2, h3, h4, h5, h6, p, label, div {
    color: #e5e7eb;
}
.section-title {
    color: #38bdf8;
    font-size: 1.7rem;
    font-weight: 700;
    margin-top: 1.4rem;
    margin-bottom: 1rem;
}
.small-note {
    color: #94a3b8;
    font-size: 0.9rem;
}
hr {
    border-color: #1f2937;
}
[data-testid="stSidebar"] {
    background-color: #111827;
}
[data-testid="stExpander"] {
    background-color: #111827;
    border: 1px solid #1f2937;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def load_image(path):
    return Image.open(path)

def safe_image(path):
    if os.path.exists(path):
        return load_image(path)
    return None

def load_current_data():
    metadata_path = os.path.join(METADATA_DIR, "metadata.json")
    timemap_path = os.path.join(METADATA_DIR, "timemap.json")
    if not os.path.exists(metadata_path) or not os.path.exists(timemap_path):
        return None, None
    return load_json(metadata_path), load_json(timemap_path)

st.sidebar.title("🔐 Chrono-Auth")

attack_mode = st.sidebar.toggle("Simulate Attack", value=True)
browser_text = st.sidebar.text_input("Browser Transaction", "Transfer: $50 to Alice")
default_hidden = "CONFIRM: PAY $5000 TO MALLORY" if attack_mode else "CONFIRM: PAY $50 TO ALICE"
hidden_text = st.sidebar.text_input("Hidden Transaction", default_hidden)

st.sidebar.markdown("---")
n_strips = st.sidebar.slider("Payload Strips", 3, 10, 6)
n_decoys = st.sidebar.slider("Decoy Frames", 0, 20, 6)
block_size = st.sidebar.slider("Scramble Block Size", 10, 40, 20, step=5)
session_key = st.sidebar.text_input("Session Key", "chrono_2025_sec")
show_debug_marks = st.sidebar.checkbox("Show Debug Labels", True)

generate_clicked = st.sidebar.button("🚀 Generate Demo", use_container_width=True)

if generate_clicked or "generated_once" not in st.session_state:
    with st.spinner("Generating Chrono-Auth demo..."):
        generate_assets(
            browser_text=browser_text,
            hidden_text=hidden_text,
            simulate_attack=attack_mode,
            n_strips=n_strips,
            n_decoys=n_decoys,
            session_key=session_key,
            show_debug_marks=show_debug_marks,
            block_size=block_size
        )
        st.session_state["generated_once"] = True

metadata, timemap = load_current_data()
if metadata is None:
    st.error("No generated assets found.")
    st.stop()

bank_ui = safe_image(os.path.join(OUTPUT_DIR, "bank_ui.png"))
hidden_message = safe_image(os.path.join(OUTPUT_DIR, "hidden_message.png"))
scrambled_message = safe_image(os.path.join(OUTPUT_DIR, "scrambled_message.png"))
recovered_correct = safe_image(os.path.join(OUTPUT_DIR, "recovered_correct.png"))
recovered_wrong_frames = safe_image(os.path.join(OUTPUT_DIR, "recovered_wrong_frames.png"))
recovered_wrong_key = safe_image(os.path.join(OUTPUT_DIR, "recovered_wrong_key.png"))
stream_gif_path = os.path.join(OUTPUT_DIR, "stream.gif")

frame_files = sorted([f for f in os.listdir(FRAMES_DIR) if f.lower().endswith(".png")])

st.title("🔐 Chrono-Auth")
st.caption("Time-Interleaved Visual Cryptography for Transaction Verification")

st.markdown('<div class="section-title">1. UI vs Real Transaction</div>', unsafe_allow_html=True)
st.divider()

c1, c2 = st.columns(2)
with c1:
    st.subheader("💻 Compromised Browser View")
    if bank_ui:
        st.image(bank_ui, width='stretch')

with c2:
    st.subheader("🔒 Chrono-Auth Hidden Payload")
    if hidden_message:
        st.image(hidden_message, width='stretch')

if metadata["simulate_attack"]:
    st.error("Attack mode active: browser transaction differs from the hidden verified transaction.")
else:
    st.success("Normal mode: browser and hidden transaction match.")

st.markdown('<div class="section-title">2. Scrambling Stage</div>', unsafe_allow_html=True)
st.divider()

c3, c4 = st.columns(2)
with c3:
    st.subheader("Original Hidden Message")
    if hidden_message:
        st.image(hidden_message, width='stretch')

with c4:
    st.subheader("Globally Scrambled Message")
    if scrambled_message:
        st.image(scrambled_message, width='stretch')

st.markdown('<div class="section-title">3. Optical Stream</div>', unsafe_allow_html=True)
st.divider()

if os.path.exists(stream_gif_path):
    st.image(stream_gif_path, caption="Animated Chrono-Auth stream", width='stretch')
else:
    st.warning("stream.gif not found. Regenerate demo.")

st.markdown('<div class="section-title">4. Reconstruction Results</div>', unsafe_allow_html=True)
st.divider()

r1, r2, r3 = st.columns(3)
with r1:
    st.subheader("✅ Correct")
    if recovered_correct:
        st.image(recovered_correct, width='stretch')
    st.caption("Correct frames + correct key")

with r2:
    st.subheader("❌ Wrong Frames")
    if recovered_wrong_frames:
        st.image(recovered_wrong_frames, width='stretch')
    st.caption("Actual output from incorrect frame selection")

with r3:
    st.subheader("❌ Wrong Key")
    if recovered_wrong_key:
        st.image(recovered_wrong_key, width='stretch')
    st.caption("Actual output from incorrect session key")

st.markdown('<div class="section-title">5. Stream Inspection</div>', unsafe_allow_html=True)
st.divider()

with st.expander("Inspect generated frames", expanded=False):
    if frame_files:
        selected_frame = st.selectbox("Select frame", frame_files)
        st.image(load_image(os.path.join(FRAMES_DIR, selected_frame)), width='stretch')

with st.expander("Verifier metadata", expanded=False):
    st.dataframe(pd.DataFrame(timemap), width='stretch')
    st.caption(f"Session ID: {metadata['session_id']}")
    st.caption(f"Payload Frames: {metadata['payload_frames']} | Decoy Frames: {metadata['decoy_frames']} | Block Size: {metadata['block_size']}")