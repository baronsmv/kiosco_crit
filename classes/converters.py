from datetime import date, datetime


class DateConverter:
    regex = r"\d{4}-\d{2}-\d{2}"

    def to_python(self, value) -> date:
        return datetime.strptime(value, "%Y-%m-%d").date()

    def to_url(self, value) -> str:
        return value.strftime("%Y-%m-%d")
