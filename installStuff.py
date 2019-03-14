from pip._internal import main as pipmain

pipmain(["install", "-r", "requirements.txt"])
pipmain(["install", "-r", "requirements2.txt"])
