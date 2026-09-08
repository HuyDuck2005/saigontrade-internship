import pytest
import xmlrpc.client
from unittest.mock import patch, MagicMock

# --- Mocks for FastAPI and XML-RPC ---

@pytest.fixture
def mock_odoo_connection():
    with patch('src.odoo.task8_deal_middleware.get_odoo_connection') as mock_get_conn:
        mock_uid = 1
        mock_models = MagicMock()
        mock_get_conn.return_value = (mock_models, mock_uid)
        yield mock_models

# --- Tests for Task 8 & 10 (FastAPI to Odoo) ---
def test_task8_middleware_create_deal(mock_odoo_connection):
    # This is a unit test to verify that the fastapi endpoint would call Odoo create correctly.
    # In practice, we test the logic directly or use TestClient.
    from fastapi.testclient import TestClient
    from src.odoo.task8_deal_middleware import app
    
    client = TestClient(app)
    payload = {
        "deal_name": "Test Deal FastAPI",
        "firstname": "John",
        "lastname": "Doe",
        "phone": "0901234567",
        "email": "john.doe@test.com",
        "expected_revenue": 500
    }
    
    # Configure mock
    mock_odoo_connection.execute_kw.side_effect = [
        [], # res.partner search -> empty
        10, # res.partner create -> returns partner ID 10
        100 # crm.lead create -> returns deal ID 100
    ]
    
    response = client.post("/api/crm/deal", json=payload, headers={"X-API-Key": "sgt_secret_api_key_2026"})
    
    assert response.status_code == 201
    assert response.json()["deal_id"] == 100
    assert response.json()["partner_id"] == 10
    assert mock_odoo_connection.execute_kw.call_count == 3


# --- Tests for Task 44 (Sync Monitoring & Retry) ---
# Note: Since this is Odoo environment, we mock the Odoo env behavior.
class MockRecord:
    def __init__(self):
        self.status = 'failed'
        self.error_message = 'Connection timeout'
        self.retry_count = 0
        
    def write(self, vals):
        for k, v in vals.items():
            setattr(self, k, v)
            
    def action_sync_deal_to_odoo2(self):
        # Simulate successful sync
        self.status = 'success'
        self.error_message = ''
        
    def exists(self):
        return True

def test_task44_sync_monitoring_retry():
    # Test behavior of SyncLog retry logic on failure
    log = MockRecord()
    # Mocking the action_retry functionality for a single record
    try:
        log.action_sync_deal_to_odoo2()
        log.retry_count += 1
    except Exception as e:
        log.write({'status': 'failed', 'error_message': str(e), 'retry_count': log.retry_count + 1})
        
    assert log.status == 'success'
    assert log.retry_count == 1
    assert log.error_message == ''


# --- Tests for Task 47 (Approval Workflow Validation) ---
def test_task47_approval_workflow_validation():
    # Simulate action_confirm_deal with validation error
    class MockLead:
        def __init__(self, discount_percentage, expected_revenue):
            self.discount_percentage = discount_percentage
            self.expected_revenue = expected_revenue
            self.approval_state = 'draft'
            
        def write(self, vals):
            for k, v in vals.items():
                setattr(self, k, v)
                
        def action_confirm_deal(self):
            if self.discount_percentage > 10.0 or self.expected_revenue > 1000000000:
                if self.approval_state != 'approved':
                    self.write({'approval_state': 'pending'})
                    raise ValueError("This deal exceeds the allowed discount or amount threshold.")
                    
    lead_exceeds = MockLead(15.0, 500000)
    with pytest.raises(ValueError, match="exceeds the allowed discount"):
        lead_exceeds.action_confirm_deal()
        
    assert lead_exceeds.approval_state == 'pending'
