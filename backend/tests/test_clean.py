"""Smoke tests for the cleaner."""
from ingest.clean import clean

_HTML = """
<html><head><title>Om oss - Compileit</title></head>
<body>
<nav>Meny</nav>
<main>
  <h1>Om oss</h1>
  <p>Compileit hjälper företag att bygga AI-lösningar. Vi har kontor i Stockholm
  och arbetar med kunder inom finans, industri och offentlig sektor.</p>
  <p>Vårt team består av erfarna ingenjörer och dataforskare som brinner för att
  leverera värde genom modern teknik.</p>
</main>
<footer>© Compileit</footer>
</body></html>
"""


def test_clean_extracts_main_content():
    result = clean("https://compileit.com/om-oss", _HTML)
    assert result is not None
    assert result.url == "https://compileit.com/om-oss"
    assert "Compileit" in result.title
    assert "Stockholm" in result.text
    assert "Meny" not in result.text  # nav stripped
