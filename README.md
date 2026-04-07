⏱️ Chrono-Auth: Time-Interleaved Visual Cryptography

An Academic Prototype for Transaction Integrity Verification against Man-in-the-Browser (MitB) Attacks.

📖 Overview
Traditional Multi-Factor Authentication (OTP, SMS) authenticates the user, but fails to verify the transaction intent. In a Man-in-the-Browser (MitB) attack, malware can alter the transaction details (e.g., changing the recipient and amount) while displaying a fake, harmless UI to the user.

Existing visual verification methods (like static QR codes or PhotoTAN) are vulnerable to screen-recording and offline analysis by advanced malware.

Chrono-Auth solves this by shifting visual cryptography from the spatial domain (a static image) to the temporal domain (a synchronized, time-interleaved optical stream). The hidden transaction payload is shattered across time, interleaved with decoy frames, and cryptographically chained to ensure that capturing partial frames yields 0% readable data.

✨ Key Cryptographic Innovations
Deterministic Tile Encoding: Converts text into 8x8 binary noise blocks. Prevents "ghosting" or partial structural leakage (reconstructs as ? if corrupted).
Shannon Diffusion Layer: Links every pixel mathematically. Guarantees the Avalanche Effect during decryption.
Logistic Chaos Mapping: Uses non-linear dynamics (X_n+1 = r * X_n * (1 - X_n)) for highly key-sensitive spatial scrambling and masking.
Stateful Temporal Chaining: Strips are XOR-chained bidirectionally. A single dropped frame breaks the recursive decryption chain.
Decoy Interleaving: Real payload frames are hidden among mathematically identical noise frames, requiring a synchronized timemap.json to extract.
⚙️ Installation & Setup
Clone the repository or download the source code.
Ensure you have Python 3.8+ installed.
Install the required dependencies by running the following command in your terminal:
Bash

pip install numpy pillow opencv-python streamlit
🚀 How to Run the Demo
The project features an interactive dashboard to simulate the attack and the cryptographic verification.

Navigate to the project folder in your terminal.
Run the Streamlit application using this command:
Bash

streamlit run app.py
A local server will start, and the dashboard will open in your default web browser (usually at http://localhost:8501).
🎮 Using the Dashboard (Simulation)
Generate the Stream: In the left sidebar, enter a fake transaction (what the malware shows), the real hidden transaction, and a Session Key. Click Generate Optical Stream.
The Compromised Browser: Watch the generated stream.gif on the left. To a human and to malware, it appears as statistically uniform flickering noise.
Scan & Verify: Click the ✅ button to simulate the user's smartphone scanning the stream. It will filter decoys, decrypt the chain, and reveal the true transaction intent.
Attack Simulations:
Click Wrong Session Key to see the Avalanche Effect of the Chaos Map.
Click Dropped Frame / Tampering to see the Shannon Diffusion and Temporal Chaining in action (results in a 100% cascade failure, outputting pure ??????).
📁 Project Structure
crypto_engine.py: Handles spatial cryptography (Tile Encoding, Shannon Diffusion, Chaos Map Generation, Block Scrambling).
temporal_pipeline.py: Handles time-domain cryptography (Horizontal Slicing, Recursive Bidirectional Mixing, Masking).
stream_generator.py: Assembles the final payload, generates Decoy frames, embeds data, and outputs stream.gif and timemap.json.
app.py: The frontend UI built with Streamlit, simulating the Browser vs. Smartphone interaction.
🛡️ Security Metrics Proven
Strict Error Bounds: Standard CBC limits error propagation. Chrono-Auth's recursive bidirectional mixing combined with Shannon diffusion ensures a 1-bit error or a single dropped frame cascades to corrupt 100% of the 256x256 grid.
Zero Partial Leakage: Due to the 8x8 Tile mapping, corrupted pixels do not reveal "halves" of letters. They fail the strict array-matching check and return as unreadable null characters.
Developed as a final-year academic research project in Cybersecurity and Applied Cryptography.