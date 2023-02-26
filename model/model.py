import typing

import numpy as np
from numpy.typing import NDArray
from scipy.spatial import ConvexHull
from sklearn.metrics import pairwise_distances

import model.embedding
from model.abstract import Object, IModel


class Model(Object, IModel):
    def __init__(
        self, embedding: str, dimension: int, smoothing: float | int, samples: int
    ) -> None:
        super().__init__()
        self._embedder = getattr(model.embedding, embedding)()
        if dimension > 0:
            from sklearn.random_projection import GaussianRandomProjection

            self._projection = GaussianRandomProjection(n_components=dimension)
            self._projection.fit(self._embedder.embed(["a"]))
        self._smoothing = smoothing
        self._samples = samples
        self._norm: float

    def _embed(self, words: typing.List[str]) -> NDArray[np.float32]:
        if not hasattr(self, "_projection"):
            return self._embedder.embed(words)
        return self._projection.transform(self._embedder.embed(words))

    def fit(self, category: str, examples: typing.List[str]) -> None:
        self._category = category
        self._examples = examples
        self._n = len(self._examples)
        self._seed_vectors = self._embed(self._examples)
        self._centroid = np.mean(self._seed_vectors, axis=0)
        self._scale = np.max(pairwise_distances(self._seed_vectors))
        self._slack = self._scale * self._smoothing
        # incorporate n_examples and category frequency into slack calculation
        # e.g., slack = scale * smoothing * f(normed_category_frequency) / f(n_examples)
        # maybe incorporate category embedding into scale calculation for when n=1?
        # also consider customizing distance metric at least for centroid model
        # relatedly might drop convex hull model due to computational concerns in high dimensions

    def _calc_proximity(self, points: NDArray[np.float32]) -> NDArray[np.float32]:
        raise NotImplementedError()

    def _score(self, points: NDArray[np.float32]) -> NDArray[np.float32]:
        proximity = self._calc_proximity(points)
        assert 0 <= np.min(proximity) and np.max(proximity) <= 1
        return proximity  # tweak shape later

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


class ConvexHullModel(Model):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._hull: ConvexHull

    def _sample_jitter(self):
        jitter = np.vstack(
            [
                np.tile(
                    np.random.normal(size=self._seed_vectors.shape[1]).reshape(-1, 1),
                    self._seed_vectors.shape[0],
                ).T
                for _ in range(self._samples)
            ]
        )
        return jitter / np.linalg.norm(jitter, axis=1).reshape(-1, 1)

    def _build_convex_hull(self) -> ConvexHull:
        return ConvexHull(
            np.vstack([self._seed_vectors for _ in range(self._samples)])
            + self._slack * self._jitter
        )

    def fit(self, category: str, examples: typing.List[str]) -> None:
        super().fit(category, examples)
        self._jitter = self._sample_jitter()
        self._hull = self._build_convex_hull()
        self._norm = self._distance_to_hull(self._centroid)

    def _distance_to_hull(self, point: NDArray[np.float32]) -> float:
        distances = point @ self._hull.equations[:, :-1].T + self._hull.equations[:, -1]
        return np.min(-distances)

    def _calc_proximity(self, points: NDArray[np.float32]) -> NDArray[np.float32]:
        distances = np.array([self._distance_to_hull(point) for point in points])
        return np.clip(distances / self._norm, 0, 1)


class CentroidModel(Model):
    def fit(self, category: str, examples: typing.List[str]) -> None:
        super().fit(category, examples)
        self._norm = np.max(pairwise_distances(self._seed_vectors, [self._centroid]))

    def _calc_proximity(self, points: NDArray[np.float32]) -> NDArray[np.float32]:
        distances = pairwise_distances(points, [self._centroid]).flatten()
        return 1 - np.clip((distances - self._norm) / self._norm, 0, 1)
