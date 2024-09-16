import subprocess

def git_diff_branch(branch='main'):
    """
    Get the git diff of staged changes against a specified branch.
    """
    result = subprocess.run(['git', 'diff', '--cached', branch], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')

