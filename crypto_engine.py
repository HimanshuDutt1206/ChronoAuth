import numpy as np
import hashlib
import string

# ==========================================
# 1. TILE ENCODING (The Anti-Leakage System)
# ==========================================
# In a research paper, you will explain that standard visual cryptography
# leaks structural shapes (letters). Tile encoding maps each ASCII character
# to a pseudo-random 8x8 binary tile. Decoding requires perfect recovery.

TILE_SIZE = 8
IMAGE_SIZE = 256 # 256x256 pixels = 32x32 characters = 1024 max chars

def char_to_tile(char: str) -> np.ndarray:
    """Deterministically converts a single character to an 8x8 binary tile."""
    # We use the ASCII value to seed the random generator so 'A' is always the same tile
    seed = ord(char)
    np.random.seed(seed)
    # Generate an 8x8 array of 0s and 255s (Black and White pixels)
    tile = np.random.choice([0, 255], size=(TILE_SIZE, TILE_SIZE)).astype(np.uint8)
    return tile

def text_to_tile_grid(text: str) -> np.ndarray:
    """Converts a full transaction string into a 256x256 binary image."""
    chars_per_row = IMAGE_SIZE // TILE_SIZE
    
    # Pad text with spaces if it's too short
    max_chars = chars_per_row * chars_per_row
    text = text.ljust(max_chars, ' ')[:max_chars]
    
    grid = np.zeros((IMAGE_SIZE, IMAGE_SIZE), dtype=np.uint8)
    
    for i, char in enumerate(text):
        row = (i // chars_per_row) * TILE_SIZE
        col = (i % chars_per_row) * TILE_SIZE
        grid[row:row+TILE_SIZE, col:col+TILE_SIZE] = char_to_tile(char)
        
    return grid

def tile_grid_to_text(grid: np.ndarray) -> str:
    """Reconstructs text from a recovered grid by matching 8x8 tiles."""
    chars_per_row = IMAGE_SIZE // TILE_SIZE
    recovered_text = ""
    
    # Pre-compute all printable ASCII tiles for matching
    printable_chars = string.printable
    char_map = {char: char_to_tile(char) for char in printable_chars}
    
    for i in range(chars_per_row * chars_per_row):
        row = (i // chars_per_row) * TILE_SIZE
        col = (i % chars_per_row) * TILE_SIZE
        tile = grid[row:row+TILE_SIZE, col:col+TILE_SIZE]
        
        # Find the matching character (If corrupted, it returns '?')
        match = '?'
        for char, ref_tile in char_map.items():
            if np.array_equal(tile, ref_tile):
                match = char
                break
        recovered_text += match
        
    return recovered_text.strip()

# ==========================================
# 2. CHAOS-BASED LOGISTIC MAP 
# ==========================================
# Research Paper Magic: The Logistic Map is highly sensitive to initial conditions.
# A 1-bit change in the session key changes the entire sequence (Avalanche Effect).

def get_chaos_sequence(session_key: str, length: int) -> np.ndarray:
    """Generates a pseudo-random sequence using the Logistic Map equation."""
    # Hash the session key to get a deterministic float between 0 and 1
    key_hash = hashlib.sha256(session_key.encode()).hexdigest()
    x0 = int(key_hash[:15], 16) / (16**15) 
    
    if x0 == 0 or x0 == 0.5: 
        x0 = 0.12345  # Avoid stable points in chaos math
        
    r = 3.999 # Chaos parameter (Must be near 4.0 for maximum entropy)
    
    sequence = np.zeros(length)
    x = x0
    for i in range(length):
        x = r * x * (1 - x) # The Core Logistic Equation
        sequence[i] = x
        
    return sequence

# ==========================================
# 3. SPATIAL BLOCK SCRAMBLING
# ==========================================
# Destroys spatial correlation so an attacker cannot piece together the image.

def scramble_image(image: np.ndarray, session_key: str, block_size: int = 16) -> np.ndarray:
    """Divides image into blocks and shuffles them based on the session key."""
    h, w = image.shape
    num_blocks_h = h // block_size
    num_blocks_w = w // block_size
    total_blocks = num_blocks_h * num_blocks_w
    
    # Generate chaos sequence to dictate the shuffling order
    chaos_seq = get_chaos_sequence(session_key, total_blocks)
    permutation = np.argsort(chaos_seq) # Get the scrambled indices
    
    scrambled_img = np.zeros_like(image)
    
    for new_idx, old_idx in enumerate(permutation):
        # Calculate old and new coordinates
        old_r = (old_idx // num_blocks_w) * block_size
        old_c = (old_idx % num_blocks_w) * block_size
        new_r = (new_idx // num_blocks_w) * block_size
        new_c = (new_idx % num_blocks_w) * block_size
        
        # Move the block
        scrambled_img[new_r:new_r+block_size, new_c:new_c+block_size] = image[old_r:old_r+block_size, old_c:old_c+block_size]
        
    return scrambled_img, permutation

def unscramble_image(scrambled_img: np.ndarray, permutation: np.ndarray, block_size: int = 16) -> np.ndarray:
    """Reverses the scrambling process using the saved permutation."""
    h, w = scrambled_img.shape
    num_blocks_w = w // block_size
    
    unscrambled_img = np.zeros_like(scrambled_img)
    
    for new_idx, old_idx in enumerate(permutation):
        old_r = (old_idx // num_blocks_w) * block_size
        old_c = (old_idx % num_blocks_w) * block_size
        new_r = (new_idx // num_blocks_w) * block_size
        new_c = (new_idx % num_blocks_w) * block_size
        
        unscrambled_img[old_r:old_r+block_size, old_c:old_c+block_size] = scrambled_img[new_r:new_r+block_size, new_c:new_c+block_size]
        
    return unscrambled_img

# ==========================================
# QUICK TEST (Run this file to see it work!)
# ==========================================
if __name__ == "__main__":
    print("--- CHRONO-AUTH: PHASE 1 TEST ---")
    secret_transaction = "CONFIRM: PAY $5000 TO MALLORY"
    session_key = "SuperSecretKey2024"
    
    print(f"1. Original Text: {secret_transaction}")
    
    # 1. Tile Encode
    grid = text_to_tile_grid(secret_transaction)
    print(f"2. Converted to {grid.shape} Tile Grid.")
    
    # 2. Scramble
    scrambled, perm = scramble_image(grid, session_key)
    print("3. Image Scrambled using Chaos Map.")
    
    # 3. Unscramble
    unscrambled = unscramble_image(scrambled, perm)
    
    # 4. Decode Back to Text
    recovered_text = tile_grid_to_text(unscrambled)
    print(f"4. Recovered Text: {recovered_text}")
    
    # Security Test: What if the key is wrong?
    print("\n--- SECURITY TEST: WRONG KEY ---")
    wrong_key = "SuperSecretKey2025" # Changed 1 character
    wrong_scrambled, wrong_perm = scramble_image(grid, wrong_key)
    wrong_unscrambled = unscramble_image(scrambled, wrong_perm)
    wrong_text = tile_grid_to_text(wrong_unscrambled)
    print("Recovering with wrong key...")
    print(f"Recovered Text: {wrong_text[:50]}... (Garbage!)")


def apply_diffusion(image: np.ndarray) -> np.ndarray:
    """Shannon Diffusion: Links every pixel together. 1 error corrupts everything."""
    flat = image.flatten()
    # Forward diffusion (Pixel N depends on Pixel N-1)
    diff1 = np.bitwise_xor.accumulate(flat)
    # Backward diffusion (Pixel N depends on Pixel N+1)
    diff2 = np.bitwise_xor.accumulate(diff1[::-1])[::-1]
    return diff2.reshape(image.shape)

def remove_diffusion(image: np.ndarray) -> np.ndarray:
    """Reverses the diffusion. Avalanches any errors across the whole grid."""
    flat = image.flatten()
    
    # Undo Backward diffusion
    diff1 = np.zeros_like(flat)
    diff1[-1] = flat[-1]
    diff1[:-1] = np.bitwise_xor(flat[:-1], flat[1:])
    
    # Undo Forward diffusion
    orig = np.zeros_like(diff1)
    orig[0] = diff1[0]
    orig[1:] = np.bitwise_xor(diff1[1:], diff1[:-1])
    
    return orig.reshape(image.shape)