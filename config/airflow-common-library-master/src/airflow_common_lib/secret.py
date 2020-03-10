import os
import json
import logging
from pprint import pformat
from datetime import timedelta
from airflow.hooks.base_hook import BaseHook
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.contrib.kubernetes.volume import Volume
from airflow.contrib.kubernetes.volume_mount import VolumeMount

from airflow_common_lib.vault import AppRole

def vault_access_task(dag,
                      task_id,
                      task_list,
                      app_role,
                      ttl='1h',
                      service_account_name=None,
                      execution_timeout=timedelta(minutes=1)):
    if ttl == '':
        raise Exception('ttl should not be empty')

    if app_role == '':
        raise Exception('app_role should not be empty')

    task_list_str = json.dumps(task_list)

    vault_image = os.environ['VAULT_ACCESS_IMAGE']
    vault_addr = os.environ['VAULT_ADDR']
    vault_namespace = os.environ.get('VAULT_NAMESPACE', '')
    vault_access_service_account = service_account_name

    vault_access_volume_name = 'vault-access-config'

    volume_mount = VolumeMount(vault_access_volume_name,
                                mount_path='/home/vault/config.hcl',
                                sub_path='config.hcl',
                                read_only=True)

    volume_config= {
        'configMap':
          {
            'name': '%s-vault-access-config' % dag.dag_id.replace('_', '-')
          }
        }

    volume = Volume(name=vault_access_volume_name, configs=volume_config)

    return KubernetesPodOperator(
        dag=dag,
        task_id=task_id,
        name='vault-access',
        image=vault_image,
        arguments=[app_role, ttl, task_list_str, '/airflow/xcom/return.json'],
        env_vars={
            'VAULT_ADDR': vault_addr,
            'VAULT_NAMESPACE': vault_namespace,
        },
        execution_timeout=execution_timeout,
        service_account_name=vault_access_service_account,
        labels={'dag_id': dag.dag_id, 'task_id': task_id},
        xcom_push=True,
        do_xcom_push=True,
        volumes=[volume],
        volume_mounts=[volume_mount])

class VaultSecretReader():
    def __init__(self, task_instance, token_from):
        conn_id =  "%s_role_id" % task_instance.dag_id
        role_id = BaseHook.get_connection(conn_id).password

        value = task_instance.xcom_pull(task_ids=token_from)
        token = value[task_instance.task_id]

        v = AppRole(role_id)
        secret_id = v.unwrap_secret_id(token)
        v.login(secret_id)

        self.vault = v

    def get_secret(self, secret_path):
        return self.vault.read_secret_v2(secret_path)

