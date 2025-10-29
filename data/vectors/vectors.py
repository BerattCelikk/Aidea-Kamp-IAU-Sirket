# data/vectors/vectors.py

import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

# --- 1. Dosya Yollarını Tanımla ---
# Projenin ana klasörüne göre yolları belirle
CSV_PATH = 'data/processed/patentAI.csv'
INDEX_PATH = 'data/vectors/patent_embeddings.faiss'

def create_vector_database():
    """
    patentAI.csv dosyasını okur, 'title' sütununu vektöre dönüştürür
    ve bir FAISS indeksi olarak kaydeder.
    """

    # --- 2. Veriyi Oku ---
    print(f"Veri okunuyor: {CSV_PATH}")
    if not os.path.exists(CSV_PATH):
        print(f"HATA: CSV dosyası bulunamadı: {CSV_PATH}")
        print("Lütfen script'i projenin ana klasöründen (Beratınki) çalıştırdığınızdan emin olun.")
        return

    try:
        df = pd.read_csv(CSV_PATH)
        df = df.head(100) # SADECE İLK 100 SATIRI AL (Test için)
        print("!!! DEBUG: Sadece ilk 100 satır işleniyor !!!")
    except Exception as e:
        print(f"CSV okuma hatası: {e}")
        return

    if 'title' not in df.columns:
        print("HATA: CSV dosyasında 'title' sütunu bulunamadı.")
        return

    df['title'] = df['title'].fillna('')
    texts = df['title'].tolist()

    print(f"Toplam {len(texts)} adet patent metni okundu.")

    # --- 3. Modeli Yükle ve Vektörleri Oluştur ---
    print("Dil modeli yükleniyor (all-MiniLM-L6-v2)... Bu işlem biraz sürebilir.")
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2') 
    except Exception as e:
         print(f"HATA: SentenceTransformer modeli yüklenemedi: {e}")
         print("İnternet bağlantınızı kontrol edin veya model adını doğrulayın.")
         return

    print("Metinler vektörlere dönüştürülüyor (Embedding)...")
    embeddings = model.encode(texts, show_progress_bar=True)
    embeddings = np.array(embeddings).astype('float32') 

    print(f"Vektörler oluşturuldu. Boyut: {embeddings.shape}")

    # --- 4. FAISS İndeksi Oluştur ve Kaydet ---
    try:
        d = embeddings.shape[1]
        index = faiss.IndexFlatL2(d) 

        print("Vektörler FAISS indeksine ekleniyor...")
        index.add(embeddings)

        print(f"İndeks FAISS dosyasına kaydediliyor: {INDEX_PATH}")
        faiss.write_index(index, INDEX_PATH)

        print("\nİşlem Tamamlandı!")
        print(f"'{INDEX_PATH}' başarıyla oluşturuldu.")
    except Exception as e:
         print(f"HATA: FAISS indeksi oluşturulurken/kaydedilirken hata oluştu: {e}")


if __name__ == "__main__":
    create_vector_database()