<div id="top">

<!-- HEADER STYLE: CLASSIC -->
<div align="center">

<img src="readmeai/assets/logos/purple.svg" width="30%" style="position: relative; top: 0; right: 0;" alt="Project Logo"/>

# <code>Patent AI</code>

<em>İAÜ ŞİRKET</em>

<!-- BADGES -->
<!-- local repository, no metadata badges. -->

<em>Built with the tools and technologies:</em>

<img src="https://img.shields.io/badge/Python-3776AB.svg?style=default&logo=Python&logoColor=white" alt="Python">

</div>
<br>

---

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
    - [Project Index](#project-index)
- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Usage](#usage)
    - [Testing](#testing)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Overview

**Team Members:**  
- Berat Erol Çelik – Deep Learning, Group Representative  
- Emre Aldemir – Backend, API  
- Umut Odabaş – Frontend  
- Ömer Altıntaş – ML  
- Efkan Çıtak – LLM  

---

## Problem

Patent süreçleri uzun, karmaşık ve maliyetlidir. Girişimciler, araştırmacılar veya Ar-Ge ekipleri, fikirlerinin daha önce patentlenip patentlenmediğini, hangi alanlarda yoğun başvuru olduğunu veya hangi kısmının gerçekten yenilik taşıdığını anlamakta zorlanıyor.  
Mevcut sistemler:  
- Yalnızca İngilizce çalışıyor, Türkçe patent verilerini kapsamaz.  
- Sadece arama yapan araçlar seviyesinde kalıyor, kullanıcıya akıllı öneriler sunmuyor.  
- Patent sonrası benzer başvuruları takip etmiyor.  

---

## Çözüm

PatentAI
- Fikri veya patent dokümanını analiz eder
- Benzer patentleri bulur ve farklarını özetler
- Yenilik potansiyelini değerlendirir
- Girişimciler, Ar-Ge Ekipleri ve araştırmacıları için akıllı öneriler sunar

---

## Key Features
- 🔍 Patent Fark Analizi ve Yenilik Değerlendirmesi:
    Girilen fikir veya patent dokümanını mevcut patentlerle kıyaslayarak farklarını ve yenilik potansiyelini analiz eder.
- 🧠 LLM-Tabanlı Anlamlandırma ve Danışmanlık:
    LLM (ör. Llama 3 veya GPT-4) modelleri ile metni anlamsal düzeyde yorumlar, güçlü ve geliştirilebilir yönleri hakkında öneriler sunar.
- 💡 Patentlenebilirlik Önerileri:
    Fikrin hangi yönlerinin patentlenebilir olduğunu değerlendirir, kullanıcıya stratejik tavsiyeler verir.
- 🌐 Türkçe Patent Desteği ve Yerel Çözümler:
    Türk Patent verileri üzerinde çalışan, Türkçe dilinde fark analizi yapabilen ilk sistemlerden biridir.
- 📊 Yoğunluk ve Boşluk Analizi:
    Patent öncesi aşamada belirli alanlarda yoğun başvuru olup olmadığını analiz eder, “hangi alanda boşluk var?” sorusuna yanıt verir.
- 🔔 Patent Takip ve Uyarı Sistemi (Future):
    Patent sonrası dönemde benzer başvurular yapıldığında kullanıcıyı bilgilendirir.
- 🎯 Stratejik Öneriler:
    Patent farklarını sadece teknik açıdan değil, pazar ve strateji yönünden de değerlendirir.
- 👩‍💼 Hedef Kullanıcılar için Özel Raporlar:
    * Girişimciler: 5 dakikada yenilik raporu alabilir.
    * Patent Vekilleri: Müvekkil fikriyle ilgili dayanak patentleri görebilir.
    * Akademisyenler / Öğrenciler: Fikrin literatürle ilişkisini görselleştirebilir.
- 🌟 Genişletilebilir Yapı:
     Gelecekte marka, tasarım ve telif haklarına da uyarlanabilecek esnek bir sistem mimarisi.
    

---

## Project Structure
Patent AI, yapay zekâ destekli bir “patent fark analizi ve yenilik danışmanı”dır. Sistem, girilen fikri veya patent dokümanını analiz eder, mevcut patentlerle kıyaslar, farklarını bulur ve yenilik potansiyelini değerlendirir.

---

## Project Structure

```sh
└── /
    ├── ai_models
    │   ├── embeddings
    │   ├── evaluation
    │   ├── llm_analysis
    │   └── similarity
    ├── backend
    │   └── app
    ├── data
    │   ├── processed
    │   ├── raw
    │   └── vectors
    ├── deployment
    │   └── deployment.py
    ├── docs
    │   ├── api
    │   ├── technical
    │   └── user_guide
    └── frontend
        ├── assets
        └── components
```

## Getting Started

### Prerequisites

- Python 3.10+  
- pip 

### Installation


1. **Clone the repository:**

    ```sh
    ❯ git clone https://github.com/BerattCelikk/Aidea-Kamp-IAU-Sirket.git

    ```

2. **Navigate to the project directory:**

    ```sh
    ❯ cd  Aidea-Kamp-IAU-Sirket

    ```

3. **Install the dependencies:**

pip install -r requirements.txt

### Usage

Run the project with:

echo 'INSERT-RUN-COMMAND-HERE'

### Testing

 uses the {__test_framework__} test framework. Run the test suite with:

echo 'INSERT-TEST-COMMAND-HERE'

---

## Roadmap

- [X] **`Task 1`**: <strike>Implement feature one.</strike>
- [ ] **`Task 2`**: Implement feature two.
- [ ] **`Task 3`**: Implement feature three.

---

## Contributing

- **💬 [Join the Discussions](https://LOCAL///discussions)**: Share your insights, provide feedback, or ask questions.
- **🐛 [Report Issues](https://LOCAL///issues)**: Submit bugs found or log feature requests for the `` project.
- **💡 [Submit Pull Requests](https://LOCAL///blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your LOCAL account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone .
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to LOCAL**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="left">
   <a href="https://LOCAL{///}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=/">
   </a>
</p>
</details>

---

## License

 is protected under the [LICENSE](https://choosealicense.com/licenses) License. For more details, refer to the [LICENSE](https://choosealicense.com/licenses/) file.

---

## Acknowledgments

- Credit `contributors`, `inspiration`, `references`, etc.

<div align="right">

[![][back-to-top]](#top)

</div>


[back-to-top]: https://img.shields.io/badge/-BACK_TO_TOP-151515?style=flat-square


---



