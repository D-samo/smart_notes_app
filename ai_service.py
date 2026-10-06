import os
import time
from google import genai
from PIL import Image
import re

class SmartAIService:
    def __init__(self, api_keys: list):
        self.api_keys = [k.strip() for k in api_keys if k.strip() and "BURAYA" not in k]
        self.exhausted_keys = set()
        self.current_key_index = 0
        self.client = None
        self._init_client()

    def _init_client(self):
        initial_index = self.current_key_index
        while self.current_key_index in self.exhausted_keys:
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys) if self.api_keys else 0
            if self.current_key_index == initial_index:
                self.client = None
                return

        if self.api_keys:
            key = self.api_keys[self.current_key_index]
            os.environ["GEMINI_API_KEY"] = key
            try:
                self.client = genai.Client(api_key=key)
            except Exception as e:
                print(f"Client hatası: {e}")

    def _rotate_key(self):
        if not self.api_keys:
            return False
        self.exhausted_keys.add(self.current_key_index)
        
        if len(self.exhausted_keys) >= len(self.api_keys):
            self.client = None
            return False

        self._init_client()
        return True

    def classify_image(self, image_path: str) -> str:
        prompt = (
            "Bu ders tahtası, ders notu veya sınav sorusu fotoğrafını analiz et. "
            "İçerikteki ana konuyu/dersi belirle. Sadece şu derslerden hangisine aitse O DERSİN ADINI BİREBİR YAZ: "
            "Matematik, Fen Bilimleri, Sosyal Bilgiler, Türkçe / Türk Dili ve Edebiyatı, "
            "Fizik, Kimya, Biyoloji, Tarih, Coğrafya, Yabancı Dil, Din Kültürü ve Ahlak Bilgisi. "
            "Eğer bunlardan hiçbiri değilse veya emin değilsen sadece 'Gruplandırılacak' yaz."
        )

        attempts = 0
        max_attempts = max(len(self.api_keys) * 2, 2)

        while attempts < max_attempts:
            if not self.client:
                break
            try:
                img = Image.open(image_path)
                response = self.client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=[prompt, img]
                )
                raw_text = response.text.strip()
                clean_text = re.sub(r'[*_"\']', '', raw_text)
                
                categories = [
                    "Matematik", "Fen Bilimleri", "Sosyal Bilgiler", 
                    "Türkçe / Türk Dili ve Edebiyatı", "Fizik", "Kimya", 
                    "Biyoloji", "Tarih", "Coğrafya", "Yabancı Dil", 
                    "Din Kültürü ve Ahlak Bilgisi"
                ]
                
                for cat in categories:
                    if cat.lower() in clean_text.lower():
                        return cat
                return "Gruplandırılacak"
            except Exception as e:
                attempts += 1
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "503" in err_str:
                    if not self._rotate_key():
                        break
                else:
                    break

        return "Gruplandırılacak"

    def generate_quiz(self, image_path: str) -> str:
        prompt = (
            "Fotoğraftaki notlardan veya sorulardan yararlanarak öğrenci için 3 adet kısa sınav/çalışma sorusu ve cevaplarını oluştur.\n"
            "FORMAT:\n"
            "Soru 1: ...\nCevap 1: ...\n\n"
            "Düz metin ve temiz Türkçe kullan. LaTeX kodları kullanma."
        )
        while len(self.exhausted_keys) < len(self.api_keys):
            if not self.client:
                break
            try:
                img = Image.open(image_path)
                response = self.client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=[prompt, img]
                )
                return response.text
            except Exception as e:
                if not self._rotate_key():
                    break
        return "⚠️ Çalışma kartı üretilemedi. Servis kotasını kontrol edin."

    def start_chat_session(self, image_path: str):
        return AIChatSession(self, image_path)


class AIChatSession:
    def __init__(self, ai_service: SmartAIService, image_path: str):
        self.ai_service = ai_service
        self.image_path = image_path
        self.chat = None
        self.first_turn = True
        self._create_chat()

    def _create_chat(self):
        if self.ai_service.client:
            try:
                self.chat = self.ai_service.client.chats.create(model="gemini-3.8-flash")
            except Exception as e:
                print(f"Chat hatası: {e}")

    def send_message(self, user_prompt: str) -> str:
        prompt_text = user_prompt
        if self.first_turn:
            prompt_text = (
                "Sen öğrencilere yardım eden uzman bir ders öğretmenisin.\n\n"
                "ÇOK ÖNEMLİ FORMAT KURALLARI:\n"
                "1. KESİNLİKLE ters eğik çizgi (\\) veya LaTeX kodları (örneğin \\frac, \\sqrt, \\alpha, \\pi) KULLANMA.\n"
                "2. Bütün matematik formüllerini DÜZ METİN ile yaz (örneğin: a / b, log_3(x), x^2, √x).\n"
                "3. Açıklamaları adım adım, çok temiz ve anlaşılır bir Türkçe ile sun.\n\n"
                f"Kullanıcının İsteği: {user_prompt}"
            )

        while len(self.ai_service.exhausted_keys) < len(self.ai_service.api_keys):
            if not self.ai_service.client:
                break
            try:
                if self.first_turn:
                    img = Image.open(self.image_path)
                    response = self.chat.send_message(message=[prompt_text, img])
                    self.first_turn = False
                else:
                    response = self.chat.send_message(message=user_prompt)
                
                return response.text
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "503" in err_str:
                    if self.ai_service._rotate_key():
                        self._create_chat()
                        self.first_turn = True
                        continue
                    else:
                        break
                return f"⚠️ Bir hata oluştu: {err_str}"

        return "⚠️ Sunucu yoğunluğu veya kota sınırına ulaşıldı. Lütfen daha sonra tekrar deneyin."