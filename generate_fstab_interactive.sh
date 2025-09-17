#!/bin/bash
# Script: generate_fstab_interactive.sh
# Descrição: Gera /etc/fstab interativo com UUIDs e flags recomendadas (estilo Arch Linux)
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
# Cabeçalho do fstab
# ----------------------------
cat > "$DESTINO" <<EOF
# /etc/fstab: static file system information.
# Gerado automaticamente pelo generate_fstab_interactive.sh
# UUIDs com flags recomendadas por sistema de arquivos (Arch Linux)
EOF

# ----------------------------
# Flags recomendadas por FS
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
# Detectar partições
# ----------------------------
info "Detectando partições disponíveis..."
mapfile -t partitions < <(lsblk -ndo NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE | grep -E 'part|lvm')

declare -A mount_points

for part in "${partitions[@]}"; do
    name=$(echo "$part" | awk '{print $1}')
    size=$(echo "$part" | awk '{print $2}')
    fstype=$(echo "$part" | awk '{print $5}')
    mountpoint=$(echo "$part" | awk '{print $4}')
    # Ignora partições montadas em tmpfs, swap temporário
    [[ "$fstype" =~ tmpfs|devtmpfs ]] && continue
    echo "$name ($size) - FS: $fstype Mount: $mountpoint"
done

# ----------------------------
# Função para selecionar partição
# ----------------------------
select_partition() {
    local purpose="$1"
    echo -e "${CYAN}Selecione a partição para $purpose:${NC}"
    read -r part_name
    echo "$part_name"
}

# ----------------------------
# Tipos de partições principais
# ----------------------------
declare -A fs_types=(
    ["/"]=""
    ["/home"]=""
    ["/boot"]=""
    ["/boot/efi"]=""
    [swap]=""
)

# ----------------------------
# Seleção interativa
# ----------------------------
for mp in "${!fs_types[@]}"; do
    read -p "Digite o nome da partição para $mp (ex: sda1) ou enter para pular: " part
    if [[ -n "$part" ]]; then
        fs_types["$mp"]="$part"
    fi
done

# ----------------------------
# Gerar linhas fstab
# ----------------------------
for mp in "${!fs_types[@]}"; do
    part="${fs_types[$mp]}"
    [[ -z "$part" ]] && continue
    device="/dev/$part"
    fstype=$(lsblk -no FSTYPE "$device")
    [[ "$mp" == "swap" ]] && mp="swap"
    uuid=$(blkid -s UUID -o value "$device")
    flags=$(get_flags "$fstype")
    # Comentário explicativo
    echo "# $mp -> $device ($fstype)" >> "$DESTINO"
    echo "UUID=$uuid $mp $fstype $flags 0 0" >> "$DESTINO"
    success "Adicionada linha: UUID=$uuid $mp $fstype $flags 0 0"
done

# ----------------------------
# Confirmação antes de sobrescrever
# ----------------------------
if [[ "$DESTINO" != "fstab.generated" ]]; then
    read -p "Deseja copiar para $DESTINO como root? (y/N) " ans
    if [[ "$ans" =~ ^[Yy]$ ]]; then
        sudo cp "$DESTINO" "$DESTINO"
        success "Arquivo copiado para $DESTINO"
    else
        warn "Arquivo gerado em $DESTINO, mas não copiado."
    fi
fi

success "fstab interativo gerado com sucesso!"
