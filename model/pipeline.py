import typing

import model.embedding
import model.model
from model.abstract import Object


class Pipeline(Object):
    def __init__(
        self,
        category: str,
        examples: typing.Tuple[str],
        targets: typing.Tuple[str],
        modeltype: str,
        smoothing: float | int,
        embedding: str,
        dimension: int = 0,
        samples: int = 0,
    ) -> None:
        super().__init__()
        assert isinstance(category, str)
        assert isinstance(examples, tuple)
        assert all(isinstance(example, str) for example in examples)
        assert isinstance(targets, tuple)
        assert all(isinstance(target, str) for target in targets)
        assert isinstance(modeltype, str)
        assert modeltype in dir(model.model)
        assert any(isinstance(smoothing, t) for t in (float, int))
        assert smoothing > 0
        assert isinstance(embedding, str)
        assert embedding in dir(model.embedding)
        assert isinstance(dimension, int)
        assert dimension >= 0
        assert isinstance(samples, int)
        assert samples >= 0
        self._category = category
        self._examples = list(examples)
        self._targets = list(targets)
        self._model = getattr(model.model, modeltype)(
            embedding, dimension, smoothing, samples
        )

    def run(self, mode) -> None:
        assert mode in ("eval", "plot")
        self._model.fit(self._category, self._examples)
        if mode == "eval":
            self._model.evaluate(self._targets)
        elif mode == "plot":
            self._model.plot(self._targets)
