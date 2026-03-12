import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import json
import random
import hashlib
from datetime import datetime

BASE_OUTPUT_DIR = "output"
FRAMES_DIR = os.path.join(BASE_OUTPUT_DIR, "frames")
METADATA_DIR = os.path.join(BASE_OUTPUT_DIR, "metadata")

os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)
os.makedirs(FRAMES_DIR, exist_ok=True)
os.makedirs(METADATA_DIR, exist_ok=True)


# =========================================
# BASIC UTILITIES
# =========================================

def xor_img(a, b):
    return np.bitwise_xor(a, b)


def save_image(path, img):
    cv2.imwrite(path, img)


def clear_old_files():
    for folder in [FRAMES_DIR, METADATA_DIR]:
        os.makedirs(folder, exist_ok=True)
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

    for file in os.listdir(BASE_OUTPUT_DIR):
        path = os.path.join(BASE_OUTPUT_DIR, file)
        if os.path.isfile(path):
            os.remove(path)


# =========================================
# IMAGE GENERATION
# =========================================

def create_fake_bank_ui(text, width=1000, height=500):
    img = np.ones((height, width, 3), dtype=np.uint8) * 245

    cv2.rectangle(img, (0, 0), (width, 80), (44, 62, 108), -1)
    cv2.putText(img, "SecureNet Banking Portal", (35, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)

    cv2.rectangle(img, (70, 120), (930, 320), (255, 255, 255), -1)
    cv2.rectangle(img, (70, 120), (930, 320), (210, 210, 210), 2)

    cv2.putText(img, "Transaction Summary", (110, 165),
                cv2.FONT_HERSHEY_SIMPLEX, 0.95, (45, 45, 45), 2)

    cv2.putText(img, text, (110, 235),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (20, 20, 20), 2)

    cv2.rectangle(img, (390, 370), (630, 445), (46, 163, 86), -1)
    cv2.putText(img, "APPROVE", (445, 418),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

    cv2.putText(img, "Chrono-Auth secure verification required", (235, 485),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (85, 85, 85), 2)

    return img


def create_message_image(text, width=900, height=320):
    img = Image.new("L", (width, height), color=255)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 42)
    except:
        font = ImageFont.load_default()

    draw.text((40, 120), text, fill=0, font=font)

    arr = np.array(img)
    binary = np.where(arr < 128, 0, 255).astype(np.uint8)
    return binary


# =========================================
# SCRAMBLING
# =========================================

def seed_to_int(session_key):
    digest = hashlib.sha256(session_key.encode()).hexdigest()
    return int(digest[:16], 16)


def scramble_image_blocks(img, session_key, block_size=20):
    h, w = img.shape

    h_trim = (h // block_size) * block_size
    w_trim = (w // block_size) * block_size
    trimmed = img[:h_trim, :w_trim]

    rows = h_trim // block_size
    cols = w_trim // block_size
    total_blocks = rows * cols

    blocks = []
    for r in range(rows):
        for c in range(cols):
            y1 = r * block_size
            y2 = y1 + block_size
            x1 = c * block_size
            x2 = x1 + block_size
            blocks.append(trimmed[y1:y2, x1:x2].copy())

    perm = list(range(total_blocks))
    rng = random.Random(seed_to_int(session_key))
    rng.shuffle(perm)

    scrambled_blocks = [None] * total_blocks
    for original_idx, new_idx in enumerate(perm):
        scrambled_blocks[new_idx] = blocks[original_idx]

    scrambled = np.ones_like(trimmed) * 255
    idx = 0
    for r in range(rows):
        for c in range(cols):
            y1 = r * block_size
            y2 = y1 + block_size
            x1 = c * block_size
            x2 = x1 + block_size
            scrambled[y1:y2, x1:x2] = scrambled_blocks[idx]
            idx += 1

    final_img = img.copy()
    final_img[:h_trim, :w_trim] = scrambled

    meta = {
        "block_size": block_size,
        "rows": rows,
        "cols": cols,
        "perm": perm,
        "h_trim": h_trim,
        "w_trim": w_trim
    }
    return final_img, meta


def unscramble_image_blocks(scrambled_img, session_key, block_size=20):
    h, w = scrambled_img.shape

    h_trim = (h // block_size) * block_size
    w_trim = (w // block_size) * block_size
    trimmed = scrambled_img[:h_trim, :w_trim]

    rows = h_trim // block_size
    cols = w_trim // block_size
    total_blocks = rows * cols

    scrambled_blocks = []
    for r in range(rows):
        for c in range(cols):
            y1 = r * block_size
            y2 = y1 + block_size
            x1 = c * block_size
            x2 = x1 + block_size
            scrambled_blocks.append(trimmed[y1:y2, x1:x2].copy())

    perm = list(range(total_blocks))
    rng = random.Random(seed_to_int(session_key))
    rng.shuffle(perm)

    original_blocks = [None] * total_blocks
    for original_idx, new_idx in enumerate(perm):
        original_blocks[original_idx] = scrambled_blocks[new_idx]

    descrambled = np.ones_like(trimmed) * 255
    idx = 0
    for r in range(rows):
        for c in range(cols):
            y1 = r * block_size
            y2 = y1 + block_size
            x1 = c * block_size
            x2 = x1 + block_size
            descrambled[y1:y2, x1:x2] = original_blocks[idx]
            idx += 1

    final_img = scrambled_img.copy()
    final_img[:h_trim, :w_trim] = descrambled
    return final_img


# =========================================
# CHAOS FUNCTIONS
# =========================================

def derive_seed(session_key, strip_idx):
    seed_material = f"{session_key}_{strip_idx}".encode()
    digest = hashlib.sha256(seed_material).hexdigest()
    value = int(digest[:12], 16)
    x0 = 0.1 + (value % 800000) / 1000000.0
    return x0


def logistic_map_sequence(length, x0, r=3.99, warmup=100):
    x = x0
    for _ in range(warmup):
        x = r * x * (1 - x)

    seq = []
    for _ in range(length):
        x = r * x * (1 - x)
        seq.append(x)

    return np.array(seq, dtype=np.float32)


def chaotic_binary_mask(shape, session_key, strip_idx):
    h, w = shape
    total = h * w

    x0 = derive_seed(session_key, strip_idx)
    seq = logistic_map_sequence(total, x0)

    binary = np.where(seq > 0.5, 255, 0).astype(np.uint8)
    return binary.reshape((h, w))


# =========================================
# SPLITTING + ENCRYPTION
# =========================================

def split_into_strips(img, n_strips):
    h, w = img.shape
    strip_h = h // n_strips
    strips = []

    for i in range(n_strips):
        y1 = i * strip_h
        y2 = h if i == n_strips - 1 else (i + 1) * strip_h
        strips.append({
            "strip_idx": i,
            "y1": y1,
            "y2": y2,
            "data": img[y1:y2, :]
        })
    return strips


def encrypt_strip_with_chaos(strip_data, session_key, strip_idx):
    mask = chaotic_binary_mask(strip_data.shape, session_key, strip_idx)
    return xor_img(strip_data, mask)


def decrypt_strip_with_chaos(encrypted_strip, session_key, strip_idx):
    mask = chaotic_binary_mask(encrypted_strip.shape, session_key, strip_idx)
    return xor_img(encrypted_strip, mask)


# =========================================
# FRAME CREATION
# =========================================

def create_payload_frame(full_shape, strip_info, frame_id, session_key, show_debug_marks=True):
    raw_frame = np.random.randint(0, 2, full_shape, dtype=np.uint8) * 255

    y1 = strip_info["y1"]
    y2 = strip_info["y2"]
    strip_idx = strip_info["strip_idx"]

    encrypted_strip = encrypt_strip_with_chaos(strip_info["data"], session_key, strip_idx)
    raw_frame[y1:y2, :] = encrypted_strip

    display_frame = cv2.cvtColor(raw_frame.copy(), cv2.COLOR_GRAY2BGR)

    if show_debug_marks:
        cv2.putText(display_frame, f"PAYLOAD ID:{frame_id}", (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.rectangle(display_frame, (0, y1), (full_shape[1] - 1, y2 - 1), (0, 255, 0), 2)

    return raw_frame, display_frame


def create_decoy_frame(shape, frame_id, show_debug_marks=True):
    raw_frame = np.random.randint(0, 2, shape, dtype=np.uint8) * 255
    display_frame = cv2.cvtColor(raw_frame.copy(), cv2.COLOR_GRAY2BGR)

    if show_debug_marks:
        cv2.putText(display_frame, f"DECOY ID:{frame_id}", (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

    return raw_frame, display_frame


# =========================================
# STREAM GENERATION
# =========================================

def generate_stream(scrambled_message_img, session_key, n_strips, n_decoys, show_debug_marks=True):
    strips = split_into_strips(scrambled_message_img, n_strips)

    all_frames = []
    timemap = []

    frame_ids = list(range(1, n_strips + n_decoys + 1))
    random.shuffle(frame_ids)

    for strip in strips:
        frame_id = frame_ids.pop()

        raw_frame, display_frame = create_payload_frame(
            scrambled_message_img.shape, strip, frame_id, session_key, show_debug_marks
        )

        frame_info = {
            "frame_id": frame_id,
            "type": "payload",
            "strip_idx": strip["strip_idx"],
            "y1": strip["y1"],
            "y2": strip["y2"],
            "raw_frame": raw_frame,
            "display_frame": display_frame
        }
        all_frames.append(frame_info)

        timemap.append({
            "frame_id": frame_id,
            "strip_idx": strip["strip_idx"],
            "y1": strip["y1"],
            "y2": strip["y2"]
        })

    for _ in range(n_decoys):
        frame_id = frame_ids.pop()
        raw_frame, display_frame = create_decoy_frame(scrambled_message_img.shape, frame_id, show_debug_marks)

        frame_info = {
            "frame_id": frame_id,
            "type": "decoy",
            "strip_idx": None,
            "y1": None,
            "y2": None,
            "raw_frame": raw_frame,
            "display_frame": display_frame
        }
        all_frames.append(frame_info)

    random.shuffle(all_frames)
    return all_frames, timemap


# =========================================
# RECONSTRUCTION
# =========================================

def reconstruct_scrambled_image_from_timemap(all_frames, timemap, shape, session_key):
    reconstructed = np.ones(shape, dtype=np.uint8) * 255
    frame_lookup = {frame["frame_id"]: frame for frame in all_frames}

    for item in timemap:
        frame_id = item["frame_id"]
        strip_idx = item["strip_idx"]
        y1 = item["y1"]
        y2 = item["y2"]

        raw_frame = frame_lookup[frame_id]["raw_frame"]
        encrypted_strip = raw_frame[y1:y2, :]
        decrypted_strip = decrypt_strip_with_chaos(encrypted_strip, session_key, strip_idx)
        reconstructed[y1:y2, :] = decrypted_strip

    return reconstructed


def reconstruct_scrambled_image_from_selected_ids(all_frames, selected_frame_ids, shape, session_key, n_strips):
    reconstructed = np.random.randint(0, 2, shape, dtype=np.uint8) * 255
    frame_lookup = {frame["frame_id"]: frame for frame in all_frames}
    h = shape[0]
    strip_h = h // n_strips

    for i, frame_id in enumerate(selected_frame_ids[:n_strips]):
        if frame_id not in frame_lookup:
            continue

        y1 = i * strip_h
        y2 = h if i == n_strips - 1 else (i + 1) * strip_h
        encrypted_strip = frame_lookup[frame_id]["raw_frame"][y1:y2, :]
        decrypted_strip = decrypt_strip_with_chaos(encrypted_strip, session_key, i)
        reconstructed[y1:y2, :] = decrypted_strip

    return reconstructed


# =========================================
# GIF GENERATION
# =========================================

def save_stream_gif(frame_paths, output_gif_path, duration=400):
    pil_frames = []
    for path in frame_paths:
        img = Image.open(path).convert("RGB")
        pil_frames.append(img)

    if pil_frames:
        pil_frames[0].save(
            output_gif_path,
            save_all=True,
            append_images=pil_frames[1:],
            duration=duration,
            loop=0
        )


# =========================================
# MAIN GENERATION
# =========================================

def generate_assets(
    browser_text="Transfer: $50 to Alice",
    hidden_text="CONFIRM: PAY $5000 TO MALLORY",
    simulate_attack=True,
    n_strips=6,
    n_decoys=6,
    session_key="chrono_auth_session_2025",
    show_debug_marks=True,
    block_size=20
):
    clear_old_files()

    session_id = f"SESSION_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    bank_ui = create_fake_bank_ui(browser_text)
    save_image(os.path.join(BASE_OUTPUT_DIR, "bank_ui.png"), bank_ui)

    hidden_message = create_message_image(hidden_text)
    save_image(os.path.join(BASE_OUTPUT_DIR, "hidden_message.png"), hidden_message)

    scrambled_message, scramble_meta = scramble_image_blocks(
        hidden_message, session_key, block_size=block_size
    )
    save_image(os.path.join(BASE_OUTPUT_DIR, "scrambled_message.png"), scrambled_message)

    all_frames, timemap = generate_stream(
        scrambled_message, session_key, n_strips, n_decoys, show_debug_marks
    )

    frame_manifest = []
    saved_frame_paths = []

    for i, frame in enumerate(all_frames):
        filename = f"stream_order_{i+1:02d}_id_{frame['frame_id']}_{frame['type']}.png"
        filepath = os.path.join(FRAMES_DIR, filename)
        save_image(filepath, frame["display_frame"])
        saved_frame_paths.append(filepath)

        frame_manifest.append({
            "stream_order": i + 1,
            "frame_id": frame["frame_id"],
            "type": frame["type"],
            "strip_idx": frame["strip_idx"],
            "y1": frame["y1"],
            "y2": frame["y2"],
            "filename": filename
        })

    # Save animated stream gif
    save_stream_gif(saved_frame_paths, os.path.join(BASE_OUTPUT_DIR, "stream.gif"), duration=450)

    # Correct reconstruction
    recovered_scrambled = reconstruct_scrambled_image_from_timemap(
        all_frames, timemap, hidden_message.shape, session_key
    )
    recovered_correct = unscramble_image_blocks(
        recovered_scrambled, session_key, block_size=block_size
    )

    # Wrong frame selection
    wrong_selection_ids = [frame["frame_id"] for frame in all_frames[:n_strips]]
    recovered_wrong_scrambled = reconstruct_scrambled_image_from_selected_ids(
        all_frames, wrong_selection_ids, hidden_message.shape, session_key, n_strips
    )
    recovered_wrong_frames = unscramble_image_blocks(
        recovered_wrong_scrambled, session_key, block_size=block_size
    )

    # Wrong key reconstruction
    recovered_wrong_key_scrambled = reconstruct_scrambled_image_from_timemap(
        all_frames, timemap, hidden_message.shape, "wrong_session_key"
    )
    recovered_wrong_key = unscramble_image_blocks(
        recovered_wrong_key_scrambled, "wrong_session_key", block_size=block_size
    )

    save_image(os.path.join(BASE_OUTPUT_DIR, "recovered_correct.png"), recovered_correct)
    save_image(os.path.join(BASE_OUTPUT_DIR, "recovered_wrong_frames.png"), recovered_wrong_frames)
    save_image(os.path.join(BASE_OUTPUT_DIR, "recovered_wrong_key.png"), recovered_wrong_key)

    with open(os.path.join(METADATA_DIR, "timemap.json"), "w") as f:
        json.dump(timemap, f, indent=4)

    metadata = {
        "session_id": session_id,
        "session_key": session_key,
        "simulate_attack": simulate_attack,
        "browser_text": browser_text,
        "hidden_text": hidden_text,
        "n_strips": n_strips,
        "n_decoys": n_decoys,
        "total_frames": len(all_frames),
        "payload_frames": n_strips,
        "decoy_frames": n_decoys,
        "block_size": block_size,
        "frame_manifest": frame_manifest,
        "wrong_selection_ids": wrong_selection_ids,
        "scramble_meta": scramble_meta
    }

    with open(os.path.join(METADATA_DIR, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=4)

    print("Chrono-Auth demo assets generated successfully.")
    print("Session ID:", session_id)
    print("Attack mode:", simulate_attack)

    return metadata


if __name__ == "__main__":
    generate_assets()