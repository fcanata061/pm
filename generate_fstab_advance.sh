#!/bin/bash
# Script: generate_fstab_advanced.sh
# Descrição: Gera /etc/fstab com UUIDs e flags recomendadas, estilo Arch Linux
# Autor: Fernando Canata

set -euo pipefail

# ----------------------------
# Cores
# ----------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()    { echo -e "${CYAN}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn()    { echo -e "${YELLOW}[AVISO]${NC} $1"; }
error()   { echo -e "${RED}[ERRO]${NC} $1"; }

# ----------------------------
# Destino do fstab
# ----------------------------
DESTINO="${1:-fstab.generated}"
info "Arquivo fstab será salvo em: $DESTINO"

# ----------------------------
# Cabeçalho
# ----------------------------
cat > "$DESTINO" <<EOF
# /etc/fstab: static file system information.
# Gerado automaticamente pelo generate_fstab_advanced.sh
# UUIDs com flags recomendadas por sistema de arquivos (Arch Linux)
EOF

# ----------------------------
# Função: flags recomendadas por fs
# ----------------------------
get_flags() {
    local fstype="$1"
    case "$fstype" in
        ext4) echo "defaults,noatime" ;;
        xfs)  echo "defaults,noatime,attr2,inode64" ;;
        btrfs) echo "defaults,compress=zstd,ssd,discard=async" ;;
        swap) echo "sw" ;;
        vfat|fat32|msdos) echo "defaults" ;;
        ntfs) echo "defaults" ;;
        *) echo "defaults" ;;
    esac
}

# ----------------------------
# Detectar partições montadas
# ----------------------------
info "Detectando partições montadas..."
while read -r device mountpoint fstype options rest; do
    # Ignorar tmpfs, devtmpfs, sysfs, proc
    [[ "$fstype" =~ tmpfs|devtmpfs|proc|sysfs ]] && continue

    # Obter UUID
    uuid=$(blkid -s UUID -o value "$device" 2>/dev/null || echo "")
    if [ -z "$uuid" ]; then
        warn "Não foi possível obter UUID de $device. Pulando..."
        continue
    fi

    # Obter flags recomendadas
    flags=$(get_flags "$fstype")

    # Gerar linha fstab
    line="UUID=$uuid $mountpoint $fstype $flags 0 0"
    echo "$line" >> "$DESTINO"
    success "Adicionada: $line"

done < <(mount | grep '^/' | awk '{print $1, $3, $5, $6}')

# ----------------------------
# Confirmar sobrescrever
# ----------------------------
if [[ "$DESTINO" != "fstab.generated" ]]; then
    info "Deseja copiar para $DESTINO como root? (y/N)"
    read -r ans
    if [[ "$ans" =~ ^[Yy]$ ]]; then
        sudo cp "$DESTINO" "$DESTINO"
        success "Arquivo copiado para $DESTINO"
    else
        warn "Arquivo gerado em $DESTINO, mas não copiado."
    fi
fi

success "fstab gerado com sucesso!"
