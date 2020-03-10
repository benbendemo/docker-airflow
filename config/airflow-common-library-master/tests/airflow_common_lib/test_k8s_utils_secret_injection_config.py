import pytest

from airflow_common_lib.k8s_utils import SecretFileConfig, SecretInjectionConfig

@pytest.fixture()
def secret_injection_config(request):
    def _fixture_factory(param):
        def _config_factory():
            return SecretInjectionConfig(
                role=param['role'],
                env=param['env'],
                secret_files=param['secret_files'])
        return _config_factory
    return _fixture_factory

@pytest.fixture(params=[{
    'role': 'airflow',
    'env': 'test',
    'secret_files': [SecretFileConfig(
        mount_path='/etc/properties',
        filename='secret.yml',
        secret_path='secret/my_app',
        content_template="""datasouce:
  username: {{ .Data.data.username }}
  password: {{ .Data.data.password }}""")]
    }])
def valid_secret_injection_config(request, secret_injection_config):
    return secret_injection_config(param=request.param)

@pytest.fixture(params=[{
    'role': None,
    'env': None,
    'secret_files': None
    }, {
    'role': 'airflow',
    'env': 'test',
    'secret_files': None
    }, {
    'role': 'airflow',
    'env': 'test',
    'secret_files': []
    }])
def invalid_secret_injection_config(request, secret_injection_config):
    return secret_injection_config(param=request.param)

def test_raise_error_when_arg_none(invalid_secret_injection_config):
    with pytest.raises(ValueError, match=r".*should.*"):
        invalid_secret_injection_config()

def test_construct_success(valid_secret_injection_config):
    assert valid_secret_injection_config() is not None

test_file_1 = SecretFileConfig(
        mount_path='/etc/properties',
        filename='secret.yml',
        secret_path='secret/my_app',
        content_template="""datasouce:
  username: {{ .Data.data.username }}
  password: {{ .Data.data.password }}""")

test_file_2 = SecretFileConfig(
        mount_path='/etc/properties',
        sub_path='secret.yml',
        filename='secret.yml',
        secret_path='secret/my_app',
        content_template="""datasouce:
  username: {{ .Data.data.username }}
  password: {{ .Data.data.password }}""")

test_file_3 = SecretFileConfig(
        mount_path='/etc/properties',
        sub_path='secret2.yml',
        filename='secret2.yml',
        secret_path='secret/my_app2',
        content_template=""""spring": {
  "datasource": {
    "username": "{{ .Data.data.username }}",
    "password": "{{ .Data.data.password }}"
  }
}""")

test_data=[({
    'role': 'airflow',
    'env': 'test',
    'secret_files': [test_file_1]
    }, """vaultConfig:
  namespace: test
  role: airflow

secretFiles:
  - containerName: base
    content: |
      <<EOH
      {{- with secret "secret/my_app" -}}
      datasouce:
        username: {{ .Data.data.username }}
        password: {{ .Data.data.password }}
      {{ end -}}
      EOH
    filename: secret.yml
    mountPath: /etc/properties
  """),({
    'role': 'airflow',
    'env': 'test',
    'secret_files': [test_file_2, test_file_3]
    }, """vaultConfig:
  namespace: test
  role: airflow

secretFiles:
  - containerName: base
    content: |
      <<EOH
      {{- with secret "secret/my_app" -}}
      datasouce:
        username: {{ .Data.data.username }}
        password: {{ .Data.data.password }}
      {{ end -}}
      EOH
    filename: secret.yml
    mountPath: /etc/properties
    subPath: secret.yml
  - containerName: base
    content: |
      <<EOH
      {{- with secret "secret/my_app2" -}}
      "spring": {
        "datasource": {
          "username": "{{ .Data.data.username }}",
          "password": "{{ .Data.data.password }}"
        }
      }
      {{ end -}}
      EOH
    filename: secret2.yml
    mountPath: /etc/properties
    subPath: secret2.yml
  """)]

@pytest.mark.parametrize("valid_secret_injection_config, expected", test_data, indirect=["valid_secret_injection_config"])
def test_to_yaml(valid_secret_injection_config, expected):
    config = valid_secret_injection_config()
    result = config.to_yaml()
    assert result == expected

@pytest.mark.parametrize("valid_secret_injection_config, expected", test_data, indirect=["valid_secret_injection_config"])
def test_get_pod_annotation(valid_secret_injection_config, expected):
    config = valid_secret_injection_config()
    result = config.get_pod_annotation()
    assert result['vault.welab.io/v1-file-inject'] == expected
