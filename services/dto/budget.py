from pydantic import BaseModel, Field, field_validator


class CreateBudgetDTO(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    base_currency: str = Field(min_length=3, max_length=3)
    aux_currency_1: str | None = Field(default=None, min_length=3, max_length=3)
    aux_currency_2: str | None = Field(default=None, min_length=3, max_length=3)
    timezone: str = Field(min_length=1, max_length=64)

    @field_validator("base_currency", "aux_currency_1", "aux_currency_2", mode="before")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip().upper()
