from src.CLI.command_line_interface import cli
import typer


def main():
    typer.run(cli)


if __name__ == "__main__":
    main()