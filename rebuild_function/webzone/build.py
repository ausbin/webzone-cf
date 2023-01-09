import subprocess

def clone_shallow(clone_url, repo_path):
    subprocess.run(['git', 'clone', '--depth', '1', clone_url, repo_path], check=True)

def hugo_build(repo_path, hugo_out_path):
    # Use --buildFuture because we probably shouldn't trust the local time of
    # this system (doing so has caused serious confusion for me in the past)
    subprocess.run(['hugo', '--verbose', '--buildFuture', '--destination', hugo_out_path], cwd=repo_path, check=True)
