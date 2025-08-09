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
