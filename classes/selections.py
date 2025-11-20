from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class SelectClause:
    name: str
    sql_name: str
    sql_expression: str
    format: Optional[str] = None


Selection = Tuple[SelectClause, ...]


@dataclass(frozen=True)
class SelectionList:
    web: Selection
    subject: Selection = ()
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

        for field_name in ("api", "pdf", "excel"):
            if not getattr(self, field_name):
                object.__setattr__(self, field_name, self.web)
