from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import sys
from sqlalchemy.orm import Session

# Mevcut dizini Python path'ine ekle
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

print(f"📁 Çalışma dizini: {current_dir}")
print(f"📁 Mevcut dosyalar: {os.listdir(current_dir)}")

# FALLBACK MODELS - ÖNCE BUNU EKLEYELİM
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from datetime import datetime

Base = declarative_base()

class AnalysisReport(Base):
    __tablename__ = "analysis_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    text_to_analyze = Column(Text, nullable=False)
    novelty_score = Column(Float, default=0.0)
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# SQLite database oluştur
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./patent_ai.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tabloları oluştur
Base.metadata.create_all(bind=engine)
print("✅ Database tabloları oluşturuldu")

# RELATIVE IMPORT'ları kullan
try:
    from core.config import settings
    print("✅ Config import edildi")
except ImportError as e:
    print(f"❌ Config import hatası: {e}")
    # Fallback settings
    class Settings:
        PROJECT_NAME = "Patent AI"
    settings = Settings()

try:
    from ai_models import llm_service
    print("✅ AI Models import edildi")
except ImportError as e:
    print(f"❌ AI Models import hatası: {e}")
    llm_service = None

# Yeni servisleri import etmeyi dene
try:
    from services.analysis_service import PatentAnalysisService
    print("✅ Patent Analysis Service başarıyla import edildi")
    ANALYSIS_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Patent Analysis Service import edilemedi: {e}")
    ANALYSIS_SERVICE_AVAILABLE = False
    PatentAnalysisService = None

# --- Pydantic Modelleri (API Kontratı) ---
class AnalysisRequest(BaseModel):
    text_to_analyze: str
    analysis_level: str = "deep"

class PatentAnalysisRequest(BaseModel):
    patent_text: str

class SimilarPatent(BaseModel):
    patent_id: str
    title: str
    similarity_score: float

class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    novelty_score: float
    similar_patents: List[SimilarPatent]
    summary: str

class ComprehensiveAnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    similar_patents: List[dict]
    ai_analysis: dict
    detailed_report: str
    user_input: str

# --- Veritabanı Bağımlılığı ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- FastAPI Uygulaması ---
app = FastAPI(title=settings.PROJECT_NAME)

# --- CORS ayarları ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CSV dosya yolu
BASE_DIR = os.path.dirname(current_dir)  # backend klasörü
AA_DIR = os.path.dirname(BASE_DIR)  # AA klasörü
CSV_PATH = os.path.join(AA_DIR, 'data', 'processed', 'patentAI.csv')

print(f"📁 CSV yolu: {CSV_PATH}")

# CSV KONTROLÜ
if os.path.exists(CSV_PATH):
    print("✅ CSV dosyası mevcut")
    try:
        import pandas as pd
        df = pd.read_csv(CSV_PATH)
        print(f"📊 CSV istatistikleri:")
        print(f"   - Satır sayısı: {len(df)}")
        print(f"   - Sütun sayısı: {len(df.columns)}")
        print(f"   - Sütun isimleri: {list(df.columns)}")
    except Exception as e:
        print(f"⚠️  CSV detay okuma hatası: {e}")
else:
    print("❌ CSV dosyası bulunamadı!")

# --- API UÇ NOKTALARI ---

@app.get("/")
def read_root():
    return {"message": f"{settings.PROJECT_NAME} API'sine hoş geldiniz!"}

@app.get("/health")
def health_check():
    """Sistem sağlık kontrolü"""
    return {
        "status": "healthy", 
        "services": {
            "database": "active",
            "llm_service": "active" if llm_service else "inactive", 
            "patent_analysis_service": "active" if ANALYSIS_SERVICE_AVAILABLE else "inactive",
            "csv_data": "available" if os.path.exists(CSV_PATH) else "missing"
        },
        "project": settings.PROJECT_NAME,
        "csv_file": os.path.basename(CSV_PATH) if os.path.exists(CSV_PATH) else "not_found"
    }

# MEVCUT ENDPOINT
@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_patent_idea(request: AnalysisRequest, db: Session = Depends(get_db)):
    """
    Mevcut analiz endpoint'i
    """
    if not llm_service:
        # Fallback analiz
        db_report = AnalysisReport(
            text_to_analyze=request.text_to_analyze,
            novelty_score=0.7,
            summary="LLM servisi şu anda kullanılamıyor. Temel analiz sağlandı."
        )
        
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        
        return AnalysisResponse(
            analysis_id=str(db_report.id),
            status="completed",
            novelty_score=0.7,
            summary="LLM servisi şu anda kullanılamıyor. Temel analiz sağlandı.",
            similar_patents=[]
        )
    
    print(f"Analiz için gelen metin: '{request.text_to_analyze}'")

    try:
        # LLM servisini çağır
        analysis_result = await llm_service.get_llm_analysis(request.text_to_analyze)

        # Veritabanına kaydet
        db_report = AnalysisReport(
            text_to_analyze=request.text_to_analyze,
            novelty_score=analysis_result.get("novelty_score", 0.5),
            summary=analysis_result.get("summary", "Analiz tamamlandı")
        )
        
        db.add(db_report)
        db.commit()
        db.refresh(db_report)

        return AnalysisResponse(
            analysis_id=str(db_report.id),
            status="completed",
            novelty_score=analysis_result.get("novelty_score", 0.5),
            summary=analysis_result.get("summary", "Analiz tamamlandı"),
            similar_patents=[]
        )
        
    except Exception as e:
        print(f"❌ Analiz hatası: {e}")
        # Fallback response
        db_report = AnalysisReport(
            text_to_analyze=request.text_to_analyze,
            novelty_score=0.5,
            summary=f"Analiz sırasında hata oluştu: {str(e)}"
        )
        
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        
        return AnalysisResponse(
            analysis_id=str(db_report.id),
            status="completed",
            novelty_score=0.5,
            summary=f"Analiz sırasında hata oluştu: {str(e)}",
            similar_patents=[]
        )

