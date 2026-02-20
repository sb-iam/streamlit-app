from dataclasses import dataclass, field


@dataclass
class Finding:
    rule_id: str
    description: str
    severity: str  # "critical", "warning", "info"
    location: str  # "Firm-Level" or file name
    component: str
    issue: str
    remediation: str
    estimated_fix_time: str


@dataclass
class ComponentResult:
    name: str
    description: str
    findings: list[Finding] = field(default_factory=list)

    @property
    def status(self) -> str:
        severities = [f.severity for f in self.findings]
        if "critical" in severities:
            return "critical"
        if "warning" in severities:
            return "warning"
        return "pass"

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "critical")

    @property
    def warning_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "warning")


@dataclass
class FileResult:
    file_id: str
    client_name: str
    engagement_type: str
    standard: str
    engagement_partner: str
    prepared_by: str
    assertions_passed: int
    assertions_total: int
    overall_status: str
    findings: list[Finding] = field(default_factory=list)


@dataclass
class ScanResult:
    firm_name: str
    license_number: str
    jurisdiction: str
    next_inspection_due: str
    readiness_score: float
    predicted_outcome: str
    total_assertions: int
    passed_assertions: int
    critical_count: int
    warning_count: int
    info_count: int
    files_scanned: int
    post_fix_score: float = 0.0
    post_fix_outcome: str = ""
    estimated_fix_hours: float = 0.0
    components: list[ComponentResult] = field(default_factory=list)
    file_results: list[FileResult] = field(default_factory=list)
    all_findings: list[Finding] = field(default_factory=list)
