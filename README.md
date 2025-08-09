# syllabreak

[![Tests](https://github.com/apakabarfm/syllabreak/actions/workflows/tests.yml/badge.svg)](https://github.com/apakabarfm/syllabreak/actions/workflows/tests.yml)

Multilingual library for accurate and deterministic hyphenation and syllable counting without relying on dictionaries.

## Usage

```python
>>> from syllabreak import Syllabreak
>>> s = Syllabreak("-")
>>> s.syllabify("hello")
'hel-lo'
>>> s.detect_language("hello")
['en']
```

## Language Detection

The library returns all matching languages sorted by confidence:

```python
>>> from syllabreak import Syllabreak
>>> s = Syllabreak()
>>> s.detect_language("hello")
['eng', 'srp-latn']  # Matches both English and Serbian Latin
>>> s.detect_language("čovek")
['srp-latn']  # Serbian Latin with unique letter č
```
