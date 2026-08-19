/**
 * KKDİK Uyumlu Sektörel GBF Şablonları (Presets)
 * Boya, Tiner, Poliüretan Sertleştirici (İzosiyanat) ve Su Bazlı Kimyasallar için
 * 4, 5, 6, 7, 8, 10 ve 13. bölümlerin mevzuata tam uyumlu hazır metin kütüphanesi.
 */

export const SECTOR_PRESETS = [
  {
    id: 'tiner',
    name: 'Tiner & Solvent Karışımları',
    description: 'Selülozik, Sentetik, Poliüretan, Akrilik ve Epoksi Tinerler için yüksek alevlenirlik, aspirasyon ve solvent güvenlik şablonu.',
    icon: '🧪',
    badge: 'Alevlenir Sıvı / Solvent',
    sections: {
      b4_ilk_yardim: {
        b4_1: {
          soluma: 'Kazazedeyi derhal temiz havaya çıkarınız. Rahat nefes alabileceği bir pozisyonda tutunuz. Nefes darlığı, baş dönmesi veya baygınlık durumunda derhal tıbbi yardım alınız; solunum durmuşsa suni solunum uygulayınız.',
          cilt_temasi: 'Kirlenmiş giysileri derhal çıkarınız. Cildi bol su ve sabunla en az 15 dakika iyice yıkayınız. Tahriş veya kızarıklık devam ederse doktora başvurunuz.',
          goz_temasi: 'Göz kapaklarını açık tutarak en az 15 dakika boyunca bol temiz su ile yıkayınız. Varsa ve kolaysa kontakt lensleri çıkarınız. Derhal bir göz hekimine başvurunuz.',
          yutma: 'Ağzı bol su ile çalkalayınız. KESİNLİKLE KUSTURMAYINIZ (Akciğerlere kimyasal aspirasyon ve ölümcül kimyasal pnömoni riski!). Bilinci kapalı kişiye asla ağızdan sıvı vermeyiniz. Derhal acil tıbbi yardım (114 UZEM / 112) alınız.'
        },
        b4_2_belirtiler_etkiler: 'Buharların solunması baş dönmesi, uyuşukluk, baş ağrısı, mide bulantısı ve merkezi sinir sistemi depresyonuna yol açabilir. Tekrarlı veya uzun süreli cilt teması ciltte kuruluğa ve çatlamaya neden olur.',
        b4_3_acil_tibbi_mudahale: 'Semptomatik ve destekleyici tedavi uygulayınız. Yutulması halinde aspirasyon tehlikesi nedeniyle mide yıkaması sadece endotrakeal entübasyon kontrolünde yapılmalıdır.'
      },
      b5_yangin_mucadele: {
        b5_1: {
          uygun_sondurucu: 'Alkol dirençli köpük, kuru kimyevi toz (KKT), karbon dioksit (CO2), su sisi.',
          uygun_olmayan_sondurucu: 'Yüksek basınçlı tam su jeti (Alev alan sıvının sıçramasına ve yangının geniş alana yayılmasına yol açar).'
        },
        b5_2_ozel_zararlar: 'Kolay alevlenir sıvı ve buhar. Buharları havadan ağırdır, zemin boyunca yayılarak uzak mesafelerdeki ateşleme kaynaklarına ulaşıp geri alev alabilir. Yanma sonucu toksik karbon monoksit (CO) ve karbon dioksit (CO2) gazları açığa çıkar.',
        b5_3_sondurme_ekibi_tavsiyeleri: 'Pozitif basınçlı bağımsız solunum cihazı (SCBA) ve tam koruyucu itfaiyeci elbisesi (EN 469) kullanınız. Isıya maruz kalan kapalı ambalajları ve tankları uzaktan su püskürterek soğutunuz.'
      },
      b6_kaza_sonucu_yayilma: {
        b6_1: {
          kisisel_onlemler_acil_olmayan: 'Alanı derhal boşaltınız ve yeterli havalandırma sağlayınız. Tüm açık alev, kıvılcım, sıcak yüzey ve statik elektrik kaynaklarını uzaklaştırınız. Sigara içmeyiniz. Kıvılcım çıkarmaz el aletleri ve antistatik ekipman kullanınız.',
          kisisel_onlemler_acil_mudahale: 'Bölüm 8\'de belirtilen kişisel koruyucu donanımları (A tipi solvent filtreli maske, nitril eldiven, antistatik tulum ve koruyucu gözlük) giyiniz.'
        },
        b6_2_cevresel_onlemler: 'Döküntünün kanalizasyona, yağmur suyu drenajlarına, yüzey sularına, yer altı sularına ve toprağa karışmasını engelleyiniz. Çevresel yayılma durumunda ilgili çevre otoritelerine haber veriniz.',
        b6_3_kontrol_temizleme_yontemleri: 'Kıvılcım çıkarmaz pompalar veya kum, toprak, diyatomit gibi yanıcı olmayan inert emici malzemelerle toplayınız. Toplanan emiciyi bertaraf edilmek üzere uygun etiketlenmiş kapalı atık kaplarına aktarınız.',
        b6_4_diger_bolumlere_atif: 'Kişisel korunma önlemleri için Bölüm 8\'e, atık bertarafı bilgileri için Bölüm 13\'e bakınız.'
      },
      b7_ellecme_depolama: {
        b7_1_guvenli_ellecleme: 'Sadece iyi havalandırılan veya lokal emiş sistemi bulunan alanlarda kullanınız. Buharlarını ve sisini solumaktan kaçınınız. Göz ve cilt temasını önleyiniz. Statik elektrik birikimine karşı tüm kapları ve boru hatlarını topraklayınız. Kıvılcım çıkarmaz ekipman kullanınız. Çalışma alanında yemek yemeyiniz, içmeyiniz ve sigara içmeyiniz.',
        b7_2: {
          guvenli_depolama_kosullari: 'Orijinal, sıkıca kapalı ambalajında, serin (5-30°C), kuru, doğrudan güneş ışığından ve hava koşullarından uzak, iyi havalandırılan alev almaz depolarda saklayınız. Açılan ambalajlar sızıntıyı önlemek için dikkatlice tekrar kapatılmalı ve dik tutulmalıdır.',
          uyumsuzluklar: 'Kuvvetli oksitleyici maddeler, kuvvetli asitler, bazlar ve doğrudan ısı kaynaklarından uzak tutunuz.'
        },
        b7_3_belirli_son_kullanimlar: 'Endüstriyel ve profesyonel boya/vernik inceltme, viskozite ayarlama ve ekipman temizleme uygulamaları içindir.'
      },
      b8_maruz_kalma_kontrolu: {
        b8_2: {
          muhendislik_kontrolleri: 'Buhar konsantrasyonunu mesleki maruziyet sınır değerlerinin altında tutmak için patlamaya dayanıklı (Ex-proof) lokal egzoz ve genel mekanik havalandırma sağlayınız.',
          kkd: {
            goz_yuz: 'Sıvı sıçramalarına ve buhara karşı yan siperlikli tam koruyucu gözlük veya yüz siperi (EN 166).',
            cilt_el: 'Çözücülere dayanıklı nitril, bütil veya florokauçuk koruyucu eldivenler (EN 374, geçirgenlik süresi >480 dk).',
            cilt_diger: 'Antistatik koruyucu iş tulumu/önlük ve kaymaz, solvente dayanıklı antistatik güvenlik ayakkabıları (EN ISO 20345).',
            solunum: 'Yetersiz havalandırma veya maruziyet sınırının aşıldığı durumlarda organik buharlara karşı A tipi filtreli yarım veya tam yüz gaz maskesi (EN 14387 / EN 140).'
          },
          cevresel_kontroller: 'Havalandırma ve proses ekipmanlarından çıkan emisyonların ulusal çevre mevzuatı limitlerine uygunluğu kontrol edilmelidir.'
        }
      },
      b10_kararlilik_tepkime: {
        b10_1_tepkime: 'Tavsiye edilen depolama ve kullanım koşullarında tehlikeli bir reaksiyon vermez.',
        b10_2_kimyasal_kararlilik: 'Normal ortam sıcaklığı ve basıncında kararlıdır.',
        b10_3_zararli_reaksiyon_olasiligi: 'Normal şartlar altında tehlikeli polimerizasyon veya zararlı reaksiyon oluşmaz.',
        b10_4_kacinilmasi_gereken_durumlar: 'Aşırı ısı, açık alev, kıvılcım, sıcak yüzeyler, doğrudan güneş ışığı ve elektrostatik boşalma.',
        b10_5_kacinilmasi_gereken_maddeler: 'Kuvvetli oksitleyici ajanlar, konsantre asitler ve alkaliler.',
        b10_6_zararli_bozunma_urunleri: 'Normal depolamada ayrışmaz. Yangın halinde karbon monoksit (CO), karbon dioksit (CO2) ve toksik hidrokarbon dumanları açığa çıkar.'
      },
      b13_bertaraf: {
        b13_1_atik_isleme_yontemleri: 'Atıklar evsel çöplerle karıştırılmamalı ve kanalizasyona dökülmemelidir. 02.04.2015 tarihli Atık Yönetimi Yönetmeliği uyarınca lisanslı tehlikeli atık bertaraf/geri kazanım tesislerine verilmelidir (Önerilen Atık Kodu: 14 06 03* Diğer çözücüler ve çözücü karışımları veya 08 01 11*).',
        b13_1_ambalaj_atik_isleme: 'Boşalan ambalajlarda yanıcı buhar kalıntısı riski bulunur; delmeyiniz, kesmeyiniz, kaynak yapmayınız. Lisanslı ambalaj geri kazanım tesislerine teslim edilmelidir (Atık Kodu: 15 01 10*).',
        b13_1_kanalizasyon_uyarisi: 'Kanalizasyona, su yollarına veya toprağa kesinlikle boşaltmayınız.'
      }
    }
  },

  {
    id: 'sertlestirici',
    name: 'Poliüretan / Epoksi Sertleştiriciler',
    description: 'İzosiyanat (HDI, TDI, IPDI) ve Poliamin esaslı sertleştiriciler için alerji, astım, neme duyarlılık, HCN dumanı ve dekontaminasyon güvenlik şablonu.',
    icon: '🛡️',
    badge: 'İzosiyanat / Alerjen / Neme Duyarlı',
    sections: {
      b4_ilk_yardim: {
        b4_1: {
          soluma: 'Kazazedeyi derhal temiz havaya çıkarınız ve rahat nefes alabileceği pozisyonda dinlendiriniz. Solunum güçlüğü veya astım benzeri hırıltı varsa oksijen veriniz ve ACİL DOKTORA BAŞVURUNUZ. Daha önce izosiyanatlara karşı duyarlılaşmış kişilerde astım krizleri tetiklenebilir.',
          cilt_temasi: 'Kirlenmiş giysileri derhal çıkarınız. Cildi bol su ve sabunla (mümkünse polietilen glikol 400 ile) en az 15 dakika iyice yıkayınız. Ciltte alerjik reaksiyon veya döküntü oluşursa tıbbi yardım alınız.',
          goz_temasi: 'Göz kapaklarını açık tutarak en az 15 dakika boyunca bol temiz su ile yıkayınız. Varsa kontakt lensleri çıkarınız. Derhal bir göz hekimine başvurunuz.',
          yutma: 'Ağzı bol su ile çalkalayınız. KESİNLİKLE KUSTURMAYINIZ. Bilinci kapalı kişiye asla ağızdan sıvı vermeyiniz. Derhal acil tıbbi yardım (114 UZEM / 112) alınız.'
        },
        b4_2_belirtiler_etkiler: 'Buhar veya aerosollerin solunması solunum yollarında duyarlılaşmaya, astım nöbetlerine ve solunum güçlüğüne (H334); cilt teması alerjik cilt reaksiyonlarına (H317) yol açabilir. Semptomlar maruziyetten saatler sonra ortaya çıkabilir.',
        b4_3_acil_tibbi_mudahale: 'Semptomatik tedavi uygulayınız. İzosiyanat maruziyeti sonrası hasta en az 48 saat hekim gözetiminde tutulmalı ve solunum fonksiyonları izlenmelidir. İzosiyanat alerjisi gelişen kişiler bir daha bu maddelerle temas ettirilmemelidir.'
      },
      b5_yangin_mucadele: {
        b5_1: {
          uygun_sondurucu: 'Alkol dirençli köpük, kuru kimyevi toz (KKT), karbon dioksit (CO2).',
          uygun_olmayan_sondurucu: 'Yüksek debili tam su jeti (Kapalı ambalajlarda su ile reaksiyona girerek tehlikeli CO2 gazı basıncı oluşturur).'
        },
        b5_2_ozel_zararlar: 'Yangın sırasında son derece toksik Hidrojen Siyanür (HCN), Azot Oksitler (NOx), İzosiyanat buharları, Karbon Monoksit (CO) ve CO2 gazları açığa çıkar. Su ile temas ettiğinde CO2 gazı üreterek kapalı kaplarda basınç artışına ve patlamaya yol açabilir.',
        b5_3_sondurme_ekibi_tavsiyeleri: 'Pozitif basınçlı tam yüz bağımsız solunum cihazı (SCBA) ve kimyasal koruyucu elbise kullanınız. Yangına maruz kalan kapları uzaktan su sisiyle soğutunuz, fakat ambalajların içine su girmesini kesinlikle önleyiniz.'
      },
      b6_kaza_sonucu_yayilma: {
        b6_1: {
          kisisel_onlemler_acil_olmayan: 'Alanı derhal tahliye ediniz ve havalandırınız. Buhar ve aerosolleri solumaktan kaçınınız. Ateşleme kaynaklarını uzaklaştırınız. Koruyucu ekipman giymeden döküntüye yaklaşmayınız.',
          kisisel_onlemler_acil_mudahale: 'İzosiyanatlara dayanıklı kimyasal koruyucu tulum, bütil/nitril eldiven, koruyucu gözlük ve kombine A2P3 filtreli tam yüz maskesi kullanınız.'
        },
        b6_2_cevresel_onlemler: 'Döküntünün kanalizasyona, drenajlara, su yollarına ve toprağa karışmasını önleyiniz.',
        b6_3_kontrol_temizleme_yontemleri: 'Döküntüyü yanıcı olmayan inert emiciyle (kum, diyatomit) toplayınız. Alanı DEKONTAMİNASYON SOLÜSYONU (%90 su + %8 konsantre amonyak + %2 sıvı deterjan veya %90 su + %5 sodyum karbonat + %5 deterjan) ile yıkayarak izosiyanatları nötralize ediniz. Reaksiyon sonucu CO2 gazı çıkışı olacağından toplanan atık bidonlarının kapağını en az 24 saat sıkıca kapatmayınız, gaz tahliyesine izin veriniz.',
        b6_4_diger_bolumlere_atif: 'Bölüm 8 ve Bölüm 13\'e bakınız.'
      },
      b7_ellecme_depolama: {
        b7_1_guvenli_ellecleme: 'Sadece çok iyi havalandırılan veya lokal egzoz bulunan alanlarda kullanınız. Neme ve suya karşı kesinlikle koruyunuz. Buhar ve aerosolleri solumayınız. Astım veya solunum rahatsızlığı geçmişi olan personelin temasını engelleyiniz.',
        b7_2: {
          guvenli_depolama_kosullari: 'Orijinal, hava ve nem geçirmez kaplarında, kuru, serin (10-25°C), doğrudan güneş ışığından uzak ve iyi havalandırılan depolarda saklayınız. Nemle temas CO2 gazı çıkışına ve ambalajın tehlikeli şekilde şişmesine/patlamasına neden olur. Kuru azot gazı koruması altında saklanması tavsiye edilir.',
          uyumsuzluklar: 'Su, nem, aminler, alkoller, kuvvetli bazlar ve asitler ile şiddetli reaksiyona girer.'
        },
        b7_3_belirli_son_kullanimlar: 'Poliüretan ve epoksi esaslı boya ve vernikler için sertleştirici komponent.'
      },
      b8_maruz_kalma_kontrolu: {
        b8_2: {
          muhendislik_kontrolleri: 'Ortam izosiyanat konsantrasyonunu mevzuat sınır değerlerinin altında tutmak için yüksek verimli lokal emiş ve genel mekanik havalandırma zorunludur.',
          kkd: {
            goz_yuz: 'Yan siperlikli tam koruyucu gözlük veya yüz siperi (EN 166).',
            cilt_el: 'Bütil kauçuk, florokauçuk veya lamine nitril koruyucu eldivenler (EN 374, geçirgenlik >480 dk).',
            cilt_diger: 'İzosiyanat geçirmez kimyasal koruyucu tulum ve güvenlik botları.',
            solunum: 'Aerosol ve buhar oluşumunda A2P3 kombine filtreli maske veya basınçlı hava beslemeli maske (EN 14387 / EN 14594).'
          },
          cevresel_kontroller: 'Egzoz havası izosiyanat filtreleme sistemlerinden geçirilmeli ve emisyon sınırlarına uyulmalıdır.'
        }
      },
      b10_kararlilik_tepkime: {
        b10_1_tepkime: 'Su, nem, aminler, alkoller ve bazlar ile ekzotermik (ısı veren) reaksiyon verir ve CO2 gazı açığa çıkarır.',
        b10_2_kimyasal_kararlilik: 'Kuru ve nemsiz ortamda önerilen depolama sıcaklıklarında kararlıdır.',
        b10_3_zararli_reaksiyon_olasiligi: 'Nem veya su ile temasında kapalı ambalajlarda tehlikeli basınç artışına ve kabın yırtılmasına yol açar.',
        b10_4_kacinilmasi_gereken_durumlar: 'Nem, su teması, 30°C üzeri yüksek sıcaklıklar, donma, kıvılcım ve açık alev.',
        b10_5_kacinilmasi_gereken_maddeler: 'Su, alkoller, aminler, kuvvetli bazlar, asitler ve oksitleyiciler.',
        b10_6_zararli_bozunma_urunleri: 'Yangında Hidrojen Siyanür (HCN), Azot Oksitler (NOx), İzosiyanat buharları, Karbon Monoksit (CO) ve CO2.'
      },
      b13_bertaraf: {
        b13_1_atik_isleme_yontemleri: 'Tehlikeli atık olarak lisanslı yakma/bertaraf tesislerine teslim edilmelidir (Önerilen Atık Kodu: 08 05 01* Atık izosiyanatlar veya 08 01 11*).',
        b13_1_ambalaj_atik_isleme: 'Boş ambalajlar dekontaminasyon solüsyonu ile nötralize edildikten sonra lisanslı geri kazanım tesislerine teslim edilmelidir (Atık Kodu: 15 01 10*).',
        b13_1_kanalizasyon_uyarisi: 'Kanalizasyona, su yollarına veya toprağa kesinlikle dökülmemelidir.'
      }
    }
  },

  {
    id: 'solvent_boya',
    name: 'Solvent Bazlı Boya & Vernikler',
    description: 'Sonkat, Astar, Dolgu, Parlak/Mat Vernikler için solventli alevlenirlik, statik elektrik, viskozite ve püskürtme güvenlik şablonu.',
    icon: '🎨',
    badge: 'Solventli Boya / Vernik',
    sections: {
      b4_ilk_yardim: {
        b4_1: {
          soluma: 'Kazazedeyi derhal temiz havaya çıkarınız. Rahat nefes alabileceği bir pozisyonda dinlendiriniz. Solunum sıkıntısı devam ederse tıbbi yardım alınız.',
          cilt_temasi: 'Kirlenmiş giysileri çıkarınız. Cildi bol su ve sabunla yıkayınız. Tiner veya solventle cildi temizlemeyiniz. Tahriş durumunda doktora başvurunuz.',
          goz_temasi: 'Göz kapaklarını açık tutarak en az 15 dakika bol temiz su ile yıkayınız. Varsa kontakt lensleri çıkarınız. Tıbbi yardım alınız.',
          yutma: 'Ağzı suyla çalkalayınız. KESİNLİKLE KUSTURMAYINIZ. Derhal acil tıbbi yardım (114 UZEM) alınız.'
        },
        b4_2_belirtiler_etkiler: 'Buharların solunması baş ağrısı, baş dönmesi, yorgunluk ve göz tahrişine neden olabilir. Tekrarlı temas ciltte kuruluğa ve çatlamaya yol açar.',
        b4_3_acil_tibbi_mudahale: 'Semptomatik tedavi uygulayınız.'
      },
      b5_yangin_mucadele: {
        b5_1: {
          uygun_sondurucu: 'Alkol dirençli köpük, kuru kimyevi toz (KKT), karbon dioksit (CO2), su sisi.',
          uygun_olmayan_sondurucu: 'Yüksek basınçlı tam su jeti.'
        },
        b5_2_ozel_zararlar: 'Alevlenir sıvı ve buhar. Yanma anında toksik karbon monoksit (CO), karbon dioksit (CO2) ve yoğun siyah duman açığa çıkar.',
        b5_3_sondurme_ekibi_tavsiyeleri: 'Bağımsız solunum cihazı (SCBA) ve tam koruyucu itfaiyeci elbisesi kullanınız. Isınan kapları su sisiyle soğutunuz.'
      },
      b6_kaza_sonucu_yayilma: {
        b6_1: {
          kisisel_onlemler_acil_olmayan: 'Alanı havalandırınız. Ateşleme ve kıvılcım kaynaklarını uzaklaştırınız. Sigara içmeyiniz. Antistatik kıyafetler kullanınız.',
          kisisel_onlemler_acil_mudahale: 'Bölüm 8\'de belirtilen kişisel koruyucu ekipmanları (solvent maskesi, eldiven, gözlük) takınız.'
        },
        b6_2_cevresel_onlemler: 'Döküntünün kanalizasyona, su kanallarına ve toprağa karışmasını önleyiniz.',
        b6_3_kontrol_temizleme_yontemleri: 'Kum, talaş veya inert emici ile emdiriniz ve kıvılcım çıkarmaz aletlerle kapalı atık kaplarına toplayınız.',
        b6_4_diger_bolumlere_atif: 'Bölüm 8 ve 13\'e bakınız.'
      },
      b7_ellecme_depolama: {
        b7_1_guvenli_ellecleme: 'İyi havalandırılan yerlerde kullanınız. Buharlarını solumaktan ve temastan kaçınınız. Ekipmanları topraklayınız. Açık alev ve kıvılcımdan uzak tutunuz.',
        b7_2: {
          guvenli_depolama_kosullari: 'Orijinal, sıkıca kapalı ambalajında, serin (5-30°C), kuru, doğrudan güneş ışığından uzak ve iyi havalandırılan alev almaz depolarda saklayınız.',
          uyumsuzluklar: 'Kuvvetli oksitleyiciler, asitler ve bazlardan uzak tutunuz.'
        },
        b7_3_belirli_son_kullanimlar: 'Sanayi ve profesyonel ahşap, metal ve oto yüzey boyama ve kaplama uygulamaları içindir.'
      },
      b8_maruz_kalma_kontrolu: {
        b8_2: {
          muhendislik_kontrolleri: 'Püskürtme ve kurutma kabinlerinde Ex-proof lokal emiş ve genel havalandırma sağlayınız.',
          kkd: {
            goz_yuz: 'EN 166 uyumlu yan siperlikli koruyucu gözlük.',
            cilt_el: 'EN 374 uyumlu nitril/bütil koruyucu eldiven.',
            cilt_diger: 'Antistatik koruyucu iş tulumu ve emniyet ayakkabısı.',
            solunum: 'Püskürtme uygulamalarında A2P2 filtreli kombine maske (EN 14387).'
          },
          cevresel_kontroller: 'Boya kabini filtrelerinin ve baca emisyonlarının standartlara uygunluğunu sağlayınız.'
        }
      },
      b10_kararlilik_tepkime: {
        b10_1_tepkime: 'Normal kullanım koşullarında tehlikeli tepkime vermez.',
        b10_2_kimyasal_kararlilik: 'Normal koşullarda kararlıdır.',
        b10_3_zararli_reaksiyon_olasiligi: 'Tehlikeli polimerizasyon oluşmaz.',
        b10_4_kacinilmasi_gereken_durumlar: 'Aşırı ısı, açık alev, kıvılcım ve statik elektrik.',
        b10_5_kacinilmasi_gereken_maddeler: 'Kuvvetli oksitleyiciler ve asitler.',
        b10_6_zararli_bozunma_urunleri: 'Yangında karbon monoksit ve karbon dioksit.'
      },
      b13_bertaraf: {
        b13_1_atik_isleme_yontemleri: 'Lisanslı tehlikeli atık tesislerine verilmelidir (Önerilen Atık Kodu: 08 01 11* Organik çözücüler veya diğer tehlikeli maddeler içeren atık boya ve vernikler).',
        b13_1_ambalaj_atik_isleme: 'Boş ambalajlar lisanslı geri kazanım tesislerine teslim edilmelidir (Atık Kodu: 15 01 10*).',
        b13_1_kanalizasyon_uyarisi: 'Kanalizasyona ve su yollarına dökülmemelidir.'
      }
    }
  },

  {
    id: 'su_bazli',
    name: 'Su Bazlı Boya, Astar & Vernikler',
    description: 'Su bazlı akrilik, PVA ve emülsiyon esaslı alevlenmez kaplamalar için düşük VOC, donma hassasiyeti ve genel hijyen güvenlik şablonu.',
    icon: '💧',
    badge: 'Su Bazlı / Alevlenmez',
    sections: {
      b4_ilk_yardim: {
        b4_1: {
          soluma: 'Kazazedeyi temiz havaya çıkarınız. Rahatsızlık devam ederse tıbbi yardım alınız.',
          cilt_temasi: 'Cildi bol su ve sabunla yıkayınız. Tahriş oluşursa doktora başvurunuz.',
          goz_temasi: 'Göz kapaklarını açık tutarak en az 10-15 dakika bol temiz su ile yıkayınız. Tahriş devam ederse hekime başvurunuz.',
          yutma: 'Ağzı su ile çalkalayınız. Bol su içiniz. Kendiliğinden kusma olmadıkça kusturmayınız. Tıbbi yardım alınız.'
        },
        b4_2_belirtiler_etkiler: 'Önemli bir akut veya gecikmeli etki beklenmez. Hassas kişilerde hafif cilt veya göz tahrişi görülebilir.',
        b4_3_acil_tibbi_mudahale: 'Semptomatik tedavi uygulayınız.'
      },
      b5_yangin_mucadele: {
        b5_1: {
          uygun_sondurucu: 'Ürün su bazlı olup alevlenmez. Çevredeki yangına uygun söndürücü (Köpük, KKT, CO2, su sisi) kullanınız.',
          uygun_olmayan_sondurucu: 'Bilinen uygun olmayan söndürücü yoktur.'
        },
        b5_2_ozel_zararlar: 'Ürün alevlenmez. Yangın ortamında suyunun buharlaşması sonrası kuru kalıntı yanarak karbon oksitler oluşturabilir.',
        b5_3_sondurme_ekibi_tavsiyeleri: 'Standart yangın koruyucu kıyafet ve solunum cihazı kullanınız.'
      },
      b6_kaza_sonucu_yayilma: {
        b6_1: {
          kisisel_onlemler_acil_olmayan: 'Kaygan zemin tehlikesine dikkat ediniz. Kişisel koruyucu eldiven ve gözlük takınız.',
          kisisel_onlemler_acil_mudahale: 'Standart koruyucu iş kıyafeti ve eldiven giyiniz.'
        },
        b6_2_cevresel_onlemler: 'Büyük döküntülerin kanalizasyona ve su yollarına karışmasını önleyiniz.',
        b6_3_kontrol_temizleme_yontemleri: 'Kum, toprak veya emici materyal ile toplayınız. Kalan ince kalıntıları bol su ile yıkayınız.',
        b6_4_diger_bolumlere_atif: 'Bölüm 8 ve 13\'e bakınız.'
      },
      b7_ellecme_depolama: {
        b7_1_guvenli_ellecleme: 'İyi havalandırılan alanlarda kullanınız. Göz ve cilt temasından kaçınınız. Çalışma sonrası ellerinizi yıkayınız.',
        b7_2: {
          guvenli_depolama_kosullari: 'Orijinal, sıkıca kapalı kaplarında, donmaya karşı korumalı (5-35°C), serin ve kuru yerde saklayınız. Doğrudan güneş ışığından koruyunuz.',
          uyumsuzluklar: 'Kuvvetli asitler ve oksitleyici maddelerden uzak tutunuz.'
        },
        b7_3_belirli_son_kullanimlar: 'İç ve dış cephe, ahşap veya duvar yüzey kaplama uygulamaları içindir.'
      },
      b8_maruz_kalma_kontrolu: {
        b8_2: {
          muhendislik_kontrolleri: 'Genel mekanik havalandırma yeterlidir.',
          kkd: {
            goz_yuz: 'Sıçramalara karşı standart koruyucu gözlük (EN 166).',
            cilt_el: 'Koruyucu kauçuk/nitril eldiven (EN 374).',
            cilt_diger: 'Standart koruyucu iş kıyafeti.',
            solunum: 'Yetersiz havalandırmada veya püskürtme anında P2 toz/sis maskesi (EN 149).'
          },
          cevresel_kontroller: 'Atık suların arıtılmadan çevreye verilmesi engellenmelidir.'
        }
      },
      b10_kararlilik_tepkime: {
        b10_1_tepkime: 'Normal şartlarda reaktif değildir.',
        b10_2_kimyasal_kararlilik: 'Normal sıcaklık ve basınçta kararlıdır.',
        b10_3_zararli_reaksiyon_olasiligi: 'Tehlikeli reaksiyon beklenmez.',
        b10_4_kacinilmasi_gereken_durumlar: 'Donma ve 40°C üzerindeki aşırı sıcaklıklar.',
        b10_5_kacinilmasi_gereken_maddeler: 'Kuvvetli asitler ve bazlar.',
        b10_6_zararli_bozunma_urunleri: 'Normal koşullarda oluşmaz.'
      },
      b13_bertaraf: {
        b13_1_atik_isleme_yontemleri: 'Atık mevzuatına uygun olarak bertaraf edilmelidir (Atık Kodu: 08 01 12 08 01 11 dışındaki atık boya ve vernikler).',
        b13_1_ambalaj_atik_isleme: 'Tamamen temizlenmiş ve kurutulmuş ambalajlar geri dönüştürülebilir (Atık Kodu: 15 01 02 veya 15 01 04).',
        b13_1_kanalizasyon_uyarisi: 'Doğrudan kanalizasyona dökülmemelidir.'
      }
    }
  }
];
