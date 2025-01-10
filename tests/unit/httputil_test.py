import copy
import datetime
import logging
import pickle
import time
import unittest
import urllib.parse
from typing import Dict, List, Tuple

from tornado.escape import native_str, utf8
from tornado.httputil import (
    HTTPFile,
    HTTPHeaders,
    HTTPInputError,
    HTTPServerRequest,
    format_timestamp,
    parse_cookie,
    parse_multipart_form_data,
    parse_request_start_line,
    qs_to_qsl,
    url_concat,
)
from tornado.log import gen_log
from tornado.test.util import ignore_deprecation
from tornado.testing import ExpectLog


def form_data_args() -> Tuple[Dict[str, List[bytes]], Dict[str, List[HTTPFile]]]:
    """Return two empty dicts suitable for use with parse_multipart_form_data.

    mypy insists on type annotations for dict literals, so this lets us avoid
    the verbose types throughout this test.
    """
    return {}, {}


class TestUrlConcat(unittest.TestCase):
    def test_url_concat_no_query_params(self):
        url = url_concat("https://localhost/path", [("y", "y"), ("z", "z")])
        assert url == "https://localhost/path?y=y&z=z"

    def test_url_concat_encode_args(self):
        url = url_concat("https://localhost/path", [("y", "/y"), ("z", "z")])
        assert url == "https://localhost/path?y=%2Fy&z=z"

    def test_url_concat_trailing_q(self):
        url = url_concat("https://localhost/path?", [("y", "y"), ("z", "z")])
        assert url == "https://localhost/path?y=y&z=z"

    def test_url_concat_q_with_no_trailing_amp(self):
        url = url_concat("https://localhost/path?x", [("y", "y"), ("z", "z")])
        assert url == "https://localhost/path?x=&y=y&z=z"

    def test_url_concat_trailing_amp(self):
        url = url_concat("https://localhost/path?x&", [("y", "y"), ("z", "z")])
        assert url == "https://localhost/path?x=&y=y&z=z"

    def test_url_concat_mult_params(self):
        url = url_concat("https://localhost/path?a=1&b=2", [("y", "y"), ("z", "z")])
        assert url == "https://localhost/path?a=1&b=2&y=y&z=z"

    def test_url_concat_no_params(self):
        url = url_concat("https://localhost/path?r=1&t=2", [])
        assert url == "https://localhost/path?r=1&t=2"

    def test_url_concat_none_params(self):
        url = url_concat("https://localhost/path?r=1&t=2", None)
        assert url == "https://localhost/path?r=1&t=2"

    def test_url_concat_with_frag(self):
        url = url_concat("https://localhost/path#tab", [("y", "y")])
        assert url == "https://localhost/path?y=y#tab"

    def test_url_concat_multi_same_params(self):
        url = url_concat("https://localhost/path", [("y", "y1"), ("y", "y2")])
        assert url == "https://localhost/path?y=y1&y=y2"

    def test_url_concat_multi_same_query_params(self):
        url = url_concat("https://localhost/path?r=1&r=2", [("y", "y")])
        assert url == "https://localhost/path?r=1&r=2&y=y"

    def test_url_concat_dict_params(self):
        url = url_concat("https://localhost/path", {"y": "y"})
        assert url == "https://localhost/path?y=y"


class QsParseTest(unittest.TestCase):
    def test_parsing(self):
        qsstring = "a=1&b=2&a=3"
        qs = urllib.parse.parse_qs(qsstring)
        qsl = list(qs_to_qsl(qs))
        assert ("a", "1") in qsl
        assert ("a", "3") in qsl
        assert ("b", "2") in qsl


