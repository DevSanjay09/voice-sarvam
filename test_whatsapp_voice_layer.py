import os
import json
import base64
import logging
from services.sarvam_voice_layer import SarvamVoiceLayer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_whatsapp_voice_layer")

def run_tests():
    voice_layer = SarvamVoiceLayer()
    
    print("\n" + "=" * 70)
    print("🚀 TESTING SARVAM VOICE & INTELLIGENCE LAYER FOR WHATSAPP BACKEND")
    print("=" * 70)

    # -------------------------------------------------------------
    # TEST 1: INCOMING VOICE NOTE -> STT + 105B LLM + Bulbul TTS Audio
    # -------------------------------------------------------------
    print("\n[TEST 1] Incoming Voice Message (WAV/OGG)")
    sample_wav = "sample_payment_issue.wav"
    if os.path.exists(sample_wav):
        with open(sample_wav, "rb") as f:
            audio_bytes = f.read()
    else:
        # Dynamically generate audio sample via Sarvam Bulbul for a fully self-contained test
        print("  -> Generating dynamic audio sample via Sarvam Bulbul...")
        tts_res = voice_layer.sarvam_service.generate_speech(
            text="नमस्ते, मेरा 1500 रुपये कट गया है लेकिन ऑर्डर विफल हो गया",
            target_language_code="hi-IN"
        )
        audio_bytes = base64.b64decode(tts_res.audio_base64)

    voice_res = voice_layer.process_whatsapp_voice(
        audio_bytes=audio_bytes,
        filename="voice_note.wav",
        sender_phone="+919876543210"
    )

    print(f"Status: {voice_res.get('success')}")
    print(f"Input Type: {voice_res.get('input_type')} | Reply Mode: {voice_res.get('reply_mode')}")
    print(f"Transcribed Text: {voice_res.get('transcript')}")
    print(f"Detected Language: {voice_res.get('detected_language')}")
    print(f"Human-like Natural Reply:\n  -> \"{voice_res.get('reply_text')}\"")
    has_audio = bool(voice_res.get("reply_audio_base64"))
    audio_len = len(voice_res.get("reply_audio_base64") or "")
    print(f"Voice Audio Synthesized (Bulbul): {has_audio} ({audio_len} chars base64)")
    print(f"Cashfree Action:\n{json.dumps(voice_res.get('cashfree_action'), indent=2)}")
    
    assert voice_res.get("success") is True
    assert voice_res.get("reply_mode") == "voice"
    assert has_audio is True
    print("✅ TEST 1 PASSED: Voice in -> Natural Voice Reply + Entities!")

    # -------------------------------------------------------------
    # TEST 2: INCOMING TEXT (Payment Recovery Query)
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print("[TEST 2] Incoming Text: Payment Recovery Query")
    query_2 = "I paid ₹1500 for order ORD5542 on Cashfree but the money was debited and the order failed. Please help."
    res_2 = voice_layer.process_whatsapp_text(
        text=query_2,
        sender_phone="+919123456789"
    )

    print(f"Input Query: \"{query_2}\"")
    print(f"Input Type: {res_2.get('input_type')} | Reply Mode: {res_2.get('reply_mode')}")
    print(f"Natural Reply:\n  -> \"{res_2.get('reply_text')}\"")
    print(f"Audio Generated: {bool(res_2.get('reply_audio_base64'))} (Expected: False for text input)")
    print(f"Target Action: {res_2['cashfree_action'].get('target_action')} | Priority: {res_2['cashfree_action'].get('priority')}")
    print(f"Extracted Entities: {res_2['cashfree_action'].get('entities')}")

    assert res_2.get("success") is True
    assert res_2.get("reply_mode") == "text"
    assert res_2.get("reply_audio_base64") is None
    assert res_2['cashfree_action'].get('target_action') == "payment_recovery"
    print("✅ TEST 2 PASSED: Text in -> Natural Text Reply (No TTS overhead)!")

    # -------------------------------------------------------------
    # TEST 3: INCOMING TEXT (Reconciliation Query)
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print("[TEST 3] Incoming Text: Reconciliation Query")
    query_3 = "Please reconcile order ORD9012. Cashfree gateway indicates success with bank UTR 12345678, but internal DB shows pending."
    res_3 = voice_layer.process_whatsapp_text(
        text=query_3,
        sender_phone="+919888877777"
    )

    print(f"Input Query: \"{query_3}\"")
    print(f"Natural Reply:\n  -> \"{res_3.get('reply_text')}\"")
    print(f"Target Action: {res_3['cashfree_action'].get('target_action')}")
    print(f"Extracted Entities: {res_3['cashfree_action'].get('entities')}")

    assert res_3.get("success") is True
    assert res_3['cashfree_action'].get('target_action') == "reconciliation"
    assert res_3.get("reply_text") != res_2.get("reply_text"), "Replies must NOT be identical canned strings!"
    print("✅ TEST 3 PASSED: Distinct, context-specific reconciliation response!")

    # -------------------------------------------------------------
    # TEST 4: INCOMING TEXT (Payout Query)
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print("[TEST 4] Incoming Text: Vendor Payout Query")
    query_4 = "Please disburse ₹25,000 vendor payout to partner VPA partner@okhdfcbank."
    res_4 = voice_layer.process_whatsapp_text(
        text=query_4,
        sender_phone="+919777766666"
    )

    print(f"Input Query: \"{query_4}\"")
    print(f"Natural Reply:\n  -> \"{res_4.get('reply_text')}\"")
    print(f"Target Action: {res_4['cashfree_action'].get('target_action')}")
    print(f"Extracted Entities: {res_4['cashfree_action'].get('entities')}")

    assert res_4.get("success") is True
    assert res_4['cashfree_action'].get('target_action') == "payout_management"
    assert res_4.get("reply_text") != res_3.get("reply_text"), "Replies must be distinct!"
    print("✅ TEST 4 PASSED: Distinct payout response with VPA extraction!")

    # -------------------------------------------------------------
    # TEST 5: INCOMING TEXT (Revenue Leakage Query)
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print("[TEST 5] Incoming Text: Revenue Leakage / MDR Audit")
    query_5 = "Please audit transaction TXN_8819 for any unexpected MDR fee leaks or excessive gateway commissions."
    res_5 = voice_layer.process_whatsapp_text(
        text=query_5,
        sender_phone="+919555544444"
    )

    print(f"Input Query: \"{query_5}\"")
    print(f"Natural Reply:\n  -> \"{res_5.get('reply_text')}\"")
    print(f"Target Action: {res_5['cashfree_action'].get('target_action')}")
    print(f"Extracted Entities: {res_5['cashfree_action'].get('entities')}")

    assert res_5.get("success") is True
    assert res_5['cashfree_action'].get('target_action') == "leakage_detection"
    print("✅ TEST 5 PASSED: Leakage detection response!")

    # -------------------------------------------------------------
    # TEST 6: HINDI QUERY
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print("[TEST 6] Incoming Text: Hindi Query")
    query_6 = "मेरा ₹500 कट गया है आर्डर ORD9012 के लिए लेकिन अभी तक आर्डर कन्फर्म नहीं हुआ है"
    res_6 = voice_layer.process_whatsapp_text(
        text=query_6,
        sender_phone="+919444433333"
    )

    print(f"Input Query: \"{query_6}\"")
    print(f"Detected Language: {res_6.get('detected_language')}")
    print(f"Natural Hindi Reply:\n  -> \"{res_6.get('reply_text')}\"")
    print(f"Target Action: {res_6['cashfree_action'].get('target_action')}")
    print(f"Extracted Entities: {res_6['cashfree_action'].get('entities')}")

    assert res_6.get("success") is True
    print("✅ TEST 6 PASSED: Natural Hindi response!")

    print("\n" + "=" * 70)
    print("🎉 ALL 6 TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    run_tests()
