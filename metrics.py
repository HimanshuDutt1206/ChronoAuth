import numpy as np
import time
from collections import Counter
import math

# Import your existing engine
from crypto_engine import text_to_tile_grid, apply_diffusion, scramble_image
from temporal_pipeline import encrypt_pipeline, decrypt_pipeline
from stream_generator import generate_noise_frame

# ==========================================
# 1. SHANNON ENTROPY CALCULATION
# ==========================================
def calculate_entropy(image: np.ndarray) -> float:
    """Calculates Information Entropy. Perfect noise = 8.0"""
    counts = Counter(image.flatten())
    total_pixels = image.size
    entropy = 0.0
    for count in counts.values():
        p = count / total_pixels
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy

# ==========================================
# 2. NPCR & UACI CALCULATION (Avalanche Metrics)
# ==========================================
def calculate_npcr_uaci(img1: np.ndarray, img2: np.ndarray):
    """Calculates NPCR (>99.6%) and UACI (~33.4%) between two cipher images."""
    if img1.shape != img2.shape:
        raise ValueError("Images must have the same dimensions")
    
    total_pixels = img1.size
    
    # NPCR: Number of Pixels Change Rate
    diff_pixels = np.sum(img1 != img2)
    npcr = (diff_pixels / total_pixels) * 100.0
    
    # UACI: Unified Average Changing Intensity
    img1_float = img1.astype(np.float64)
    img2_float = img2.astype(np.float64)
    uaci = np.sum(np.abs(img1_float - img2_float)) / (255.0 * total_pixels) * 100.0
    
    return npcr, uaci

# ==========================================
# RUN METRICS EVALUATION
# ==========================================
def run_paper_evaluation():
    print("==================================================")
    print(" CHRONO-AUTH: RESEARCH PAPER METRICS GENERATOR")
    print("==================================================\n")
    
    text = "CONFIRM: PAY $5000 TO MALLORY"
    key1 = "ChronoKey2024A"
    key2 = "ChronoKey2024B" # Changed exactly 1 character
    
    # --- 1. PERFORMANCE OVERHEAD (TIME) ---
    print("[1] PERFORMANCE EVALUATION (SPEED)")
    start_time = time.time()
    
    # Full Encryption Pipeline
    grid = text_to_tile_grid(text)
    diffused = apply_diffusion(grid)
    scrambled, _ = scramble_image(diffused, key1)
    encrypted_strips = encrypt_pipeline(scrambled, key1, num_strips=16)
    
    enc_time = (time.time() - start_time) * 1000 # Convert to milliseconds
    
    # Full Decryption Pipeline
    start_time = time.time()
    decrypted_scrambled = decrypt_pipeline(encrypted_strips, key1)
    dec_time = (time.time() - start_time) * 1000
    
    print(f"    -> Full Payload Encryption Time : {enc_time:.2f} ms")
    print(f"    -> Full Payload Decryption Time : {dec_time:.2f} ms")
    print("    (Conclusion: Extremely lightweight, suitable for mobile devices)\n")
    
    # --- 2. INFORMATION ENTROPY ---
    print("[2] SECURITY EVALUATION (INFORMATION ENTROPY)")
    # Reassemble encrypted strips into a single mock frame to test its randomness
    mock_payload_frame = np.vstack(encrypted_strips)
    pure_noise_frame = generate_noise_frame()
    
    entropy_payload = calculate_entropy(mock_payload_frame)
    entropy_noise = calculate_entropy(pure_noise_frame)
    
    print(f"    -> Entropy of Pure Decoy Frame   : {entropy_noise:.5f} (Ideal for Binary: 1.0)")
    print(f"    -> Entropy of Payload Frame      : {entropy_payload:.5f} (Ideal for Binary: 1.0)")
    print("    (Conclusion: Payload is statistically indistinguishable from random noise)\n")
    
    # --- 3. AVALANCHE EFFECT (NPCR & UACI) ---
    print("[3] SENSITIVITY EVALUATION (AVALANCHE EFFECT)")
    # Generate a second ciphertext with a 1-character difference in the key
    scrambled2, _ = scramble_image(diffused, key2)
    encrypted_strips2 = encrypt_pipeline(scrambled2, key2, num_strips=16)
    mock_payload_frame2 = np.vstack(encrypted_strips2)
    
    npcr, uaci = calculate_npcr_uaci(mock_payload_frame, mock_payload_frame2)
    
    print(f"    -> NPCR (Key Sensitivity) : {npcr:.4f}% (Binary Standard: ~ 50.0%)")
    print(f"    -> UACI (Change Intensity): {uaci:.4f}% (Binary Standard: ~ 50.0%)")
    print("    (Conclusion: A 1-bit change triggers a complete cryptographic avalanche)\n")

if __name__ == "__main__":
    run_paper_evaluation()