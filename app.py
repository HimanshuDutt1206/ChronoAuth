import streamlit as st
import numpy as np
import json
from PIL import Image
import os
from crypto_engine import remove_diffusion

# Import our custom cryptographic modules
from crypto_engine import text_to_tile_grid, scramble_image, unscramble_image, tile_grid_to_text
from temporal_pipeline import decrypt_pipeline
from stream_generator import create_optical_stream

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Chrono-Auth Demo", layout="wide", initial_sidebar_state="expanded")

st.title("⏱️ Chrono-Auth: Time-Interleaved Visual Cryptography")
st.markdown("""
**Academic Prototype for Transaction Integrity Verification**  
*Mitigating Man-in-the-Browser (MitB) attacks by shifting visual verification from spatial artifacts (QR codes) to synchronized temporal streams.*
""")

# ==========================================
# SIDEBAR: SETUP & GENERATION
# ==========================================
st.sidebar.header("1. Transaction Setup")
fake_transaction = st.sidebar.text_input("Fake Browser UI Shows:", "TRANSFER: $50 TO ALICE")
real_transaction = st.sidebar.text_input("Hidden Verification Payload:", "CONFIRM: PAY $5000 TO MALLORY")
session_key = st.sidebar.text_input("Session Key (Phone & Server share this):", "ChronoKey2024")

if st.sidebar.button("Generate Optical Stream"):
    with st.spinner("Generating Tile Grid, Scrambling, and Chaining Temporal Stream..."):
        # Generate the GIF and JSON using our Phase 3 code
        create_optical_stream(real_transaction, session_key, total_frames=60, num_strips=16)
    st.sidebar.success("stream.gif and timemap.json generated successfully!")

# ==========================================
# HELPER: DECRYPTION WRAPPER
# ==========================================
def extract_and_decrypt(stream_path, timemap_path, key, drop_frame=False):
    """Simulates the smartphone scanning the GIF and decrypting it."""
    try:
        # 1. Load the Timemap
        with open(timemap_path, 'r') as f:
            timemap = json.load(f)
            
        # 2. Extract frames from GIF
        gif = Image.open(stream_path)
        frames = []
        for i in range(gif.n_frames):
            gif.seek(i)
            frames.append(np.array(gif.convert('L'))) # Convert to Grayscale numpy array
            
        # 3. Filter Decoys and Extract Payload Strips
        extracted_strips = []
        payload_frames = [int(fid) for fid, data in timemap.items() if data['type'] == 'PAYLOAD']
        payload_frames.sort()
        
        for i, frame_id in enumerate(payload_frames):
            data = timemap[str(frame_id)]
            y1, y2 = data['y_start'], data['y_end']
            
            # SIMULATE DROPPED FRAME ATTACK: Replace strip #8 with pure noise
            if drop_frame and i == 8:
                noise_strip = np.random.choice([0, 255], size=(y2-y1, 256)).astype(np.uint8)
                extracted_strips.append(noise_strip)
            else:
                strip = frames[frame_id][y1:y2, :]
                extracted_strips.append(strip)
                
        # 4. Temporal Decryption (Reverse Chaos & Unmix)
        decrypted_scrambled_grid = decrypt_pipeline(extracted_strips, key)
        
        # 5. Spatial Unscrambling
        # To unscramble, we need the exact permutation. We get it by scrambling a dummy image with the key.
        dummy_image = np.zeros((256, 256), dtype=np.uint8)
        _, permutation = scramble_image(dummy_image, key)
        final_grid = unscramble_image(decrypted_scrambled_grid, permutation)
        final_grid = remove_diffusion(final_grid)
        # 6. Decode Tiles to Text
        recovered_text = tile_grid_to_text(final_grid)
        return recovered_text, final_grid
        
    except Exception as e:
        return f"ERROR: {str(e)}", None

# ==========================================
# MAIN DASHBOARD UI
# ==========================================
col1, col2 = st.columns(2)

with col1:
    st.header("🖥️ The Compromised Browser")
    st.error("**What the user sees (Manipulated by Malware):**")
    st.info(f"💸 **{fake_transaction}**")
    
    st.markdown("---")
    st.subheader("Optical Transmission Stream")
    st.markdown("This flickering box is what the browser displays. It contains decoy frames and payload frames mixed together.")
    
    if os.path.exists('stream.gif'):
        st.image('stream.gif', caption="Synchronized Temporal Stream (Contains hidden payload)", use_container_width=True)
    else:
        st.warning("👈 Please click 'Generate Optical Stream' in the sidebar.")

with col2:
    st.header("📱 The Smartphone Verifier")
    st.success("**What the secure app reconstructs:**")
    
    # INTERACTIVE DEMO BUTTONS
    st.markdown("### Simulation Controls")
    
    if st.button("✅ Scan & Verify (Correct Key & Sync)"):
        text, grid = extract_and_decrypt('stream.gif', 'timemap.json', session_key, drop_frame=False)
        st.image(grid, caption="Recovered Tile Grid (Before decoding)", width=200)
        st.success(f"**Verified Transaction Intent:**\n\n{text}")
        if text == real_transaction:
            st.balloons()

    if st.button("❌ Attack: Wrong Session Key"):
        wrong_key = session_key + "X" # Change key slightly
        text, grid = extract_and_decrypt('stream.gif', 'timemap.json', wrong_key, drop_frame=False)
        st.image(grid, caption="Corrupted Tile Grid", width=200)
        st.error(f"**Reconstructed Text:**\n\n{text[:60]}... (Garbage)")
        st.caption("Proof of Key Sensitivity (Avalanche Effect).")

    if st.button("⚠️ Attack: Dropped Frame / Tampering"):
        text, grid = extract_and_decrypt('stream.gif', 'timemap.json', session_key, drop_frame=True)
        st.image(grid, caption="Cascade Failure Tile Grid", width=200)
        st.error(f"**Reconstructed Text:**\n\n{text[:60]}... (Garbage)")
        st.caption("Proof of Stateful Chaining. Missing 1 out of 60 frames destroys the entire reconstruction, preventing partial leakage.")