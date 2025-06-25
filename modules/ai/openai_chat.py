# =======================
# modules/ai/openai_chat.py - GPT-4o Entegrasyonu
# =======================

import openai
import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import time

from config.settings import AISettings
from modules.system.logger import SystemLogger


class OpenAIChat:
    """OpenAI GPT-4o ile sohbet sistemi"""
    
    def __init__(self, settings: AISettings, logger: SystemLogger):
        self.settings = settings
        self.logger = logger
        
        # OpenAI client
        self.client = None
        
        # Konuşma geçmişi
        self.conversation_history = []
        self.max_history_length = 10
        
        # Sistem mesajları
        self.system_messages = {
            'tr': {
                'greeting': "Merhaba! Ben Expo-Humanoid robotuyum. Size nasıl yardımcı olabilirim?",
                'goodbye': "Hoşçakalın! Tekrar görüşmek üzere.",
                'default': "İlginç bir soru. Size nasıl yardımcı olabilirim?",
                'error': "Özür dilerim, şu anda size yardımcı olamıyorum."
            },
            'en': {
                'greeting': "Hello! I'm Expo-Humanoid robot. How can I help you?",
                'goodbye': "Goodbye! See you next time.",
                'default': "That's an interesting question. How can I help you?",
                'error': "Sorry, I can't help you right now."
            }
        }
        
        # İstatistikler
        self.total_requests = 0
        self.total_tokens_used = 0
        self.average_response_time = 0.0
        
    def initialize(self) -> bool:
        """OpenAI client'ını başlat"""
        try:
            if not self.settings.openai_api_key:
                self.logger.error("OpenAI API key bulunamadı")
                return False
            
            openai.api_key = self.settings.openai_api_key
            self.client = openai
            
            # Test isteği gönder
            test_response = self._make_request("Test message", test=True)
            
            if test_response:
                self.logger.info("OpenAI GPT-4o bağlantısı başarılı")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"OpenAI başlatılamadı: {e}")
            return False
    
    def _make_request(self, message: str, test: bool = False) -> Optional[str]:
        """OpenAI API'ye istek gönder"""
        try:
            start_time = time.time()
            
            # Sistem prompt'u oluştur
            system_prompt = self._create_system_prompt()
            
            # Mesaj listesi hazırla
            messages = [{"role": "system", "content": system_prompt}]
            
            # Konuşma geçmişini ekle
            if not test:
                messages.extend(self.conversation_history[-self.max_history_length:])
            
            # Kullanıcı mesajını ekle
            messages.append({"role": "user", "content": message})
            
            # API isteği
            response = self.client.ChatCompletion.create(
                model=self.settings.model,
                messages=messages,
                max_tokens=self.settings.max_tokens,
                temperature=self.settings.temperature
            )
            
            # Yanıtı al
            reply = response.choices[0].message.content.strip()
            
            # İstatistikleri güncelle
            response_time = time.time() - start_time
            self.total_requests += 1
            self.total_tokens_used += response.usage.total_tokens
            
            # Ortalama yanıt süresini güncelle
            self.average_response_time = (
                (self.average_response_time * (self.total_requests - 1) + response_time) 
                / self.total_requests
            )
            
            # Konuşma geçmişini güncelle (test değilse)
            if not test:
                self.conversation_history.append({"role": "user", "content": message})
                self.conversation_history.append({"role": "assistant", "content": reply})
            
            return reply
            
        except Exception as e:
            self.logger.error(f"OpenAI API hatası: {e}")
            return None
    
    def _create_system_prompt(self) -> str:
        """Sistem prompt'unu oluştur"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if self.settings.language == 'tr':
            return f"""Sen Expo-Humanoid adında interaktif bir robotsun. Teknoloji fuarında ziyaretçilerle konuşuyorsun.
            
Özelliklerini:
- Dostça ve yardımsever
- Teknoloji ve robotik hakkında bilgili
- Türkçe konuşuyor
- Kısa ve net cevaplar veriyor
- Ziyaretçileri eğlendiriyor

Şu anki zaman: {current_time}

Yanıtların 2-3 cümleyi geçmemeli ve konuşma tarzında olmalı."""

        else:  # English
            return f"""You are Expo-Humanoid, an interactive robot at a technology fair talking to visitors.

Your characteristics:
- Friendly and helpful
- Knowledgeable about technology and robotics
- Speaking English
- Giving short and clear answers
- Entertaining visitors

Current time: {current_time}

Your responses should not exceed 2-3 sentences and should be conversational."""
    
    def get_response(self, user_input: str) -> str:
        """Kullanıcı girdisine yanıt üret"""
        if not self.client:
            return self._get_default_message('error')
        
        # Özel durumları kontrol et
        user_lower = user_input.lower().strip()
        
        # Selamlama
        greetings = ['merhaba', 'selam', 'hello', 'hi', 'hey']
        if any(greeting in user_lower for greeting in greetings):
            return self._get_default_message('greeting')
        
        # Vedalaşma
        goodbyes = ['güle güle', 'hoşçakal', 'bye', 'goodbye', 'see you']
        if any(goodbye in user_lower for goodbye in goodbyes):
            return self._get_default_message('goodbye')
        
        # Normal yanıt
        response = self._make_request(user_input)
        
        if response:
            return response
        else:
            return self._get_default_message('error')
    
    def _get_default_message(self, message_type: str) -> str:
        """Varsayılan mesajları döndür"""
        messages = self.system_messages.get(self.settings.language, self.system_messages['tr'])
        return messages.get(message_type, messages['default'])
    
    def clear_conversation(self):
        """Konuşma geçmişini temizle"""
        self.conversation_history.clear()
        self.logger.info("Konuşma geçmişi temizlendi")
    
    def set_language(self, language: str):
        """Dil ayarını değiştir"""
        if language in ['tr', 'en']:
            self.settings.language = language
            self.clear_conversation()  # Dil değiştiğinde geçmişi temizle
            self.logger.info(f"Dil ayarı değiştirildi: {language}")
    
    def get_stats(self) -> Dict[str, Any]:
        """İstatistikleri döndür"""
        return {
            "total_requests": self.total_requests,
            "total_tokens_used": self.total_tokens_used,
            "average_response_time": round(self.average_response_time, 3),
            "conversation_length": len(self.conversation_history),
            "current_language": self.settings.language,
            "api_connected": self.client is not None
        }
