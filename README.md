# Short URL generation

This package uses an AWS cloudfront setup that serves out static files.
It started from an AWS document about using cloudfront to redirect and became a library that can be used inside your python code.

To use it you need to import Settings and ShortUrl.

What do you need:
AWS Access
an s3 bucket setup for website hosting for your redirects
a cloudfront distro with ssl certs that points to your s3 bucket