class MultipartFormDataTest(unittest.TestCase):
    def test_file_upload(self):
        data = b"""\
--1234
Content-Disposition: form-data; name="files"; filename="ab.txt"

Foo
--1234--""".replace(
            b"\n",
            b"\r\n",
        )
        args, files = form_data_args()
        parse_multipart_form_data(b"1234", data, args, files)
        file = files["files"][0]
        assert file["filename"] == "ab.txt"
        assert file["body"] == b"Foo"

    def test_unquoted_names(self):
        # quotes are optional unless special characters are present
        data = b"""\
--1234
Content-Disposition: form-data; name=files; filename=ab.txt

Foo
--1234--""".replace(
            b"\n",
            b"\r\n",
        )
        args, files = form_data_args()
        parse_multipart_form_data(b"1234", data, args, files)
        file = files["files"][0]
        assert file["filename"] == "ab.txt"
        assert file["body"] == b"Foo"

    def test_special_filenames(self):
        filenames = [
            "a;b.txt",
            'a"b.txt',
            'a";b.txt',
            'a;"b.txt',
            'a";";.txt',
            'a\\"b.txt',
            "a\\b.txt",
        ]
        for filename in filenames:
            logging.debug("trying filename %r", filename)
            str_data = """\
--1234
Content-Disposition: form-data; name="files"; filename="%s"

Foo
--1234--""" % filename.replace(
                "\\",
                "\\\\",
            ).replace(
                '"',
                '\\"',
            )
            data = utf8(str_data.replace("\n", "\r\n"))
            args, files = form_data_args()
            parse_multipart_form_data(b"1234", data, args, files)
            file = files["files"][0]
            assert file["filename"] == filename
            assert file["body"] == b"Foo"

    def test_non_ascii_filename(self):
        data = b"""\
--1234
Content-Disposition: form-data; name="files"; filename="ab.txt"; filename*=UTF-8''%C3%A1b.txt

Foo
--1234--""".replace(
            b"\n",
            b"\r\n",
        )
        args, files = form_data_args()
        parse_multipart_form_data(b"1234", data, args, files)
        file = files["files"][0]
        assert file["filename"] == "áb.txt"
        assert file["body"] == b"Foo"

    def test_boundary_starts_and_ends_with_quotes(self):
        data = b"""\
--1234
Content-Disposition: form-data; name="files"; filename="ab.txt"

Foo
--1234--""".replace(
            b"\n",
            b"\r\n",
        )
        args, files = form_data_args()
        parse_multipart_form_data(b'"1234"', data, args, files)
        file = files["files"][0]
        assert file["filename"] == "ab.txt"
        assert file["body"] == b"Foo"

    def test_missing_headers(self):
        data = b"""\
--1234

Foo
--1234--""".replace(
            b"\n",
            b"\r\n",
        )
        args, files = form_data_args()
        with ExpectLog(gen_log, "multipart/form-data missing headers"):
            parse_multipart_form_data(b"1234", data, args, files)
        assert files == {}

    def test_invalid_content_disposition(self):
        data = b"""\
--1234
Content-Disposition: invalid; name="files"; filename="ab.txt"

Foo
--1234--""".replace(
            b"\n",
            b"\r\n",
        )
        args, files = form_data_args()
        with ExpectLog(gen_log, "Invalid multipart/form-data"):
            parse_multipart_form_data(b"1234", data, args, files)
        assert files == {}

    def test_line_does_not_end_with_correct_line_break(self):
        data = b"""\
--1234
Content-Disposition: form-data; name="files"; filename="ab.txt"

Foo--1234--""".replace(
            b"\n",
            b"\r\n",
        )
        args, files = form_data_args()
        with ExpectLog(gen_log, "Invalid multipart/form-data"):
            parse_multipart_form_data(b"1234", data, args, files)
        assert files == {}

    def test_content_disposition_header_without_name_parameter(self):
        data = b"""\
--1234
Content-Disposition: form-data; filename="ab.txt"

Foo
--1234--""".replace(
            b"\n",
            b"\r\n",
        )
        args, files = form_data_args()
        with ExpectLog(gen_log, "multipart/form-data value missing name"):
            parse_multipart_form_data(b"1234", data, args, files)
        assert files == {}

    def test_data_after_final_boundary(self):
        # The spec requires that data after the final boundary be ignored.
        # http://www.w3.org/Protocols/rfc1341/7_2_Multipart.html
        # In practice, some libraries include an extra CRLF after the boundary.
        data = b"""\
--1234
Content-Disposition: form-data; name="files"; filename="ab.txt"

Foo
--1234--
""".replace(
            b"\n",
            b"\r\n",
        )
        args, files = form_data_args()
        parse_multipart_form_data(b"1234", data, args, files)
        file = files["files"][0]
        assert file["filename"] == "ab.txt"
        assert file["body"] == b"Foo"


