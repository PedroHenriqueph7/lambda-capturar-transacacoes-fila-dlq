from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class SettlementFailedEvent(BaseModel):
    # model_config garante a exclusão de campos não mapeados (comportamento padrão, mas explícito é melhor)
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    idempotency_key: str = Field(alias="idempotencyKey")
    batch_id: str = Field(alias="batchId")
    failure_reason: str = Field(alias="failureReason")
    failed_at: datetime = Field(alias="failedAt")