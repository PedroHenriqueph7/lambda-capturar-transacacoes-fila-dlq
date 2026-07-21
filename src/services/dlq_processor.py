import json
import logging
from pydantic import ValidationError
from src.domain.models import SettlementFailedEvent
from src.adapters.sqs_producer import SqsProducer

logger = logging.getLogger(__name__)

class DlqProcessorService:
    def __init__(self, producer: SqsProducer):
        self._producer = producer

    def process_and_forward(self, raw_body: str) -> None:
        try:
            raw_data = json.loads(raw_body)
            
            # Valida e higieniza o payload bruto
            filtered_event = SettlementFailedEvent(**raw_data)
            
            # Publica utilizando o alias (idempotencyKey) exigido pelo Scheduler
            self._producer.publish(filtered_event.model_dump(by_alias=True))
            
            logger.info(f"Roteamento concluído para idempotencyKey: {filtered_event.idempotency_key}")
            
        except ValidationError as e:
            logger.error(f"Payload inválido. Campos obrigatórios ausentes. Erro: {e.errors()}")
            raise
        except json.JSONDecodeError:
            logger.error("Body recebido não é um JSON válido.")
            raise
    
        







