from rapidfuzz import distance
from typing import Sequence, Hashable

class Distances:
    """
    Calculate various distances between two sequences.
    """
    def __init__(self, source: Sequence[Hashable], target: Sequence[Hashable]):
        self.source = source
        self.target = target

    def levenshtein_distance(self):
        """
        Calculate the Levenshtein distance between the source and target sequences.
        """
        return distance.Levenshtein.distance(self.source, self.target)

    def levenshtein_normalized_distance(self):
        """
        Calculate the normalized Levenshtein distance between the source and target sequences.
        """
        return distance.Levenshtein.normalized_distance(self.source, self.target)
    
    def levenshtein_similarity(self):
        """
        Calculate the Levenshtein similarity between the source and target sequences.
        """
        return distance.Levenshtein.similarity(self.source, self.target)

    def levenshtein_normalized_similarity(self):
        """
        Calculate the normalized Levenshtein similarity between the source and target sequences.
        """
        return distance.Levenshtein.normalized_similarity(self.source, self.target)

    def levenshtein_editops(self) -> distance.Editops:
        """
        Calculate the Levenshtein edit operations between the source and target sequences.
        """
        return distance.Levenshtein.editops(self.source, self.target)

    def levenshtein_opcodes(self) -> distance.Opcodes:
        """
        Calculate the Levenshtein opcodes between the source and target sequences.
        """
        return distance.Levenshtein.opcodes(self.source, self.target)

    def damerau_levenshtein_distance(self) -> int:
        """
        Calculate the Damerau-Levenshtein distance between the source and target sequences.
        """
        return distance.DamerauLevenshtein.distance(self.source, self.target)

    def damerau_levenshtein_similarity(self) -> int:
        """
        Calculate the Damerau-Levenshtein edit operations between the source and target sequences.
        """
        return distance.DamerauLevenshtein.similarity(self.source, self.target)

    def damerau_levenshtein_normalized_distance(self) -> float:
        """
        Calculate the normalized Damerau-Levenshtein distance between the source and target sequences.
        """
        return distance.DamerauLevenshtein.normalized_distance(self.source, self.target)

    def damerau_levenshtein_normalized_similarity(self) -> float:
        """
        Calculate the normalized Damerau-Levenshtein similarity between the source and target sequences.
        """
        return distance.DamerauLevenshtein.normalized_similarity(self.source, self.target)

    def hamming_distance(self) -> int:
        """
        Calculate the Hamming distance between the source and target sequences.
        """
        return distance.Hamming.distance(self.source, self.target)

    def hamming_similarity(self) -> float:
        """
        Calculate the Hamming similarity between the source and target sequences.
        """
        return distance.Hamming.similarity(self.source, self.target)

    def hamming_normalized_distance(self) -> float:
        """
        Calculate the normalized Hamming distance between the source and target sequences.
        """
        return distance.Hamming.normalized_distance(self.source, self.target)

    def hamming_normalized_similarity(self) -> float:
        """
        Calculate the normalized Hamming similarity between the source and target sequences.
        """
        return distance.Hamming.normalized_similarity(self.source, self.target)

    def hamming_editops(self) -> distance.Editops:
        """
        Calculate the edit operations (insertions, deletions, substitutions) required to transform the source sequence into the target sequence.
        """
        return distance.Hamming.editops(self.source, self.target)

    def hamming_opcodes(self) -> distance.Opcodes:
        """
        Calculate the opcodes required to transform the source sequence into the target sequence.
        """
        return distance.Hamming.opcodes(self.source, self.target)

    def indel_distance(self) -> float:
        """
        Calculate the Indel distance between the source and target sequences.
        """
        return distance.Indel.distance(self.source, self.target)

    def indel_normalized_distance(self) -> float:
        """
        Calculate the normalized Indel distance between the source and target sequences.
        """
        return distance.Indel.normalized_distance(self.source, self.target)

    def indel_similarity(self) -> float:
        """
        Calculate the Indel similarity between the source and target sequences.
        """
        return distance.Indel.similarity(self.source, self.target)

    def indel_normalized_similarity(self) -> float:
        """
        Calculate the normalized Indel similarity between the source and target sequences.
        """
        return distance.Indel.normalized_similarity(self.source, self.target)

    def indel_editops(self) -> distance.Editops:
        """
        Calculate the Editops between the source and target sequences.
        """
        return distance.Indel.editops(self.source, self.target)

    def indel_opcodes(self) -> distance.Opcodes:
        """
        Calculate the Opcodes between the source and target sequences.
        """
        return distance.Indel.opcodes(self.source, self.target)

    def jaro_distance(self) -> float:
        """
        Calculate the Jaro distance between the source and target sequences.
        """
        return distance.Jaro.distance(self.source, self.target)

    def jaro_similarity(self) -> float:
        """
        Calculate the Jaro similarity between the source and target sequences.
        """
        return distance.Jaro.similarity(self.source, self.target)

    def jaro_normalized_distance(self) -> float:
        """
        Calculate the Jaro normalized distance between the source and target sequences.
        """
        return distance.Jaro.normalized_distance(self.source, self.target)

    def jaro_normalized_similarity(self) -> float:
        """
        Calculate the Jaro normalized similarity between the source and target sequences.
        """
        return distance.Jaro.normalized_similarity(self.source, self.target)

    def jaro_winkler_distance(self) -> float:
        """
        Calculate the Jaro-Winkler distance between the source and target sequences.
        """
        return distance.JaroWinkler.distance(self.source, self.target)

    def jaro_winkler_similarity(self) -> float:
        """
        Calculate the Jaro-Winkler similarity between the source and target sequences.
        """
        return distance.JaroWinkler.similarity(self.source, self.target)

    def jaro_winkler_normalized_distance(self) -> float:
        """
        Calculate the Jaro-Winkler normalized distance between the source and target sequences.
        """
        return distance.JaroWinkler.normalized_distance(self.source, self.target)

    def jaro_winkler_normalized_similarity(self) -> float:
        """
        Calculate the Jaro-Winkler normalized similarity between the source and target sequences.
        """
        return distance.JaroWinkler.normalized_similarity(self.source, self.target)

    def osa_distance(self) -> float:
        """
        Calculate the OSA distance between the source and target sequences.
        """
        return distance.OSA.distance(self.source, self.target)

    def osa_similarity(self) -> float:
        """
        Calculate the OSA similarity between the source and target sequences.
        """
        return distance.OSA.similarity(self.source, self.target)

    def osa_normalized_distance(self) -> float:
        """
        Calculate the OSA normalized distance between the source and target sequences.
        """
        return distance.OSA.normalized_distance(self.source, self.target)

    def osa_normalized_similarity(self) -> float:
        """
        Calculate the OSA normalized similarity between the source and target sequences.
        """
        return distance.OSA.normalized_similarity(self.source, self.target)

    def prefix_distance(self) -> int:
        """
        Calculate the prefix distance between the source and target sequences.
        """
        return distance.Prefix.distance(self.source, self.target)

    def prefix_similarity(self) -> float:
        """
        Calculate the prefix similarity between the source and target sequences.
        """
        return distance.Prefix.similarity(self.source, self.target)

    def prefix_normalized_distance(self) -> float:
        """
        Calculate the prefix normalized distance between the source and target sequences.
        """
        return distance.Prefix.normalized_distance(self.source, self.target)

    def prefix_normalized_similarity(self) -> float:
        """
        Calculate the prefix normalized similarity between the source and target sequences.
        """
        return distance.Prefix.normalized_similarity(self.source, self.target)

    def postfix_distance(self) -> int:
        """
        Calculate the postfix distance between the source and target sequences.
        """
        return distance.Postfix.distance(self.source, self.target)

    def postfix_similarity(self) -> float:
        """
        Calculate the postfix similarity between the source and target sequences.
        """
        return distance.Postfix.similarity(self.source, self.target)

    def postfix_normalized_distance(self) -> float:
        """
        Calculate the postfix normalized distance between the source and target sequences.
        """
        return distance.Postfix.normalized_distance(self.source, self.target)

    def postfix_normalized_similarity(self) -> float:
        """
        Calculate the postfix normalized similarity between the source and target sequences.
        """
        return distance.Postfix.normalized_similarity(self.source, self.target)