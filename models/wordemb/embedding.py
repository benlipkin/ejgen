import typing

import gensim.downloader as api
import numpy as np
from numpy.typing import NDArray

from models.wordemb.abstract import Object, IEmbedder


class Random(Object, IEmbedder):
    def embed(self, words: typing.List[str]) -> NDArray[np.float32]:
        return np.array([np.random.rand(128) for _ in words])


class GensimEmbedder(Object, IEmbedder):
    def __init__(self):
        super().__init__()
        self._vectors = api.load(self._id)

    @property
    def _id(self) -> str:
        raise NotImplementedError()

    def embed(self, words: typing.List[str]) -> NDArray[np.float32]:
        return np.array([self._vectors[word] for word in words])


class GloVe(GensimEmbedder):
    @property
    def _id(self) -> str:
        return "glove-wiki-gigaword-300"


class Word2Vec(GensimEmbedder):
    @property
    def _id(self) -> str:
        return "word2vec-google-news-300"


class FastText(GensimEmbedder):
    @property
    def _id(self) -> str:
        return "fasttext-wiki-news-subwords-300"


# consider incorporating transformers that use a contextualized embedding
# of the category conditioned on the form, "X, Y, Z, and other C"
