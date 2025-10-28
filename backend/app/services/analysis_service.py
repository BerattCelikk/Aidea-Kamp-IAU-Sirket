from .ollama_service import OllamaService
from .csv_pipeline import CSVPipeline
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PatentAnalysisService:
    def __init__(self, csv_path: str):
        print("🚀 Patent Analysis Service başlatılıyor...")
        self.csv_path = csv_path
        
        try:
            # CSV Pipeline'ı başlat
            self.pipeline = CSVPipeline(csv_path)
            print("✅ CSV Pipeline başarıyla başlatıldı")
        except Exception as e:
            print(f"❌ CSV Pipeline başlatma hatası: {e}")
            self.pipeline = None
        
        try:
            # Ollama Service'i başlat
            self.ollama = OllamaService()
            print("✅ Ollama Service başarıyla başlatıldı")
        except Exception as e:
            print(f"❌ Ollama Service başlatma hatası: {e}")
            self.ollama = None
    
    def analyze_patent(self, user_patent_text: str) -> Dict[str, Any]:
        """Tam patent analizi pipeline'ı"""
        print(f"🔍 Patent analizi başlatılıyor: {user_patent_text[:80]}...")
        
        similar_patents = []
        
        # 1. Benzer patentleri bul (CSV Pipeline ile)
        if self.pipeline and hasattr(self.pipeline, 'is_ready') and self.pipeline.is_ready():
            print("📊 CSV Pipeline ile benzer patentler aranıyor...")
            similar_patents = self.pipeline.find_similar_patents(user_patent_text)
        else:
            print("⚠️  CSV Pipeline hazır değil, boş liste döndürülüyor")
            similar_patents = []
        
        # 2. Benzer patent metinlerini hazırla
        similar_texts = []
        for pat in similar_patents:
            text = f"Başlık: {pat.get('title', 'Başlık Yok')}"
            if pat.get('technology_category'):
                text += f", Kategori: {pat['technology_category']}"
            if pat.get('assignee'):
                text += f", Atanan: {pat['assignee']}"
            similar_texts.append(text)
        
        print(f"📝 {len(similar_texts)} benzer patent metni hazırlandı")
        
        # 3. Ollama ile fark analizi
        analysis = {}
        if self.ollama:
            try:
                print("🤖 Ollama ile fark analizi yapılıyor...")
                analysis = self.ollama.analyze_patent_differences(
                    user_patent_text, 
                    similar_texts
                )
                print("✅ Ollama analizi tamamlandı")
            except Exception as e:
                print(f"❌ Ollama analiz hatası: {e}")
                analysis = self._get_fallback_analysis()
        else:
            print("⚠️  Ollama Service kullanılamıyor")
            analysis = self._get_fallback_analysis()
        
        # 4. Detaylı rapor oluştur
        report = ""
        if self.ollama:
            try:
                print("📄 Detaylı rapor oluşturuluyor...")
                report = self.ollama.generate_patent_report(analysis)
                print("✅ Rapor oluşturuldu")
            except Exception as e:
                print(f"❌ Rapor oluşturma hatası: {e}")
                report = "Rapor oluşturulamadı. Lütfen daha sonra tekrar deneyin."
        else:
            report = "AI rapor servisi şu anda kullanılamıyor."
        
        return {
            'similar_patents': similar_patents,
            'ai_analysis': analysis,
            'detailed_report': report,
            'user_input': user_patent_text
        }
    
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Fallback analiz verisi"""
        return {
            "teknik_farklar": ["Sistem şu anda analiz yapamıyor"],
            "yenilik_puani": "Belirsiz",
            "yenilikçi_yonler": ["Servis başlatılıyor"],
            "gelistirme_onerileri": ["Lütfen birkaç dakika sonra tekrar deneyin"],
            "ticari_degelerlendirme": "Sistem hazırlanıyor",
            "risk_analizi": "Değerlendirme yapılamadı",
            "patentlenebilirlik": "Belirsiz"
        }
    
    def is_ready(self) -> bool:
        """Servisin hazır olup olmadığını kontrol eder"""
        pipeline_ready = self.pipeline and self.pipeline.is_ready()
        ollama_ready = self.ollama is not None
        return pipeline_ready and ollama_ready