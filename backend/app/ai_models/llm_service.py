# app/ai_models/llm_service.py

import asyncio

async def get_llm_analysis(text: str) -> dict:
    """
    Asenkron olarak bir LLM analizini simüle eder.
    Gelecekte burası gerçek Ollama, Llama veya GPT çağrısını yapacak.
    """
    
    print(f"Yapay Zeka Modeli Düşünüyor... (Metin: {text[:20]}...)")
    
    # Gerçek bir LLM çağrısının alacağı süreyi simüle etmek için 2 saniye bekle
    await asyncio.sleep(2) 
    
    # Sahte ama dinamik bir sonuç üret
    # (Örn: Metin uzunluğuna göre sahte bir skor)
    novelty_score = round(len(text) % 100, 1) 
    
    # Gelen metni cevaba dahil et ki dinamik olduğu anlaşılsın
    summary = (f"'{text}' fikrinizin analizi tamamlandı. "
               f"Bu, LLM servisinden gelen dinamik bir cevaptır. "
               f"Metniniz {len(text)} karakter uzunluğundadır.")
    
    print("Yapay Zeka Analizi Tamamlandı.")
    
    # Analiz sonucunu bir sözlük olarak döndür
    return {
        "novelty_score": novelty_score,
        "summary": summary
    }