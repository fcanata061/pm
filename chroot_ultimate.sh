#!/bin/bash
# Script: chroot_ultimate.sh
# Descrição: Chroot avançado ultimate com histórico separado, prompt dinâmico, cores e barra de status
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
# Detecta se já está dentro de um chroot
# =======================
if [ -f /proc/1/root ]; then
    ROOT1=$(readlink /proc/1/root)
    CURRENT=$(readlink /proc/self/root)
    if [ "$ROOT1" != "$CURRENT" ]; then
        warn "Já parece estar dentro de um chroot! Montagens podem ser duplicadas."
    fi
fi

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
# Shell interativo ultimate
# =======================
info "Entrando no chroot ultimate. Para sair, digite 'exit' ou Ctrl+D.'"

# Arquivo de histórico separado
HISTFILE="/root/.bash_history_chroot"
HISTSIZE=1000
HISTFILESIZE=2000

# Exporta variáveis essenciais do host
HOST_ENV="PATH=$PATH LANG=$LANG LC_ALL=$LC_ALL"

# Função para definir prompt dinâmico com cores
read -r -d '' CHROOT_PROMPT <<'EOF'
# Prompt dinâmico por diretório
set_prompt() {
    local BLUE="\[\033[0;34m\]"
    local GREEN="\[\033[0;32m\]"
    local RED="\[\033[0;31m\]"
    local YELLOW="\[\033[1;33m\]"
    local MAGENTA="\[\033[0;35m\]"
    local CYAN="\[\033[0;36m\]"
    local NC="\[\033[0m\]"

    case "$PWD" in
        /root*) COLOR=$RED ;;
        /home*) COLOR=$BLUE ;;
        /var*) COLOR=$YELLOW ;;
        /etc*) COLOR=$MAGENTA ;;
        *) COLOR=$GREEN ;;
    esac

    PS1="${COLOR}[CHROOT \u@\h:\w]\$ ${NC}"
}
PROMPT_COMMAND=set_prompt
EOF

# Executa chroot com shell interativo ultimate
sudo chroot "$CHROOT_DIR" /bin/bash --login -c "
export PS1='[CHROOT \u@\h:\w]\$ '
export HISTFILE='$HISTFILE'
export HISTSIZE=$HISTSIZE
export HISTFILESIZE=$HISTFILESIZE
export $HOST_ENV
shopt -s histappend
$CHROOT_PROMPT
exec /bin/bash
"
