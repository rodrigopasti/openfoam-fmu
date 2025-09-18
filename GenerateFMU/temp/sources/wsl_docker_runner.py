import subprocess
import time
import re

def process_exists(pid):
    result = subprocess.run(
        ["tasklist", "/FI", f"PID eq {pid}"],
        capture_output=True,
        text=True
    )
    return str(pid) in result.stdout

def to_wsl_path(win_path):
    """
    Converts a Windows path (C:\folder\file) to /mnt/c/folder/file
    """
    m = re.match(r'^([A-Za-z]):[\\/](.*)', str(win_path))
    if not m:
        # If already in Linux/WSL format, return it directly
        return str(win_path)
    drive, rest = m.groups()
    # forward slashes and lowercase drive
    linux_rest = rest.replace('\\', '/').replace('//', '/')
    return f"/mnt/{drive.lower()}/{linux_rest}"

def run_command(cmd, check=True, capture_output=True, shell=False):
    try:
        result = subprocess.run(
            cmd,
            check=check,
            capture_output=capture_output,
            text=True, 
            shell=shell
        )
        if capture_output:
            return result.stdout.strip()
        return None

    except subprocess.CalledProcessError as e:
        print("❌ Error while executing the command:")
        print("Command:", e.cmd)
        print("Return code:", e.returncode)
        
        if e.stdout:
            print("Standard output (stdout):")
            print(e.stdout.strip())

        if e.stderr:
            print("Standard error (stderr):")
            print(e.stderr.strip())

        raise  # Re-raise the exception if further handling is needed


def run_wsl_command(command, silent=False):
    """Executa um comando bash dentro do WSL corretamente."""
    try:
        result = subprocess.run(
            ["wsl", "bash", "-c", command],
            capture_output=True, text=True, check=True
        )
        if not silent:
            return result.stdout.strip()
        return ""
    
    except subprocess.CalledProcessError as e:
        print("❌ Error while executing the WSL command:")
        print("Command:", e.cmd)
        print("Return code:", e.returncode)
        
        if e.stdout:
            print("Standard output (stdout):")
            print(e.stdout.strip())

        if e.stderr:
            print("Standard error (stderr):")
            print(e.stderr.strip())
    if not silent:
        raise  # Re-raise the exception if further handling is needed

def get_default_wsl_distro():
    output = run_command(["wsl", "--list", "--verbose"], capture_output=True)
    for line in output.splitlines():
        # Remove caracteres invisíveis e espaços
        clean_line = line.strip().replace('\x00', '').replace('\r', '').replace('\ufeff', '')
        if '*' in clean_line:
            # O nome da distro vem antes do primeiro espaço
            return clean_line.replace('*', '').strip().split()[0]
    return None

def set_default_wsl_distro(distro):
    print(f"[INFO] Changing WSL default distro to '{distro}'...")
    run_command(["wsl", "--set-default", distro])

def start_dockerd(distro="Ubuntu-Minimal"):
    print("[INFO] Starting dockerd in WSL...")

    # execute a subprocess and keep it running with docker daemon
    process = subprocess.Popen(
        ["wsl", "-d", "Ubuntu-Minimal", "--", "sudo", "dockerd"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for dockerd to start
    for i in range(10):
        try:
            print(f"[DEBUG] Checking if Docker is available (attempt {i+1})...")
            output = run_command(["wsl", "-d", distro, "--", "docker", "version"], capture_output=True)
            if "Server" in output:
                print("[INFO] Docker is active!")
                # Salva o PID do processo localmente
                print(f"dockerd iniciado com PID {process.pid}")
                return process.pid
        except subprocess.CalledProcessError:
	
            time.sleep(5)

    print("[WARNING] Docker could not be started directly.")
    default_distro = get_default_wsl_distro()
    print(f"[DEBUG] Current default distro: {default_distro}")

    if default_distro != distro:
        set_default_wsl_distro(distro)
        print("[INFO] Trying to restart Docker after changing the default distro...")
        return start_dockerd(distro)

    raise RuntimeError("Docker could not be started in WSL even after attempting to change the default distro.")

def import_container(distro, container):
    print(f"[INFO] Importing container from Docker Hub")
    # subprocess.run(["docker", "pull", container], check=True)
    output = run_command(["wsl", "-d", distro, "--", "docker", "pull", container], capture_output=True)
    print(f"[INFO] Container successfully imported: {output}")

def create_runtime_container(distro, container_name, image, root_dir, pid):
    host_path = to_wsl_path(root_dir)
    working_dir = "/" + root_dir.name + "/"
    container_identity = f"{container_name}_{pid}"
    
    create_user_in_wsl(uid=1000, gid=1000)

    print(f"Creating runtime container: {container_identity}")
    output = run_command([
        "wsl", "-d", distro, "--", 
        "docker", "create", "--name", container_identity,
        "--user", "1000:1000",
        "-v", f"{host_path}:{working_dir}",
        "-w", working_dir,
        image,
        "sleep", "infinity"
    ], capture_output=True, check=True)
    print(f"[INFO] Container successfully created: {output}")

def start_and_run_script_in_container(distro, container_name, file, dir_in_container, pid):
    container_path = f"/{dir_in_container}"
    container_identity = f"{container_name}_{pid}"

    print(f"Starting container: {container_identity}")
    run_command(["wsl", "-d", distro, "--", "docker", "start", container_identity], capture_output=True, check=True)

    print(f"Running {file} inside container")
    output = run_command([
        "wsl", "-d", distro, "--", 
        "docker", "exec", container_identity,
        "python3", f"{container_path}/{file}"
    ], capture_output=True, check=True)
    print(f"[INFO] Execution concluded: {output}")

###### Criação do usuário openfoam no WSL/Ubuntu
def group_exists(gid):
    cmd = f"getent group {gid}"
    try:
        run_wsl_command(cmd, silent=True)
        return True
    except SystemExit:
        return False

def user_exists(username):
    cmd = f"id -u {username}"
    try:
        run_wsl_command(cmd, silent=True)
        return True
    except SystemExit:
        return False
    
def create_user_in_wsl(username="openfoamuser", uid=1000, gid=1000):
    created = False

    if not group_exists(gid):
        run_wsl_command(f"sudo groupadd -g {gid} {username}")
        print(f"✅ Grupo '{username}' criado com GID={gid}.")
        created = True

    if not user_exists(username):
        run_wsl_command(f"sudo useradd -m -u {uid} -g {gid} -s /bin/bash {username}")
        print(f"✅ Usuário '{username}' criado com UID={uid}.")
        created = True

    # Sempre grava o arquivo .env (pode ser útil mesmo se já existia)
    env_content = f"USER_NAME={username}\\nUSER_UID={uid}\\nUSER_GID={gid}"
    env_cmd = f"echo -e \"{env_content}\" | sudo tee /tmp/openfoam_user_info.env > /dev/null"
    run_wsl_command(env_cmd, silent=True)

    if created:
        print("✅ Informações salvas em /tmp/openfoam_user_info.env (no WSL).")