import os
import hvac

class Vault():
    def __init__(self):
        self.client = hvac.Client(
            url=os.environ.get('VAULT_ADDR'),
            namespace=os.environ.get('VAULT_NAMESPACE', ''),
        )

    def unwrap(self, token):
        self.client.token = token
        return self.client.sys.unwrap()

class AppRole(Vault):
    def __init__(self, role_id):
        Vault.__init__(self)
        self.role_id = role_id

    def unwrap_secret_id(self, token):
        response = self.unwrap(token)
        return response['data']['secret_id']

    def login(self, secret_id):
       self.client.auth_approle(self.role_id, secret_id)

    def read_secret_v2(self, secret_path):
        secret_version_response = self.client.secrets.kv.v2.read_secret_version(path=secret_path)
        return secret_version_response['data']['data']
