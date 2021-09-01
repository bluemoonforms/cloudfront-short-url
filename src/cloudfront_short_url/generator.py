"""Module for redirect url generation."""
import random
import string
from dataclasses import dataclass

import boto3
import botocore
from botocore.client import Config


def make_cached_property(func, cache_on_class=False):
    """Helper function for cached_property and class_cached_property decorator."""
    attr_name = "_cache_" + func.__name__

    @property
    def _cached_property(self):
        obj = self.__class__ if cache_on_class else self

        if not hasattr(obj, attr_name):
            setattr(obj, attr_name, func(self))

        return getattr(obj, attr_name)

    return _cached_property


def cached_property(func):
    """
    Return a property decorator that will cache the computed value on object.

    This allows the property to be computed only once when
    first accessed, with all further calls returning the cached value.
    """
    return make_cached_property(func, cache_on_class=False)


def class_cached_property(func):
    """
    Return a property decorator that will cache the computed value on class.

    This allows the property to be computed
    only once when first accessed (by any instance), with all further calls
    from any instance returning the value cached on the class object.
    """
    return make_cached_property(func, cache_on_class=True)


@dataclass
class Settings:
    """Settings object"""

    region: str
    bucket: str
    prefix: str
    cloudfront_distro: str
    random_digits: int = 8
    boto_signature_version: str = "s3v4"


class ShortUrl:
    """Create a short redirect URL."""

    def __init__(self, settings: Settings):
        self.settings = settings

    @class_cached_property
    def s3_client(self):
        """Boto3 S3 client."""
        return boto3.client(
            "s3",
            region_name=self.settings.region,
            config=Config(signature_version=self.settings.boto_signature_version),
        )

    def generate_random(self):
        """Generate a random string of n characters, lowercase and numbers."""
        return "".join(
            random.SystemRandom().choice(string.ascii_lowercase + string.digits)
            for _ in range(self.settings.random_digits)
        )

    def exists_s3_key(self, key):
        """
        Check whether an object already exists in the Amazon S3 bucket
        we do a head_object, if it throws a 404 error then the object does not exist
        """
        try:
            self.s3_client.head_object(Bucket=self.settings.bucket, Key=key)
            return True
        except botocore.exceptions.ClientError as exc:
            # if ListBucket access is granted, then missing file returns 404
            if exc.response["Error"]["Code"] == "404":
                return False
            # if ListBucket access is not granted, then missing file returns 403
            if exc.response["Error"]["Code"] == "403":
                return False
            raise exc  # otherwise re-raise the exception

    def upload_kwargs(self, key, native_url):
        """Generate args for uploads, useful for testing."""
        return {
            "Bucket": self.settings.bucket,
            "Key": key,
            "Body": b"",
            "WebsiteRedirectLocation": native_url,
            "ContentType": "text/plain",
        }

    def upload_object(self, key, native_url):
        """Upload the redirect object to s3."""
        kwargs = self.upload_kwargs(key=key, native_url=native_url)
        self.s3_client.put_object(**kwargs)

    def generate(self, native_url):
        """Generate the url."""
        check = True
        while check:
            short_id = self.generate_random()
            short_key = "{}/{}".format(self.settings.prefix, short_id)
            check = self.exists_s3_key(key=short_key)
        self.upload_object(key=short_key, native_url=native_url)
        return "{}/{}".format(self.settings.cloudfront_distro, short_key)
