import os

from argparse import ArgumentParser


def main():
    parser = ArgumentParser()

    cmd_run = parser.add_argument_group("run")
    cmd_run.add_argument("command")

    args = parser.parse_args()


if __name__ == "__main__":
    main()
