import shutil
from subprocess import PIPE, run
import sys
import abc

import pytest

import pikepdf


@pytest.fixture
def pal(resources):
    return pikepdf.open(resources / 'pal-1bit-rgb.pdf')


class FilterThru(TokenFilter):
    def handle_token(self, token):
        return token


class FilterDrop(TokenFilter):
    def handle_token(self, token):
        return None


class FilterNumbers(TokenFilter):
    def handle_token(self, token):
        if token.type_ in (
            pikepdf._qpdf.TokenType.real,
            pikepdf._qpdf.TokenType.integer,
        ):
            return [token, pikepdf._qpdf.Token(pikepdf._qpdf.TokenType.space, b" ")]


@pytest.mark.parametrize(
    'filter, expected',
    [
        (FilterThru(), b'q\n144.0000 0 0 144.0000 0.0000 0.0000 cm\n/Im0 Do\nQ'),
        (FilterDrop(), b''),
        (FilterNumbers(), b'144.0000 0 0 144.0000 0.0000 0.0000 '),
    ],
)
def test_filter_thru(pal, filter, expected):
    page = pikepdf.Page(pal.pages[0])
    # page._filter_page_contents(filter())
    page.add_content_token_filter(filter)
    after = page.obj.Contents.read_bytes()
    assert after == expected
    pal.save('_.pdf')
