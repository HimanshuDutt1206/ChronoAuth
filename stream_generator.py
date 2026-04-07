import numpy as np
import json
import random
from PIL import Image
from crypto_engine import apply_diffusion, remove_diffusion

# Import our previous engines
from crypto_engine import text_to_tile_grid, scramble_image, unscramble_image, tile_grid_to_text
from temporal_pipeline import encrypt_pipeline, split_into_strips

# ==========================================
# 1. DECOY FRAME GENERATION
# ==========================================
# A Decoy frame must look mathematically identical (statistically uniform)
# to a Payload frame so an attacker cannot tell them apart.

def generate_noise_frame(shape=(256, 256)):
    """Generates a pure random noise frame."""
    return np.random.choice([0, 255], size=shape).astype(np.uint8)

# ==========================================
# 2. STREAM ASSEMBLY
# ==========================================

def create_optical_stream(transaction_text: str, session_key: str, total_frames: int = 60, num_strips: int = 16):
    """Generates the full time-interleaved optical stream (GIF) and Timemap."""
    
    # --- STEP 1: SPATIAL ENCRYPTION ---
    print("1. Tile-encoding and Scrambling Payload...")
    grid = text_to_tile_grid(transaction_text)
    diffused_grid = apply_diffusion(grid)
    
    scrambled_grid, scramble_permutation = scramble_image(diffused_grid, session_key)
    
    # --- STEP 2: TEMPORAL ENCRYPTION ---
    print("2. Slicing and Chaining Temporal Strips...")
    encrypted_strips = encrypt_pipeline(scrambled_grid, session_key, num_strips)
    
    # --- STEP 3: ALLOCATING PAYLOAD TO FRAMES ---
    print("3. Generating Decoys and Interleaving...")
    # We have `total_frames` (e.g., 60) and `num_strips` (e.g., 16 payload pieces).
    # We must randomly select 16 frame indices to hold our payload.
    payload_frame_indices = sorted(random.sample(range(total_frames), num_strips))
    
    timemap = {}
    frames = []
    
    strip_idx = 0
    strip_h = 256 // num_strips
    
    for frame_id in range(total_frames):
        # Create a base noise frame
        frame = generate_noise_frame()
        
        if frame_id in payload_frame_indices:
            # THIS IS A REAL PAYLOAD FRAME
            # Insert the encrypted strip into its correct spatial position
            y_start = strip_idx * strip_h
            y_end = (strip_idx + 1) * strip_h
            
            # Embed the secret strip into the noise frame
            frame[y_start:y_end, :] = encrypted_strips[strip_idx]
            
            # Record it in the Timemap (User's phone needs this!)
            timemap[frame_id] = {
                "type": "PAYLOAD",
                "strip_index": strip_idx,
                "y_start": y_start,
                "y_end": y_end
            }
            strip_idx += 1
            
        else:
            # THIS IS A DECOY FRAME (Do nothing, just noise)
            timemap[frame_id] = {
                "type": "DECOY"
            }
            
        # Convert numpy array to PIL Image for GIF saving
        pil_img = Image.fromarray(frame)
        frames.append(pil_img)
        
    # --- STEP 4: SAVE OUTPUTS ---
    print("4. Saving stream.gif and timemap.json...")
    frames[0].save('stream.gif', save_all=True, append_images=frames[1:], duration=100, loop=0)
    
    with open('timemap.json', 'w') as f:
        json.dump(timemap, f, indent=4)
        
    print(f"\nSUCCESS! Created stream.gif ({total_frames} frames).")
    return scramble_permutation

# ==========================================
# QUICK TEST (Run this file to build the GIF!)
# ==========================================
if __name__ == "__main__":
    transaction = "CONFIRM: TRANSFER $50,000 TO ACCOUNT 1234-5678"
    session_key = "ChronoKey2024"
    
    print("--- CHRONO-AUTH: PHASE 3 TEST ---")
    
    # This will generate stream.gif and timemap.json in your folder
    create_optical_stream(transaction, session_key, total_frames=60, num_strips=16)
    
    print("\nGo to your folder and open 'stream.gif'. It should look like pure flickering noise.")
    print("Open 'timemap.json'. You will see exactly which frames contain the hidden transaction.")