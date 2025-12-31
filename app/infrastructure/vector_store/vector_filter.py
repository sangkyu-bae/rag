from dataclasses import dataclass
from typing import Any, Literal, Optional

FilterType = Literal["match", "range"]

@dataclass
class VectorFilter:
    key: str
    filter_type: FilterType
    value: Any = None
    gte: Optional[int] = None
    lte: Optional[int] = None
    gt: Optional[int] = None
    lt: Optional[int] = None

    @classmethod
    def match(cls, key: str, value: Any) -> "VectorFilter":
        return cls(
            key=key,
            filter_type="match",
            value=value
        )

    @classmethod
    def range(
            cls,
            key: str,
            *,
            gte: int | None = None,
            lte: int | None = None,
            gt: int | None = None,
            lt: int | None = None,
    ) -> "VectorFilter":
        return cls(
            key=key,
            filter_type="range",
            gte=gte,
            lte=lte,
            gt=gt,
            lt=lt,
        )

    def to_vector_filter(self):
        if self.filter_type == "match":
            return {
                "key": self.key,
                "match_text": {"text": self.value}
            }

        if self.filter_type == "range":
            range_body = {
                k: v
                for k, v in {
                    "gte": self.gte,
                    "lte": self.lte,
                    "gt": self.gt,
                    "lt": self.lt,
                }.items()
                if v is not None
            }

            return {
                "key": self.key,
                "range": range_body
            }