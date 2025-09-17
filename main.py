#!/usr/bin/env python3
import argparse
from core import (
    install, remove, build, search, groups, hooks, dependency,
    updater, version_tracker, recipe_sync, logger, chroot
)

def main():
    parser = argparse.ArgumentParser(prog="pm", description="Gerenciador de pacotes completo PM")
    sub = parser.add_subparsers(dest="cmd")

    # ----------------- INSTALL -----------------
    p_install = sub.add_parser("install", aliases=["i"], help="Instala um pacote")
    p_install.add_argument("package", help="Nome do pacote")
    p_install.add_argument("-b", "--build-only", action="store_true", help="Baixa e compila, não instala")
    p_install.add_argument("-j", "--jobs", type=int, default=1, help="Número de jobs para compilação")

    # ----------------- REMOVE -----------------
    p_remove = sub.add_parser("remove", aliases=["rm"], help="Remove um pacote")
    p_remove.add_argument("package", help="Nome do pacote")
    p_remove.add_argument("-o", "--orphans", action="store_true", help="Remove pacotes órfãos")

    # ----------------- BUILD -----------------
    p_build = sub.add_parser("build", aliases=["b"], help="Compila pacotes")
    p_build.add_argument("package", nargs="?", default=None, help="Nome do pacote (ou todos)")
    p_build.add_argument("-j", "--jobs", type=int, default=1, help="Número de jobs para compilação")
    p_build.add_argument("--clean", action="store_true", help="Limpa diretórios de trabalho antes de compilar")

    # ----------------- SEARCH -----------------
    p_search = sub.add_parser("search", aliases=["s"], help="Busca pacotes")
    p_search.add_argument("query", nargs="?", default="", help="Nome ou parte do nome")
    p_search.add_argument("-g", "--group", help="Filtra por grupo")

    # ----------------- GROUPS -----------------
    p_groups = sub.add_parser("groups", aliases=["gr"], help="Mostra pacotes por grupo")
    p_groups.add_argument("group", nargs="?", default=None, help="Nome do grupo")

    # ----------------- HOOKS -----------------
    p_hooks = sub.add_parser("hooks", aliases=["hk"], help="Executa hooks")
    p_hooks.add_argument("type", choices=["pre_build","post_build","pre_install","post_install","post_remove"], help="Tipo de hook")

    # ----------------- REVDEP -----------------
    p_revdep = sub.add_parser("revdep", aliases=["rd"], help="Ver dependentes de um pacote")
    p_revdep.add_argument("package", help="Nome do pacote")

    # ----------------- UPDATER -----------------
    p_update = sub.add_parser("update", aliases=["up"], help="Atualiza pacotes opcionais")
    p_update.add_argument("--group", help="Atualiza todos os pacotes de um grupo")

    # ----------------- VERSION TRACKER -----------------
    p_vercheck = sub.add_parser("version-check", aliases=["vc"], help="Mostra pacotes com nova versão")
    p_verupdate = sub.add_parser("version-update", aliases=["vu"], help="Atualiza um pacote específico")
    p_verupdate.add_argument("package", help="Nome do pacote")

    # ----------------- RECIPE SYNC -----------------
    p_sync_all = sub.add_parser("sync-recipes", aliases=["sr"], help="Sincroniza todas as receitas")
    p_sync_one = sub.add_parser("sync-recipe", aliases=["sro"], help="Sincroniza uma receita específica")
    p_sync_one.add_argument("package", help="Nome do pacote")

    # ----------------- DEPENDENCY -----------------
    p_dep = sub.add_parser("dep", aliases=["d"], help="Mostra ordem de build topológica")
    p_dep.add_argument("packages", nargs="+", help="Pacotes para ordenação")

    # ----------------- CHROOT -----------------
    p_chroot = sub.add_parser("chroot", help="Gerencia ambientes chroot")
    p_chroot.add_argument("diretorios", nargs="+", help="Diretórios dos chroots")

    args = parser.parse_args()

    if args.cmd in ["install","i"]:
        install.install(args.package, build_only=args.build_only, jobs=args.jobs)

    elif args.cmd in ["remove","rm"]:
        remove.remove(args.package, remove_orphans=args.orphans)

    elif args.cmd in ["build","b"]:
        build.build(args.package, jobs=args.jobs, clean=args.clean)

    elif args.cmd in ["search","s"]:
        search.search(query=args.query, group=args.group)

    elif args.cmd in ["groups","gr"]:
        groups.show(args.group)

    elif args.cmd in ["hooks","hk"]:
        hooks.run_hook(args.type)

    elif args.cmd in ["revdep","rd"]:
        dependents = dependency.revdep(args.package)
        print(f"Pacotes que dependem de {args.package}: {dependents}")

    elif args.cmd in ["update","up"]:
        if args.group:
            updater.update_group(args.group)
        else:
            updater.check_updates()

    elif args.cmd in ["version-check","vc"]:
        version_tracker.display_updates()

    elif args.cmd in ["version-update","vu"]:
        version_tracker.update_package(args.package)

    elif args.cmd in ["sync-recipes","sr"]:
        recipe_sync.sync_all()

    elif args.cmd in ["sync-recipe","sro"]:
        recipe = database.find_recipe(args.package)
        if recipe:
            recipe_sync.sync_recipe(recipe)
        else:
            logger.warn(f"Receita {args.package} não encontrada")

    elif args.cmd in ["dep","d"]:
        order = dependency.topological_sort(args.packages)
        print("Ordem de build:", order)

    elif args.cmd == "chroot":
        from modules.chroot_manager import gerenciar_chroots
        gerenciar_chroots(args.diretorios)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
