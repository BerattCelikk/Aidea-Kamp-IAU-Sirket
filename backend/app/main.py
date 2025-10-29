# app/main.py

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import sys
from sqlalchemy.orm import Session
import pandas as pd # CSV Kontrolü için eklendi
from datetime import datetime

# --- 1. PROJE YOLUNU AYARLA ---
# Mevcut dizini Python path'ine ekle
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

print(f"📁 Çalışma dizini: {current_dir}")

# --- 2. GERÇEK DOSYALARDAN IMPORT ET ---
# main.py içindeki gereksiz tanımlamalar kaldırıldı.
# DOĞRU Importlar

try:
    from backend.app.core.config import settings # DOĞRU: Tam yolu verdik
    print("✅ Config import edildi")
except ImportError as e:
    print(f"❌ Config import hatası: {e}")
    # Fallback settings
    class Settings:
        PROJECT_NAME = "Patent AI"
    settings = Settings()

try:
    # Veritabanı ve Modelleri doğru yerden import et
    from backend.app.database import engine, SessionLocal, Base # DOĞRU: Tam yolu verdik
    from backend.app.models import AnalysisReport # DOĞRU: Tam yolu verdik
    print("✅ Veritabanı ve Modeller import edildi")
    
    # Tabloları oluştur
    Base.metadata.create_all(bind=engine)
    print("✅ Database tabloları oluşturuldu")
    
except ImportError as e:
    print(f"❌ Veritabanı/Model import hatası: {e}")
    # Uygulamanın çökmemesi için fallback
    Base = object
    class AnalysisReport(Base): pass
    SessionLocal = None
    def get_db(): yield None


# Yeni servisleri import et
try:
    from backend.app.services.analysis_service import PatentAnalysisService # DOĞRU: Tam yolu verdik
    print("✅ Patent Analysis Service başarıyla import edildi")
    ANALYSIS_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Patent Analysis Service import edilemedi: {e}")
    ANALYSIS_SERVICE_AVAILABLE = False
    PatentAnalysisService = None

# --- (Kodun geri kalanı aynı) ---

# --- 3. PYDANTIC MODELLERİ (API KONTRATI) ---
# (Bu kısım aynı kaldı)
class PatentAnalysisRequest(BaseModel):
    patent_text: str

class ComprehensiveAnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    similar_patents: List[dict]
    ai_analysis: dict
    detailed_report: str
    user_input: str

# --- 4. VERİTABANI BAĞIMLILIĞI ---
# (Bu kısım, SessionLocal'in doğru import edildiğini varsayar)
def get_db():
    if SessionLocal is None:
        print("❌ Veritabanı oturumu oluşturulamadı (SessionLocal None).")
        yield None
        return
        
    db = SessionLocal()
    try:
        yield db
    finally:
        if db:
            db.close()

# --- 5. FASTAPI UYGULAMASI ---
app = FastAPI(title=settings.PROJECT_NAME)

# --- CORS ayarları ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CSV DOSYA YOLU VE KONTROLÜ ---
# (Bu kısım aynı kaldı)
BASE_DIR = os.path.dirname(current_dir)  # backend klasörü
AA_DIR = os.path.dirname(BASE_DIR)  # Proje ana klasörü (PatentAI)
CSV_PATH = os.path.join(AA_DIR, 'data', 'processed', 'patentAI.csv')

print(f"📁 CSV yolu: {CSV_PATH}")

if os.path.exists(CSV_PATH):
    print("✅ CSV dosyası mevcut")
    try:
        df = pd.read_csv(CSV_PATH)
        print(f"📊 CSV istatistikleri:")
        print(f"   - Satır sayısı: {len(df)}")
        print(f"   - Sütun sayısı: {len(df.columns)}")
    except Exception as e:
        print(f"⚠️  CSV detay okuma hatası: {e}")
else:
    print("❌ CSV dosyası bulunamadı!")


# --- 6. API UÇ NOKTALARI ---

@app.get("/")
def read_root():
    return {"message": f"{settings.PROJECT_NAME} API'sine hoş geldiniz!"}

@app.get("/health")
def health_check():
    """Sistem sağlık kontrolü"""
    return {
        "status": "healthy", 
        "services": {
            "database": "active" if SessionLocal else "inactive",
            "llm_service": "inactive (deprecated)", # Eski servisin artık olmadığını belirt
            "patent_analysis_service": "active" if ANALYSIS_SERVICE_AVAILABLE else "inactive",
            "csv_data": "available" if os.path.exists(CSV_PATH) else "missing"
        },
        "project": settings.PROJECT_NAME,
        "csv_file": os.path.basename(CSV_PATH) if os.path.exists(CSV_PATH) else "not_found"
    }

