import json
import gzip
import functools
import base64
import re
from urllib.parse import urlparse, parse_qs

import requests

from _vendor.python_docker.base import Image, Layer
from _vendor.python_docker import schema


class Registry:

    tls_verify = True

    def __init__(
        self,
        hostname: str = "https://registry-1.docker.io",
        username: str = None,
        password: str = None,
        verify: bool = True,
    ):
        self.hostname = hostname
        self.username = username
        self.password = password
        if not verify:
            self.tls_verify = False
        self.detect_authentication()
        self.session = requests.Session()
        if not verify:
            self.session.verify = False

    def detect_authentication(self):
        response = requests.get(f"{self.hostname}/v2/", verify=self.tls_verify)
        if "www-authenticate" in response.headers:
            auth_scheme, parameters = response.headers[
                "www-authenticate"].split(" ", 1)
            self.authentication_type = auth_scheme
            self.authentication_parameters = {
                key: value
                for key, value in re.findall('([^,=]*)="([^"]*)"', parameters)
            }
            if auth_scheme == "Basic":
                if self.username is None or self.password is None:
                    raise ValueError(
                        "registry requires basic authentication and username and or password not specified when initializing client"
                    )
            elif auth_scheme == "Bearer":
                pass
            else:
                raise ValueError(
                    f"authentication type {auth_scheme} not supported")
        else:
            self.authentication_type = None

    def basic_authenticate(self, image: str = None, action: str = None):
        credentials = base64.b64encode(
            f"{self.username}:{self.password}".encode("utf-8")).decode("utf-8")
        self.session.headers.update({"Authorization": f"Basic {credentials}"})

    def token_authenticate(self, image: str = None, action: str = None):
        query = {}
        headers = {}

        if "service" in self.authentication_parameters:
            query["service"] = self.authentication_parameters["service"]

        if image is not None and action is not None:
            query["scope"] = f"repository:{image}:{action}"

        if self.username is not None:
            query["account"] = self.username

        if self.username is not None and self.password is not None:
            credentials = base64.b64encode(
                f"{self.username}:{self.password}".encode("utf-8")).decode(
                    "utf-8")
            headers["Authorization"] = f"Basic {credentials}"

        base_url = self.authentication_parameters["realm"]
        if query:
            base_url += "?" + "&".join(
                f"{key}={value}" for key, value in query.items())

        response = requests.get(base_url,
                                headers=headers,
                                verify=self.tls_verify)
        if response.status_code != 200:
            raise ValueError(f"token authentication failed for {base_url}")

        token = response.json()["token"]
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def authenticate(self, image: str = None, action: str = None):
        if self.authentication_type == "Basic":
            self.basic_authenticate(image, action)
        elif self.authentication_type == "Bearer":
            self.token_authenticate(image, action)

        if not self.authenticated():
            raise ValueError("failed to authenticate")

    def authenticated(self):
        response = self.session.get(f"{self.hostname}/v2/")
        return response.status_code != 401

    def request(self,
                url: str,
                method="GET",
                headers=None,
                params=None,
                data=None,
                **kwargs):
        method_map = {
            "HEAD": self.session.head,
            "GET": self.session.get,
            "POST": self.session.post,
            "PUT": self.session.put,
            "PATCH": self.session.patch,
            "DELETE": self.session.delete,
        }

        return method_map[method](f"{self.hostname}{url}",
                                  headers=headers,
                                  params=params,
                                  data=data)

    def get_manifest(self, image: str, tag: str, version="v1"):
        version_map = {
            "v1": "application/vnd.docker.distribution.manifest.v1+json",
            "v2": "application/vnd.docker.distribution.manifest.v2+json",
        }

        if version not in version_map:
            raise ValueError(f"manifest version={version} not supported")

        response = self.request(
            f"/v2/{image}/manifests/{tag}",
            image=image,
            action="pull",
            headers={"Accept": version_map[version]},
        )

        response.raise_for_status()
        data = response.json()
        manifest = (schema.DockerManifestV1
                    if version == "v1" else schema.DockerManifestV2)

        # for pydantic 2 compatibility
        if hasattr(manifest, "model_validate"):
            return manifest.model_validate(data)
        else:
            return manifest.parse_obj(data)

    def get_manifest_configuration(self, image: str, tag: str):
        manifestV2 = self.get_manifest(image, tag, version="v2")
        config_data = json.loads(self.get_blob(image, manifestV2.config.digest))

        # for pydantic 2 compatibility
        if hasattr(schema.DockerConfig, "model_validate"):
            return schema.DockerConfig.model_validate(config_data)
        else:
            return schema.DockerConfig.parse_obj(config_data)

    def get_manifest_digest(self, image: str, tag: str):
        response = self.request(
            f"/v2/{image}/manifests/{tag}",
            method="HEAD",
            image=image,
            action="pull",
            headers={
                "Accept": "application/vnd.docker.distribution.manifest.v2+json"
            },
        )
        response.raise_for_status()
        return response.headers["Docker-Content-Digest"]

    def check_blob(self, image: str, blobsum: str):
        response = self.request(f"/v2/{image}/blobs/{blobsum}",
                                method="HEAD",
                                image=image,
                                action="pull")
        return response.status_code == 200

    def get_blob(self, image: str, blobsum: str):
        response = self.request(f"/v2/{image}/blobs/{blobsum}",
                                image=image,
                                action="pull")
        response.raise_for_status()
        return response.content

    def begin_upload(self, image: str):
        response = self.request(f"/v2/{image}/blobs/uploads/",
                                method="POST",
                                image=image,
                                action="push")
        response.raise_for_status()
        location = urlparse(response.headers["Location"])
        return location.path, parse_qs(location.query)

    def upload_blob(self, image: str, digest, checksum):
        upload_location, upload_query = self.begin_upload(image)
        upload_query["digest"] = f"sha256:{checksum}"

        response = self.request(
            upload_location,
            method="PUT",
            data=digest,
            image=image,
            action="push",
            params=upload_query,
            headers={"Content-Type": "application/octet-stream"},
        )
        response.raise_for_status()

    def upload_manifest(self, image: str, tag: str, manifest: dict):
        manifest_config, manifest_config_checksum = manifest["config"]
        manifest, manifest_checksum = manifest["manifest"]

        if not self.check_blob(image, f"sha256:{manifest_config_checksum}"):
            self.upload_blob(image, manifest_config, manifest_config_checksum)

        response = self.request(
            f"/v2/{image}/manifests/{tag}",
            method="PUT",
            data=manifest,
            image=image,
            action="push",
            headers={
                "Content-Type":
                    "application/vnd.docker.distribution.manifest.v2+json"
            },
        )
        response.raise_for_status()

    def list_images(self, n: int = None, last: int = None):
        self.authenticate()
        query = {}
        if n is not None:
            query["n"] = n
        if last is not None:
            query["last"] = last

        return self.request("/v2/_catalog", params=query).json()["repositories"]

    def list_image_tags(self, image: str, n: int = None, last: int = None):
        self.authenticate()
        query = {}
        if n is not None:
            query["n"] = n
        if last is not None:
            query["last"] = last

        return self.request(f"/v2/{image}/tags/list",
                            params=query).json()["tags"]

    def pull_image(self, image: str, tag: str = "latest", lazy: bool = False):
        """Pull specific image from docker registry

        Crates an Image object with a list of ordered Layers
        inside. If `lazy` is set to True the layer content is not
        actually downloaded unless actually referenced. Useful if you
        are making small modifications to docker images adding a few
        layers.

        """
        self.authenticate(image=image, action="pull")

        def _get_layer_blob(image, blobsum):
            return gzip.decompress(self.get_blob(image, blobsum))

        manifest = self.get_manifest(image, tag, version="v2")
        manifest_config = self.get_manifest_configuration(image, tag)

        layers = []
        parent = None
        # traverse in reverse order so that parent id can be correct
        for diffid_checksum, layer in zip(manifest_config.rootfs.diff_ids[::-1],
                                          manifest.layers[::-1]):
            checksum = diffid_checksum.split(":")[1]
            compressed_size = layer.size
            compressed_checksum = layer.digest.split(":")[1]

            if lazy:
                digest = functools.partial(_get_layer_blob, image, layer.digest)
            else:
                digest = _get_layer_blob(image, layer.digest)

            # for pydantic 2 compatibility
            if hasattr(manifest_config.config, "model_dump"):
                config = manifest_config.config.model_dump()
            else:
                config = manifest_config.config.dict()

            layers.insert(
                0,
                Layer(
                    id=checksum,
                    parent=parent,
                    architecture=manifest_config.architecture,
                    os=manifest_config.os,
                    created=manifest_config.created,
                    author=manifest_config.author,
                    config=config,
                    content=digest,
                    checksum=checksum,
                    compressed_size=compressed_size,
                    compressed_checksum=compressed_checksum,
                ),
            )

            parent = checksum
        return Image(image, tag, layers)

    def push_image(self, image: Image):
        self.authenticate(image=image.name, action="push,pull")

        for layer in image.layers:
            # make sure to check if the layer already exists on the
            # registry this way if the layer is lazy (has not actually
            # been downloaded) it does not have to be downloaded
            if not self.check_blob(image.name,
                                   f"sha256:{layer.compressed_checksum}"):
                self.upload_blob(image.name, layer.compressed_content,
                                 layer.compressed_checksum)

        self.upload_manifest(image.name, image.tag, image.manifest_v2)

    def delete_image(self, image, tag):
        self.authenticate(image=image, action="push,pull")

        digest = self.get_manifest_digest(image, tag)
        response = self.request(f"/v2/{image}/manifests/{digest}",
                                method="DELETE")
        response.raise_for_status()
