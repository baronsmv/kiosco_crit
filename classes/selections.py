from dataclasses import dataclass, field
from typing import Optional, Tuple


@dataclass(frozen=True)
class SelectClause:
    name: str
    sql_name: str
    sql_expression: str
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