# YENİ ENDPOINT: Ollama + CSV Pipeline entegrasyonu
@app.post("/api/analyze-comprehensive", response_model=ComprehensiveAnalysisResponse)
async def analyze_patent_comprehensive(request: PatentAnalysisRequest):
    """
    YENİ: Ollama + CSV Pipeline ile kapsamlı patent analizi
    """
    if not ANALYSIS_SERVICE_AVAILABLE:
        # Fallback response
        return ComprehensiveAnalysisResponse(
            analysis_id="fallback_comp",
            status="completed",
            similar_patents=[],
            ai_analysis={"novelty": 0.5, "risk_level": "medium", "recommendations": ["Servis yüklenemedi"]},
            detailed_report="Patent analiz servisi şu anda kullanılamıyor. Lütfen gereksinimleri yükleyin: pip install sentence-transformers faiss-cpu pandas ollama",
            user_input=request.patent_text
        )
    
    if not os.path.exists(CSV_PATH):
        return ComprehensiveAnalysisResponse(
            analysis_id="no_csv",
            status="completed", 
            similar_patents=[],
            ai_analysis={"novelty": 0.5, "risk_level": "medium", "recommendations": ["CSV dosyası bulunamadı"]},
            detailed_report=f"Patent veritabanı bulunamadı: {CSV_PATH}. Lütfen data/processed/patentAI.csv dosyasının varlığını kontrol edin.",
            user_input=request.patent_text
        )
    
    if not request.patent_text or len(request.patent_text.strip()) < 10:
        raise HTTPException(
            status_code=400, 
            detail="Lütfen en az 10 karakterlik bir patent açıklaması girin"
        )

    try:
        print(f"🔍 Kapsamlı analiz başlatılıyor: {request.patent_text[:100]}...")
        
        # Yeni analiz servisini kullan
        analysis_service = PatentAnalysisService(CSV_PATH)
        result = analysis_service.analyze_patent(request.patent_text)
        
        print("✅ Kapsamlı patent analizi tamamlandı")
        
        return ComprehensiveAnalysisResponse(
            analysis_id="comp_" + str(hash(request.patent_text)),
            status="completed",
            similar_patents=result['similar_patents'],
            ai_analysis=result['ai_analysis'],
            detailed_report=result['detailed_report'],
            user_input=result['user_input']
        )
        
    except Exception as e:
        print(f"❌ Kapsamlı analiz hatası: {e}")
        # Fallback with error info
        return ComprehensiveAnalysisResponse(
            analysis_id="error_comp",
            status="completed",
            similar_patents=[],
            ai_analysis={"novelty": 0.5, "risk_level": "high", "recommendations": ["Analiz hatası"]},
            detailed_report=f"Analiz sırasında hata oluştu: {str(e)}",
            user_input=request.patent_text
        )

# Demo endpoint - CSV olmadan çalışabilir
@app.post("/api/demo-analysis")
async def demo_analysis(request: PatentAnalysisRequest):
    """CSV olmadan da çalışabilen demo analiz"""
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
            "novelty": 0.75,
            "risk_level": "low", 
            "recommendations": [
                "Fikriniz yüksek yenilik potansiyeline sahip",
                "Benzer patentlerle karşılaştırma yapılması önerilir",
                "Detaylı teknik araştırma önerilir"
            ]
        },
        detailed_report=f"DEMO ANALİZ: '{request.patent_text}' fikriniz analiz edildi. 3 benzer patent bulundu. Yenilik potansiyeli: %75. Gerçek analiz için CSV veritabanı yüklenmelidir.",
        user_input=request.patent_text
    )

# Test endpoint'i - Hızlı servis kontrolü için
@app.post("/api/test")
async def test_endpoint(patent_text: str = "Test patent açıklaması"):
    """
    Hızlı test için basit endpoint
    """
    return {
        "message": "API çalışıyor!",
        "received_text": patent_text,
        "services": {
            "database": "active",
            "llm_service": "active" if llm_service else "inactive",
            "patent_analysis": "active" if ANALYSIS_SERVICE_AVAILABLE else "inactive",
            "csv_file": "available" if os.path.exists(CSV_PATH) else "missing"
        },
        "csv_path": CSV_PATH,
        "available_endpoints": [
            "GET /health - Sistem durumu",
            "POST /api/analyze - Basit analiz",
            "POST /api/analyze-comprehensive - Kapsamlı analiz (Ollama + CSV)",
            "POST /api/demo-analysis - Demo analiz (CSV olmadan çalışır)",
            "POST /api/test - Test endpoint"
        ]
    }

# Basit bir GET test endpoint'i
@app.get("/api/test")
async def simple_test():
    return {
        "message": "GET test başarılı!", 
        "status": "active",
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "csv_available": os.path.exists(CSV_PATH)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)