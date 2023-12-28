"""
Selects which keywords can be highlighted in a search result snippet on the
basis of query contents
"""

import re
import json
import numpy as np

from pqai.config.config import models_dir
from pqai.core.utils import is_generic
from pqai.core.vectorizers import SIFTextVectorizer

embed = SIFTextVectorizer().__getitem__

dictionary = json.load(open(models_dir + 'glove-dictionary.json'))
l_vocab = json.load(open(models_dir + 'glove-vocab.lemmas.json'))
l_variations = json.load(open(models_dir + 'glove-dictionary.variations.json'))

def variations(word):
    """Get syntactic variations of a word.

    Args:
        word (str): The word, e.g., "creating"

    Returns:
        list: Variations, e.g., ["create", "created", "creates", ... ]
    """
    if not word in dictionary:
        return [word]
    lemma = l_vocab[dictionary[word]]
    return l_variations[lemma]


def highlight(query, text):
    """Given a query, highlight some relevant words in the given text
    snippet which would help user judge the relevancy of the snippet for
    the given query.

    Args:
        query (str): Query
        text (str): Snippet of text.

    Returns:
        str: Snippet with relevant words wrapped in <strong></strong>
            tags (to show as html).
    """
    words = list(set(re.findall(r'[a-z]+', query.lower())))
    terms = list(set(re.findall(r'[a-z]+', text.lower())))

    words = [word for word in words if not is_generic(word)]
    terms = [term for term in terms if not is_generic(term)]

    qvecs = [embed(word) for word in words]
    tvecs = [embed(term) for term in terms]

    qvecs = qvecs / np.linalg.norm(qvecs, ord=2, axis=1, keepdims=True)
    tvecs = tvecs / np.linalg.norm(tvecs, ord=2, axis=1, keepdims=True)

    sims = np.matmul(qvecs, tvecs.transpose())
    to_highlight = []
    for i in range(sims.shape[0]):
        j = np.argmax(sims[i])
        if sims[i][j] > 0.6:
            to_highlight.append(terms[j])

    replacement = '<dGn9zx>\\1</dGn9zx>'
    for term in to_highlight:
        pattern = r'\b(' + term + r')\b'
        text = re.sub(pattern, replacement, text, count=1, flags=re.IGNORECASE)

    while True:
        flag = False
        matches = re.findall(r'([a-z]+)\s\<dGn9zx\>', text, re.IGNORECASE)
        for match in matches:
            if not is_generic(match.lower()):
                flag = True
                pattern = match + ' <dGn9zx>'
                replacement = '<dGn9zx>' + match + ' '
                text = re.sub(pattern, replacement, text, count=1, flags=re.IGNORECASE)
        if not flag:
            break

    while True:
        flag = False
        matches = re.findall(r'\<\/dGn9zx\>\s([a-z]+)', text, re.IGNORECASE)
        for match in matches:
            if not is_generic(match.lower()):
                flag = True
                pattern = f'</dGn9zx> {match}'
                replacement = f' {match}</dGn9zx>'
                text = re.sub(pattern, replacement, text, count=1, flags=re.IGNORECASE)
        if not flag:
            break

    text = re.sub(r'dGn9zx', 'strong', text)
    return (text, to_highlight)
