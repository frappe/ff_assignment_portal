import io
import frappe
import paramiko

def get_ssh_client(private_key: str):
    settings = frappe.get_cached_doc("Assignment Portal Settings")

    username = "root"
    code_server_host = settings.code_server_host
    private_key_string = private_key.replace("\\n", "\n")

    private_key = paramiko.RSAKey.from_private_key(io.StringIO(private_key_string))

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(code_server_host, username=username, pkey=private_key)

    return client
