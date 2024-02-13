import tempfile
import os

from _vendor.python_docker.base import Image


def test_read_docker_image_from_file():
    filename = "tests/assets/busybox.tar"

    image = Image.from_filename(filename)[0]

    assert image.name == "busybox"
    assert image.tag == "latest"
    assert len(image.layers) == 1
    assert (image.layers[0].checksum ==
            "5b8c72934dfc08c7d2bd707e93197550f06c0751023dabb3a045b723c5e7b373")
    assert (image.layers[0].compressed_checksum ==
            "8cff16fb5a3a3d60cbe59e72f2ec02291d78afc3e214e75e1ddbbe79766473e3")


def test_read_write_read_docker_image_from_file():
    filename = "tests/assets/busybox.tar"
    image = Image.from_filename(filename)[0]

    with tempfile.TemporaryDirectory() as tmpdir:
        filename = os.path.join(tmpdir, "docker.tar")
        image.write_filename(filename)
        new_image = Image.from_filename(filename)[0]

    assert image.name == new_image.name
    assert image.tag == new_image.tag
    assert len(image.layers) == len(new_image.layers)
    assert image.layers[0].checksum == new_image.layers[0].checksum
    assert (image.layers[0].compressed_checksum ==
            new_image.layers[0].compressed_checksum)


def test_run_read_docker_image_from_file():
    filename = "tests/assets/busybox.tar"
    image = Image.from_filename(filename)[0]

    message = "hello, world!"
    assert image.run(["echo", message]).decode("utf-8") == f"{message}\n"

    # assert default permissions
    assert (image.run(
        ["id"]).decode("utf-8") == "uid=0(root) gid=0(root) groups=10(wheel)\n")

    output = image.run(["env"])[:-1].decode("utf-8")
    environment = {
        row.split("=")[0]: row.split("=")[1] for row in output.split("\n")
    }
    assert (environment["PATH"] ==
            "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin")


def test_add_layer_from_dict_no_filter():
    filename = "tests/assets/busybox.tar"
    image = Image.from_filename(filename)[0]

    path = "/var/lib/this/is/a/path"
    message = b"hello, world!"
    contents = {
        os.path.join(path, "hello.txt"):
            message,
        os.path.join(path, "script.sh"):
            b'#!/bin/sh\n\necho "hello, world! $((1 + 2))"\n',
    }
    image.add_layer_contents(contents, filter=None)

    assert image.run([f"cat {os.path.join(path, 'hello.txt')}"]) == message
    assert image.run([f"ls {path}"]) == b"hello.txt\nscript.sh\n"


def test_add_layer_from_dict_filter():
    filename = "tests/assets/busybox.tar"
    image = Image.from_filename(filename)[0]

    path = "/var/lib/this/is/a/path"
    message = b"hello, world!"
    contents = {
        os.path.join(path, "hello.txt"):
            message,
        os.path.join(path, "script.sh"):
            b'#!/bin/sh\n\necho "hello, world! $((1 + 2))"\n',
    }

    def filename_filter(tarinfo):
        return None if tarinfo.name.endswith(".txt") else tarinfo

    image.add_layer_contents(contents, filter=filename_filter)

    assert image.run([f"ls {path}"]) == b"script.sh\n"


def test_add_layer_from_path_no_filter():
    filename = "tests/assets/busybox.tar"
    image = Image.from_filename(filename)[0]

    path = "/this/is/a/path"
    image.add_layer_path("tests/assets/example", path, filter=None)

    assert image.run([os.path.join(path, "script.sh")]) == b"hello, world! 3\n"
    assert image.run([f"ls {path}"]) == b"hello.txt\nscript.sh\n"


def test_add_layer_from_path_filter():
    filename = "tests/assets/busybox.tar"
    image = Image.from_filename(filename)[0]

    path = "/this/is/a/path"

    def filename_filter(tarinfo):
        return None if tarinfo.name.endswith(".txt") else tarinfo

    image.add_layer_path("tests/assets/example", path, filter=filename_filter)

    assert image.run([os.path.join(path, "script.sh")]) == b"hello, world! 3\n"
    assert image.run([f"ls {path}"]) == b"script.sh\n"


def test_remove_layer():
    filename = "tests/assets/busybox.tar"
    image = Image.from_filename(filename)[0]

    path = "/this/is/a/path"
    image.add_layer_path("tests/assets/example", path)

    assert image.run([f"ls {path}"]) == b"hello.txt\nscript.sh\n"

    image.remove_layer()

    assert (image.run(
        ["ls",
         "/"]) == b"bin\ndev\netc\nhome\nproc\nroot\nsys\ntmp\nusr\nvar\n")
