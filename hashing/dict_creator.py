import hashlib
from typing import Callable
import pdb
from tqdm import tqdm


sha1 = hashlib.sha1


def importSentences():
    with open('sentences.txt', 'r') as r:
        raw_sentences = r.read().strip().split('\n')

    return raw_sentences


def trimPunctuation(sentence):
    return [sentence.strip(' .?')]

def replaceXWithName(sentence, names: list[str]):
    return_values = []
    if not isinstance(names, list):
        names = [names]
    for name in names:
        return_values.append(sentence.replace('X', name))
        return_values.append(sentence.replace('X', name.lower()))
    return return_values

def getNamesFromFile():
    with open('names.txt', 'r') as r:
        return r.read().strip().split('\n')

def getAllCombinationsOfNames(names):
    results = []
    for name in names:
        for other_name in names:
            results.append(f"{name} and {other_name}")
    return results


def applyOperationToSentences(sentences: list[str], op: Callable, **kwargs):
    return_list = []
    for sentence in tqdm(sentences):
        return_list += op(sentence, **kwargs)
    return return_list


if __name__ == "__main__":
    raw_sentences = importSentences()
    print("Trimming Punctuation")
    raw_sentences = applyOperationToSentences(raw_sentences, trimPunctuation)
    raw_sentences = list(set(raw_sentences))

    print("Replacing X with single name")
    named_sentences = applyOperationToSentences(raw_sentences, replaceXWithName, names=getNamesFromFile())

    print("Replacing X with 2 names")
    combinations = getAllCombinationsOfNames(getNamesFromFile())
    double_named_sentences = applyOperationToSentences(raw_sentences, replaceXWithName, names=combinations)
    pdb.set_trace()
