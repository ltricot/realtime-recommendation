import subprocess
from testutils import testcontext


URL = 'https://meme-tinder.firebaseio.com/'

@context(testcontext.PythonPath, ['/home/loan/MEMETINDER_PROJECT/memetinder-nextgen'])
def test():
    """
        Just an example. Technically useless.

    """

    p1 = subprocess.Popen(['python', '-m', 'gapis.tqserver', '&'])
    p2 = subprocess.Popen(['python', '-m', 'testsuite.test2', '&'])
    p3 = subprocess.Popen(['python', '-m', 'testsuite.test3', '&'])

    for p in [p1, p2, p3]:
        p.kill()