class HTTPHeadersTest(unittest.TestCase):
    def test_multi_line(self):
        # Lines beginning with whitespace are appended to the previous line
        # with any leading whitespace replaced by a single space.
        # Note that while multi-line headers are a part of the HTTP spec,
        # their use is strongly discouraged.
        data = """\
Foo: bar
 baz
Asdf: qwer
\tzxcv
Foo: even
     more
     lines
""".replace(
            "\n",
            "\r\n",
        )
        headers = HTTPHeaders.parse(data)
        assert headers["asdf"] == "qwer zxcv"
        assert headers.get_list("asdf") == ["qwer zxcv"]
        assert headers["Foo"] == "bar baz,even more lines"
        assert headers.get_list("foo") == ["bar baz", "even more lines"]
        assert sorted(headers.get_all()) == [
            ("Asdf", "qwer zxcv"),
            ("Foo", "bar baz"),
            ("Foo", "even more lines"),
        ]

    def test_malformed_continuation(self):
        # If the first line starts with whitespace, it's a
        # continuation line with nothing to continue, so reject it
        # (with a proper error).
        data = " Foo: bar"
        self.assertRaises(HTTPInputError, HTTPHeaders.parse, data)

    def test_unicode_newlines(self):
        # Ensure that only \r\n is recognized as a header separator, and not
        # the other newline-like unicode characters.
        # Characters that are likely to be problematic can be found in
        # http://unicode.org/standard/reports/tr13/tr13-5.html
        # and cpython's unicodeobject.c (which defines the implementation
        # of unicode_type.splitlines(), and uses a different list than TR13).
        newlines = [
            "\u001b",  # VERTICAL TAB
            "\u001c",  # FILE SEPARATOR
            "\u001d",  # GROUP SEPARATOR
            "\u001e",  # RECORD SEPARATOR
            "\u0085",  # NEXT LINE
            "\u2028",  # LINE SEPARATOR
            "\u2029",  # PARAGRAPH SEPARATOR
        ]
        for newline in newlines:
            # Try the utf8 and latin1 representations of each newline
            for encoding in ["utf8", "latin1"]:
                try:
                    try:
                        encoded = newline.encode(encoding)
                    except UnicodeEncodeError:
                        # Some chars cannot be represented in latin1
                        continue
                    data = b"Cookie: foo=" + encoded + b"bar"
                    # parse() wants a native_str, so decode through latin1
                    # in the same way the real parser does.
                    headers = HTTPHeaders.parse(native_str(data.decode("latin1")))
                    expected = [
                        (
                            "Cookie",
                            "foo=" + native_str(encoded.decode("latin1")) + "bar",
                        ),
                    ]
                    assert expected == list(headers.get_all())
                except Exception:
                    gen_log.warning("failed while trying %r in %s", newline, encoding)
                    raise

    def test_unicode_whitespace(self):
        # Only tabs and spaces are to be stripped according to the HTTP standard.
        # Other unicode whitespace is to be left as-is. In the context of headers,
        # this specifically means the whitespace characters falling within the
        # latin1 charset.
        whitespace = [
            (" ", True),  # SPACE
            ("\t", True),  # TAB
            ("\u00a0", False),  # NON-BREAKING SPACE
            ("\u0085", False),  # NEXT LINE
        ]
        for c, stripped in whitespace:
            headers = HTTPHeaders.parse("Transfer-Encoding: %schunked" % c)
            if stripped:
                expected = [("Transfer-Encoding", "chunked")]
            else:
                expected = [("Transfer-Encoding", "%schunked" % c)]
            assert expected == list(headers.get_all())

    def test_optional_cr(self):
        # Both CRLF and LF should be accepted as separators. CR should not be
        # part of the data when followed by LF, but it is a normal char
        # otherwise (or should bare CR be an error?)
        headers = HTTPHeaders.parse("CRLF: crlf\r\nLF: lf\nCR: cr\rMore: more\r\n")
        assert sorted(headers.get_all()) == [
            ("Cr", "cr\rMore: more"),
            ("Crlf", "crlf"),
            ("Lf", "lf"),
        ]

    def test_copy(self):
        all_pairs = [("A", "1"), ("A", "2"), ("B", "c")]
        h1 = HTTPHeaders()
        for k, v in all_pairs:
            h1.add(k, v)
        h2 = h1.copy()
        h3 = copy.copy(h1)
        h4 = copy.deepcopy(h1)
        for headers in [h1, h2, h3, h4]:
            # All the copies are identical, no matter how they were
            # constructed.
            assert sorted(headers.get_all()) == all_pairs
        for headers in [h2, h3, h4]:
            # Neither the dict or its member lists are reused.
            assert headers is not h1
            assert headers.get_list("A") is not h1.get_list("A")

    def test_pickle_roundtrip(self):
        headers = HTTPHeaders()
        headers.add("Set-Cookie", "a=b")
        headers.add("Set-Cookie", "c=d")
        headers.add("Content-Type", "text/html")
        pickled = pickle.dumps(headers)
        unpickled = pickle.loads(pickled)
        assert sorted(headers.get_all()) == sorted(unpickled.get_all())
        assert sorted(headers.items()) == sorted(unpickled.items())

    def test_setdefault(self):
        headers = HTTPHeaders()
        headers["foo"] = "bar"
        # If a value is present, setdefault returns it without changes.
        assert headers.setdefault("foo", "baz") == "bar"
        assert headers["foo"] == "bar"
        # If a value is not present, setdefault sets it for future use.
        assert headers.setdefault("quux", "xyzzy") == "xyzzy"
        assert headers["quux"] == "xyzzy"
        assert sorted(headers.get_all()) == [("Foo", "bar"), ("Quux", "xyzzy")]

    def test_string(self):
        headers = HTTPHeaders()
        headers.add("Foo", "1")
        headers.add("Foo", "2")
        headers.add("Foo", "3")
        headers2 = HTTPHeaders.parse(str(headers))
        assert headers == headers2


