// === TEMA GEÇİŞİ ===
const themeBtn = document.getElementById('themeToggle');
const body = document.body;

if (localStorage.getItem('theme') === 'dark') {
  body.classList.add('dark');
  themeBtn.textContent = '☀️';
}

themeBtn.addEventListener('click', () => {
  body.classList.toggle('dark');
  if (body.classList.contains('dark')) {
    themeBtn.textContent = '☀️';
    localStorage.setItem('theme', 'dark');
  } else {
    themeBtn.textContent = '🌙';
    localStorage.setItem('theme', 'light');
  }
});

// === PATENT ANALİZ SİSTEMİ ===
const API_BASE = 'http://localhost:8000';
const sendBtn = document.getElementById('sendBtn');
const userInput = document.getElementById('userInput');
const chatBox = document.getElementById('chatBox');

// Gönder tuşu tıklandığında
sendBtn.addEventListener('click', () => {
  sendMessage();
});

// Enter tuşu basıldığında
userInput.addEventListener('keypress', (event) => {
  if (event.key === 'Enter') {
    sendMessage();
  }
});

async function sendMessage() {
  const message = userInput.value.trim();
  if (message === '') return;

  // Kullanıcının mesajını ekrana bas
  addMessage('user', message);
  userInput.value = '';

  try {
    // YENİ API: Patent analizi için
    const response = await fetch(`${API_BASE}/api/analyze-comprehensive`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        patent_text: message
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP hatası! Durum: ${response.status}`);
    }

    const data = await response.json();
    
    // Detaylı analiz sonuçlarını göster
    displayPatentAnalysis(data);
    
  } catch (error) {
    console.error('API isteği başarısız:', error);
    addMessage('bot', '❌ Sunucuya bağlanırken bir hata oluştu. Backend çalışıyor mu?');
  }
}

function displayPatentAnalysis(data) {
  const { similar_patents, ai_analysis, detailed_report } = data;
  
  let responseHTML = `
    <div class="patent-analysis">
      <div class="analysis-header">
        <h3>🔍 Patent Analiz Sonuçları</h3>
        <div class="novelty-badge ${getNoveltyClass(ai_analysis.novelty_score || ai_analysis.yenilik_puani)}">
          Yenilik: ${ai_analysis.novelty_score || ai_analysis.yenilik_puani || 'Belirsiz'}
        </div>
      </div>
      
      <div class="similar-patents">
        <h4>📊 Benzer Patentler (${similar_patents.length})</h4>
        ${similar_patents.map(patent => `
          <div class="patent-item">
            <div class="patent-rank">#${patent.rank} - ${(patent.similarity_score * 100).toFixed(1)}%</div>
            <div class="patent-title">${patent.title}</div>
            <div class="patent-details">
              <span class="patent-category">${patent.technology_category}</span>
              <span class="patent-assignee">${patent.assignee}</span>
            </div>
          </div>
        `).join('')}
      </div>
      
      <div class="ai-analysis">
        <h4>🤖 AI Değerlendirmesi</h4>
        <div class="analysis-points">
          <div class="point">
            <strong>Teknik Farklar:</strong>
            <ul>
              ${(ai_analysis.teknik_farklar || ai_analysis.differences || ['Belirsiz']).map(fark => `<li>${fark}</li>`).join('')}
            </ul>
          </div>
          
          <div class="point">
            <strong>Yenilikçi Yönler:</strong>
            <ul>
              ${(ai_analysis.yenilikçi_yonler || ai_analysis.novel_aspects || ['Belirsiz']).map(yenilik => `<li>${yenilik}</li>`).join('')}
            </ul>
          </div>
          
          <div class="point">
            <strong>Öneriler:</strong>
            <ul>
              ${(ai_analysis.gelistirme_onerileri || ai_analysis.improvement_suggestions || ['Belirsiz']).map(oner => `<li>${oner}</li>`).join('')}
            </ul>
          </div>
        </div>
      </div>
      
      <div class="detailed-report">
        <h4>📄 Detaylı Rapor</h4>
        <div class="report-content">
          ${detailed_report.replace(/\n/g, '<br>')}
        </div>
      </div>
    </div>
  `;
  
  addMessage('bot', responseHTML);
}

function getNoveltyClass(score) {
  if (!score) return 'unknown';
  const scoreStr = score.toString().toLowerCase();
  if (scoreStr.includes('yüksek') || scoreStr.includes('high')) return 'high';
  if (scoreStr.includes('orta') || scoreStr.includes('medium')) return 'medium';
  if (scoreStr.includes('düşük') || scoreStr.includes('low')) return 'low';
  return 'unknown';
}

function addMessage(sender, text) {
  const msgDiv = document.createElement('div');
  msgDiv.classList.add('message', sender);
  
  if (sender === 'bot' && text.includes('patent-analysis')) {
    msgDiv.innerHTML = text;
  } else {
    msgDiv.innerHTML = `<div class="bubble">${text}</div>`;
  }
  
  chatBox.appendChild(msgDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Sistem durumu kontrolü
async function checkSystemHealth() {
  try {
    const response = await fetch(`${API_BASE}/health`);
    const data = await response.json();
    
    let healthStatus = `✅ <strong>Sistem Durumu</strong><br>`;
    healthStatus += `📊 Database: ${data.services.database}<br>`;
    healthStatus += `🤖 LLM: ${data.services.llm_service}<br>`;
    healthStatus += `🔍 Patent Analiz: ${data.services.patent_analysis_service}<br>`;
    healthStatus += `📁 CSV Data: ${data.services.csv_data}`;
    
    addMessage('bot', healthStatus);
  } catch (error) {
    addMessage('bot', '❌ <strong>Sistem Kontrolü Hatası</strong><br>Backend çalışmıyor olabilir.');
  }
}

// Sayfa yüklendiğinde sistem durumunu göster
window.addEventListener('load', () => {
  setTimeout(() => {
    addMessage('bot', '👋 <strong>Patent AI Asistanına Hoş Geldiniz!</strong><br>Bir patent fikri yazın, ben benzer patentleri bulup analiz edeyim.<br><br><button onclick="checkSystemHealth()" style="padding: 5px 10px; margin: 5px 0;">Sistem Durumunu Kontrol Et</button>');
  }, 1000);
});