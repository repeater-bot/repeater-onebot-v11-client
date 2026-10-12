import numpy as np
from typing import Any, Iterable, Sequence, Hashable, Generator
from rapidfuzz import process, fuzz
from .typings import SCORER

class FuzzyMatch:
    """
    Fuzzy matching datas.
    """
    def __init__(self, data: Iterable[Sequence[Hashable]]):
        self.data = data

    def most_similar(
            self,
            text: Sequence[Hashable],
            *,
            scorer: SCORER[Sequence[Hashable], Sequence[Hashable], float, float] = fuzz.WRatio,
            processor: None = None,
            score_cutoff: None = None,
            score_hint: float | None = None,
            scorer_kwargs: dict[str, Any] | None = None
        ) -> tuple[Sequence[Hashable], float, int] | tuple[None, None, None]:
        """
        Match the most similar string to the given text.

        :param text: The text to match
        :param processor: The processor to use
        :param scorer: The scorer to use
        :param score_cutoff: The minimum score to match
        :param score_hint: The score hint to use
        :param scorer_kwargs: The scorer kwargs to use
        :return: The most similar string, similarity score, and index
        """
        target_string, similarity, index = process.extractOne(
            query = text,
            choices = self.data,

            scorer = scorer,
            processor = processor,
            score_cutoff = score_cutoff,
            score_hint = score_hint,
            scorer_kwargs = scorer_kwargs
        )
        return target_string, similarity, index

    def most_similar_n(
            self,
            text: Sequence[Hashable],
            *,
            scorer: SCORER[Sequence[Hashable], Sequence[Hashable], float, float] = fuzz.WRatio,
            processor: None = None,
            limit: int | None = 5,
            score_cutoff: float | None = None,
            score_hint: float | None = None,
            scorer_kwargs: dict[str, Any] | None = None
        ) -> list[tuple[Sequence[Hashable], float, int]]:
        """
        Match the most similar n strings to the given text.

        :param text: The text to match
        :param scorer: The scorer function to use
        :param processor: The processor function to use
        :param limit: The maximum number of results to return
        :param score_cutoff: The minimum similarity score to return
        :param score_hint: A hint to the scorer function
        :param scorer_kwargs: Additional keyword arguments to pass to the scorer function
        :return: A list of tuples containing the most similar strings, similarity scores, and indices
        """
        return process.extract(
            query=text,
            choices = self.data,
            scorer = scorer,
            processor = processor,
            limit = limit,
            score_cutoff = score_cutoff,
            score_hint = score_hint,
            scorer_kwargs = scorer_kwargs
        )
    
    def most_similar_n_iter(
            self,
            text: Sequence[Hashable],
            *,
            scorer: SCORER[Sequence[Hashable], Sequence[Hashable], float, float] = fuzz.WRatio,
            processor: None = None,
            score_cutoff: float | None = None,
            score_hint: float | None = None,
            scorer_kwargs: dict[str, Any] | None = None
        ) -> Generator[tuple[Sequence[Hashable], float, int], None, None]:
        """
        Match the most similar n strings to the given text.

        :param text: The text to match
        :param scorer: The scorer function to use
        :param processor: The processor to use
        :param score_cutoff: The minimum similarity score to return
        :param score_hint: A hint for the scorer function
        :param scorer_kwargs: Additional keyword arguments for the scorer function
        :return: A list of tuples containing the most similar strings, similarity scores, and indices
        """
        return process.extract_iter(
            query = text,
            choices = self.data,
            scorer = scorer,
            processor = processor,
            score_cutoff = score_cutoff,
            score_hint = score_hint,
            scorer_kwargs = scorer_kwargs
        )

    def compute_similarity_matrix(
            self,
            other: Iterable[Sequence[Hashable]],
            *,
            scorer: SCORER[Sequence[Hashable], Sequence[Hashable], float, float] = fuzz.ratio,
            processor: None = None,
            score_cutoff: float | None = None,
            score_hint: float | None = None,
            score_multiplier: float = 1,
            dtype: np.typing.DTypeLike | None = None,
            workers: int = 1,
            scorer_kwargs: dict[str, Any] | None = None
        ) -> np.typing.NDArray[Any]:
        """
        Compute distance/similarity between each pair of the two collections of inputs.

        :param other: The other collection of inputs
        :param scorer: The scorer to use
        :param processor: The processor to use
        :param score_cutoff: The minimum score to include a match
        :param score_hint: A hint for the scorer to optimize its performance
        :param score_multiplier: A multiplier for the scores
        :param dtype: The data type to use for the output matrix
        :param workers: The calculation is subdivided into workers sections and evaluated in parallel. Supply -1 to use all available CPU cores. This argument is only available for scorers using the RapidFuzz C-API so far, since it releases the Python GIL.
        :param scorer_kwargs: Additional keyword arguments to pass to the scorer
        :return: Returns a matrix of dtype with the distance/similarity between each pair of the two collections of inputs.
        """
        return process.cdist(
            other,
            self.data,
            scorer = scorer,
            processor = processor,
            score_cutoff = score_cutoff,
            score_hint = score_hint,
            score_multiplier = score_multiplier,
            dtype = dtype,
            workers = workers,
            scorer_kwargs = scorer_kwargs
        )

    def compute_similarity(
            self,
            other: Iterable[Sequence[Hashable]],
            scorer: SCORER[Sequence[Hashable], Sequence[Hashable], float, float] = fuzz.ratio,
            processor: None = None,
            score_cutoff: float | None = None,
            score_hint: float | None = None,
            score_multiplier: float = 1,
            dtype: np.typing.DTypeLike | None = None,
            workers: int = 1,
            scorer_kwargs: dict[str, Any] | None = None
        ) -> np.typing.NDArray[Any]:
        """
        Compute distance/similarity between each pair of the two collections of inputs.

        :param other: The other collection of inputs
        :param scorer: The scorer to use for computing the distance/similarity.
        :param processor: The processor to use for processing the inputs.
        :param score_cutoff: The minimum score to include in the output.
        :param score_hint: A hint for the scorer to use for optimizing the computation.
        :param score_multiplier: A multiplier for the score.
        :param dtype: The data type of the output array.
        :param workers: The number of workers to use for computation. Supply -1 to use all available CPU cores. This argument is only available for scorers using the RapidFuzz C-API so far, since it releases the Python GIL.
        :param scorer_kwargs: Additional keyword arguments to pass to the scorer.
        :return: Returns a matrix of size (n x 1) of dtype with the distance/similarity between each pair of the two collections of inputs
        """
        return process.cpdist(
            other,
            self.data,
            scorer = scorer,
            processor = processor,
            score_cutoff = score_cutoff,
            score_hint = score_hint,
            score_multiplier = score_multiplier,
            dtype = dtype,
            workers = workers,
            scorer_kwargs = scorer_kwargs
        )