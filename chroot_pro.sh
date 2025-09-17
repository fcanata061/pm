#!/bin/bash
# Script: chroot_pro.sh
# Descrição: Chroot avançado com histórico separado, prompt dinâmico e seguro
# Autor: Fernando Canata

set -e

# =======================
# Funções de cor
# =======================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

info()    { echo -e "${CYAN}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn()    { echo -e "${YELLOW}[AVISO]${NC} $1"; }
error()   { echo -e "${RED}[ERRO]${NC} $1"; }

# =======================
# Verifica diretório chroot
# =======================
if [ -z "$1" ]; then
    error "Uso: $0 /caminho/para/chroot"
    exit 1
fi

CHROOT_DIR="$1"

# Diretórios essenciais dentro do chroot
MOUNTS=(
    "proc:proc:"
    "sys:sysfs:"
    "dev:devtmpfs:"
    "dev/pts:devpts:-o gid=5,mode=620"
)

info "Preparando ambiente chroot em $CHROOT_DIR..."

# Cria diretórios se não existirem
for entry in "${MOUNTS[@]}"; do
    dir="${entry%%:*}"
    full_path="$CHROOT_DIR/$dir"
    if [ ! -d "$full_path" ]; then
        info "Criando diretório $full_path..."
        mkdir -p "$full_path"
    fi
done

# =======================
# Montagem
# =======================
mount_chroot() {
    for entry in "${MOUNTS[@]}"; do
        dir="${entry%%:*}"
        type="${entry#*:}"
        type="${type%%:*}"
        opts="${entry##*:}"
        full_path="$CHROOT_DIR/$dir"

        if mountpoint -q "$full_path"; then
            success "$full_path já está montado, pulando..."
        else
            info "Montando $full_path..."
            sudo mount -t "$type" $opts "$full_path"
            success "$full_path montado!"
        fi
    done
}

# =======================
# Desmontagem
# =======================
umount_chroot() {
    for (( idx=${#MOUNTS[@]}-1 ; idx>=0 ; idx-- )) ; do
        entry="${MOUNTS[idx]}"
        dir="${entry%%:*}"
        full_path="$CHROOT_DIR/$dir"

        if mountpoint -q "$full_path"; then
            info "Desmontando $full_path..."
            sudo umount -l "$full_path"
            success "$full_path desmontado!"
        fi
    done
}

mount_chroot
trap umount_chroot EXIT

# =======================
# Permissões corretas
# =======================
sudo chown -R root:root "$CHROOT_DIR"

# =======================
# Shell interativo avançado
# =======================
info "Entrando no chroot. Para sair, digite 'exit' ou Ctrl+D.'"

# Arquivo de histórico separado
HISTFILE="/root/.bash_history_chroot"
HISTSIZE=1000
HISTFILESIZE=2000

# Prompt dinâmico: muda de cor conforme diretório
CHROOT_PS1='${debian_chroot:+($debian_chroot)}\[\033[1;32m\]\u\[\033[0;33m\]@\h:\[\033[0;36m\]\w\[\033[0m\]\$ '

# Exporta variáveis essenciais do host
HOST_ENV="PATH=$PATH LANG=$LANG LC_ALL=$LC_ALL"

# Executa chroot com shell interativo avançado
sudo chroot "$CHROOT_DIR" /bin/bash --login -c "
export PS1='$CHROOT_PS1'
export HISTFILE='$HISTFILE'
export HISTSIZE=$HISTSIZE
export HISTFILESIZE=$HISTFILESIZE
export $HOST_ENV
shopt -s histappend
exec /bin/bash
"
