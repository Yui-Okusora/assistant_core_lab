@dataclass(frozen=True)
class Office:
    name: str
    room: str
    hours: str


class OfficeDirectory:
    def __init__(self, offices: dict[str, Office]):
        self._offices = offices

        @classmethod
        def from_csv(cls, path: Path) -> OfficeDirectory:
            try:
                with path.open(encoding="utf-8", newline="") as f:
                    rows = list(csv.DictReader(f))
            except FileNotFoundError as exc:
                raise DataError(f"office file not found: {path}") from exc
            return cls(
                {
                    r["name"].lower(): Office(r["name"], r["room"], r["hours"])
                    for r in rows
                }
            )

    @property
    def names(self) -> set[str]:
        return set(self._offices)

    def find(self, text: str) -> Office | None:
        t = text.lower()
        return next((o for name, o in self._offices.items() if name in t), None)
