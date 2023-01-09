import subprocess

def clone_shallow(clone_url, repo_path):
    subprocess.run(['git', 'clone', '--depth', '1', clone_url, repo_path], check=True)

def hugo_build(repo_path, hugo_out_path):
    subprocess.run(['hugo', '--verbose', '--buildFuture', '--destination', hugo_out_path, repo_path], cwd=repo_path, check=True)