# YENİ ENDPOINT: Ollama + CSV Pipeline + VERİTABANI KAYDI
@app.post("/api/analyze-comprehensive", response_model=ComprehensiveAnalysisResponse)
async def analyze_patent_comprehensive(request: PatentAnalysisRequest, db: Session = Depends(get_db)):
    """
    YENİ VE SON HAL: Ollama + CSV Pipeline ile kapsamlı patent analizi yapar
    VE sonucu veritabanına kaydeder.
    """
    
    # --- Servis Kontrolleri ---
    if not ANALYSIS_SERVICE_AVAILABLE:
        return ComprehensiveAnalysisResponse(
            analysis_id="fallback_comp", status="error", similar_patents=[],
            ai_analysis={"error": "Patent analiz servisi yüklenemedi."},
            detailed_report="Patent analiz servisi şu anda kullanılamıyor. Lütfen gereksinimleri yükleyin: pip install pandas ollama",
            user_input=request.patent_text
        )
    
    if not os.path.exists(CSV_PATH):
        return ComprehensiveAnalysisResponse(
            analysis_id="no_csv", status="error", similar_patents=[],
            ai_analysis={"error": "CSV dosyası bulunamadı"},
            detailed_report=f"Patent veritabanı bulunamadı: {CSV_PATH}.",
            user_input=request.patent_text
        )
    
    if not request.patent_text or len(request.patent_text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Lütfen en az 10 karakterlik bir patent açıklaması girin")
    
    # --- Veritabanı Kontrolü ---
    if db is None:
        print("❌ Veritabanı bağlantı hatası. Analiz kaydedilemeyecek.")
        return ComprehensiveAnalysisResponse(
            analysis_id="db_error", status="error", similar_patents=[],
            ai_analysis={"error": "Veritabanı bağlantı hatası."},
            detailed_report="Sunucu veritabanına bağlanamadı. Analiz işlemi iptal edildi.",
            user_input=request.patent_text
        )

    # --- Gerçek Analiz ve Veritabanı Kaydı ---
    try:
        print(f"🔍 Kapsamlı analiz başlatılıyor: {request.patent_text[:100]}...")
        
        # 1. GERÇEK AI'YI ÇAĞIR
        analysis_service = PatentAnalysisService(CSV_PATH)
        result = analysis_service.analyze_patent(request.patent_text)
        
        print("✅ Kapsamlı patent analizi tamamlandı")
        
        # 2. VERİTABANINA KAYDET
        print("💾 Analiz sonucu veritabanına kaydediliyor...")
        
        # TODO: AI analizinden (result['ai_analysis']) gelen string skoru ('Yüksek' gibi) float'a çevir.
        
        db_report = AnalysisReport(
            text_to_analyze=request.patent_text,
            summary=result.get('detailed_report', 'Rapor oluşturulamadı.'),
            novelty_score=0.0 # Şimdilik 0.0
        )
        
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        
        print(f"✅ Kapsamlı analiz veritabanına kaydedildi, ID: {db_report.id}")

        # 3. KULLANICIYA DÖN
        return ComprehensiveAnalysisResponse(
            analysis_id=str(db_report.id), # Gerçek veritabanı ID'si
            status="completed",
            similar_patents=result['similar_patents'],
            ai_analysis=result['ai_analysis'],
            detailed_report=result['detailed_report'],
            user_input=result['user_input']
        )
        
    except Exception as e:
        print(f"❌ Kapsamlı analiz hatası: {e}")
        try:
            db_report_error = AnalysisReport(
                text_to_analyze=request.patent_text,
                summary=f"Analiz sırasında hata oluştu: {str(e)}",
                novelty_score=0.0
            )
            db.add(db_report_error)
            db.commit()
            db.refresh(db_report_error)
        except Exception as db_e:
            print(f"❌ Hata kaydı sırasında veritabanı hatası: {db_e}")

        return ComprehensiveAnalysisResponse(
            analysis_id="error_comp", status="error", similar_patents=[],
            ai_analysis={"error": f"Analiz hatası: {str(e)}"},
            detailed_report=f"Analiz sırasında bir sunucu hatası oluştu: {str(e)}",
            user_input=request.patent_text
        )

# Diğer demo/test endpoint'leri (bunlara dokunmadık)
@app.post("/api/demo-analysis")
async def demo_analysis(request: PatentAnalysisRequest):
    # ... (kod aynı)
    demo_patents = [
        {"patent_id": "demo_1", "title": "Akıllı Telefon Batarya Sistemi", "similarity_score": 0.85},
        {"patent_id": "demo_2", "title": "Yenilenebilir Enerji Depolama", "similarity_score": 0.72},
        {"patent_id": "demo_3", "title": "IoT Enerji Yönetimi", "similarity_score": 0.68}
    ]
    return ComprehensiveAnalysisResponse(
        analysis_id="demo_" + str(hash(request.patent_text)),
        status="completed",
        similar_patents=demo_patents,
        ai_analysis={
            "novelty": 0.75, "risk_level": "low", 
            "recommendations": [
                "Fikriniz yüksek yenilik potansiyeline sahip",
                "Benzer patentlerle karşılaştırma yapılması önerilir",
                "Detaylı teknik araştırma önerilir"
            ]
        },
        detailed_report=f"DEMO ANALİZ: '{request.patent_text}' fikriniz analiz edildi. 3 benzer patent bulundu. Yenilik potansiyeli: %75. Gerçek analiz için CSV veritabanı yüklenmelidir.",
        user_input=request.patent_text
    )

@app.post("/api/test")
async def test_endpoint(patent_text: str = "Test patent açıklaması"):
    # ... (kod aynı)
    return {
        "message": "API çalışıyor!", "received_text": patent_text,
        "services": {
            "database": "active" if SessionLocal else "inactive",
            "llm_service": "inactive (deprecated)",
            "patent_analysis": "active" if ANALYSIS_SERVICE_AVAILABLE else "inactive",
            "csv_file": "available" if os.path.exists(CSV_PATH) else "missing"
        },
        "csv_path": CSV_PATH,
        "available_endpoints": [
            "GET /health - Sistem durumu",
            "POST /api/analyze-comprehensive - Kapsamlı analiz (Ollama + CSV)",
            "POST /api/demo-analysis - Demo analiz (CSV olmadan çalışır)",
            "POST /api/test - Test endpoint"
        ]
    }

@app.get("/api/test")
async def simple_test():
    # ... (kod aynı)
    return {
        "message": "GET test başarılı!", "status": "active",
        "timestamp": datetime.now().isoformat(),
        "csv_available": os.path.exists(CSV_PATH)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)