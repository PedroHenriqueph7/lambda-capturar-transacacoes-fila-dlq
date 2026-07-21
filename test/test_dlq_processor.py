import json
import pytest
from unittest.mock import Mock
from pydantic import ValidationError
from src.services.dlq_processor import DlqProcessorService

def test_process_and_forward_extracts_correct_payload_from_dirty_dlq_event():
    # Arrange
    mock_producer = Mock()
    service = DlqProcessorService(producer=mock_producer)
    
    # Simula um body gigante e poluído vindo da processing-batch-dlq
    dirty_dlq_body = json.dumps({
        "idempotencyKey": "a1b2c3d4-e5f6-7890-1234-56789abcdef0",
        "batchId": "f9e8d7c6-b5a4-3210-fedc-ba0987654321",
        "failureReason": "Business Validation: Invalid Document",
        "failedAt": "2026-07-19T13:22:00-03:00",
        "customer_data": {"name": "John Doe", "score": 950},
        "internal_stacktrace": "NullPointerException at line 42...",
        "processing_attempts": 3
    })
    
    # O Pydantic serializa o datetime de volta para string ISO com 'Z' ou offset 
    # ao aplicar o model_dump(mode='json') ou model_dump_json()
    expected_published_payload = {
        "idempotencyKey": "a1b2c3d4-e5f6-7890-1234-56789abcdef0",
        "batchId": "f9e8d7c6-b5a4-3210-fedc-ba0987654321",
        "failureReason": "Business Validation: Invalid Document",
        "failedAt": "2026-07-19T13:22:00-03:00"
    }

    # Act
    service.process_and_forward(dirty_dlq_body)

    # Assert
    mock_producer.publish.assert_called_once()
    
    # Captura o argumento exato que foi enviado para o SQS
    published_args = mock_producer.publish.call_args[0][0]
    
    # Valida se os campos excedentes (customer_data, stacktrace) foram totalmente removidos
    assert published_args == expected_published_payload
    assert "customer_data" not in published_args


def test_process_and_forward_fails_when_batch_id_is_missing():
    # Arrange
    mock_producer = Mock()
    service = DlqProcessorService(producer=mock_producer)
    
    incomplete_body = json.dumps({
        "idempotencyKey": "a1b2c3d4-e5f6-7890-1234-56789abcdef0",
        "failureReason": "Timeout",
        "failedAt": "2026-07-19T13:22:00-03:00"
        # batchId está ausente
    })

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        service.process_and_forward(incomplete_body)

    assert "batchId" in str(exc_info.value)
    mock_producer.publish.assert_not_called()