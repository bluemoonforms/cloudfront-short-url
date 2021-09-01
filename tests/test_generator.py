# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest
from unittest.mock import MagicMock

from cloudfront_short_url import ShortUrl, Settings


class TestSettings(unittest.TestCase):
    """First time using dataclass so might as see how it works."""

    def test_invalid_settings(self):
        """Invalid settings."""

        with self.assertRaises(TypeError):
            Settings()

    def valid_settings(self):
        """Valid settings."""
        settings = Settings(
            region="blah-blah",
            bucket="blah",
            prefix="a",
            cloudfront_distro="shor.ty",
            random_digits=4,
        )
        self.assertEqual(settings.region, "blah-blah")


class TestShortUrlGeneration(unittest.TestCase):
    """Test as much of the url generation as possible with mocked S3 and CDN"""

    def test_initialize(self):
        """Test init of class."""
        settings = Settings(
            region="blah-blah",
            bucket="blah",
            prefix="a",
            cloudfront_distro="shor.ty",
            random_digits=4,
        )
        url_shortener = ShortUrl(settings=settings)
        url_shortener.exists_s3_key = MagicMock(return_value=False)
        url_shortener.upload_object = MagicMock(return_value=None)
        self.assertEqual(url_shortener.settings.region, "blah-blah")
        results = url_shortener.generate('http://www.google.com')
        self.assertEqual(len(results), 14)
        self.assertTrue(results.startswith(settings.cloudfront_distro))
        values = results.split('/')
        self.assertEqual(len(values), 3)
        self.assertEqual(len(values[-1]), settings.random_digits)


if __name__ == "__main__":
    unittest.main()
