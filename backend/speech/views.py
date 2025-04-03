from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from gtts import gTTS
import speech_recognition as sr
import os
import json

LANGUAGE_MAPPING = {
    "eng": "en", "hin": "hi", "spa": "es", "fra": "fr", "ara": "ar", "jpn": "ja"
}

@csrf_exempt  # Temporarily disable CSRF for testing
def generate_speech(request):
    """Convert Text to Speech (TTS)"""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        data = json.loads(request.body)
        text = data.get("text", "").strip()
        lang_code = data.get("language", "eng")
        gtts_lang_code = LANGUAGE_MAPPING.get(lang_code, "en")

        if not text:
            return JsonResponse({"error": "Text is required"}, status=400)

        # Generate speech using gTTS
        tts = gTTS(text=text, lang=gtts_lang_code)
        file_path = "temp_audio.mp3"
        tts.save(file_path)

        # Send generated audio file as response
        with open(file_path, "rb") as audio_file:
            response = HttpResponse(audio_file.read(), content_type="audio/mpeg")
            response["Content-Disposition"] = 'attachment; filename="speech.mp3"'

        os.remove(file_path)  # Cleanup temporary file
        return response

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def speech_to_text(request):
    """Convert Speech to Text (STT)"""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    if "audio" not in request.FILES:
        return JsonResponse({"error": "No audio file provided"}, status=400)

    try:
        audio_file = request.FILES["audio"]
        recognizer = sr.Recognizer()

        # Save uploaded audio file
        file_path = "temp_audio.wav"
        with open(file_path, "wb") as f:
            for chunk in audio_file.chunks():
                f.write(chunk)

        # Convert audio to text
        with sr.AudioFile(file_path) as source:
            audio_data = recognizer.record(source)
            detected_text = recognizer.recognize_google(audio_data)

        os.remove(file_path)  # Cleanup temporary file
        return JsonResponse({"text": detected_text}, status=200)

    except sr.UnknownValueError:
        return JsonResponse({"error": "Could not understand audio"}, status=400)
    except sr.RequestError as e:
        return JsonResponse({"error": f"Speech recognition service error: {e}"}, status=500)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
