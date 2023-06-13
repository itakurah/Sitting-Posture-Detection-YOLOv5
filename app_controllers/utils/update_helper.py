import urllib.request
import urllib.error


def is_update():
    url = "https://raw.githubusercontent.com/itakurah/SittingPostureDetection/main/commit_hash.txt"
    with open('./commit_hash.txt', 'r') as file:
        commit_hash = file.read()
    try:
        with urllib.request.urlopen(url) as response:
            file_contents = response.read().decode('utf-8')
        return 'Update available' if commit_hash != file_contents else 'Latest version'
    except urllib.error.URLError:
        return 'Could not check for updates'
