import os
import shutil
import tempfile
from core import logger

class Sandbox:
    def __init__(self, base_dir: str = "/tmp/pm_sandbox", keep: bool = False, use_fakeroot: bool = False):
        """
        Cria um sandbox para builds.
        :param base_dir: diretório base para todos os sandboxes
        :param keep: se True mantém o sandbox após build
        :param use_fakeroot: se True executa comandos com fakeroot
        """
        self.base_dir = base_dir
        self.keep = keep
        self.use_fakeroot = use_fakeroot
        self.path = tempfile.mkdtemp(prefix="pm-build-", dir=self.base_dir)
        os.chmod(self.path, 0o700)  # Somente dono tem acesso
        logger.debug(f"📂 Sandbox criada em {self.path} com permissões 700")

    def run(self, cmd: str, cwd: str = None, check: bool = True):
        """
        Executa um comando dentro do sandbox.
        """
        cwd = cwd or self.path
        full_cmd = f"fakeroot {cmd}" if self.use_fakeroot else cmd
        logger.debug(f"🏗 Executando no sandbox: {full_cmd} (cwd={cwd})")
        result = os.system(f"cd {cwd} && {full_cmd}")
        if check and result != 0:
            logger.error(f"❌ Comando falhou no sandbox: {full_cmd}")
            raise RuntimeError(f"Falha ao executar: {full_cmd}")
        return result

    def copy_to_sandbox(self, src: str, dest: str = None):
        """
        Copia arquivos ou diretórios para dentro do sandbox e ajusta permissões.
        """
        dest_path = os.path.join(self.path, dest) if dest else os.path.join(self.path, os.path.basename(src))
        if os.path.isdir(src):
            shutil.copytree(src, dest_path)
            for root, dirs, files in os.walk(dest_path):
                for d in dirs:
                    os.chmod(os.path.join(root, d), 0o700)
                for f in files:
                    os.chmod(os.path.join(root, f), 0o600)
        else:
            shutil.copy2(src, dest_path)
            os.chmod(dest_path, 0o600)
        logger.debug(f"📁 Copiado {src} para {dest_path} com permissões seguras")
        return dest_path

    def cleanup(self):
        """
        Remove o sandbox, se keep=False.
        """
        if not self.keep:
            shutil.rmtree(self.path, ignore_errors=True)
            logger.debug(f"🧹 Sandbox {self.path} removida")
        else:
            logger.debug(f"💾 Sandbox preservada em {self.path}")

    def get_path(self):
        """
        Retorna o caminho do sandbox.
        """
        return self.path

    def destdir_path(self, subdir: str = ""):
        """
        Retorna um DESTDIR seguro dentro do sandbox.
        """
        path = os.path.join(self.path, subdir) if subdir else self.path
        os.makedirs(path, exist_ok=True)
        os.chmod(path, 0o700)
        return path
