"""Test README.md code examples."""

import re
from pathlib import Path

import pytest


def extract_python_code_blocks(markdown_text):
    """Extract Python code blocks from markdown."""
    pattern = r"```python\n(.*?)\n```"
    blocks = re.findall(pattern, markdown_text, re.DOTALL)
    return blocks


def test_readme_examples():
    """Test all Python code examples in README.md."""
    readme_path = Path(__file__).parent / "README.md"
    readme_text = readme_path.read_text()
    
    code_blocks = extract_python_code_blocks(readme_text)
    
    # We should have at least some examples
    assert len(code_blocks) > 0, "No Python code blocks found in README.md"
    
    # Import what we need for examples
    from syllabreak import Syllabreak
    
    for i, code in enumerate(code_blocks):
        # Skip import lines as they're already done
        lines = [line for line in code.split('\n') if not line.strip().startswith('from ') and not line.strip().startswith('import ')]
        
        # Create a namespace for execution
        namespace = {'Syllabreak': Syllabreak}
        
        # Process each line as if it were in interactive mode
        for line in lines:
            if line.startswith('>>> '):
                # This is a command
                cmd = line[4:]
                if cmd.strip():
                    try:
                        result = eval(cmd, namespace)
                        if result is not None:
                            namespace['_'] = result
                    except:
                        exec(cmd, namespace)
            elif line.startswith("'") and not line.startswith('...'):
                # This is expected output
                expected = eval(line)
                if '_' in namespace:
                    actual = namespace['_']
                    assert actual == expected, f"Block {i}: Expected {expected!r}, got {actual!r}"