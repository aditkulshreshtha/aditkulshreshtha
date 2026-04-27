from dataclasses import dataclass

@dataclass
class Risk:
    risk_id: str
    title: str
    domain: str
    likelihood: int
    impact: int
    control_status: str
    owner: str
    due_date: str

    @property
    def score(self) -> int:
        return self.likelihood * self.impact

    @property
    def severity(self) -> str:
        score = self.score
        if score >= 16:
            return 'Critical'
        if score >= 9:
            return 'High'
        if score >= 4:
            return 'Medium'
        return 'Low'