class FormatTimestampTest(unittest.TestCase):
    # Make sure that all the input types are supported.
    TIMESTAMP = 1359312200.503611
    EXPECTED = "Sun, 27 Jan 2013 18:43:20 GMT"

    def check(self, value):
        assert format_timestamp(value) == self.EXPECTED

    def test_unix_time_float(self):
        self.check(self.TIMESTAMP)

    def test_unix_time_int(self):
        self.check(int(self.TIMESTAMP))

    def test_struct_time(self):
        self.check(time.gmtime(self.TIMESTAMP))

    def test_time_tuple(self):
        tup = tuple(time.gmtime(self.TIMESTAMP))
        assert len(tup) == 9
        self.check(tup)

    def test_utc_naive_datetime(self):
        self.check(
            datetime.datetime.fromtimestamp(self.TIMESTAMP, datetime.timezone.utc).replace(
                tzinfo=None,
            ),
        )

    def test_utc_naive_datetime_deprecated(self):
        with ignore_deprecation():
            self.check(datetime.datetime.utcfromtimestamp(self.TIMESTAMP))

    def test_utc_aware_datetime(self):
        self.check(datetime.datetime.fromtimestamp(self.TIMESTAMP, datetime.timezone.utc))

    def test_other_aware_datetime(self):
        # Other timezones are ignored; the timezone is always printed as GMT
        self.check(
            datetime.datetime.fromtimestamp(
                self.TIMESTAMP,
                datetime.timezone(datetime.timedelta(hours=-4)),
            ),
        )


# HTTPServerRequest is mainly tested incidentally to the server itself,
# but this tests the parts of the class that can be tested in isolation.
class HTTPServerRequestTest(unittest.TestCase):
    def test_default_constructor(self):
        # All parameters are formally optional, but uri is required
        # (and has been for some time).  This test ensures that no
        # more required parameters slip in.
        HTTPServerRequest(uri="/")

    def test_body_is_a_byte_string(self):
        requets = HTTPServerRequest(uri="/")
        assert isinstance(requets.body, bytes)

    def test_repr_does_not_contain_headers(self):
        request = HTTPServerRequest(uri="/", headers=HTTPHeaders({"Canary": ["Coal Mine"]}))
        assert "Canary" not in repr(request)


class ParseRequestStartLineTest(unittest.TestCase):
    METHOD = "GET"
    PATH = "/foo"
    VERSION = "HTTP/1.1"

    def test_parse_request_start_line(self):
        start_line = f"{self.METHOD} {self.PATH} {self.VERSION}"
        parsed_start_line = parse_request_start_line(start_line)
        assert parsed_start_line.method == self.METHOD
        assert parsed_start_line.path == self.PATH
        assert parsed_start_line.version == self.VERSION


