import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from services.sarvam_voice_layer import SarvamVoiceLayer
from schemas import WhatsAppTextRequest, WhatsAppProcessResponse

app = FastAPI(
    title="Sarvam AI Voice & Intelligence Layer (WhatsApp API)",
    description="Multilingual Voice Ingestion (Saaras v3) -> Financial Intelligence & Natural Reply (105B) -> WhatsApp Voice Synthesis (Bulbul v3)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

whatsapp_voice_layer = SarvamVoiceLayer()

@app.get("/api/health")
def health():
    return {
        "status": "online",
        "service": "Sarvam AI Voice & Intelligence Layer",
        "models": {
            "stt": "saaras:v3",
            "llm": "sarvam-105b-conversations",
            "tts": "bulbul:v3"
        },
        "endpoints": [
            "POST /api/whatsapp/process (Unified voice / text)",
            "POST /api/whatsapp/process-voice (Audio upload)",
            "POST /api/whatsapp/process-text (JSON text)"
        ]
    }

@app.post("/api/whatsapp/process")
async def process_whatsapp_unified(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None),
    language_code: Optional[str] = Form(None)
):
    """
    Unified WhatsApp message ingestion endpoint:
    - If audio file is provided: Transcribes via Saaras, extracts entities via 105B,
      formulates natural reply, and synthesizes localized Bulbul audio.
    - If text is provided: Extracts entities via 105B, formulates natural reply,
      skips audio generation for speed.
    """
    try:
        if file:
            audio_bytes = await file.read()
            return whatsapp_voice_layer.process_whatsapp_voice(
                audio_bytes=audio_bytes,
                filename=file.filename or "whatsapp_audio.ogg",
                sender_phone=phone_number,
                language_hint=language_code
            )
        elif text:
            return whatsapp_voice_layer.process_whatsapp_text(
                text=text,
                sender_phone=phone_number,
                language_hint=language_code
            )
        else:
            raise HTTPException(status_code=400, detail="Either 'file' or 'text' must be provided.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/whatsapp/process-voice")
async def process_whatsapp_voice(
    file: UploadFile = File(...),
    phone_number: Optional[str] = Form(None),
    language_code: Optional[str] = Form(None)
):
    """Dedicated voice-only endpoint for WhatsApp audio notes (OGG/Opus, MP3, WAV, M4A)."""
    try:
        audio_bytes = await file.read()
        return whatsapp_voice_layer.process_whatsapp_voice(
            audio_bytes=audio_bytes,
            filename=file.filename or "whatsapp_audio.ogg",
            sender_phone=phone_number,
            language_hint=language_code
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/whatsapp/process-text")
def process_whatsapp_text(
    request: WhatsAppTextRequest
):
    """Dedicated JSON endpoint for incoming WhatsApp text messages."""
    try:
        return whatsapp_voice_layer.process_whatsapp_text(
            text=request.text,
            sender_phone=request.phone_number,
            language_hint=request.language_code
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 65)
    print("🚀 Sarvam Voice & Intelligence Layer running at: http://localhost:8000")
    print("=" * 65 + "\n")
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
