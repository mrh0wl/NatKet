
import signal
import subprocess

from colorama import Fore, Style


def print_info(message):
    print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} {message}")


def print_run(message):
    print(f"{Fore.YELLOW}[RUN]{Style.RESET_ALL} {message}")


def print_done(message):
    print(f"{Fore.GREEN}[DONE]{Style.RESET_ALL} {message}")


def print_fail(message):
    print(f"{Fore.RED}[FAIL]{Style.RESET_ALL} {message}")


def signal_handler(signalnumb, frame):
    pass


# With 'SIGINT' (CTRL + C), we can register our signal handler.
signal.signal(signal.SIGINT, signal_handler)



def seed():
    py = "python"
    manage = "manage.py"
    print_info("Resetting the database")
    subprocess.run([py, manage, "flush", "--noinput"], check=True)
    print_done("Database reset")

    print_info("Running migrations")
    subprocess.run([py, manage, "makemigrations"], check=True)
    subprocess.run([py, manage, "migrate"], check=True)
    print_done("Migrations completed")

    print_info("Running seed data script")
    subprocess.run([py, manage, "seed"], check=True)
    print_done("Seed data script executed")


def dev():
    subprocess.check_call(["uvicorn", "app:app", "--reload"])
