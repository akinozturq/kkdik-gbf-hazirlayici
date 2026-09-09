import pytest
from app.services.transport_engine import transport_engine


def test_transport_engine_flammable_thinner():
    # Tiner karışımı: Parlama noktası 15°C, Kaynama noktası 78°C, H225
    sds_data = {
        "b9_fiziksel_kimyasal": {
            "b9_1": {
                "parlama_noktasi": "15",
                "kaynama_noktasi_araligi": "78"
            }
        },
        "b2_zarar_tanimi": {
            "b2_2": {
                "h_ifadeleri": ["H225", "H315"]
            }
        },
        "b3_bilesim": {
            "bilesenler": [
                {"ad": "Toluen", "konsantrasyon": 50},
                {"ad": "Aseton", "konsantrasyon": 50}
            ]
        }
    }

    res = transport_engine.evaluate_transport(sds_data, urun_adi="Polchem Selülozik Tiner")
    assert res["b14_1_un_numarasi"] == "UN 1263"
    assert res["b14_2_un_tasimacilik_adi"] == "BOYA İLE İLGİLİ MALZEME"
    assert res["b14_2_un_tasimacilik_adi_en"] == "PAINT RELATED MATERIAL"
    assert res["b14_3_tasimacilik_sinifi"] == "3 (Alevlenir Sıvılar)"
    assert res["b14_4_ambalajlama_grubu"] == "PG II"
    assert "(D/E)" in res["b14_6_kullanici_ozel_onlemler"]
    assert "Deniz Kirletici değildir" in res["b14_5_cevresel_zararlar"]


def test_transport_engine_flammable_low_boiling_point():
    # Çok alevlenir sıvı: Kaynama noktası <= 35°C -> PG I
    sds_data = {
        "b9_fiziksel_kimyasal": {
            "b9_1": {
                "parlama_noktasi": "-20",
                "kaynama_noktasi_araligi": "34"
            }
        },
        "b2_zarar_tanimi": {
            "b2_2": {
                "h_ifadeleri": ["H224"]
            }
        }
    }

    res = transport_engine.evaluate_transport(sds_data, urun_adi="Eter Karışımı")
    assert res["b14_1_un_numarasi"] == "UN 1993"
    assert res["b14_4_ambalajlama_grubu"] == "PG I"


def test_transport_engine_corrosive_liquid():
    # Aşındırıcı sıvı: H314 var, alevlenir değil
    sds_data = {
        "b9_fiziksel_kimyasal": {
            "b9_1": {
                "parlama_noktasi": "110",
                "kaynama_noktasi_araligi": "105"
            }
        },
        "b2_zarar_tanimi": {
            "b2_2": {
                "h_ifadeleri": ["H314"]
            }
        }
    }

    res = transport_engine.evaluate_transport(sds_data, urun_adi="Asidik Yüzey Temizleyici")
    assert res["b14_1_un_numarasi"] == "UN 1760"
    assert "AŞINDIRICI SIVI" in res["b14_2_un_tasimacilik_adi"]
    assert res["b14_3_tasimacilik_sinifi"] == "8 (Aşındırıcı Maddeler)"


def test_transport_engine_marine_pollutant():
    # Sucul zararlı: H410 var
    sds_data = {
        "b2_zarar_tanimi": {
            "b2_2": {
                "h_ifadeleri": ["H410"]
            }
        }
    }

    res = transport_engine.evaluate_transport(sds_data, urun_adi="Bakır Oksit Çözeltisi")
    assert res["b14_1_un_numarasi"] == "UN 3082"
    assert "Deniz Kirleticidir (Marine Pollutant - Evet)" in res["b14_5_cevresel_zararlar"]


def test_transport_engine_non_hazardous():
    # Su bazlı zararsız karışım
    sds_data = {
        "b9_fiziksel_kimyasal": {
            "b9_1": {
                "parlama_noktasi": "95"
            }
        },
        "b2_zarar_tanimi": {
            "b2_2": {
                "h_ifadeleri": []
            }
        }
    }

    res = transport_engine.evaluate_transport(sds_data, urun_adi="Su Bazlı Akrilik Boya")
    assert "tehlikeli madde değildir" in res["b14_1_un_numarasi"].lower()
    assert "Uygulanabilir değildir" in res["b14_2_un_tasimacilik_adi"]


def test_transport_engine_polyurethane_hardener():
    # Poliüretan Sertleştirici: Butil Asetat / Poliizosiyanat, PN: 27°C, KN: 126°C, H226
    sds_data = {
        "b9_fiziksel_kimyasal": {
            "b9_1": {
                "parlama_noktasi": "27",
                "kaynama_noktasi_araligi": "126"
            }
        },
        "b2_zarar_tanimi": {
            "b2_2": {
                "h_ifadeleri": ["H226", "H317", "H336"]
            }
        },
        "b3_bilesim": {
            "bilesenler": [
                {"ad": "n-Butil Asetat", "konsantrasyon": 50},
                {"ad": "Heksametilen diizosiyanat polimeri", "konsantrasyon": 50}
            ]
        }
    }

    res = transport_engine.evaluate_transport(sds_data, urun_adi="Polchem Poliüretan Parlak Sertleştirici")
    assert res["b14_1_un_numarasi"] == "UN 1263"
    assert res["b14_2_un_tasimacilik_adi"] == "BOYA İLE İLGİLİ MALZEME"
    assert res["b14_2_un_tasimacilik_adi_en"] == "PAINT RELATED MATERIAL"
    assert res["b14_3_tasimacilik_sinifi"] == "3 (Alevlenir Sıvılar)"
    assert res["b14_4_ambalajlama_grubu"] == "PG III"
    assert "(D/E)" in res["b14_6_kullanici_ozel_onlemler"]


def test_transport_engine_pure_paint():
    # Son kat boya: PN 21°C -> PG II
    sds_data = {
        "b9_fiziksel_kimyasal": {
            "b9_1": {
                "parlama_noktasi": "21",
                "kaynama_noktasi_araligi": "110"
            }
        },
        "b2_zarar_tanimi": {
            "b2_2": {
                "h_ifadeleri": ["H225"]
            }
        },
        "b3_bilesim": {
            "karisim": {
                "bilesenler": [
                    {"ad": "Ksilen", "konsantrasyon": 30},
                    {"ad": "Titanyum Dioksit", "konsantrasyon": 20}
                ]
            }
        }
    }

    res = transport_engine.evaluate_transport(sds_data, urun_adi="Polchem Poliüretan Parlak Beyaz Boya")
    assert res["b14_1_un_numarasi"] == "UN 1263"
    assert res["b14_2_un_tasimacilik_adi"] == "BOYA"
    assert res["b14_2_un_tasimacilik_adi_en"] == "PAINT"
    assert res["b14_4_ambalajlama_grubu"] == "PG II"


