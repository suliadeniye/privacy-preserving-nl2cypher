import re

def deobfuscate_query(query):
    # Multi-character patterns first (ordered)
    multi_char_subs = {
        '!!': 'll',
        '11': 'll',
        'l1': 'll',
        '1l': 'll',
        '3e': 'ee',
    }

    # Single-character substitutions
    char_subs = {
        '@': 'a',
        '0': 'o',
        '1': 'l',
        '3': 'e',
        '5': 's',
        '7': 't',
        '$': 's',
        '!': 'l',
    }
    
    def apply_substitutions(word):
        if word.isdigit():
            return word

        # First apply multi-character substitutions
        for pattern, replacement in multi_char_subs.items():
            word = word.replace(pattern, replacement)

        # Then apply single-character substitutions
        return ''.join(char_subs.get(c, c) for c in word)

    # Tokenize as before to preserve spacing and punctuation
    tokens = re.findall(r'[^\s]+|\s+', query)
    result = []

    for token in tokens:
        if any(c.isalpha() for c in token):
            result.append(apply_substitutions(token))
        else:
            result.append(token)

    return ''.join(result)

    