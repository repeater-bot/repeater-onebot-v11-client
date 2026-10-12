from typing import Hashable, Sequence, Protocol, TypeVar

class PROCESSOR(Protocol):
    def __call__(self, s: Sequence[Hashable]) -> Sequence[Hashable]:
        ...

HashableSequenceFirst = TypeVar("HashableSequenceFirst", contravariant=True, bound=Sequence[Hashable])
HashableSequenceSecond = TypeVar("HashableSequenceSecond", contravariant=True, bound=Sequence[Hashable])
ResultType = TypeVar("ResultType", int, float, contravariant=True)
Result = TypeVar("Result", int, float, covariant=True)

class SCORER(Protocol[HashableSequenceFirst, HashableSequenceSecond, ResultType, Result]):
    def __call__(
        self,
        __s1: HashableSequenceFirst,
        __s2: HashableSequenceSecond,
        *,
        score_cutoff: ResultType | None
    ) -> Result:
        ...