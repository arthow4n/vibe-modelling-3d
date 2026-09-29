"""Small JSON-ready answers, explicitly separating completion from adequacy."""
from dataclasses import asdict, dataclass, field
import json
from pathlib import Path

@dataclass
class AnalysisResult:
    case: str
    status: str
    completed: bool = False
    metrics: dict = field(default_factory=dict)
    history: list = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    provenance: dict = field(default_factory=dict)
    artifacts: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)

    def write(self, path):
        Path(path).write_text(json.dumps(self.to_dict(), indent=2, allow_nan=False)+'\n')

    def require_completed(self):
        if not self.completed:
            raise RuntimeError(f'{self.case}: {self.status}: {self.errors}')
        return self

    def check_strain_limits(self):
        """Conditional material screen, separate from numerical completion."""
        self.require_completed()
        return {name: {
            'max_abs_principal_strain': self.metrics['max_strain_by_part'][name],
            'limit': limit,
            'passes': self.metrics['max_strain_by_part'][name] <= limit if limit is not None else None,
        } for name, limit in self.metrics['strain_limits'].items()}
