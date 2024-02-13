import pytest

from _vendor.python_docker import docker
from _vendor.python_docker.registry import Registry
from _vendor.python_docker.base import Image


@pytest.mark.parametrize(
    "hostname, image_name, tag, layers",
    [
        ("https://registry-1.docker.io", "library/hello-world", "latest", 1),
        ("https://registry-1.docker.io", "library/busybox", "1.34.0", 1),
        ("https://registry-1.docker.io", "condaforge/miniforge3", "4.10.3-7",
         2),
        ("https://registry-1.docker.io", "library/ubuntu", "xenial", 4),
        ("https://quay.io", "libpod/alpine", "latest", 1),
    ],
)
def test_dockerhub_pull(hostname, image_name, tag, layers):
    registry = Registry(hostname)
    # use lazy to avoid actual downloads of layers for this test
    image = registry.pull_image(image_name, tag, lazy=True)
    assert image.name == image_name
    assert image.tag == tag
    assert len(image.layers) == layers


@pytest.mark.parametrize(
    "config, image, action",
    [
        (dict(hostname="http://localhost:5000"), None, None),
        (
            dict(
                hostname="http://localhost:6000",
                username="admin",
                password="password",
            ),
            None,
            None,
        ),
        (dict(hostname="https://registry-1.docker.io"), "library/alpine",
         "pull"),
        (dict(hostname="https://quay.io"), "libpod/alpine", "pull"),
    ],
)
def test_registry_authenticated(config, image, action):
    r = Registry(**config)
    r.authenticate(image, action)


@pytest.mark.parametrize(
    "config",
    [
        dict(
            hostname="http://localhost:6000",
            username="admin",
            password="passwordwrong",
        ),
    ],
)
def test_registry_not_authenticated(config):
    with pytest.raises(ValueError):
        r = Registry(**config)
        r.authenticate()


def test_local_docker_pull():
    image_filename = "tests/assets/busybox.tar"
    image, tag = "busybox", "latest"
    new_image_full, new_image, new_tag = (
        "localhost:5000/library/mybusybox",
        "library/mybusybox",
        "mylatest",
    )

    docker.load(image_filename)
    docker.tag(image, tag, new_image_full, new_tag)
    docker.push(new_image_full, new_tag)

    registry = Registry(hostname="http://localhost:5000")

    assert new_image in registry.list_images()
    assert new_tag in registry.list_image_tags("library/mybusybox")

    image = registry.pull_image(new_image, new_tag)

    assert image.name == new_image
    assert image.tag == new_tag
    assert len(image.layers) == 1


@pytest.mark.parametrize(
    "config",
    [
        dict(hostname="http://localhost:5000"),
        dict(
            hostname="http://localhost:6000",
            username="admin",
            password="password",
        ),
    ],
)
def test_local_docker_push(config):
    filename = "tests/assets/hello-world.tar"
    image = Image.from_filename(filename)[0]

    registry = Registry(**config)
    registry.push_image(image)

    assert image.name in registry.list_images()
    assert image.tag in registry.list_image_tags(image.name)


def test_local_docker_delete():
    image_filename = "tests/assets/busybox.tar"
    image, tag = "busybox", "latest"
    new_image_full, new_image, new_tag = (
        "localhost:5000/library/mybusybox",
        "library/mybusybox",
        "mylatest",
    )

    docker.load(image_filename)
    docker.tag(image, tag, new_image_full, new_tag)
    docker.push(new_image_full, new_tag)

    registry = Registry(hostname="http://localhost:5000")

    assert new_image in registry.list_images()
    assert new_tag in registry.list_image_tags(new_image)

    registry.delete_image(new_image, new_tag)

    available_tags = registry.list_image_tags(new_image)
    assert available_tags is None or new_tag not in available_tags
