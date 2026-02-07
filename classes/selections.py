from dataclasses import dataclass, field
from typing import Optional, Tuple


@dataclass(frozen=True)
class Table:
    name: str
    sql_expression: str
    parent: str = "SCRITS2"

    def __str__(self) -> str:
        return f"{self.parent}.{self.sql_expression} AS {self.name}"


@dataclass(frozen=True)
class Join:
    left: Table
    right: Table
    on: str
    join_type: str = "LEFT"

    def __str__(self) -> str:
        return (
            f"{self.join_type} JOIN {self.right}\n"
            f"    ON {self.left.name}.{self.on} = {self.right.name}.{self.on}"
        )

    def with_extra(self, extra: str) -> str:
        return f"{self}\n    {extra}" if extra else str(self)

    def inner(self):
        return Join(
            left=self.left, right=self.right, on=self.on, join_type="INNER"
        )


@dataclass(frozen=True)
class SelectClause:
    name: str
    sql_name: str
    sql_expression: str
    table: Optional[Table] = None
    format: Optional[str] = None
    required: bool = field(default=False)


Selection = Tuple[SelectClause, ...]


@dataclass(frozen=True)
class SelectionList:
    subject: Selection = ()
    web: Selection = ()
    api: Selection = ()
    pdf: Selection = ()
    excel: Selection = ()
    sql: Selection = ()

    def __post_init__(self):
        merged = {
            select
            for sub in (self.web, self.subject, self.api, self.pdf, self.excel)
            for select in sub
        }
        object.__setattr__(self, "sql", tuple(merged))
