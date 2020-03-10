import pytest
from airflow_common_lib.vault import Vault, AppRole

def test_vault_construct():
    v = Vault()
    assert v is not None

def test_app_role_construct():
    ar = AppRole(role_id="abc")
    assert ar is not None

def test_app_role_construct_failure():
    with pytest.raises(TypeError):
        ar = AppRole()
