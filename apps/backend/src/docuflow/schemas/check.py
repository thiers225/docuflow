from pydantic import BaseModel

from docuflow.db.models import CheckSeverity


class ExtractionCheckRead(BaseModel):
    id: int
    rule: str
    passed: bool
    severity: CheckSeverity
    message: str

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "rule": "amounts_coherent",
                    "passed": False,
                    "severity": "error",
                    "message": (
                        "Incohérence des montants : HT 185000 + taxe 33300 = 218300, "
                        "mais TTC extrait = 220000 (écart : 1700)."
                    ),
                }
            ]
        },
    }
