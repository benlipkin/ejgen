import typing

import numpy as np
from numpy.typing import NDArray
from sklearn.metrics import pairwise_distances

import model.embedding
from model.abstract import Object, IModel


class CentroidModel(Object, IModel):
    def __init__(self, embedding: str, smoothing: float | int, metric: str) -> None:
        super().__init__()
        self._embedder = getattr(model.embedding, embedding)()
        self._smoothing = smoothing
        self._metric = metric
        self._norm: float

    def _embed(self, words: typing.List[str]) -> NDArray[np.float32]:
        return self._embedder.embed(words)

    def fit(self, category: str, examples: typing.List[str]) -> None:
        self._category = category
        self._examples = examples
        self._seed_vectors = self._embed(self._examples)
        self._centroid = np.mean(self._seed_vectors, axis=0)
        self._norm = pairwise_distances(
            self._seed_vectors, [self._centroid], metric=self._metric
        ).max()
        self._slack = self._smoothing / np.sqrt(len(self._examples))
        # can adjust slack calculation later
        # maybe incorporate category embedding somehow when n=1?

    def _score(self, points: NDArray[np.float32]) -> NDArray[np.float32]:
        distances = pairwise_distances(points, [self._centroid]).flatten()
        normed = (1 - distances / self._norm) / self._slack
        normed[normed > 0] = 0
        return np.exp(-(normed**2))  # can adjust shape later

    def evaluate(self, targets: typing.List[str]) -> None:
        scores = self._score(self._embed(targets))
        for score, target in zip(scores, targets):
            self.info(f"Score for '{target}': {score}")

    def plot(self, targets: typing.List[str]) -> None:
        import matplotlib.pyplot as plt
        from sklearn.decomposition import PCA

        assert self._seed_vectors.shape[1] >= 3
        points = self._embed(targets)
        pca = PCA(n_components=3)
        pca.fit(np.vstack([self._seed_vectors, points]))
        vectors_3d = pca.transform(self._seed_vectors)
        points_3d = pca.transform(points)

        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        example_scores = self._score(self._seed_vectors)
        for target, vector_3d, score in zip(self._examples, vectors_3d, example_scores):
            color = np.array([1 - score, score, 0])
            ax.scatter(*vector_3d, color=color)
            ax.text(*vector_3d, f"{target} ({score:.2f})")
        target_scores = self._score(points)
        for target, point_3d, score in zip(targets, points_3d, target_scores):
            color = np.array([1 - score, score, 0])
            ax.scatter(*point_3d, color=color)
            ax.text(*point_3d, f"{target} ({score:.2f})")
        ax_min = np.min(np.vstack([vectors_3d, points_3d]))
        ax_max = np.max(np.vstack([vectors_3d, points_3d]))
        ax.set_xlim3d(ax_min, ax_max)
        ax.set_ylim3d(ax_min, ax_max)
        ax.set_zlim3d(ax_min, ax_max)
        plt.show()
