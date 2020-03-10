import yaml
import re

indent_char = '  '
indent_size = 2

def indent_string(s, size):
    return re.sub(r'\n', '\n' + size * indent_char, s)

class SecretFileConfig():
    def __init__(
            self,
            mount_path,
            filename,
            secret_path,
            content_template,
            sub_path=None):
        if mount_path is None:
            raise ValueError("mount_path should not be None")
        if filename is None:
            raise ValueError("mount_path should not be None")
        if secret_path is None:
            raise ValueError("mount_path should not be None")
        if content_template is None:
            raise ValueError("mount_path should not be None")

        self.mount_path = mount_path
        self.sub_path = sub_path
        self.filename = filename
        self.secret_path = secret_path
        self.content_template = content_template

    def __repr__(self):
        return "{}(mount_path={}, sub_path={}, filename={}, secret_path={}, content_template={})".format(
                SecretFileConfig.__name__,
                self.mount_path,
                self.sub_path,
                self.filename,
                self.secret_path,
                self.content_template)

    def to_yaml(self, in_array=False):
        output_dict = {
            'containerName': 'base',
            'mountPath': self.mount_path,
            'filename': self.filename,
            'content': {}
        }
        if self.sub_path:
            output_dict['subPath'] = self.sub_path

        if in_array:
            output_yaml = yaml.dump([output_dict], indent=indent_size)
        else:
            output_yaml = yaml.dump(output_dict, indent=indent_size)

        content = """|
<<EOH
{{{{- with secret "{}" -}}}}
{}
{{{{ end -}}}}
EOH""".format(self.secret_path, self.content_template)

        if in_array:
            # add 2 indent to content_template
            indented_content = indent_string(content, 2)
        else:
            # add 1 indent to content_template
            indented_content = indent_string(content, 1)

        return output_yaml.format(indented_content)

class SecretInjectionConfig():
    def __init__(
            self,
            role,
            env,
            secret_files
            ):
        self.role = role
        self.env = env
        self.secret_files = secret_files
        if role is None:
            raise ValueError("role should not be None")
        if env is None:
            raise ValueError("env should not be None")
        if not isinstance(secret_files, list):
            raise ValueError("secret_files should be a list")
        if len(secret_files) == 0:
            raise ValueError("secret_files should not be empty")

    def __repr__(self):
        return "{}(role={}, env={}, secret_files={})".format(
                SecretInjectionConfig.__name__,
                self.role,
                self.env,
                self.secret_files)

    def to_yaml(self):
        output_dict = {
            'vaultConfig': {
                'role': self.role,
                'namespace': self.env
                },
            }

        secret_files_yaml = ""
        for sf in self.secret_files:
            secret_files_yaml += sf.to_yaml(in_array=True)

        indented_secret_files_yaml = indent_string(secret_files_yaml, 1)

        output_yaml = yaml.dump(output_dict, indent=indent_size) + """
secretFiles:
  {}""".format(indented_secret_files_yaml)

        return output_yaml

    """
    get_pod_annotation generated the a dict with the following format
    {
        'vault.welab.io/v1-file-inject': '''vaultConfig:
  namespace: test
  role: airflow

secretFiles:
  - containerName: base
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
    mountPath: /etc/properties'''
    }"""
    def get_pod_annotation(self):
        value = self.to_yaml()
        annotation = {
            'vault.welab.io/v1-file-inject': value
        }

        return annotation

