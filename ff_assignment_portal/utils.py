import io
import frappe
import paramiko

def get_ssh_client(private_key: str):
    settings = frappe.get_cached_doc("Assignment Portal Settings")

    username = "root"
    code_server_host = settings.code_server_host
    private_key_string = private_key.replace("\\n", "\n")

    key_class = None
    if settings.private_key_type == "rsa":
        key_class = paramiko.RSAKey
    elif settings.private_key_type == "ed25519":
        key_class = paramiko.Ed25519Key
    else:
        frappe.throw("Invalid key type")

    private_key = key_class.from_private_key(io.StringIO(private_key_string))

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(code_server_host, username=username, pkey=private_key)

    return client
