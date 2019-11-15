import subprocess
import sys


def install(package):
    try:
        import pip
    except ImportError:
        print("installing pip")
        cmd = "sudo easy_install pip"
        subprocess.call([sys.executable, cmd])

    subprocess.call([sys.executable, "-m", "pip", "install", package])


if __name__ == '__main__':
    packages_to_install = [
        "aiohttp",
        "aiofiles",
        "pandas"
    ]
    for package in packages_to_install:
        install(package)
