import os
import shutil
import tempfile
from core import logger

class Sandbox:
    def __init__(self, base_dir: str = "/tmp/pm_sandbox", keep: bool = False):
        """
        Cria um sandbox para builds.
        :param base_dir: diretório base para todos os sandboxes
        :param keep: se True mantém o sandbox após build
        """
        self.base_dir = base_dir
        self.keep = keep
        self.path = tempfile.mkdtemp(prefix="pm-build-", dir=self.base_dir)
        logger.debug(f"📂 Sandbox criada em {self.path}")

    def run(self, cmd: str, cwd: str = None, check: bool = True):
        """
        Executa um comando dentro do sandbox.
        """
        cwd = cwd or self.path
        logger.debug(f"🏗 Executando no sandbox: {cmd} (cwd={cwd})")
        result = os.system(f"cd {cwd} && {cmd}")
        if check and result != 0:
            logger.error(f"❌ Comando falhou no sandbox: {cmd}")
            raise RuntimeError(f"Falha ao executar: {cmd}")
        return result

    def copy_to_sandbox(self, src: str, dest: str = None):
        """
        Copia arquivos ou diretórios para dentro do sandbox.
        """
        dest_path = os.path.join(self.path, dest) if dest else os.path.join(self.path, os.path.basename(src))
        if os.path.isdir(src):
            shutil.copytree(src, dest_path)
        else:
            shutil.copy2(src, dest_path)
        logger.debug(f"📁 Copiado {src} para {dest_path}")
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
