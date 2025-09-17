#!/bin/bash
# Wrapper PM: cria ambiente Linux completo e toolchain stages
# Autor: Fernando Canata

set -euo pipefail

# ----------------------------
# Configurações
# ----------------------------
ROOTFS_DIR="${1:-/mnt/lfs}"      # Diretório do rootfs
PM_CMD="${PM_CMD:-pm}"           # Caminho para o gerenciador PM
LOGFILE="${ROOTFS_DIR}/build_stage.log"

# Cores
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
info()    { echo -e "${CYAN}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn()    { echo -e "${YELLOW}[AVISO]${NC} $1"; }
error()   { echo -e "${RED}[ERRO]${NC} $1"; }

# ----------------------------
# Criação do rootfs
# ----------------------------
info "Criando diretórios base do Linux em $ROOTFS_DIR..."
dirs=(bin boot dev etc home lib lib64 proc root run sbin sys tmp usr var)
for d in "${dirs[@]}"; do
    mkdir -p "$ROOTFS_DIR/$d"
done
chmod 1777 "$ROOTFS_DIR/tmp"
chmod 755 "$ROOTFS_DIR"
success "Diretórios criados com sucesso."

# ----------------------------
# Montagem segura via módulo chroot
# ----------------------------
info "Montando pseudo-filesystems usando módulo chroot do PM..."
# Supondo que o PM tenha um subcomando 'chroot' para montar e desmontar diretórios
$PM_CMD chroot "$ROOTFS_DIR" mount
success "Pseudo-filesystems montados."

# ----------------------------
# Função cleanup (desmonta automaticamente)
# ----------------------------
cleanup() {
    info "Desmontando pseudo-filesystems via módulo chroot..."
    $PM_CMD chroot "$ROOTFS_DIR" umount || true
}
trap cleanup EXIT

# ----------------------------
# Construção automática de stages
# ----------------------------
stages=(stage1 stage2 stage3)
for stage in "${stages[@]}"; do
    info "Construindo $stage..."
    # Chama PM dentro do chroot
    $PM_CMD chroot "$ROOTFS_DIR" "$stage" | tee -a "$LOGFILE"
    success "$stage concluído."
done

success "Todos os stages foram construídos com sucesso!"
