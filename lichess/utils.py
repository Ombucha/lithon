"""
MIT License

Copyright (c) 2022 Omkaar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


from __future__ import annotations

from urllib.parse import quote
from typing import Any, Callable, Union, Tuple, List, TYPE_CHECKING

from .endpoints import BASE_URL
from .exceptions import LichessException

if TYPE_CHECKING:
    from requests import Response

    from .client import Client


def _get(path: str, client: Client, *, ndjson: bool = False, text: bool = False, **kwargs) -> Union[list, dict, Response]:
    headers = client.session.headers
    if ndjson:
        headers.update({"Accept": "application/x-ndjson"})
    elif text:
        headers.update({"Accept": "plain/text"})
    else:
        headers.update({"Accept": "application/json"})
    response = client.session.get(f"{BASE_URL}{quote(path)}", headers = headers, **kwargs)
    if response.status_code != 200:
        raise LichessException(response.json()["error"])
    if kwargs.get("stream", None):
        return response
    return response.json()


def _post(url: str,  client: Client, *, ndjson: bool = False, text: bool = False, **kwargs) -> Union[list, dict, Response]:
    headers = client.session.headers
    if ndjson:
        headers.update({"Accept": "application/x-ndjson"})
    elif text:
        headers.update({"Accept": "plain/text"})
    else:
        headers.update({"Accept": "application/json"})
    response = client.session.post(f"{BASE_URL}{quote(url)}", headers = headers, **kwargs)
    if response.status_code != 200:
        raise LichessException(response.json()["error"])
    if kwargs.get("stream", None):
        return response
    return response.json()


def _replace(dictionary: dict, target: Any, function: Callable) -> dict:
    output = {}
    for key, value in dictionary.items():
        if isinstance(value, dict):
            output[key] = _replace(value, target, function)
        elif key == target:
            output[key] = function(value)
        else:
            output[key] = value
    return output


class Range:

    """
    A class that represents an integer range.
    """

    def __class_getitem__(cls, bounds: Tuple[int, int]) -> List[range]:
        if bounds[0] > bounds[1]:
            raise ValueError("invalid range.")
        return list(range(bounds[0], bounds[1] + 1))
