"""Small undirected simple graph contract (stdlib-only foundation)."""
from __future__ import annotations

from dataclasses import dataclass, field
from collections import deque


@dataclass
class Graph:
    """Symmetric adjacency sets, with explicit isolated nodes."""

    adjacency: dict[int, set[int]] = field(default_factory=dict)

    @classmethod
    def with_nodes(cls, n: int) -> "Graph":
        if n < 0:
            raise ValueError("number of nodes must be nonnegative")
        return cls({i: set() for i in range(n)})

    @property
    def n(self) -> int:
        return len(self.adjacency)

    @property
    def m(self) -> int:
        return sum(map(len, self.adjacency.values())) // 2

    def add_edge(self, u: int, v: int) -> None:
        if u == v:
            raise ValueError("simple graph disallows self-loops")
        if u not in self.adjacency or v not in self.adjacency:
            raise KeyError("edge endpoint is not in graph")
        self.adjacency[u].add(v)
        self.adjacency[v].add(u)

    def remove_edge(self, u: int, v: int) -> None:
        self.adjacency[u].remove(v)
        self.adjacency[v].remove(u)

    def edges(self) -> list[tuple[int, int]]:
        return [(u, v) for u in sorted(self.adjacency) for v in sorted(self.adjacency[u]) if u < v]

    def validate(self) -> None:
        for u, nbrs in self.adjacency.items():
            if u in nbrs:
                raise ValueError("graph contains a self-loop")
            for v in nbrs:
                if v not in self.adjacency or u not in self.adjacency[v]:
                    raise ValueError("graph contains an asymmetric edge")

    def components(self) -> list[set[int]]:
        unseen = set(self.adjacency)
        result: list[set[int]] = []
        while unseen:
            start = min(unseen)
            comp = {start}
            queue = deque([start])
            unseen.remove(start)
            while queue:
                u = queue.popleft()
                for v in sorted(self.adjacency[u]):
                    if v in unseen:
                        unseen.remove(v)
                        comp.add(v)
                        queue.append(v)
            result.append(comp)
        return sorted(result, key=lambda c: (-len(c), min(c)))

    def distances(self, source: int, allowed: set[int] | None = None) -> dict[int, int]:
        d = {source: 0}
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for v in self.adjacency[u]:
                if v not in d and (allowed is None or v in allowed):
                    d[v] = d[u] + 1
                    queue.append(v)
        return d
