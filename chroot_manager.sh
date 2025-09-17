#!/bin/bash
# Script: chroot_manager.sh
# Descrição: Módulo profissional para gerenciar múltiplos chroots
# Autor: Fernando Canata

set -euo pipefail

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

log_file="/tmp/chroot_manager.log"

info()    { echo -e "${CYAN}[INFO]${NC} $1"; echo "[INFO] $1" >> "$log_file"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; echo "[OK] $1" >> "$log_file"; }
warn()    { echo -e "${YELLOW}[AVISO]${NC} $1"; echo "[AVISO] $1" >> "$log_file"; }
error()   { echo -e "${RED}[ERRO]${NC} $1"; echo "[ERRO] $1" >> "$log_file"; }

# =======================
# Verifica dependências
# =======================
for cmd in mount umount chroot sudo; do
    if ! command -v "$cmd" &> /dev/null; then
        error "Comando $cmd não encontrado. Instale antes de usar."
        exit 1
    fi
done

# =======================
# Recebe múltiplos chroots
# =======================
if [ "$#" -lt 1 ]; then
    error "Uso: $0 /caminho/para/chroot1 [/caminho/para/chroot2 ...]"
    exit 1
fi

CHROOTS=("$@")

# Diretórios essenciais para cada chroot
MOUNTS=(
    "proc:proc:"
    "sys:sysfs:"
    "dev:devtmpfs:"
    "dev/pts:devpts:-o gid=5,mode=620"
)

# =======================
# Função: preparar chroot
# =======================
prepare_chroot() {
    local CHROOT_DIR="$1"
    info "Preparando chroot: $CHROOT_DIR"

    if [ ! -d "$CHROOT_DIR" ]; then
        error "Diretório $CHROOT_DIR não existe. Pulando..."
        return 1
    fi

    # Cria diretórios essenciais
    for entry in "${MOUNTS[@]}"; do
        dir="${entry%%:*}"
        full_path="$CHROOT_DIR/$dir"
        [ -d "$full_path" ] || mkdir -p "$full_path"
    done

    # Monta diretórios
    for entry in "${MOUNTS[@]}"; do
        dir="${entry%%:*}"
        type="${entry#*:}"
        type="${type%%:*}"
        opts="${entry##*:}"
        full_path="$CHROOT_DIR/$dir"

        if mountpoint -q "$full_path"; then
            success "$full_path já está montado."
        else
            info "Montando $full_path..."
            sudo mount -t "$type" $opts "$full_path"
            success "$full_path montado."
        fi
    done

    # Permissões root
    sudo chown -R root:root "$CHROOT_DIR"
}

# =======================
# Função: desmontar chroot
# =======================
cleanup_chroot() {
    local CHROOT_DIR="$1"
    info "Desmontando chroot: $CHROOT_DIR"
    for (( idx=${#MOUNTS[@]}-1; idx>=0; idx-- )); do
        entry="${MOUNTS[idx]}"
        dir="${entry%%:*}"
        full_path="$CHROOT_DIR/$dir"
        if mountpoint -q "$full_path"; then
            info "Desmontando $full_path..."
            sudo umount -l "$full_path"
            success "$full_path desmontado."
        fi
    done
}

# =======================
# Função: shell interativo avançado
# =======================
launch_chroot_shell() {
    local CHROOT_DIR="$1"
    local HISTFILE="/root/.bash_history_chroot"
    local HISTSIZE=1000
    local HISTFILESIZE=2000
    local HOST_ENV="PATH=$PATH LANG=$LANG LC_ALL=$LC_ALL"

    read -r -d '' CHROOT_PROMPT <<'EOF'
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

    info "Entrando no chroot: $CHROOT_DIR"
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
}

# =======================
# Loop por todos os chroots
# =======================
for CHROOT_DIR in "${CHROOTS[@]}"; do
    prepare_chroot "$CHROOT_DIR" || continue
    trap "cleanup_chroot '$CHROOT_DIR'" EXIT
    launch_chroot_shell "$CHROOT_DIR"
    cleanup_chroot "$CHROOT_DIR"
done

success "Todos os chroots foram encerrados com segurança."
