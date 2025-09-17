# core/chroot.py

import os
import subprocess

def montar_diretorio(diretorio):
    if not os.path.ismount(diretorio):
        print(f"[INFO] Montando {diretorio}...")
        subprocess.run(["sudo", "mount", "-o", "bind", diretorio, diretorio], check=True)
    else:
        print(f"[OK] {diretorio} já está montado.")

def desmontar_diretorio(diretorio):
    if os.path.ismount(diretorio):
        print(f"[INFO] Desmontando {diretorio}...")
        subprocess.run(["sudo", "umount", "-l", diretorio], check=True)
    else:
        print(f"[OK] {diretorio} não está montado.")

def gerenciar_chroots(diretorios):
    for diretorio in diretorios:
        # Montagem de diretórios essenciais
        for subdir in ["proc", "sys", "dev", "dev/pts"]:
            full_path = os.path.join(diretorio, subdir)
            os.makedirs(full_path, exist_ok=True)
            montar_diretorio(full_path)
        
        print(f"[INFO] Entrando no chroot {diretorio}...")
        subprocess.run(["sudo", "chroot", diretorio], check=True)

        # Desmontagem segura
        for subdir in reversed(["proc", "sys", "dev/pts", "dev"]):
            full_path = os.path.join(diretorio, subdir)
            desmontar_diretorio(full_path)
