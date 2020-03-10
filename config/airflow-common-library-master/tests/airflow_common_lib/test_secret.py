import os
import pytest
import mock
import json
from airflow import DAG
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.utils.dates import days_ago
from airflow.models.taskinstance import TaskInstance

from airflow_common_lib.secret import vault_access_task, VaultSecretReader

class TestVaultAccessTask:
    def test_should_return_k8s_pod_operator(self, monkeypatch):
        monkeypatch.setenv("VAULT_ACCESS_IMAGE", "approle-token-generator:latest")
        monkeypatch.setenv("VAULT_ADDR", "http://localhost:8200")
        monkeypatch.setenv("VAULT_ACCESS_SERVICE_ACCOUNT", "envelope-creator")
        monkeypatch.setenv("VAULT_NAMESPACE", "TEST")

        default_args = {
            'namespace': 'airflow'
        }

        dag_id = "abcd"

        dag = DAG(dag_id,
                  default_args=default_args,
                  start_date=days_ago(5),
                  schedule_interval='0 0 * * *')

        result = vault_access_task(dag, task_id='any_task_id', task_list=["key1", "key2"], app_role='any_app_role')

        assert type(result) is KubernetesPodOperator

    def test_should_raise_value_error(self, monkeypatch):
        monkeypatch.delenv("VAULT_ACCESS_IMAGE", raising=False)
        monkeypatch.delenv("VAULT_ADDR", raising=False)
        monkeypatch.delenv("VAULT_ACCESS_SERVICE_ACCOUNT", raising=False)
        monkeypatch.delenv("VAULT_NAMESPACE", raising=False)
        with pytest.raises(KeyError):
            default_args = {
                'namespace': 'airflow'
            }

            dag_id = "abcd"

            dag = DAG(dag_id,
                      default_args=default_args,
                      start_date=days_ago(5),
                      schedule_interval='0 0 * * *')

            result = vault_access_task(dag, task_id='any_task_id', task_list=["key1", "key2"], app_role='any_app_role', ttl='60s')

    def test_should_pass_arg_to_operator(self, monkeypatch):
        monkeypatch.setenv("VAULT_ACCESS_IMAGE", "approle-token-generator:latest")
        monkeypatch.setenv("VAULT_ADDR", "http://localhost:8200")
        monkeypatch.setenv("VAULT_ACCESS_SERVICE_ACCOUNT", "envelope-creator")
        monkeypatch.setenv("VAULT_NAMESPACE", "TEST")

        default_args = {
            'namespace': 'airflow'
        }

        dag_id = "abcd"

        dag = DAG(dag_id,
                  default_args=default_args,
                  start_date=days_ago(5),
                  schedule_interval='0 0 * * *')

        app_role = 'any_app_role'
        ttl = '60s'
        keys = ["key1", "key2"]
        keys_str = json.dumps(keys)
        output_file = '/airflow/xcom/return.json'

        result = vault_access_task(dag, task_id='any_task_id', task_list=keys, app_role=app_role, ttl=ttl)

        assert type(result) is KubernetesPodOperator
        assert result.arguments == [app_role, ttl, keys_str, output_file]

def get_connection(conn_id):
    return mock.Mock()

class TestGetVaultSecret:
    def test_should_return_secret(self, mocker, monkeypatch):
        from airflow.hooks.base_hook import BaseHook
        monkeypatch.setattr(BaseHook, 'get_connection', get_connection)
        ti = mocker.MagicMock()
        ti.dag_id = 'any_dag_id'
        ti.task_id = 'any_task_id'
        ti.xcom_pull.return_value = {'any_task_id': 'some_token'}

        from airflow_common_lib.vault import AppRole
        mocker.patch.object(AppRole, 'unwrap_secret_id').return_value = 'abc'
        mocker.patch.object(AppRole, 'login')
        mocked_secret = 'any_secret'
        mock_read_secret_v2 = mocker.patch.object(AppRole, 'read_secret_v2')
        mock_read_secret_v2.return_value = mocked_secret

        vsr = VaultSecretReader(ti, token_from='any_task_id')
        secret = vsr.get_secret('any/secret/path/')

        mock_read_secret_v2.assert_called_once_with("any/secret/path/")
        assert secret == mocked_secret
