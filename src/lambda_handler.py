import os
import boto3
import logging
from typing import Any, Dict
from src.adapters.sqs_producer import SqsProducer
from src.services.dlq_processor import DlqProcessorService
from src.settings.Settings import Settings
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Inicialização Global para reaproveitamento no Cold Start
settings = Settings()
sqs_client = boto3.client("sqs")


producer = SqsProducer(sqs_client, settings.PUBLISH_QUEUE_URL)
dlq_service = DlqProcessorService(producer)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    failed_message_ids = []

    for record in event.get("Records", []):
        message_id = record.get("messageId")
        try:
            dlq_service.process_and_forward(record["body"])
        except Exception as e:
            logger.error(f"Falha ao processar mensagem {message_id}: {str(e)}")
            failed_message_ids.append({"itemIdentifier": message_id})

    # Retorna as falhas parciais para que o SQS não reenvie as mensagens com sucesso
    return {"batchItemFailures": failed_message_ids}


