from __future__ import annotations

from decimal import Decimal
from typing import Any, List, Optional, Union

from numpy.random import default_rng

Number = Union[Decimal, int, float]


class ProbabilityNode:
    ROUND_TO = 2

    rng = default_rng()

    def __init__(
        self,
        probability: Optional[Number] = None,
        name: str = "",
        value: Any = None,
        children: Optional[List[ProbabilityNode]] = None,
    ) -> None:
        self._probability = self._initial_probability = probability
        if isinstance(self._probability, (float, int)):
            self._probability = self._decimalize(self._probability)
        self.name = name
        self.value = value
        if not children:
            children = []
        self.children = children
        for child in self.children:
            child.parent = self

    def choice(self) -> ProbabilityNode:
        if not self.children:
            return self
        return self.rng.choice(
            self.children,
            p=[i.probability for i in self.children],
        )

    def choice_recursive(self) -> ProbabilityNode:
        result = self.choice()
        if result.children:
            return result.choice_recursive()
        else:
            return result

    def get_child_by_name(
        self,
        name: str,
    ) -> Optional[ProbabilityNode]:
        return {
            child.name: child
            for child in self.children
            if child.name
        }.get(name) # yapf: disable

    def add_child(
        self,
        child: Optional[ProbabilityNode] = None,
        **kwargs,
    ) -> None:
        if not child: child = ProbabilityNode(**kwargs)
        self.children.append(child)
        child.parent = self

    def set_children_probabilities(
        self,
        probabilities: Union[list, dict],
    ) -> None:
        if isinstance(probabilities, list):
            for child, prob in zip(self.children, probabilities):
                child._probability = prob
        if isinstance(probabilities, dict):
            for k, v in probabilities.items():
                self.get_child_by_name(k)._probability = self._decimalize(v)

    def reset_children(self) -> None:
        for child in self.children:
            child._reset()

    def reset_children_recursive(self) -> None:
        for child in self.children:
            if child.children:
                child.reset_children_recursive()
            child._reset()

    @property
    def probability(self) -> Number:
        return self._probability

    @probability.setter
    def probability(self, value: Number) -> None:
        if value > 1:
            raise ValueError  # TODO: Add error detail
        if isinstance(value, (int, float)):
            value = self._decimalize(value)
        diff = value - self._probability
        siblings = self._get_siblings()
        for sibling in siblings:
            sibling._probability -= diff * (sibling.probability /
                                            (1 - self._probability))
        self._probability = value

    def _get_siblings(self) -> Optional[List[ProbabilityNode]]:
        return [child for child in self.parent.children if child is not self]

    def _reset(self) -> None:
        self._probability = self._initial_probability

    def _decimalize(self, num: Number) -> Decimal:
        if isinstance(num, Decimal): return num
        return Decimal(f"{num:.{self.ROUND_TO}f}")

    def __repr__(self) -> str:
        return f"<ProbabilityNode {self.name}: {self.probability}>"


if __name__ == "__main__":
    root = ProbabilityNode()
    root.add_child(ProbabilityNode(name="a", probability=0.5))
    root.add_child(ProbabilityNode(name="b", probability=0.4))
    root.add_child(ProbabilityNode(name="c", probability=0.08))
    root.add_child(ProbabilityNode(name="d", probability=0.02))
    print(root.children)
    print(root.choice_recursive())
    a = root.get_child_by_name("a")
    a.probability = 1
    print(root.children)
    root.reset_children_recursive()
    print(root.children)
