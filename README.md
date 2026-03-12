# Chrono-Auth

A Streamlit-based research prototype for **time-interleaved visual cryptography** for transaction verification.

---

## Overview

Chrono-Auth is a proof-of-concept system that explores how transaction verification data can be hidden across a **dynamic noisy visual stream** instead of a single static image.

The central idea is that a browser or client interface may be manipulated by malware and therefore cannot always be trusted to display the real transaction being approved. Instead of relying only on what the browser shows, Chrono-Auth creates a second visual verification channel in which the real transaction data is fragmented, encrypted, and distributed across time.

This project is implemented as a **final-year academic prototype** and is intended to demonstrate the methodology, architecture, and research potential of temporal visual verification.

---

## Problem Statement

In online banking and digital transaction systems, malware such as **Man-in-the-Browser (MitB)** can silently alter:

* transaction amount
* recipient account
* destination identity
* payment details

while still showing a harmless-looking transaction summary to the user.

Traditional security methods like OTPs or browser confirmations may not always guarantee that the **exact transaction semantics** being approved are independently verified under hostile client conditions.

Chrono-Auth addresses this by shifting verification from:

* a **static visible object**

to

* a **time-interleaved hidden visual stream**

---

## Core Idea

Instead of displaying the verification payload as one static image, Chrono-Auth:

1. converts the hidden transaction into a binary visual form
2. scrambles it using a session-dependent transformation
3. splits it into temporal strips
4. encrypts those strips using chaos-inspired masking
5. mixes them with decoy frames
6. reconstructs the message only when the correct frame set and session key are used

The output stream appears as noisy random frames, but the correct reconstruction process can recover the original transaction.

---

## Methodology

The system works in multiple stages:

### 1. Transaction Encoding

The real transaction confirmation text is converted into a binary image.

Example:

```
CONFIRM: PAY $5000 TO MALLORY
```

This image becomes the hidden verification payload.

---

### 2. Session-Key-Based Scrambling

Before temporal splitting, the payload is globally scrambled using a session-dependent block permutation.

This means the hidden message is no longer visually readable even before encryption. The data is rearranged spatially, so no local region directly corresponds to readable plaintext.

---

### 3. Temporal Fragmentation

The scrambled image is split into multiple horizontal strips.

Each strip is treated as one temporal fragment of the final secret.

This moves the security model from a single spatial image to a sequence of frames across time.

---

### 4. Chaos-Inspired Encryption

Each strip is masked using a deterministic pseudo-random binary pattern generated from a session key.

This introduces a chaos-based visual masking layer, so every payload fragment appears noisy and unintelligible on its own.

---

### 5. Decoy Interleaving

In addition to valid payload frames, the system generates decoy frames containing only noise.

The final stream is made of both:

* valid payload frames
* decoy frames

These are shuffled into one mixed sequence, making it difficult to identify which frames actually matter.

---

### 6. Stream Generation

The mixed payload and decoy frames are exported as:

* individual frame images
* an animated GIF stream

To a normal observer, the stream appears as random flickering noise.

---

### 7. Reconstruction

The verifier uses:

* the correct session key
* the correct frame-selection map
* the correct reconstruction logic

to recover the hidden transaction.

The system also demonstrates failure cases:

* wrong frame set
* wrong session key

Both lead to corrupted or unreadable outputs.

---

## Features

* Fake banking UI generation
* Hidden transaction image generation
* Global block scrambling of hidden payload
* Temporal splitting into multiple payload strips
* Decoy frame injection
* Noisy animated stream generation
* Correct reconstruction output
* Wrong-frame reconstruction output
* Wrong-key reconstruction output
* Streamlit dashboard for visual demonstration

---

## Files

### `generate_demo.py`

Generates all required demo assets:

* fake bank UI
* hidden message image
* scrambled payload
* payload and decoy frames
* animated stream GIF
* metadata and timemap
* reconstruction outputs

---

### `app.py`

Streamlit app that visualizes:

* browser transaction view
* hidden Chrono-Auth payload
* scrambling stage
* animated optical stream
* correct and incorrect reconstructions
* frame inspection
* verifier metadata

---

## Installation

Create and activate a virtual environment if needed:

```
python -m venv .venv
```

Windows PowerShell:

```
.\.venv\Scripts\Activate.ps1
```

Install all required packages:

```
python -m pip install streamlit pandas pillow opencv-python numpy
```

---

## How to Run

### 1. Generate all demo assets

```
python generate_demo.py
```

This creates the required files inside the `output/` folder.

---

### 2. Launch the Streamlit app

```
streamlit run app.py
```

---

## Output Structure

After generation, the project creates a structure like:

```
output/
│
├── bank_ui.png
├── hidden_message.png
├── scrambled_message.png
├── recovered_correct.png
├── recovered_wrong_frames.png
├── recovered_wrong_key.png
├── stream.gif
│
├── frames/
│   └── generated payload and decoy frame images
│
└── metadata/
    ├── metadata.json
    └── timemap.json
```

---

## Demo Flow

The Streamlit app demonstrates the system in stages:

### 1. Browser View vs Hidden Payload

The browser shows one transaction, while Chrono-Auth encodes a hidden verification payload.

---

### 2. Scrambling Stage

The hidden payload is globally scrambled before being split and transmitted.

---

### 3. Optical Stream

A noisy animated stream of payload and decoy frames is shown.

---

### 4. Reconstruction Results

The app compares:

* correct reconstruction
* wrong-frame reconstruction
* wrong-key reconstruction

---

### 5. Frame Inspection

Individual frames can be viewed to understand how the protocol emits data over time.

---

## Why This Project Matters

Chrono-Auth explores a security model where trust is not placed entirely in the browser or client UI.

Its main contribution is the idea of **temporal visual verification**, where:

* the secret is distributed across time
* visibility alone is not enough for interpretation
* reconstruction depends on synchronization and session knowledge

This makes it a useful research prototype for studying:

* transaction integrity under client compromise
* visual cryptography extensions
* time-based hiding mechanisms
* optical-style secondary verification channels

---

## Technical Stack

This prototype uses:

* Python
* NumPy for binary image operations
* OpenCV for frame generation and image saving
* Pillow for text rendering
* Streamlit for the dashboard UI
* Pandas for metadata display

---

## Limitations

This is a prototype, not a production-ready banking system.

* The app currently runs as a single-device simulation.
* The current implementation is intended to demonstrate the concept and methodology rather than provide formal cryptographic guarantees.
* It is best understood as a research and educational proof of concept.

---

## Author

Final project prototype by **[Your Name]**

---

## License

You may add a license such as **MIT** if desired.
