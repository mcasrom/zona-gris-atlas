from zonagris.dedupe import dedupe_rows, similarity, text_hash, url_hash


def test_hash_is_stable_for_same_url():
    assert url_hash("https://example.org/a#x") == url_hash("https://example.org/a")


def test_text_hash_ignores_urls_and_case():
    assert text_hash("Hola https://example.org") == text_hash("hola")


def test_similarity_detects_repeated_title():
    assert similarity("Corte de red en el norte", "Corte de red en el norte.") > 0.9
    assert similarity("Corte de red", "Aumento del precio del trigo") < 0.5


def test_dedupe_rows_keeps_one():
    rows = [
        {"title": "Corte de red en el norte"},
        {"title": "Corte de red en el norte."},
        {"title": "Aumento del precio del trigo"},
    ]
    assert len(dedupe_rows(rows)) == 2
