import datetime
import os

from _vendor.python_docker import docker
from _vendor.python_docker.base import Image
from _vendor.python_docker.registry import Registry


def test_local_docker_push_pull_lazy():
    """Full end to end test of working with a docker registry lazily

    1. Authenticate with unauthenticated docker registry
    2. Push docker image to registry
    3. Pull same docker image LAZILY
    3. Add content to image
    4. Check that pulled docker image does not actually have any of the layer contents locally
    5. Push new content to registry (without having the actual full docker image)
    6. Check that docker image STILL does not actually have any of the layer contents locally
    7. Run the docker image
    8. Check that the act of running the docker image forced the contents to be fetched and got the right result
    9. Pull new docker image that was just pushed not lazily
    10. Check that the act of running the docker image got the right result

    """
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

    image = registry.pull_image(new_image, new_tag, lazy=True)

    assert image.name == new_image
    assert image.tag == new_tag
    assert len(image.layers) == 1

    content_path = "/a/b/c/d.txt"
    content_message = b"a layer"
    image.add_layer_contents({content_path: content_message})

    # check that all but first layer are not fetched
    # since they still lazily exist at registry
    assert hasattr(image.layers[0], "_cached_content")
    for layer in image.layers[1:]:
        assert not hasattr(layer, "_cached_content")

    image.tag = "anothertagname"
    registry.push_image(image)

    assert image.run([f"cat {content_path}"]) == content_message

    new_image = registry.pull_image(image.name, image.tag)
    assert len(new_image.layers) == 2
    new_image.write_filename("example.tar")
    assert new_image.run([f"cat {content_path}"]) == content_message


def test_dockerhub_push():
    registry = Registry(
        hostname="https://registry-1.docker.io",
        username=os.environ["DOCKER_USERNAME"],
        password=os.environ["DOCKER_PASSWORD"],
    )

    utcnow_str = datetime.datetime.utcnow().strftime("%m-%d-%Y-%H-%M-%S")
    image = Image("costrouc/pytest-python-docker", utcnow_str)
    image.add_layer_contents(
        {"/a/b/c.txt": "some content {utcnow_str}".encode("utf-8")})

    registry.push_image(image)


def test_quayio_push():
    registry = Registry(
        hostname="https://quay.io",
        username=os.environ["QUAY_USERNAME"],
        password=os.environ["QUAY_PASSWORD"],
    )

    utcnow_str = datetime.datetime.utcnow().strftime("%m-%d-%Y-%H-%M-%S")
    image = Image("costrouc/pytest-python-docker", utcnow_str)
    image.add_layer_contents(
        {"/a/b/c.txt": "some content {utcnow_str}".encode("utf-8")})

    registry.push_image(image)
