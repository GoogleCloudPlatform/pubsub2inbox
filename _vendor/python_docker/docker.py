import subprocess


def load(filename):
    subprocess.check_output(["docker", "load", "-i", filename])


def tag(image, tag, new_image, new_tag):
    command = ["docker", "tag", f"{image}:{tag}", f"{new_image}:{new_tag}"]
    subprocess.check_output(command)


def push(image, tag):
    command = ["docker", "push", f"{image}:{tag}"]
    subprocess.check_output(command)


def pull(image, tag):
    command = ["docker", "pull", f"{image}:{tag}"]
    subprocess.check_output(command)


def run(image, tag, cmd=None):
    command = ["docker", "run", f"{image}:{tag}"]
    if cmd:
        command = command + cmd
    return subprocess.check_output(command)
