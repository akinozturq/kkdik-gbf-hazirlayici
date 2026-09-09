import pytest
from app.services.phrase_service import phrase_service


def test_phrase_service_loads_all():
    phrases = phrase_service.get_phrases()
    assert len(phrases) >= 15
    for p in phrases:
        assert "id" in p
        assert "section" in p
        assert "text_tr" in p
        assert "text_en" in p


def test_phrase_service_filter_by_section():
    b4_phrases = phrase_service.get_phrases(section="b4")
    assert len(b4_phrases) >= 5
    for p in b4_phrases:
        assert p["section"] == "b4"

    b7_phrases = phrase_service.get_phrases(section="b7")
    assert len(b7_phrases) >= 2
    for p in b7_phrases:
        assert p["section"] == "b7"


def test_phrase_service_filter_by_subfield():
    inh_phrases = phrase_service.get_phrases(section="b4", subfield="soluma")
    assert len(inh_phrases) >= 1
    assert any("temiz havaya" in p["text_tr"].lower() for p in inh_phrases)


def test_phrase_service_search_query():
    results = phrase_service.get_phrases(query="nitril")
    assert len(results) >= 1
    assert any("en 374" in r["text_tr"].lower() for r in results)

    # İngilizce metin araması
    results_en = phrase_service.get_phrases(query="breathing")
    assert len(results_en) >= 1
