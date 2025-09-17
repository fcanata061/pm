def handle(action, group_name):
    groups = {
        "base": ["gcc", "glibc", "binutils", "kernel"],
        "desktop": ["xorg", "firefox", "vim"]
    }

    if action == "list":
        for g, pkgs in groups.items():
            print(f"{g}: {', '.join(pkgs)}")
    elif action == "install" and group_name in groups:
        for pkg in groups[group_name]:
            print(f"Instalando {pkg} do grupo {group_name}")
    elif action == "remove" and group_name in groups:
        for pkg in groups[group_name]:
            print(f"Removendo {pkg} do grupo {group_name}")
