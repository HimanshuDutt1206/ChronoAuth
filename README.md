# ⏱️ Chrono-Auth: Time-Interleaved Visual Cryptography

**An Academic Prototype for Transaction Integrity Verification against Man-in-the-Browser (MitB) Attacks.**

---

## 📖 Overview

Traditional Multi-Factor Authentication (OTP, SMS) authenticates the user, but fails to verify the **transaction intent**. In a Man-in-the-Browser (MitB) attack, malware can alter the transaction details (e.g., changing the recipient and amount) while displaying a fake, harmless UI to the user.

Existing visual verification methods (like static QR codes or PhotoTAN) are vulnerable to screen-recording and offline analysis by advanced malware.

**Chrono-Auth** solves this by shifting visual cryptography from the **spatial domain** (a static image) to the **temporal domain** (a synchronized, time-interleaved optical stream). The hidden transaction payload is shattered across time, interleaved with decoy frames, and cryptographically chained to ensure that capturing partial frames yields **0% readable data**.

---

## ✨ Key Cryptographic Functions

- **Deterministic Tile Encoding**  
  Converts text into 8×8 binary noise blocks. Prevents "ghosting" or partial structural leakage (reconstructs as `?` if corrupted).

- **Shannon Diffusion Layer**  
  Links every pixel mathematically. Guarantees the **Avalanche Effect** during decryption.

- **Logistic Chaos Mapping**  
  Uses non-linear dynamics:  
  `Xₙ₊₁ = r * Xₙ * (1 - Xₙ)`  
  for highly key-sensitive spatial scrambling and masking.

- **Stateful Temporal Chaining**  
  Strips are XOR-chained bidirectionally. A single dropped frame breaks the recursive decryption chain.

- **Decoy Interleaving**  
  Real payload frames are hidden among mathematically identical noise frames, requiring a `timemap.json` to extract.

---

## ⚙️ Installation & Setup

1. Clone the repository or download the source code.  
2. Ensure you have **Python 3.8+** installed.  
3. Install the required dependencies:

```bash
pip install numpy pillow opencv-python streamlit
```

---

## 🚀 How to Run the Demo

1. Navigate to the project folder in your terminal.  
2. Run the Streamlit application:

```bash
streamlit run app.py
```

3. A local server will start, and the dashboard will open in your default web browser (usually at `http://localhost:8501`).

---

## 🎮 Using the Dashboard (Simulation)

### 🔹 Generate the Stream
- In the left sidebar, enter:
  - Fake transaction (what malware shows)
  - Real hidden transaction
  - Session Key  
- Click **Generate Optical Stream**

### 🔹 The Compromised Browser
- Observe `stream.gif` on the left  
- Appears as statistically uniform flickering noise (to both humans and malware)

### 🔹 Scan & Verify
- Click the **✅ button**  
- Simulates smartphone scanning:
  - Filters decoys  
  - Decrypts chain  
  - Reveals true transaction intent  

### 🔹 Attack Simulations

- **Wrong Session Key**  
  → Demonstrates Avalanche Effect via Chaos Mapping  

- **Dropped Frame / Tampering**  
  → Demonstrates:
  - Shannon Diffusion  
  - Temporal Chaining  
  → Results in **100% cascade failure** (`??????` output)

---

## 📁 Project Structure

- `crypto_engine.py`  
  Handles spatial cryptography:
  - Tile Encoding  
  - Shannon Diffusion  
  - Chaos Map Generation  
  - Block Scrambling  

- `temporal_pipeline.py`  
  Handles time-domain cryptography:
  - Horizontal Slicing  
  - Recursive Bidirectional Mixing  
  - Masking  

- `stream_generator.py`  
  - Assembles final payload  
  - Generates decoy frames  
  - Embeds data  
  - Outputs `stream.gif` and `timemap.json`  

- `app.py`  
  - Streamlit frontend  
  - Simulates Browser vs Smartphone interaction  

---

## 🛡️ Security Metrics Proven

- **Strict Error Bounds**  
  Standard CBC limits error propagation. Chrono-Auth’s recursive bidirectional mixing + Shannon diffusion ensures:
  - 1-bit error OR
  - single dropped frame  
  ⇒ **100% corruption of the 256×256 grid**

- **Zero Partial Leakage**  
  Due to 8×8 Tile mapping:
  - No partial character reconstruction  
  - Corrupted pixels fail strict array matching  
  ⇒ Output becomes unreadable (`null` characters)

