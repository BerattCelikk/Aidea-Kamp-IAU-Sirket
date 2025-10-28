import pandas as pd
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class CSVPipeline:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.patent_data = None
        self._initialize_pipeline()
    
    def _initialize_pipeline(self):
        """Basit CSV yükleme - embedding olmadan"""
        try:
            # CSV'yi yükle - İLK 50 PATENT
            full_data = pd.read_csv(self.csv_path)
            self.patent_data = full_data.head(50)
            print(f"✅ BASİT CSV PIPELINE: İlk 50 patent yüklendi (Toplam: {len(full_data)})")
            print(f"📋 Sütunlar: {list(self.patent_data.columns)}")
            
            # Örnek patentleri göster
            print("📄 İlk 3 örnek patent:")
            for i in range(min(3, len(self.patent_data))):
                patent = self.patent_data.iloc[i]
                title = patent.get('title', 'Başlık Yok')[:70]
                category = patent.get('technology_category', 'Kategori Yok')
                print(f"   {i+1}. {title}...")
                print(f"      Kategori: {category}")
                
        except Exception as e:
            print(f"❌ Basit CSV yükleme hatası: {e}")
            self.patent_data = pd.DataFrame()
    
    def find_similar_patents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Basit benzer patent bulma - keyword eşleştirme"""
        try:
            print(f"🔍 Basit benzer patent aranıyor: '{query}'")
            
            if self.patent_data is None or len(self.patent_data) == 0:
                print("❌ Patent verisi yok!")
                return self._get_sample_patents()
            
            # Basit keyword eşleştirme
            query_lower = query.lower()
            results = []
            
            for i in range(len(self.patent_data)):
                patent = self.patent_data.iloc[i]
                title = patent.get('title', '').lower()
                category = patent.get('technology_category', '').lower()
                
                # Basit skorlama
                score = 0.0
                
                # Başlıkta keyword var mı?
                if any(keyword in title for keyword in query_lower.split()):
                    score += 0.6
                
                # Kategoride keyword var mı?
                if any(keyword in category for keyword in query_lower.split()):
                    score += 0.4
                
                if score > 0.3:  # Eşik değer
                    result = {
                        'rank': len(results) + 1,
                        'similarity_score': round(score, 2),
                        'title': patent.get('title', 'Başlık Yok'),
                        'patent_id': patent.get('patent_id', f'ID_{i+1}'),
                        'assignee': patent.get('assignee', 'Atanmamış'),
                        'technology_category': patent.get('technology_category', 'Kategori Yok'),
                        'publication_date': patent.get('publication_date', 'Tarih Yok'),
                        'filing_date': patent.get('filing_date', 'Dosyalama Yok')
                    }
                    results.append(result)
                
                if len(results) >= top_k:
                    break
            
            # Eğer hiç sonuç yoksa, örnek patentler döndür
            if len(results) == 0:
                print("⚠️  Keyword eşleşmesi bulunamadı, örnek patentler döndürülüyor")
                results = self._get_sample_patents()
            
            print(f"✅ {len(results)} benzer patent bulundu (basit mod)")
            return results
            
        except Exception as e:
            print(f"❌ Basit benzer patent arama hatası: {e}")
            return self._get_sample_patents()
    
    def _get_sample_patents(self) -> List[Dict[str, Any]]:
        """Örnek patentler döndürür"""
        samples = []
        if self.patent_data is not None and len(self.patent_data) > 0:
            for i in range(min(3, len(self.patent_data))):
                patent = self.patent_data.iloc[i]
                samples.append({
                    'rank': i + 1,
                    'similarity_score': round(0.8 - (i * 0.2), 2),
                    'title': patent.get('title', 'Başlık Yok'),
                    'patent_id': patent.get('patent_id', f'SAMPLE_{i+1}'),
                    'assignee': patent.get('assignee', 'Atanmamış'),
                    'technology_category': patent.get('technology_category', 'Kategori Yok'),
                    'publication_date': patent.get('publication_date', '2023-01-01'),
                    'filing_date': patent.get('filing_date', '2022-01-01')
                })
        else:
            # Fallback örnekler
            samples = [
                {
                    'rank': 1,
                    'similarity_score': 0.75,
                    'title': 'Akıllı telefon batarya optimizasyonu',
                    'patent_id': 'SAMPLE_001',
                    'assignee': 'Teknoloji Şirketi',
                    'technology_category': 'Elektronik',
                    'publication_date': '2023-05-15',
                    'filing_date': '2022-11-20'
                },
                {
                    'rank': 2,
                    'similarity_score': 0.65,
                    'title': 'Mobil cihaz güç yönetim sistemi',
                    'patent_id': 'SAMPLE_002', 
                    'assignee': 'İnovasyon A.Ş.',
                    'technology_category': 'Yazılım',
                    'publication_date': '2023-03-10',
                    'filing_date': '2022-09-05'
                }
            ]
        return samples

    def get_patent_count(self) -> int:
        return len(self.patent_data) if self.patent_data is not None else 0

    def is_ready(self) -> bool:
        return self.patent_data is not None and len(self.patent_data) > 0