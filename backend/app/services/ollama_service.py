import ollama
import logging
from typing import List, Dict, Any
import json

logger = logging.getLogger(__name__)

class OllamaService:
    def __init__(self, model_name="llama3"):
        self.model_name = model_name
        self.client = ollama.Client(host='http://localhost:11434') 
        print("🔧 Ollama Client başlatıldı. GPU kullanımı kontrol ediliyor...")
        print("💡 CPU kullanımı için ayar denendi (Not: Asıl ayar model çağrısındadır).")
        
    def analyze_patent_differences(self, user_patent: str, similar_patents: List[str]) -> Dict[str, Any]:

        prompt = f"""
        Patent Fark Analizi Görevi:
        
        Kullanıcının Patent Fikri: {user_patent}  # Kullanıcının girdiği patent fikri
        
        Benzer Patentler:
        {chr(10).join([f"{i+1}. {patent}" for i, patent in enumerate(similar_patents)])}  # Benzer patentleri liste şeklinde göster
        
        Lütfen:
        1. Kullanıcının fikri ile benzer patentler arasındaki temel farkları bul
        2. Yenilik potansiyelini değerlendir (Yüksek/Orta/Düşük)
        3. Hangi yönlerin gerçekten yeni olduğunu belirt
        4. Geliştirme önerileri sun
        5. Stratejik tavsiyeler ver
        
        JSON formatında cevap ver:  # AI'dan yapılandırılmış JSON cevap istiyoruz
        {{
            "differences": ["fark1", "fark2", ...],  # Farklılıklar listesi
            "novelty_score": "Yüksek/Orta/Düşük",  # Yenilik puanı
            "novel_aspects": ["yenilik1", "yenilik2", ...],  # Yeni olan yönler
            "improvement_suggestions": ["öneri1", "öneri2", ...],  # Geliştirme önerileri
            "strategic_advice": "stratejik tavsiye",  # Stratejik tavsiye
            "risk_assessment": "risk değerlendirmesi"  # Risk analizi
        }}
        """
        try:
            # Ollama'ya prompt'u gönder ve cevap al
            response = self.client.generate(
                model=self.model_name,  # Kullanılacak model
                prompt=prompt,  # Hazırladığımız prompt
                options={
                    'temperature': 0.3,  # Düşük temperature = daha tutarlı cevaplar
                    'top_p': 0.9,  # Kelime seçiminde çeşitlilik kontrolü
                    # YENİ EKLENEN SATIR: GPU kullanımını kapatmayı dene
                    'num_gpu': 0
                }
            )
            
            # AI'dan gelen ham metni JSON'a dönüştür
            result = self._parse_json_response(response['response'])
            return result  # Analiz sonuçlarını döndür
            
        except Exception as e:  # Herhangi bir hata olursa
            logger.error(f"Ollama analiz hatası: {e}")  # Hatayı logla
            return self._get_default_response()  # Varsayılan hata mesajını döndür
    
    def generate_patent_report(self, analysis_results: Dict[str, Any]) -> str:
        """AI analiz sonuçlarını kullanarak detaylı patent raporu oluşturur"""
        
        # Rapor oluşturma prompt'u
        prompt = f"""
        Patent Analiz Raporu Oluştur:
        
        Analiz Sonuçları: {json.dumps(analysis_results, ensure_ascii=False)}  # Analiz sonuçlarını JSON olarak ekle
        
        Türkçe olarak profesyonel bir patent analiz raporu oluştur:
        - Giriş  # Raporun giriş bölümü
        - Yenilik Değerlendirmesi  # Yenilik analizi
        - Fark Analizi  # Farklılıkların detaylı analizi
        - Riskler ve Fırsatlar  # Risk ve fırsat değerlendirmesi
        - Öneriler  # Geliştirme önerileri
        - Sonuç  # Genel değerlendirme
        
        Rapor maksimum 500 kelime olmalı.  # Uzunluk sınırlaması
        """
        
        try:
            # AI'dan rapor oluşturmasını iste
            response = self.client.generate(
                model=self.model_name,  # Aynı modeli kullan
                prompt=prompt,  # Rapor prompt'u
                # YENİ EKLENEN OPTIONS BLOĞU: GPU kullanımını kapatmayı dene
                options={'num_gpu': 0} 
            )
            return response['response']  # Oluşturulan raporu döndür
        except Exception as e:  # Hata durumu
            logger.error(f"Rapor oluşturma hatası: {e}")  # Hatayı logla
            return "Rapor oluşturulamadı."  # Hata mesajı döndür
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """AI'dan gelen ham metni temizleyip JSON'a dönüştürür"""
        try:
            # AI bazen JSON dışında ekstra text ekleyebilir, onları temizle
            start_idx = response.find('{')  # İlk { karakterinin pozisyonunu bul
            end_idx = response.rfind('}') + 1  # Son } karakterinin pozisyonunu bul (+1 dahil etmek için)
            if start_idx != -1 and end_idx != -1:  # Eğer hem { hem } bulunduysa
                json_str = response[start_idx:end_idx]  # Sadece JSON kısmını al
                return json.loads(json_str)  # String'i JSON objesine dönüştür
        except:  # Eğer JSON parse edilemezse
            pass  # Sessizce devam et ve varsayılan response'u döndür
        
        return self._get_default_response()  # Parse edilemezse varsayılanı döndür
    
    def _get_default_response(self) -> Dict[str, Any]:
        """Sistem hataları için varsayılan response oluşturur"""
        return {
            "differences": ["Analiz yapılamadı"],  # Hata mesajı
            "novelty_score": "Belirsiz",  # Belirsiz yenilik puanı
            "novel_aspects": ["Analiz yapılamadı"],  # Hata mesajı
            "improvement_suggestions": ["Sistem hatası"],  # Hata mesajı
            "strategic_advice": "Tekrar deneyin",  # Kullanıcıya tavsiye
            "risk_assessment": "Belirsiz"  # Belirsiz risk değerlendirmesi
        }  # Kullanıcının hiç response almamasındansa bu mesajları alması daha iyi
