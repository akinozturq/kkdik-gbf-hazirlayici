"""
Pydantic 16 Bölümlük SDS Veri Modelleri Birim Testleri
"""

import pytest
from app.schemas.sds_sections import (
    SDSMeta,
    B1_Kimlik,
    B2_ZararTanimi,
    B3_Bilesim,
    B4_IlkYardim,
    B5_YanginMucadele,
    B6_KazaSonucuYayilma,
    B7_EllecmeDepolama,
    B8_MaruzKalmaKontrolu,
    B9_FizikselKimyasalOzellikler,
    B10_KararlilikTepkime,
    B11_Toksikolojik,
    B12_Ekolojik,
    B13_Bertaraf,
    B14_Tasimacilik,
    B15_Mevzuat,
    B16_DigerBilgiler,
    SDSModel,
    ClassificationItem,
    MixtureComponentItem
)


def test_sds_model_default_instantiation():
    """Boş SDSModel başlatıldığında 16 bölümün tamamı varsayılan alt modellerle oluşmalıdır."""
    sds = SDSModel()
    assert sds.meta.dil == "tr"
    assert sds.meta.versiyon_no == "1.0"
    assert sds.b1_kimlik is not None
    assert sds.b2_zarar_tanimi is not None
    assert sds.b3_bilesim is not None
    assert sds.b4_ilk_yardim is not None
    assert sds.b5_yangin_mucadele is not None
    assert sds.b6_kaza_sonucu_yayilma is not None
    assert sds.b7_ellecme_depolama is not None
    assert sds.b8_maruz_kalma_kontrolu is not None
    assert sds.b9_fiziksel_kimyasal_ozellikler is not None
    assert sds.b10_kararlilik_tepkime is not None
    assert sds.b11_toksikolojik is not None
    assert sds.b12_ekolojik is not None
    assert sds.b13_bertaraf is not None
    assert sds.b14_tasimacilik is not None
    assert sds.b15_mevzuat is not None
    assert sds.b16_diger_bilgiler is not None


def test_sds_model_serialization(sample_valid_sds_dict):
    """Geçerli bir SDS dict verisi SDSModel'e dönüştürülebilmeli ve geri serialize edilebilmelidir."""
    sds = SDSModel(**sample_valid_sds_dict)
    assert sds.b1_kimlik.b1_1.madde_karisim_adi == "Polyester Reçine Solüsyonu"
    assert sds.b2_zarar_tanimi.b2_2.uyari_kelimesi == "Dikkat"
    assert len(sds.b2_zarar_tanimi.b2_1.siniflandirmalar) == 3
    assert sds.b3_bilesim.tip == "karisim"
    assert len(sds.b3_bilesim.karisim.bilesenler) == 1
    assert sds.b14_tasimacilik.b14_1_un_numarasi == "UN 1866"

    dumped = sds.model_dump()
    assert dumped["b1_kimlik"]["b1_1"]["madde_karisim_adi"] == "Polyester Reçine Solüsyonu"
    assert dumped["b14_tasimacilik"]["b14_1_un_numarasi"] == "UN 1866"


def test_b3_substance_and_mixture_models():
    """Bileşim modellerinin alanları doğru tipte olmalıdır."""
    sds_madde = SDSModel(
        b3_bilesim=B3_Bilesim(
            tip="madde",
            madde={
                "kimyasal_kimlik": "Aseton",
                "cas_no": "67-64-1",
                "ec_no": "200-662-2",
                "safsizliklar": []
            }
        )
    )
    assert sds_madde.b3_bilesim.tip == "madde"
    assert sds_madde.b3_bilesim.madde.kimyasal_kimlik == "Aseton"
    assert sds_madde.b3_bilesim.madde.cas_no == "67-64-1"
