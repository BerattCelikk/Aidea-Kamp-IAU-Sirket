from flask import Blueprint, request, jsonify  # Flask bileşenlerini import et
from services.analysis_service import PatentAnalysisService  # Analiz servisini import et
import os  # Dosya yolları için

analysis_bp = Blueprint('analysis', __name__)  # Flask blueprint oluştur (modüler route'lar için)

# CSV dosya yolu - projenize göre ayarlayın
CSV_PATH = os.path.join('data', 'raw', 'patent_data.csv')  # Patent veritabanı CSV dosyasının yolu

@analysis_bp.route('/analyze', methods=['POST'])  # POST metodu için /analyze endpoint'i tanımla
def analyze_patent():
    try:
        data = request.get_json()  # Gelen JSON verisini al
        user_patent_text = data.get('patent_text', '')  # 'patent_text' alanını al, yoksa boş string
        
        if not user_patent_text:  # Eğer patent metni boşsa
            return jsonify({'error': 'Patent metni gerekli'}), 400  # 400 hatası döndür
        
        # Analiz servisini başlat
        analysis_service = PatentAnalysisService(CSV_PATH)  # CSV yolu ile servis oluştur
        result = analysis_service.analyze_patent(user_patent_text)  # Patent analizini çalıştır
        
        return jsonify(result)  # Sonuçları JSON formatında döndür
        
    except Exception as e:  # Herhangi bir hata olursa
        return jsonify({'error': str(e)}), 500  # 500 hatası ve hata mesajı döndür