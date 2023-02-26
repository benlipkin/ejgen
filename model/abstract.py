import abc
import logging
import pathlib
import typing

import numpy as np
from numpy.typing import NDArray


class Object(abc.ABC):
    def __init__(self) -> None:
        self._base = pathlib.Path(__file__).parents[1]
        self._name = self.__class__.__name__
        self._logger = logging.getLogger(self._name)

    def _log(self, message: str, level: str, offset: int) -> None:
        assert hasattr(self._logger, level)
        if "\n" in message:
            lines = message.split("\n")
        else:
            lines = [message]
        for line in lines:
            formatted = f"{' ' * (offset - len(self._name))}{line}"
            getattr(self._logger, level)(formatted)

    def info(self, message: str) -> None:
        self._log(message, "info", 20)

    def warn(self, message: str) -> None:
        self._log(message, "warning", 17)

    def __setattr__(self, name: str, value: typing.Any) -> None:
        super().__setattr__(name, value)

    def __getattribute__(self, name: str) -> typing.Any:
        return super().__getattribute__(name)


@typing.runtime_checkable
class IEmbedder(typing.Protocol):
    def embed(self, words: typing.List[str]) -> NDArray[np.float32]:
        raise NotImplementedError()  # pragma: no cover


@typing.runtime_checkable
class IModel(typing.Protocol):
    def fit(self, category: str, examples: typing.List[str]) -> None:
        raise NotImplementedError()  # pragma: no cover

    def evaluate(self, targets: typing.List[str]) -> None:
        raise NotImplementedError()  # pragma: no cover

    def plot(self, targets: typing.List[str]) -> None:
        raise NotImplementedError()  # pragma: no cover

