import React from "react";
import { Mail, MapPin, Phone, Github, Code2, ExternalLink } from "lucide-react";

const Contact: React.FC = () => {
  return (
    <section id="iletisim" className="py-12 lg:py-20 bg-gray-50 relative">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* --- BAŞLIK ALANI --- */}
        <div className="text-center mb-10">
          <h2 className="text-3xl font-extrabold text-gray-900 mb-3">
            İletişime Geçin
          </h2>
          <p className="text-base text-gray-600 max-w-2xl mx-auto">
            Sorularınız için bize ulaşabilir veya geliştirme sürecine katkıda bulunmak için repomuzu inceleyebilirsiniz.
          </p>
        </div>

        {/* --- KARTLAR GRID (YAN YANA) --- */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          
          {/* 1. KART: İLETİŞİM BİLGİLERİ */}
          <div className="bg-white p-8 rounded-2xl border border-gray-100 shadow-sm flex flex-col justify-center h-full">
            <h3 className="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">
              <span className="w-1 h-6 bg-blue-600 rounded-full"></span>
              Resmi İletişim Kanalları
            </h3>
            
            <div className="space-y-6">
              {/* Adres */}
              <div className="flex items-start space-x-4">
                <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center flex-shrink-0 text-blue-600">
                  <MapPin size={20} />
                </div>
                <div>
                  <p className="font-semibold text-gray-900 text-sm">Konum</p>
                  <p className="text-gray-600 text-sm mt-0.5">
                    Naim Süleymanoğlu Bulvarı<br />
                    Yıldırım, Bursa / Türkiye
                  </p>
                </div>
              </div>

              {/* Email */}
              <div className="flex items-start space-x-4">
                <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center flex-shrink-0 text-blue-600">
                  <Mail size={20} />
                </div>
                <div>
                  <p className="font-semibold text-gray-900 text-sm">E-Posta</p>
                  <a href="mailto:info@akilliserit.com" className="text-gray-600 text-sm mt-0.5 hover:text-blue-600 transition-colors block">
                    info@akilliserit.com
                  </a>
                </div>
              </div>

              {/* Telefon */}
              <div className="flex items-start space-x-4">
                <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center flex-shrink-0 text-blue-600">
                  <Phone size={20} />
                </div>
                <div>
                  <p className="font-semibold text-gray-900 text-sm">Telefon</p>
                  <p className="text-gray-600 text-sm mt-0.5">
                    +90 (224) 000 00 00
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* 2. KART: GITHUB / GELİŞTİRİCİ (Daha Kompakt) */}
          <div className="relative overflow-hidden bg-gray-900 rounded-2xl p-8 shadow-xl flex flex-col justify-between h-full group">
            
            {/* Arka Plan Efekti */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-blue-600/20 rounded-full blur-3xl -mr-16 -mt-16 transition-all duration-700 group-hover:bg-blue-600/30"></div>
            
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="p-1.5 bg-white/10 rounded-md backdrop-blur-md">
                   <Code2 className="text-blue-400" size={18} />
                </div>
                <span className="text-blue-100 text-xs font-medium tracking-wide uppercase">Open Source</span>
              </div>

              <h3 className="text-2xl font-bold text-white mb-2 leading-tight">
                Kodları İncele & <br />
                <span className="text-blue-400">Katkıda Bulun</span>
              </h3>
              
              <p className="text-gray-400 text-sm leading-relaxed mb-6">
                Projemiz açık kaynaklıdır (MIT). Algoritmalarımızı incelemek veya katkı sağlamak için GitHub'a bekliyoruz.
              </p>
            </div>

            <a
              href="https://github.com/lutfubedel/Bursa_Akilli_Sehir_Hackathon_Projesi/tree/main/web"
              target="_blank"
              rel="noopener noreferrer"
              className="
                flex items-center justify-center gap-2 w-full bg-white text-gray-900 
                px-4 py-3.5 rounded-xl font-bold text-sm
                hover:bg-blue-50 transition-all duration-300 transform hover:scale-[1.02] shadow-lg
              "
            >
              <Github size={18} />
              <span>GitHub Deposuna Git</span>
              <ExternalLink size={14} className="text-gray-400 ml-1" />
            </a>
          </div>

        </div>

        {/* --- ALT BÖLÜM: HARİTA (Tam Genişlik) --- */}
        <div className="w-full h-64 md:h-80 bg-gray-200 rounded-2xl overflow-hidden shadow-sm border border-gray-200 relative group">
          <img 
              src="https://images.unsplash.com/photo-1524661135-423995f22d0b?q=80&w=2074&auto=format&fit=crop" 
              alt="Bursa Harita Temsili" 
              className="w-full h-full object-cover opacity-90 group-hover:scale-105 transition-transform duration-700"
          />
          {/* Harita Üzeri Bilgi Çubuğu */}
          <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-sm px-4 py-2 rounded-lg shadow-sm border border-white/50 text-xs font-semibold text-gray-700 flex items-center gap-2">
            <MapPin size={14} className="text-red-500" />
            Naim Süleymanoğlu Bulvarı, Bursa
          </div>
        </div>

      </div>
    </section>
  );
};

export default Contact;