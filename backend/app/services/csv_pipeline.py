# backend/app/services/csv_pipeline.py

import pandas as pd
import logging
from typing import List, Dict, Any
import os
import numpy as np
from pathlib import Path

# --- 1. YENİ KÜTÜPHANELERİ IMPORT ET ---
try:
    import faiss
    from sentence_transformers import SentenceTransformer
    FAISS_AVAILABLE = True
except ImportError:
    print("⚠️ FAISS veya SentenceTransformers kütüphanesi bulunamadı.")
    FAISS_AVAILABLE = False

logger = logging.getLogger(__name__)

# --- 2. DOSYA YOLLARI VE MODELLER ---
try:
    CURRENT_FILE_PATH = Path(os.path.abspath(__file__))
except NameError:
    CURRENT_FILE_PATH = Path(os.path.abspath('.'))
PROJECT_ROOT = CURRENT_FILE_PATH.parent.parent.parent.parent
CSV_PATH_OBJ = PROJECT_ROOT / "data" / "processed" / "patentAI.csv"
CSV_PATH = str(CSV_PATH_OBJ)
MODEL_NAME = 'all-MiniLM-L6-v2'
# Hızlı başlatma için işlenecek patent sayısı (Tümünü işlemek için None yap)
# 18759 patentin tamamını işlemek sunucu başlangıcını 1-2 dakika yavaşlatabilir
PROCESS_LIMIT = None

