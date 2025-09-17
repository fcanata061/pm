# core/chroot_manager.py

import os
import subprocess

def montar_diretorio(diretorio):
    if not os.path.ismount(diretorio):
        print(f"Montando {diretorio}...")
        subprocess.run(["sudo", "mount", diretorio])
    else:
        print(f"{diretorio} já está montado.")

def desmontar_diretorio(diretorio):
    if os.path.ismount(diretorio):
        print(f"Desmontando {diretorio}...")
        subprocess.run(["sudo", "umount", diretorio])
    else:
        print(f"{diretorio} não está montado.")

def gerenciar_chroots(diretorios):
    for diretorio in diretorios:
        montar_diretorio(diretorio)
        print(f"Entrando no chroot {diretorio}...")
        subprocess.run(["sudo", "chroot", diretorio])
        desmontar_diretorio(diretorio)
