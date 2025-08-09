"""
Examples for README documentation.

Run with: python -m doctest examples.py -v
"""

from syllabreak import Syllabreak


def auto_detect_examples():
    """
    Auto-detect language examples.
    
    >>> s = Syllabreak("-")
    >>> s.syllabify("hello")
    'hel-lo'
    >>> s.syllabify("здраво")
    'здра-во'
    >>> s.syllabify("привет")
    'при-вет'
    """
    pass


def explicit_language_examples():
    """
    Specify language explicitly examples.
    
    >>> s = Syllabreak("-")
    >>> s.syllabify("problem", lang="eng")
    'pro-blem'
    >>> s.syllabify("problem", lang="srp-latn")
    'prob-lem'
    """
    pass


def language_detection_examples():
    """
    Language detection examples.
    
    >>> s = Syllabreak()
    >>> s.detect_language("hello")
    ['eng', 'srp-latn', 'tur']
    >>> s.detect_language("čovek")
    ['srp-latn', 'eng', 'tur']
    """
    pass