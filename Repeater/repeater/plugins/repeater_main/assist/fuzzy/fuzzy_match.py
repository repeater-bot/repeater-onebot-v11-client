import numpy as np
from typing import Any, Iterable, Sequence, Hashable, Generator
from rapidfuzz import process

class FuzzyMatch:
    """
    Fuzzy matching datas.
    """
    def __init__(self, data: Iterable[Sequence[Hashable]]):
        self.data = data

    def most_similar(self, text: Sequence[Hashable]) -> tuple[Sequence[Hashable], float, int] | tuple[None, None, None]:
        """
        Match the most similar string to the given text.

        :param text: The text to match
        :return: The most similar string, similarity score, and index
        """
        target_string, similarity, index = process.extractOne(
            text,
            self.data
        )
        return target_string, similarity, index

    def most_similar_n(self, text: Sequence[Hashable], n: int) -> list[tuple[Sequence[Hashable], float, int]]:
        """
        Match the most similar n strings to the given text.

        :param text: The text to match
        :param n: The number of matches to return
        :return: A list of tuples containing the most similar strings, similarity scores, and indices
        """
        return process.extract(text, self.data, limit=n)
    
    def most_similar_n_iter(self, text: Sequence[Hashable]) -> Generator[tuple[Sequence[Hashable], float, int], None, None]:
        """
        Match the most similar n strings to the given text.

        :param text: The text to match
        :param n: The number of matches to return
        :return: A list of tuples containing the most similar strings, similarity scores, and indices
        """
        return process.extract_iter(text, self.data)

    def compute_similarity_matrix(
            self,
            other: Iterable[Sequence[Hashable]],
            dtype: np.typing.DTypeLike | None = None,
            workers: int = 1
        ) -> np.typing.NDArray[Any]:
        """
        Compute distance/similarity between each pair of the two collections of inputs.

        :param other: The other collection of inputs
        :param dtype: The data type of the output array
        :param workers: The calculation is subdivided into workers sections and evaluated in parallel. Supply -1 to use all available CPU cores. This argument is only available for scorers using the RapidFuzz C-API so far, since it releases the Python GIL.
        """
        return process.cdist(self.data, other, dtype = dtype)

    def compute_similarity(
            self,
            other: Iterable[Sequence[Hashable]],
            dtype: np.typing.DTypeLike | None = None,
            workers: int = 1
        ) -> np.typing.NDArray[Any]:
        """
        Compute distance/similarity between each pair of the two collections of inputs.

        :param other: The other collection of inputs
        :param dtype: The data type of the output array.
        :param workers: The number of workers to use for computation. Supply -1 to use all available CPU cores. This argument is only available for scorers using the RapidFuzz C-API so far, since it releases the Python GIL.
        """
        return process.cpdist(self.data, other, dtype = dtype, workers = workers)