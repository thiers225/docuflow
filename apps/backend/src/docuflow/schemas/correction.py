from pydantic import BaseModel, Field


class FieldCorrection(BaseModel):
    """Corps de la requête de correction d'un champ."""

    corrected_value: str | None = Field(
        ...,
        description="Valeur corrigée par l'utilisateur. Null pour effacer la correction.",
        examples=["FACT-2026-00142"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"corrected_value": "FACT-2026-00142"},
            ]
        }
    }
