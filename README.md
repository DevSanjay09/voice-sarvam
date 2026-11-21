# 🎙️ Sarvam AI Voice & Intelligence Layer for WhatsApp

A specialized, production-ready Python service that bridges **WhatsApp Webhook Messages** (Voice or Text) with **Sarvam AI (Speech & 105B Intelligence)** and prepares actionable payloads for **Cashfree Agent/API workflows**.

---

## ⚡ Architecture Flow

```
Customer / Merchant on WhatsApp (Voice Note or Text)
                    │
                    ▼
WhatsApp Cloud API Webhook -> Your Python Backend
                    │
                    ▼
Sarvam Voice & Intelligence Layer
  ├─ 1. Transcribe (Voice Only) : Sarvam Saaras v3 (OGG/Opus, WAV, MP3)
  ├─ 2. Intelligence (105B)    : Sarvam 105B Conversations (Entities + Natural Reply)
  └─ 3. Synthesize (Voice Only) : Sarvam Bulbul v3 (Localized Speech Audio base64)
                    │
                    ▼
Returns Standard JSON:
  ├─ "reply_text": "I'm checking order ORD5542 and securing your ₹1500..."
  ├─ "reply_audio_base64": "<base64 wav audio>" (Only if incoming was Voice)
  └─ "cashfree_action": {
        "target_action": "payment_recovery",
        "priority": "HIGH",
        "entities": {"order_id": "ORD5542", "amount": 1500, ...},
        "action_prompt": "Verify status with Cashfree PG..."
     }
                    │
                    ▼
Your Backend dispatches reply back to WhatsApp & triggers Cashfree Agents!
```

---

## 📦 Project Structure

```
├── .env                              # Contains the pre-configured Sarvam API Key
├── config.py                         # Settings & model configurations
├── schemas.py                        # Pydantic schemas for requests/responses
├── requirements.txt                  # Python dependencies
├── api.py                            # FastAPI server with WhatsApp endpoints
├── services/
│   ├── __init__.py
│   ├── sarvam_service.py             # Sarvam Saaras, 105B & Bulbul wrapper
│   └── sarvam_voice_layer.py         # Main WhatsApp Voice & Intelligence Layer
├── test_whatsapp_voice_layer.py      # Verification test suite (Voice, Text, Multi-intent)
└── README.md
```

---

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Verify `.env` File
The `.env` file already contains your active Sarvam AI API subscription key:
```env
SARVAM_API_KEY=sk_mo7gjokr_SHI35JnystZQPPJkp1R24ZJi
SARVAM_STT_MODEL=saaras:v3
SARVAM_LLM_MODEL=sarvam-105b-conversations
SARVAM_TTS_MODEL=bulbul:v3
SARVAM_DEFAULT_TTS_SPEAKER=priya
```

### 3. Run Self-Test
```bash
python test_whatsapp_voice_layer.py
```

---

## 💻 How to Use in Your Python Backend

### Method A: Direct Python Class Import (Recommended)

```python
from services.sarvam_voice_layer import SarvamVoiceLayer

voice_layer = SarvamVoiceLayer()

# ------------------------------------------------------------------
# 1. When WhatsApp webhook delivers a VOICE NOTE (.ogg / .opus):
# ------------------------------------------------------------------
# Download the audio bytes from WhatsApp media URL, then call:
result = voice_layer.process_whatsapp_voice(
    audio_bytes=whatsapp_audio_bytes, # Raw bytes from WhatsApp
    filename="voice.ogg",             # Saaras handles .ogg directly!
    sender_phone="+918610267450"
)

# Response for WhatsApp:
# result["reply_mode"]          -> "voice"
# result["reply_text"]          -> Empathetic, question-specific text
# result["reply_audio_base64"]  -> Base64 WAV speech audio to send back as voice note!

# Action for Cashfree:
# result["cashfree_action"]     -> {"target_action": "payment_recovery", "entities": {...}}


# ------------------------------------------------------------------
# 2. When WhatsApp webhook delivers a TEXT message:
# ------------------------------------------------------------------
result = voice_layer.process_whatsapp_text(
    text="I paid ₹1500 for order ORD5542 but order failed",
    sender_phone="+918610267450"
)

# Response for WhatsApp:
# result["reply_mode"]          -> "text"
# result["reply_text"]          -> Contextual text response
# result["reply_audio_base64"]  -> None (TTS skipped for ultra-fast latency!)

# Action for Cashfree:
# result["cashfree_action"]     -> {"target_action": "payment_recovery", "entities": {...}}
```

---

### Method B: Via FastAPI REST API

Start the server:
```bash
python api.py
# Running at http://localhost:8000
```

#### Endpoints:
1. `POST /api/whatsapp/process` (Unified - Voice upload or Text form)
2. `POST /api/whatsapp/process-voice` (Voice file upload)
   ```bash
   curl -X POST "http://localhost:8000/api/whatsapp/process-voice" \
     -F "file=@voice.ogg" \
     -F "phone_number=+918610267450"
   ```
3. `POST /api/whatsapp/process-text` (JSON text payload)
   ```bash
   curl -X POST "http://localhost:8000/api/whatsapp/process-text" \
     -H "Content-Type: application/json" \
     -d '{"text": "Please reconcile order ORD9012 with UTR 12345", "phone_number": "+918610267450"}'
   ```
4. `GET /api/health` (Health & model status)

---

## 🎯 Target Actions Output for Cashfree

The module extracts and routes requests into 5 standard Cashfree actions:
- `payment_recovery` : Failed transactions, debited funds, payment retry link requests.
- `reconciliation`   : Bank statement vs gateway status discrepancies, UTR checks.
- `leakage_detection`: MDR fee audit, double refund check, commission fee discrepancies.
- `payout_management`: Vendor payouts, partner transfers, UPI VPA verification.
- `customer_support` : General queries or greeting.
