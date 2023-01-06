#!/usr/bin/env pipenv-shebang
# coding:utf8
import sys, os
import argparse
import logging
import subprocess

logging.basicConfig(level=logging.INFO)


def parse_args_or_exit():
    parser = argparse.ArgumentParser(
        description="diff between 2 terraform folder, cross environment, excluding remote backend file and .terraform folder."
    )
    parser.add_argument(
        "--env1",
        type=str,
        help="the path of the first env you want to diff.",
    )
    parser.add_argument(
        "--env2",
        type=str,
        help="the path of the second env you want to diff.",
    )

    args = parser.parse_args()
    return check_args_valid_or_exit(parser, args)


def check_args_valid_or_exit(parser, args):
    if not args.env1:
        logging.error("arg --env1 is missing, exiting early ...")
        parser.print_help()
        sys.exit(-1)

    if not os.path.exists(args.env1):
        logging.error("path provide in arg env1 not found, exiting early ...")
        sys.exit(-1)

    if not args.env2:
        logging.error("arg --env2 is missing, exiting early ...")
        parser.print_help()
        sys.exit(-1)

    if not os.path.exists(args.env2):
        logging.error("path provide in arg env2 not found, exiting early ...")
        sys.exit(-1)

    return args


def get_subfolders_list(args):
    return os.listdir(args.env1), os.listdir(args.env2)


def print_and_filter_extra_folder(env1, env2):

    diff_env1_env2 = [folder for folder in env1 if folder not in env2]
    if diff_env1_env2:
        print("extra folders found in env1")
        print(diff_env1_env2)

    diff_env2_env1 = [folder for folder in env2 if folder not in env1]
    if diff_env2_env1:
        print("extra folders found in env2")
        print(diff_env2_env1)


def compare_list(env1, env2):
    return [x for x in env2 if x in env1]


def diff_filtered_files_in_folder(folders_list, args):
    print("")
    for folder in folders_list:
        filtered_files = filter_terraform_and_backend(
            os.listdir(args.env1 + "/" + folder)
        )
        for file in filtered_files:
            file_env1 = os.path.join(args.env1, folder, file)
            file_env2 = os.path.join(args.env2, folder, file)
            is_diff = color_diff_two_files(file_env1, file_env2)

            if is_diff:
                short_file1=os.path.join(os.path.basename(args.env1) , folder , file)
                short_file2 = os.path.join(os.path.basename(args.env2) , folder , file)
                print(
                    f"diff between {short_file1} and {short_file2}\n"
                )
                print(is_diff)


def color_diff_two_files(file1, file2):
    result = subprocess.run(
        [f"diff {file1} {file2} --color=always"], capture_output=True, shell=True
    )
    if result.stdout:
        return result.stdout.decode("utf8")
    return ""


def filter_terraform_and_backend(files_list):
    return [
        file
        for file in files_list
        if file
        not in [".terraform", "config.tf", "terraform.tfvars", ".terraform.lock.hcl"]
    ]


def main():
    args = parse_args_or_exit()
    env1, env2 = get_subfolders_list(args)
    print_and_filter_extra_folder(env1, env2)
    folders_list = compare_list(env1, env2)
    diff_filtered_files_in_folder(folders_list, args)


if __name__ == "__main__":
    main()
