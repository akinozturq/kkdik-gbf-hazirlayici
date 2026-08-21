"""
Derin ve Özyinelemeli SDS Çeviri Testleri
"""

from app.services.translation_service import translation_service


def test_recursive_sds_translation_deterministic():
    sample_sds = {
        "b1_kimlik": {
            "b1_1": {
                "madde_karisim_adi": "Sentetik Tiner",
                "kayit_numarasi": "Kayıttan muaftır."
            },
            "b1_2": {
                "tanimlanmis_kullanimlar": ["Sanayi / Endüstriyel kullanım", "Yüzey temizleme"],
                "tavsiye_edilmeyen_kullanimlar": ["Gıda temaslı uygulamalarda kullanmayınız."]
            }
        },
        "b3_bilesim": {
            "tip": "karisim",
            "karisim": {
                "bilesenler": [
                    {
                        "ad": "Aseton",
                        "cas_no": "67-64-1",
                        "ec_no": "200-662-2",
                        "konsantrasyon": "%50 - %70",
                        "siniflandirma": "Alev. Sıvı 2, H225; Göz Tah. 2, H319; BHOT Tek 3, H336"
                    },
                    {
                        "ad": "Toluen",
                        "cas_no": "108-88-3",
                        "ec_no": "203-625-9",
                        "konsantrasyon": "%30 - %50",
                        "siniflandirma": "Alev. Sıvı 2, H225; Cilt Tah. 2, H315; Ür. Sis. 2, H361d; BHOT Tek 3, H336"
                    }
                ]
            }
        },
        "b4_ilk_yardim": {
            "b4_1": {
                "soluma": "Kazazedeyi temiz havaya çıkarınız.",
                "goz_temasi": "Gözleri bol su ile en az 15 dakika yıkayınız."
            }
        },
        "b9_fiziksel_kimyasal_ozellikler": {
            "b9_1": {
                "fiziksel_durum": "Sıvı",
                "renk": "Renksiz",
                "koku": "Karakteristik"
            }
        },
        "b10_kararlilik_tepkime": {
            "b10_2_kimyasal_kararlilik": "Normal depolama ve kullanım koşullarında kararlıdır."
        }
    }

    translated = translation_service.translate_sds_dict(sample_sds, lang="en")

    # Verify standard translations
    assert translated["b1_kimlik"]["b1_1"]["kayit_numarasi"] == "Exempt from registration."
    assert "Industrial" in translated["b1_kimlik"]["b1_2"]["tanimlanmis_kullanimlar"][0]

    # Verify Section 3 chemical names and CLP classification translations
    comps = translated["b3_bilesim"]["karisim"]["bilesenler"]
    assert comps[0]["ad"] == "Acetone"
    assert "Flam. Liq. 2, H225" in comps[0]["siniflandirma"]
    assert "Eye Irrit. 2, H319" in comps[0]["siniflandirma"]
    assert "STOT SE 3, H336" in comps[0]["siniflandirma"]

    assert comps[1]["ad"] == "Toluene"
    assert "Flam. Liq. 2, H225" in comps[1]["siniflandirma"]
    assert "Skin Irrit. 2, H315" in comps[1]["siniflandirma"]
    assert "Repr. 2, H361d" in comps[1]["siniflandirma"]

    # Verify Section 4 first aid
    assert "fresh air" in translated["b4_ilk_yardim"]["b4_1"]["soluma"].lower()
    assert "water" in translated["b4_ilk_yardim"]["b4_1"]["goz_temasi"].lower()

    # Verify Section 9
    assert translated["b9_fiziksel_kimyasal_ozellikler"]["b9_1"]["fiziksel_durum"] == "Liquid"
    assert translated["b9_fiziksel_kimyasal_ozellikler"]["b9_1"]["renk"] == "Colourless"
    assert translated["b9_fiziksel_kimyasal_ozellikler"]["b9_1"]["koku"] == "Characteristic"

    # Verify Section 10
    assert translated["b10_kararlilik_tepkime"]["b10_2_kimyasal_kararlilik"] == "Stable under recommended storage and handling conditions."
