from rapidfuzz import fuzz, distance
from typing import Sequence, Hashable

import rapidfuzz

rapidfuzz.utils
class Ratios:
    """
    Calculates the similarity between two sequences.
    """
    def __init__(self, source: Sequence[Hashable], target: Sequence[Hashable]):
        self.source = source
        self.target = target

    def ratio(self) -> float:
        """
        Calculates the normalized Indel similarity.
        """
        return fuzz.ratio(self.source, self.target)

    def partial_ratio(self) -> float:
        """
        Searches for the optimal alignment of the shorter string in the longer string and returns the `fuzz.ratio` for this alignment.
        """
        return fuzz.partial_ratio(self.source, self.target)

    def partial_ratio_alignment(self) -> distance.ScoreAlignment | None:
        """
        Searches for the optimal alignment of the shorter string in the longer string and returns the `fuzz.ratio` and the corresponding alignment.
        """
        return fuzz.partial_ratio_alignment(self.source, self.target)

    def partial_token_ratio(self) -> float:
        """
        Helper method that returns the maximum of `fuzz.partial_token_set_ratio` and fuzz.partial_token_sort_ratio (faster than manually executing the two functions)
        """
        return fuzz.partial_token_ratio(self.source, self.target)

    def partial_token_set_ratio(self) -> float:
        """
        Calculates the token set ratio of the two input strings.
        """
        return fuzz.partial_token_set_ratio(self.source, self.target)

    def partial_token_sort_ratio(self) -> float:
        """
        Sorts the words in the strings and calculates the fuzz.partial_ratio between them.
        """
        return fuzz.partial_token_sort_ratio(self.source, self.target)

    def token_sort_ratio(self) -> float:
        """
        Sorts the words in the strings and calculates the fuzz.ratio between them.
        """
        return fuzz.token_sort_ratio(self.source, self.target)

    def token_set_ratio(self) -> float:
        """
        Compares the words in the strings based on unique and common words between them using `fuzz.ratio`.
        """
        return fuzz.token_set_ratio(self.source, self.target)

    def wratio(self) -> float:
        """
        Calculates a weighted ratio based on the other ratio algorithms
        """
        return fuzz.WRatio(self.source, self.target)

    def qratio(self) -> float:
        """
        Calculates a quick ratio between two strings using fuzz.ratio.

        Since v3.0 this behaves similar to fuzz.ratio with the exception that this returns 0 when comparing two empty strings
        """
        return fuzz.QRatio(self.source, self.target)