class ParseCookieTest(unittest.TestCase):
    # These tests copied from Django:
    # https://github.com/django/django/pull/6277/commits/da810901ada1cae9fc1f018f879f11a7fb467b28
    def test_python_cookies(self):
        """Test cases copied from Python's Lib/test/test_http_cookies.py."""
        assert parse_cookie("chips=ahoy; vienna=finger") == {"chips": "ahoy", "vienna": "finger"}
        # Here parse_cookie() differs from Python's cookie parsing in that it
        # treats all semicolons as delimiters, even within quotes.
        assert parse_cookie('keebler="E=mc2; L=\\"Loves\\"; fudge=\\012;"') == {
            "keebler": '"E=mc2',
            "L": '\\"Loves\\"',
            "fudge": "\\012",
            "": '"',
        }
        # Illegal cookies that have an '=' char in an unquoted value.
        assert parse_cookie("keebler=E=mc2") == {"keebler": "E=mc2"}
        # Cookies with ':' character in their name.
        assert parse_cookie("key:term=value:term") == {"key:term": "value:term"}
        # Cookies with '[' and ']'.
        assert parse_cookie("a=b; c=[; d=r; f=h") == {"a": "b", "c": "[", "d": "r", "f": "h"}

    def test_cookie_edgecases(self):
        # Cookies that RFC6265 allows.
        assert parse_cookie("a=b; Domain=example.com") == {"a": "b", "Domain": "example.com"}
        # parse_cookie() has historically kept only the last cookie with the
        # same name.
        assert parse_cookie("a=b; h=i; a=c") == {"a": "c", "h": "i"}

    def test_invalid_cookies(self):
        """Cookie strings that go against RFC6265 but browsers will send if set
        via document.cookie.
        """
        # Chunks without an equals sign appear as unnamed values per
        # https://bugzilla.mozilla.org/show_bug.cgi?id=169091
        assert "django_language" in parse_cookie("abc=def; unnamed; django_language=en")
        # Even a double quote may be an unamed value.
        assert parse_cookie('a=b; "; c=d') == {"a": "b", "": '"', "c": "d"}
        # Spaces in names and values, and an equals sign in values.
        assert parse_cookie("a b c=d e = f; gh=i") == {"a b c": "d e = f", "gh": "i"}
        # More characters the spec forbids.
        assert parse_cookie('a   b,c<>@:/[]?{}=d  "  =e,f g') == {
            "a   b,c<>@:/[]?{}": 'd  "  =e,f g',
        }
        # Unicode characters. The spec only allows ASCII.
        assert parse_cookie("saint=André Bessette") == {"saint": native_str("André Bessette")}
        # Browsers don't send extra whitespace or semicolons in Cookie headers,
        # but parse_cookie() should parse whitespace the same way
        # document.cookie parses whitespace.
        assert parse_cookie("  =  b  ;  ;  =  ;   c  =  ;  ") == {"": "b", "c": ""}

    def test_unquote(self):
        # Copied from
        # https://github.com/python/cpython/blob/dc7a2b6522ec7af41282bc34f405bee9b306d611/Lib/test/test_http_cookies.py#L62
        cases = [
            (r'a="b=\""', 'b="'),
            (r'a="b=\\"', "b=\\"),
            (r'a="b=\="', "b=="),
            (r'a="b=\n"', "b=n"),
            (r'a="b=\042"', 'b="'),
            (r'a="b=\134"', "b=\\"),
            (r'a="b=\377"', "b=\xff"),
            (r'a="b=\400"', "b=400"),
            (r'a="b=\42"', "b=42"),
            (r'a="b=\\042"', "b=\\042"),
            (r'a="b=\\134"', "b=\\134"),
            (r'a="b=\\\""', 'b=\\"'),
            (r'a="b=\\\042"', 'b=\\"'),
            (r'a="b=\134\""', 'b=\\"'),
            (r'a="b=\134\042"', 'b=\\"'),
        ]
        for encoded, decoded in cases:
            with self.subTest(encoded):
                c = parse_cookie(encoded)
                assert c["a"] == decoded

    def test_unquote_large(self):
        # Adapted from
        # https://github.com/python/cpython/blob/dc7a2b6522ec7af41282bc34f405bee9b306d611/Lib/test/test_http_cookies.py#L87
        # Modified from that test because we handle semicolons differently from the stdlib.
        #
        # This is a performance regression test: prior to improvements in Tornado 6.4.2, this test
        # would take over a minute with n= 100k. Now it runs in tens of milliseconds.
        n = 100000
        for encoded in r"\\", r"\134":
            with self.subTest(encoded):
                start = time.time()
                data = 'a="b=' + encoded * n + '"'
                value = parse_cookie(data)["a"]
                end = time.time()
                assert value[:3] == "b=\\"
                assert value[-3:] == "\\\\\\"
                assert len(value) == n + 2

                # Very loose performance check to avoid false positives
                assert end - start < 1, "Test took too long"
