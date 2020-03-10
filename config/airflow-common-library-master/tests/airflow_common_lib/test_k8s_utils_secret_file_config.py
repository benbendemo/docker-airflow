import pytest

from airflow_common_lib.k8s_utils import SecretFileConfig


@pytest.fixture()
def secret_file_config(request):
    def _secret_file_config_factory(param):
        def _secret_file_config():
            return SecretFileConfig(
                mount_path=param['mount_path'],
                filename=param['filename'],
                secret_path=param['secret_path'],
                content_template=param['content_template'],
		sub_path=param.get('sub_path'))
        return _secret_file_config
    return _secret_file_config_factory

@pytest.fixture(params=[{
    'mount_path': '/etc/properties',
    'filename': 'override.properties.yml',
    'secret_path': 'secret/data/myapp/config',
    'content_template': """spring:
  datasource:
    username: {{ .Data.data.username }}
    password: {{ .Data.data.password }}"""
    }, {
    'mount_path': '/etc/override.properties.cfg',
    'sub_path': 'override.properties.cfg',
    'filename': 'override.properties.cfg',
    'secret_path': 'secret/data/myapp/config',
    'content_template': """[datasource]
username = {{ .Data.data.username }}
password = {{ .Data.data.password }}"""
    }])
def valid_secret_file_config(request, secret_file_config):
    return secret_file_config(param=request.param)

@pytest.fixture(params=[{
    'mount_path': None,
    'filename': None,
    'secret_path': None,
    'content_template': None
    }])
def invalid_secret_file_config(request, secret_file_config):
    return secret_file_config(param=request.param)

def test_raise_error_when_arg_none(invalid_secret_file_config):
    with pytest.raises(ValueError, match=r".*should not be None.*"):
        invalid_secret_file_config()

def test_construct_success(valid_secret_file_config):
    assert valid_secret_file_config() is not None

test_data =[({
    'mount_path': '/etc/properties',
    'filename': 'override.properties.yml',
    'secret_path': 'secret/data/myapp/config',
    'content_template': """spring:
  datasource:
    username: {{ .Data.data.username }}
    password: {{ .Data.data.password }}"""
    }, False, """containerName: base
content: |
  <<EOH
  {{- with secret "secret/data/myapp/config" -}}
  spring:
    datasource:
      username: {{ .Data.data.username }}
      password: {{ .Data.data.password }}
  {{ end -}}
  EOH
filename: override.properties.yml
mountPath: /etc/properties
"""), ({
    'mount_path': '/etc/properties',
    'sub_path': 'override.properties.yml',
    'filename': 'override.properties.yml',
    'secret_path': 'secret/data/myapp/config',
    'content_template': """spring:
  datasource:
    username: {{ .Data.data.username }}
    password: {{ .Data.data.password }}"""
    }, False, """containerName: base
content: |
  <<EOH
  {{- with secret "secret/data/myapp/config" -}}
  spring:
    datasource:
      username: {{ .Data.data.username }}
      password: {{ .Data.data.password }}
  {{ end -}}
  EOH
filename: override.properties.yml
mountPath: /etc/properties
subPath: override.properties.yml
"""), ({
    'mount_path': '/etc/properties',
    'filename': 'secret.yml',
    'secret_path': 'secret/my_app',
    'content_template': """datasouce:
  username: {{ .Data.data.username }}
  password: {{ .Data.data.password }}"""
        }, True, """- containerName: base
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
"""), ({
    'mount_path': '/etc/properties',
    'sub_path': 'secret.yml',
    'filename': 'secret.yml',
    'secret_path': 'secret/my_app',
    'content_template': """datasouce:
  username: {{ .Data.data.username }}
  password: {{ .Data.data.password }}"""
        }, True, """- containerName: base
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
""")]

@pytest.mark.parametrize("valid_secret_file_config, in_array, expected", test_data, indirect=["valid_secret_file_config"])
def test_to_yaml(valid_secret_file_config, in_array, expected):
    config = valid_secret_file_config()
    result = config.to_yaml(in_array)
    assert result == expected

