import urllib.error
import urllib.request


def is_update():
    url = "https://raw.githubusercontent.com/itakurah/SittingPostureDetection/main/commit_hash.txt"
    with open('./commit_hash.txt', 'r') as file:
        commit_hash = file.read()
    try:
        with urllib.request.urlopen(url) as response:
            file_contents = response.read().decode('utf-8')
        return 'update available' if commit_hash != file_contents else 'latest version'
    except urllib.error.URLError:
        return 'update check error'