class CSVPipeline:
    def __init__(self, csv_path: str = CSV_PATH):
        print("🚀 Gelişmiş CSV & FAISS Pipeline başlatılıyor...")
        self.csv_path = csv_path
        self.model_name = MODEL_NAME
        
        self.patent_data = None
        self.faiss_index = None
        self.sentence_model = None
        
        self._initialize_pipeline() # Başlatma fonksiyonunu çağır

    def _initialize_pipeline(self):
        """
        CSV verisini, FAISS indeksini ve SentenceTransformer modelini yükler.
        ...
        """
        
        global FAISS_AVAILABLE  # <-- BU SATIRI EKLE

        # --- A. CSV Verisini Oku ---
        print(f"📁 CSV verisi yükleniyor: {self.csv_path}")
        try:
            full_data = pd.read_csv(self.csv_path)
            full_data['title'] = full_data['title'].fillna('')
            
            if PROCESS_LIMIT is not None:
                print(f"⚠️ DEBUG: Hızlı başlatma için sadece ilk {PROCESS_LIMIT} patent işleniyor.")
                self.patent_data = full_data.head(PROCESS_LIMIT)
            else:
                self.patent_data = full_data
                
            print(f"✅ CSV verisi başarıyla yüklendi ({len(self.patent_data)} patent).")
        except Exception as e:
            print(f"❌ CSV yükleme hatası: {e}")
            self.patent_data = pd.DataFrame()
            return

        # --- B. FAISS ve Modeli Yükle/Oluştur ---
        if FAISS_AVAILABLE:
            try:
                # 1. Dil modelini yükle
                print(f"🤖 Dil modeli yükleniyor: {self.model_name}...")
                self.sentence_model = SentenceTransformer(self.model_name)
                print("✅ Dil modeli başarıyla yüklendi.")

                # 2. Metinleri vektöre dönüştür (Embedding)
                print(f"🧠 FAISS indeksi {len(self.patent_data)} metin için hafızada oluşturuluyor...")
                texts = self.patent_data['title'].tolist()
                embeddings = self.sentence_model.encode(texts, show_progress_bar=True)
                embeddings = np.array(embeddings).astype('float32')

                # 3. FAISS indeksini hafızada oluştur
                d = embeddings.shape[1]
                self.faiss_index = faiss.IndexFlatL2(d)
                self.faiss_index.add(embeddings)
                
                print(f"✅ FAISS indeksi hafızada başarıyla oluşturuldu ({self.faiss_index.ntotal} vektör).")

            except Exception as e:
                print(f"❌ FAISS/Model başlatma hatası: {e}")
                FAISS_AVAILABLE = False # Hata olursa basit moda düş
        else:
            print("⚠️ FAISS/SentenceTransformers kütüphaneleri eksik. Basit keyword araması kullanılacak.")

    # ... (find_similar_patents, _find_similar_patents_keyword, _get_sample_patents, vb. fonksiyonları aynı kalacak) ...
    # ... (Sadece o fonksiyonların tamamını buraya kopyalaman gerekiyor) ...
    
    # Kodu kolaylık olsun diye tam veriyorum, aşağıdaki kodun tamamını yapıştır
    # (yukarıdaki _initialize_pipeline fonksiyonunun bittiği yerden itibaren):

    def find_similar_patents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        FAISS ve SentenceTransformers kullanarak benzer patentleri bulur.
        Eğer FAISS kullanılamıyorsa, basit keyword araması yapar.
        """
        
        # --- FAISS ile GERÇEK ARAMA ---
        if self.faiss_index and self.sentence_model:
            try:
                print(f"🧠 FAISS ile benzer patent aranıyor: '{query[:50]}...'")
                
                query_vector = self.sentence_model.encode([query])
                query_vector = np.array(query_vector).astype('float32')
                distances, indices = self.faiss_index.search(query_vector, top_k)
                
                results = []
                print(f"🔍 FAISS {len(indices[0])} sonuç buldu. Detaylar getiriliyor...")
                
                for rank, (idx, dist) in enumerate(zip(indices[0], distances[0])):
                    if idx != -1:
                        try:
                            patent = self.patent_data.iloc[idx]
                            similarity_score = max(0.0, 1.0 - (dist / 2.0))
                            
                            result = {
                                'rank': rank + 1,
                                'similarity_score': round(float(similarity_score), 3), # <-- numpy float'ı normal float'a çevir
                                'title': patent.get('title', 'Başlık Yok'),
                                'patent_id': patent.get('patent_id', f'ID_{idx}'),
                                'assignee': patent.get('assignee', 'Atanmamış'),
                                'technology_category': patent.get('technology_category', 'Kategori Yok'),
                                'publication_date': patent.get('publication_date', 'Tarih Yok'),
                                'filing_date': patent.get('filing_date', 'Dosyalama Yok')
                            }
                            results.append(result)
                        except IndexError:
                             print(f"⚠️ Uyarı: FAISS indeksi {idx} CSV'de bulunamadı. Veri tutarsız olabilir.")
                        except Exception as e:
                             print(f"❌ Detay getirilirken hata: {e} (index: {idx})")

                print(f"✅ {len(results)} benzer patent FAISS ile bulundu.")
                if not results:
                     print("ℹ️  FAISS ile benzer patent bulunamadı.")
                     return self._get_sample_patents()
                return results
                
            except Exception as e:
                print(f"❌ FAISS arama hatası: {e}")
                print("⚠️ FAISS hatası nedeniyle basit keyword aramasına geçiliyor...")
                return self._find_similar_patents_keyword(query, top_k)

        # --- FALLBACK: BASİT KEYWORD ARAMASI ---
        else:
            print("⚠️ FAISS kullanılamıyor, basit keyword araması yapılıyor...")
            return self._find_similar_patents_keyword(query, top_k)


    def _find_similar_patents_keyword(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Basit benzer patent bulma - keyword eşleştirme (Fallback)"""
        try:
            print(f"🔍 Basit keyword ile benzer patent aranıyor: '{query}'")
            
            if self.patent_data is None or self.patent_data.empty:
                print("❌ Patent verisi yok!")
                return self._get_sample_patents()
            
            query_lower = query.lower()
            results = []
            
            search_limit = min(500, len(self.patent_data)) 
            for i in range(search_limit):
                patent = self.patent_data.iloc[i]
                title = patent.get('title', '').lower()
                category = patent.get('technology_category', '').lower()
                
                score = 0.0
                if any(keyword in title for keyword in query_lower.split()):
                    score += 0.6
                if any(keyword in category for keyword in query_lower.split()):
                    score += 0.4
                
                if score > 0.3:
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
            
            if len(results) == 0:
                print("⚠️ Keyword eşleşmesi bulunamadı, örnek patentler döndürülüyor")
                results = self._get_sample_patents()
            
            print(f"✅ {len(results)} benzer patent bulundu (basit mod)")
            return results
            
        except Exception as e:
            print(f"❌ Basit benzer patent arama hatası: {e}")
            return self._get_sample_patents()

    def _get_sample_patents(self) -> List[Dict[str, Any]]:
        samples = []
        if self.patent_data is not None and not self.patent_data.empty:
             for i in range(min(3, len(self.patent_data))):
                 patent = self.patent_data.iloc[i]
                 samples.append({
                     'rank': i + 1, 'similarity_score': round(0.8 - (i * 0.2), 2),
                     'title': patent.get('title', 'Başlık Yok'),
                     'patent_id': patent.get('patent_id', f'SAMPLE_{i+1}'),
                     'assignee': patent.get('assignee', 'Atanmamış'),
                     'technology_category': patent.get('technology_category', 'Kategori Yok'),
                     'publication_date': patent.get('publication_date', '2023-01-01'),
                     'filing_date': patent.get('filing_date', '2022-01-01')
                 })
        else:
            samples = [
                {'rank': 1, 'similarity_score': 0.75, 'title': 'Akıllı telefon batarya optimizasyonu', 'patent_id': 'SAMPLE_001', 'assignee': 'Teknoloji Şirketi', 'technology_category': 'Elektronik', 'publication_date': '2023-05-15', 'filing_date': '2022-11-20'},
                {'rank': 2, 'similarity_score': 0.65, 'title': 'Mobil cihaz güç yönetim sistemi', 'patent_id': 'SAMPLE_002', 'assignee': 'İnovasyon A.Ş.', 'technology_category': 'Yazılım', 'publication_date': '2023-03-10', 'filing_date': '2022-09-05'}
            ]
        return samples

    def get_patent_count(self) -> int:
        return len(self.patent_data) if self.patent_data is not None else 0

    def is_ready(self) -> bool:
        if FAISS_AVAILABLE:
             return self.faiss_index is not None and self.sentence_model is not None and self.patent_data is not None and not self.patent_data.empty
        else:
             return self.patent_data is not None and not self.patent_data.empty