#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch CCTV8K EPG through the TVShowList Y_JCE request and save it as XMLTV.

This script is modeled after scripts/2.bin:
cmdId=24997 (TVShowList)
body tag0="cctv_tv_tab_program"
body tag1="day=YYYY-MM-DD&pid=600156816&timestamp=..."
"""

from __future__ import annotations

import asyncio
import gzip
import ssl
import struct
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Optional, TypeVar



JACC_URL = "https://jacc.ysp.cctv.cn/"
CMD_TV_SHOW_LIST = 24997
DEFAULT_GUID = "093e7e5989684fd986c44f07542d8dc8"
USER_AGENT = "CCTVVideo/2.9.0 (iPad; iOS 17.2; Scale/2.00)"
CN_TZ = timezone(timedelta(hours=8))


TYPE_BYTE = 0
TYPE_SHORT = 1
TYPE_INT = 2
TYPE_LONG = 3
TYPE_FLOAT = 4
TYPE_DOUBLE = 5
TYPE_STRING1 = 6
TYPE_STRING4 = 7
TYPE_MAP = 8
TYPE_LIST = 9
TYPE_STRUCT_BEGIN = 10
TYPE_STRUCT_END = 11
TYPE_ZERO = 12
TYPE_SIMPLE_LIST = 13

T = TypeVar("T")


@dataclass
class TVShowProgram:
    title: str
    display_time: str
    start_time_stamp: int
    duration: int


class JceDecodeError(RuntimeError):
    pass


class JceWriter:
    def __init__(self) -> None:
        self.buf = bytearray()

    def to_bytes(self) -> bytes:
        return bytes(self.buf)

    def write_head(self, type_: int, tag: int) -> None:
        if tag < 15:
            self.buf.append((tag << 4) | type_)
        elif tag < 256:
            self.buf.append(0xF0 | type_)
            self.buf.append(tag)
        else:
            raise ValueError(f"JCE tag is too large: {tag}")

    def write_byte(self, value: int, tag: int) -> None:
        if value == 0:
            self.write_head(TYPE_ZERO, tag)
            return
        self.write_head(TYPE_BYTE, tag)
        self.buf.extend(struct.pack(">b", value))

    def write_short(self, value: int, tag: int) -> None:
        if -128 <= value <= 127:
            self.write_byte(value, tag)
            return
        self.write_head(TYPE_SHORT, tag)
        self.buf.extend(struct.pack(">h", value))

    def write_int(self, value: int, tag: int) -> None:
        if -32768 <= value <= 32767:
            self.write_short(value, tag)
            return
        self.write_head(TYPE_INT, tag)
        self.buf.extend(struct.pack(">i", value))

    def write_long(self, value: int, tag: int) -> None:
        if -2147483648 <= value <= 2147483647:
            self.write_int(value, tag)
            return
        self.write_head(TYPE_LONG, tag)
        self.buf.extend(struct.pack(">q", value))

    def write_string(self, value: str, tag: int) -> None:
        data = value.encode("utf-8")
        if len(data) <= 255:
            self.write_head(TYPE_STRING1, tag)
            self.buf.append(len(data))
        else:
            self.write_head(TYPE_STRING4, tag)
            self.buf.extend(struct.pack(">i", len(data)))
        self.buf.extend(data)

    def write_bytes(self, value: bytes, tag: int) -> None:
        self.write_head(TYPE_SIMPLE_LIST, tag)
        self.write_head(TYPE_BYTE, 0)
        self.write_int(len(value), 0)
        self.buf.extend(value)

    def write_struct(self, tag: int, writer: Callable[["JceWriter"], None]) -> None:
        self.write_head(TYPE_STRUCT_BEGIN, tag)
        writer(self)
        self.write_head(TYPE_STRUCT_END, 0)


class JceReader:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.pos = 0

    def _require(self, size: int) -> None:
        if self.pos + size > len(self.data):
            raise JceDecodeError("unexpected end of JCE data")

    def _read(self, size: int) -> bytes:
        self._require(size)
        value = self.data[self.pos : self.pos + size]
        self.pos += size
        return value

    def _read_head_at(self, pos: int) -> tuple[int, int, int]:
        if pos >= len(self.data):
            raise JceDecodeError("missing JCE head")
        head = self.data[pos]
        type_ = head & 0x0F
        tag = (head & 0xF0) >> 4
        if tag == 15:
            if pos + 1 >= len(self.data):
                raise JceDecodeError("missing extended JCE tag")
            tag = self.data[pos + 1]
            return type_, tag, 2
        return type_, tag, 1

    def read_head(self) -> tuple[int, int]:
        type_, tag, size = self._read_head_at(self.pos)
        self.pos += size
        return type_, tag

    def skip_to_tag(self, target_tag: int) -> bool:
        while True:
            try:
                type_, tag, head_size = self._read_head_at(self.pos)
            except JceDecodeError:
                return False
            if type_ == TYPE_STRUCT_END:
                return False
            if target_tag <= tag:
                return target_tag == tag
            self.pos += head_size
            self.skip_field_by_type(type_)

    def skip_field(self) -> None:
        type_, _ = self.read_head()
        self.skip_field_by_type(type_)

    def skip_field_by_type(self, type_: int) -> None:
        if type_ == TYPE_BYTE:
            self.pos += 1
        elif type_ == TYPE_SHORT:
            self.pos += 2
        elif type_ in (TYPE_INT, TYPE_FLOAT):
            self.pos += 4
        elif type_ in (TYPE_LONG, TYPE_DOUBLE):
            self.pos += 8
        elif type_ == TYPE_STRING1:
            size = self._read(1)[0]
            self.pos += size
        elif type_ == TYPE_STRING4:
            size = struct.unpack(">i", self._read(4))[0]
            self.pos += size
        elif type_ == TYPE_MAP:
            size = self.read_int(0, required=True)
            for _ in range(size * 2):
                self.skip_field()
        elif type_ == TYPE_LIST:
            size = self.read_int(0, required=True)
            for _ in range(size):
                self.skip_field()
        elif type_ == TYPE_STRUCT_BEGIN:
            self.skip_to_struct_end()
        elif type_ in (TYPE_STRUCT_END, TYPE_ZERO):
            return
        elif type_ == TYPE_SIMPLE_LIST:
            inner_type, _ = self.read_head()
            if inner_type != TYPE_BYTE:
                raise JceDecodeError(f"invalid simple list inner type: {inner_type}")
            size = self.read_int(0, required=True)
            self.pos += size
        else:
            raise JceDecodeError(f"invalid JCE type: {type_}")
        if self.pos > len(self.data):
            raise JceDecodeError("JCE field exceeds buffer")

    def skip_to_struct_end(self) -> None:
        while True:
            type_, _ = self.read_head()
            self.skip_field_by_type(type_)
            if type_ == TYPE_STRUCT_END:
                return

    def read_int(self, tag: int, required: bool = False, default: int = 0) -> int:
        if not self.skip_to_tag(tag):
            if required:
                raise JceDecodeError(f"required int field tag {tag} not found")
            return default
        type_, _ = self.read_head()
        if type_ == TYPE_BYTE:
            return struct.unpack(">b", self._read(1))[0]
        if type_ == TYPE_SHORT:
            return struct.unpack(">h", self._read(2))[0]
        if type_ == TYPE_INT:
            return struct.unpack(">i", self._read(4))[0]
        if type_ == TYPE_ZERO:
            return 0
        raise JceDecodeError(f"type mismatch for int tag {tag}: {type_}")

    def read_long(self, tag: int, required: bool = False, default: int = 0) -> int:
        if not self.skip_to_tag(tag):
            if required:
                raise JceDecodeError(f"required long field tag {tag} not found")
            return default
        type_, _ = self.read_head()
        if type_ == TYPE_BYTE:
            return struct.unpack(">b", self._read(1))[0]
        if type_ == TYPE_SHORT:
            return struct.unpack(">h", self._read(2))[0]
        if type_ == TYPE_INT:
            return struct.unpack(">i", self._read(4))[0]
        if type_ == TYPE_LONG:
            return struct.unpack(">q", self._read(8))[0]
        if type_ == TYPE_ZERO:
            return 0
        raise JceDecodeError(f"type mismatch for long tag {tag}: {type_}")

    def read_string(
        self, tag: int, required: bool = False, default: Optional[str] = None
    ) -> Optional[str]:
        if not self.skip_to_tag(tag):
            if required:
                raise JceDecodeError(f"required string field tag {tag} not found")
            return default
        type_, _ = self.read_head()
        if type_ == TYPE_STRING1:
            size = self._read(1)[0]
        elif type_ == TYPE_STRING4:
            size = struct.unpack(">i", self._read(4))[0]
        else:
            raise JceDecodeError(f"type mismatch for string tag {tag}: {type_}")
        return self._read(size).decode("utf-8", errors="replace")

    def read_bytes(
        self, tag: int, required: bool = False, default: Optional[bytes] = None
    ) -> Optional[bytes]:
        if not self.skip_to_tag(tag):
            if required:
                raise JceDecodeError(f"required bytes field tag {tag} not found")
            return default
        type_, _ = self.read_head()
        if type_ == TYPE_SIMPLE_LIST:
            inner_type, _ = self.read_head()
            if inner_type != TYPE_BYTE:
                raise JceDecodeError(f"invalid simple list inner type: {inner_type}")
            size = self.read_int(0, required=True)
            return self._read(size)
        if type_ == TYPE_LIST:
            size = self.read_int(0, required=True)
            return bytes(self.read_int(0, required=True) & 0xFF for _ in range(size))
        raise JceDecodeError(f"type mismatch for bytes tag {tag}: {type_}")

    def read_struct(
        self, tag: int, parser: Callable[["JceReader"], T], required: bool = False
    ) -> Optional[T]:
        if not self.skip_to_tag(tag):
            if required:
                raise JceDecodeError(f"required struct field tag {tag} not found")
            return None
        type_, _ = self.read_head()
        if type_ != TYPE_STRUCT_BEGIN:
            raise JceDecodeError(f"type mismatch for struct tag {tag}: {type_}")
        value = parser(self)
        self.skip_to_struct_end()
        return value

    def read_struct_list(
        self, tag: int, parser: Callable[["JceReader"], T], required: bool = False
    ) -> list[T]:
        if not self.skip_to_tag(tag):
            if required:
                raise JceDecodeError(f"required list field tag {tag} not found")
            return []
        type_, _ = self.read_head()
        if type_ != TYPE_LIST:
            raise JceDecodeError(f"type mismatch for list tag {tag}: {type_}")
        size = self.read_int(0, required=True)
        items: list[T] = []
        for _ in range(size):
            item = self.read_struct(0, parser, required=True)
            if item is not None:
                items.append(item)
        return items


def write_float(writer: JceWriter, value: float, tag: int) -> None:
    writer.write_head(TYPE_FLOAT, tag)
    writer.buf.extend(struct.pack(">f", value))


def write_double(writer: JceWriter, value: float, tag: int) -> None:
    writer.write_head(TYPE_DOUBLE, tag)
    writer.buf.extend(struct.pack(">d", value))


def write_empty_list(writer: JceWriter, tag: int) -> None:
    writer.write_head(TYPE_LIST, tag)
    writer.write_int(0, 0)


def write_extent_data(writer: JceWriter) -> None:
    writer.write_int(0, 0)
    writer.write_byte(0, 1)
    writer.write_string("", 2)


def write_coordinates(writer: JceWriter) -> None:
    writer.write_int(0, 0)
    write_float(writer, 0.0, 1)
    write_float(writer, 0.0, 2)
    write_double(writer, 0.0, 3)


def write_qua(writer: JceWriter) -> None:
    writer.write_string("2.9.0.23399", 0)
    writer.write_string("23399", 1)
    writer.write_int(1640, 2)
    writer.write_int(2360, 3)
    writer.write_int(5, 4)
    writer.write_string("sysver=ios17.2&device=iPad&modify_time=&lang=zh_CN", 5)
    writer.write_int(1, 6)
    writer.write_int(0, 7)
    writer.write_int(0, 8)
    writer.write_string("50001", 9)
    writer.write_string("", 10)
    writer.write_string("", 11)
    writer.write_string("", 12)
    writer.write_string("78d6ac7572afb5461e9a590f089f893d2abc0010119007", 13)
    writer.write_string("", 14)
    writer.write_struct(15, write_extent_data)
    writer.write_string("A41CD6B6-6A56-46DC-9AE0-4ECF2E9118DF", 16)
    writer.write_string("", 17)
    writer.write_string("", 18)
    writer.write_struct(19, write_coordinates)
    writer.write_string("5EE46760-11B1-5FE7-949A-FF232DAE1823", 20)
    writer.write_string("iPad Pro (12.9 inch) 3G", 21)
    writer.write_int(1, 22)
    writer.write_int(0, 23)
    writer.write_int(1, 24)
    writer.write_int(0, 25)
    writer.write_int(0, 26)
    writer.write_string("", 27)
    writer.write_string("", 28)
    writer.write_string("1c0fc6ed8a53584ae722b915200014317601", 29)


def write_log_report(writer: JceWriter) -> None:
    writer.write_string("page_columnlist", 0)
    writer.write_string("page_columnlist", 1)
    writer.write_int(6, 2)
    writer.write_string("self", 3)
    writer.write_int(0, 4)
    writer.write_string("", 5)
    writer.write_string("", 6)
    writer.write_string("10006", 8)
    writer.write_string("", 9)
    writer.write_string("", 10)


def write_request_head(writer: JceWriter, request_id: int, guid: str) -> None:
    writer.write_int(request_id, 0)
    writer.write_int(CMD_TV_SHOW_LIST, 1)
    writer.write_struct(2, write_qua)
    writer.write_string("1200013", 3)
    writer.write_string(guid, 4)
    write_empty_list(writer, 5)
    writer.write_struct(6, write_log_report)
    write_empty_list(writer, 7)
    writer.write_int(0, 8)
    writer.write_int(0, 9)
    writer.write_int(0, 10)


def make_business_body(pid: str, day: str, timestamp: int) -> bytes:
    query = urllib.parse.urlencode(
        [("day", day), ("pid", pid), ("timestamp", str(timestamp))]
    )
    writer = JceWriter()
    writer.write_string("cctv_tv_tab_program", 0)
    writer.write_string(query, 1)
    return writer.to_bytes()


def make_request_command(pid: str, day: str, timestamp: int, request_id: int, guid: str) -> bytes:
    writer = JceWriter()
    writer.write_struct(0, lambda w: write_request_head(w, request_id, guid))
    writer.write_bytes(make_business_body(pid, day, timestamp), 1)
    return writer.to_bytes()


def wrap_android_unified_protocol(
    command_body: bytes,
    *,
    request_id: int,
    guid: str,
    version_code: int = 302060,
) -> bytes:
    inner_len = len(command_body) + 17
    inner = bytearray()
    inner.append(38)
    inner.extend(struct.pack(">i", inner_len))
    inner.append(1)
    inner.extend(b"\x00" * 10)
    inner.extend(command_body)
    inner.append(40)
    compressed_inner = gzip.compress(bytes(inner))

    out = bytearray()
    out.append(19)
    out.extend(struct.pack(">i", 0))
    out.extend(struct.pack(">h", 2))
    out.extend(struct.pack(">H", 0xFF01))
    out.extend(struct.pack(">H", CMD_TV_SHOW_LIST))
    out.extend(struct.pack(">h", 0))
    out.extend(struct.pack(">q", request_id))
    out.extend(struct.pack(">i", 531))
    out.extend(struct.pack(">i", 10012))
    out.extend(struct.pack(">q", 0))
    out.extend(guid.encode("utf-8")[:32].ljust(32, b"\x00"))
    out.append(1)
    out.extend(struct.pack(">i", version_code))
    out.extend(b"\x00" * 6)
    out.append(0)
    out.extend(struct.pack(">h", 0))
    out.extend(struct.pack(">h", 0))
    out.extend(struct.pack(">i", len(inner)))
    out.extend(compressed_inner)
    out.append(3)
    struct.pack_into(">i", out, 1, len(out))
    return bytes(out)


def build_request(pid: str, day: str, timestamp: int, request_id: int, guid: str) -> bytes:
    command_body = make_request_command(pid, day, timestamp, request_id, guid)
    return wrap_android_unified_protocol(command_body, request_id=request_id, guid=guid)


def unwrap_unified_protocol(data: bytes) -> bytes:
    if len(data) < 90:
        raise JceDecodeError(f"response is too short: {len(data)} bytes")

    version = data[0]
    total_len = struct.unpack_from(">i", data, 1)[0]
    magic = struct.unpack_from(">H", data, 7)[0]
    cmd_id = struct.unpack_from(">H", data, 9)[0]
    error_code = struct.unpack_from(">H", data, 11)[0]
    flags = struct.unpack_from(">i", data, 21)[0]
    if version != 19 or total_len != len(data) or magic != 0xFF01:
        raise JceDecodeError("invalid unified protocol response header")
    if cmd_id != CMD_TV_SHOW_LIST:
        raise JceDecodeError(f"unexpected response cmd id: {cmd_id}")
    if error_code != 0:
        raise JceDecodeError(f"server returned unified protocol error: {error_code}")

    pos = 69
    pos += 1
    pos += 10
    pos += 1
    extension_len = struct.unpack_from(">H", data, pos)[0]
    pos += 2 + extension_len
    business_head_len = struct.unpack_from(">H", data, pos)[0]
    pos += 2 + business_head_len
    inner_len = struct.unpack_from(">i", data, pos)[0]
    pos += 4

    if data[-1] != 3:
        raise JceDecodeError("invalid unified protocol tail")
    payload = data[pos:-1]
    inner = gzip.decompress(payload) if flags & 2 else payload
    if len(inner) != inner_len or len(inner) < 17 or inner[0] != 38 or inner[-1] != 40:
        raise JceDecodeError("invalid inner protocol wrapper")
    return inner[16:-1]


def parse_response_head(reader: JceReader) -> dict[str, int | str]:
    return {
        "request_id": reader.read_int(0, required=True),
        "cmd_id": reader.read_int(1, required=True),
        "err_code": reader.read_int(2, required=True),
        "user_id": reader.read_string(3, required=True, default="") or "",
    }


def parse_response_command(data: bytes) -> bytes:
    reader = JceReader(data)
    head = reader.read_struct(0, parse_response_head, required=True)
    body = reader.read_bytes(1, required=True)
    if head is None or body is None:
        raise JceDecodeError("response command is missing head or body")
    if int(head["err_code"]) != 0:
        raise JceDecodeError(f"server returned command error: {head['err_code']}")
    if int(head["cmd_id"]) != CMD_TV_SHOW_LIST:
        raise JceDecodeError(f"unexpected command body cmd id: {head['cmd_id']}")
    return body


def read_scalar_by_type(reader: JceReader, type_: int) -> int | str | float:
    if type_ == TYPE_BYTE:
        return struct.unpack(">b", reader._read(1))[0]
    if type_ == TYPE_SHORT:
        return struct.unpack(">h", reader._read(2))[0]
    if type_ == TYPE_INT:
        return struct.unpack(">i", reader._read(4))[0]
    if type_ == TYPE_LONG:
        return struct.unpack(">q", reader._read(8))[0]
    if type_ == TYPE_STRING1:
        size = reader._read(1)[0]
        return reader._read(size).decode("utf-8", errors="replace")
    if type_ == TYPE_STRING4:
        size = struct.unpack(">i", reader._read(4))[0]
        return reader._read(size).decode("utf-8", errors="replace")
    if type_ == TYPE_ZERO:
        return 0
    raise JceDecodeError(f"unsupported scalar type: {type_}")


def scalar_to_int(value: int | str | float) -> int:
    if isinstance(value, str):
        return int(value) if value else 0
    return int(value)


def read_first_text_line_struct(reader: JceReader) -> str:
    text = reader.read_string(0, default="") or ""
    reader.skip_to_struct_end()
    return text


def parse_program_detail(data: bytes) -> TVShowProgram:
    reader = JceReader(data)
    title = ""
    display_time = ""
    start_time_stamp = 0
    duration = 0

    while reader.pos < len(data):
        type_, tag = reader.read_head()
        if type_ == TYPE_STRUCT_END:
            break
        if tag == 0 and type_ == TYPE_STRUCT_BEGIN:
            display_time = read_first_text_line_struct(reader)
        elif tag == 1 and type_ == TYPE_STRUCT_BEGIN:
            title = read_first_text_line_struct(reader)
        elif tag == 7 and type_ in {TYPE_BYTE, TYPE_SHORT, TYPE_INT, TYPE_LONG, TYPE_STRING1, TYPE_STRING4, TYPE_ZERO}:
            start_time_stamp = scalar_to_int(read_scalar_by_type(reader, type_))
        elif tag == 8 and type_ in {TYPE_BYTE, TYPE_SHORT, TYPE_INT, TYPE_LONG, TYPE_STRING1, TYPE_STRING4, TYPE_ZERO}:
            duration = scalar_to_int(read_scalar_by_type(reader, type_))
        else:
            reader.skip_field_by_type(type_)

    return TVShowProgram(
        title=title,
        display_time=display_time,
        start_time_stamp=start_time_stamp,
        duration=duration,
    )


def read_simple_list_bytes(reader: JceReader) -> bytes:
    inner_type, _ = reader.read_head()
    if inner_type != TYPE_BYTE:
        raise JceDecodeError(f"invalid simple-list inner type: {inner_type}")
    size_type, _ = reader.read_head()
    size = scalar_to_int(read_scalar_by_type(reader, size_type))
    return reader._read(size)


def parse_program_item(reader: JceReader) -> Optional[TVShowProgram]:
    detail: Optional[bytes] = None
    while reader.pos < len(reader.data):
        type_, tag = reader.read_head()
        if type_ == TYPE_STRUCT_END:
            break
        if tag == 4 and type_ == TYPE_SIMPLE_LIST:
            detail = read_simple_list_bytes(reader)
        else:
            reader.skip_field_by_type(type_)

    if not detail:
        return None
    program = parse_program_detail(detail)
    if not program.title or program.start_time_stamp <= 0:
        return None
    return program


def parse_tvshowlist_response(body: bytes) -> list[TVShowProgram]:
    reader = JceReader(body)
    errcode = reader.read_int(0, default=0)
    if errcode != 0:
        raise JceDecodeError(f"TVShowList returned error: {errcode}")
    if not reader.skip_to_tag(1):
        return []
    type_, _ = reader.read_head()
    if type_ != TYPE_LIST:
        raise JceDecodeError(f"expected programme list, got JCE type {type_}")

    size_type, _ = reader.read_head()
    size = scalar_to_int(read_scalar_by_type(reader, size_type))
    programs: list[TVShowProgram] = []
    for _ in range(size):
        item_type, _ = reader.read_head()
        if item_type != TYPE_STRUCT_BEGIN:
            reader.skip_field_by_type(item_type)
            continue
        program = parse_program_item(reader)
        if program is not None:
            programs.append(program)
    return programs


def fetch_epg(
    pid: str,
    day: str,
    timestamp: int,
    *,
    url: str = JACC_URL,
    timeout: float = 15.0,
    insecure: bool = False,
    request_id: int = 44,
    guid: str = DEFAULT_GUID,
    raw_response: Optional[Path] = None,
) -> list[TVShowProgram]:
    body = build_request(pid, day, timestamp, request_id, guid)
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/octet-stream",
            "User-Agent": USER_AGENT,
        },
    )
    context = ssl._create_unverified_context() if insecure else None
    with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
        response_data = response.read()
    if raw_response:
        raw_response.parent.mkdir(parents=True, exist_ok=True)
        raw_response.write_bytes(response_data)

    response_command = unwrap_unified_protocol(response_data)
    response_body = parse_response_command(response_command)
    return parse_tvshowlist_response(response_body)


async def get_epgs_ysp_jce(channel: dict, dt: datetime) -> dict:
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    pid = str(channel.get('id0'))
    day = dt.strftime("%Y-%m-%d")
    timestamp = default_timestamp()
    try:
        programs = await asyncio.to_thread(fetch_epg, pid, day, timestamp)
        programs = sorted(programs, key=lambda program: program.start_time_stamp)
        for index, program in enumerate(programs):
            stop = None
            if program.duration > 0:
                stop = program.start_time_stamp + program.duration
            elif index + 1 < len(programs):
                next_start = programs[index + 1].start_time_stamp
                if next_start > program.start_time_stamp:
                    stop = next_start
            if stop is None:
                continue
            epg = {
                'channel_id': channel_id,
                'starttime': datetime.fromtimestamp(program.start_time_stamp, CN_TZ),
                'endtime': datetime.fromtimestamp(stop, CN_TZ),
                'title': program.title,
                'desc': '',
            }
            # print(epg)
            epgs.append(epg)
    except Exception as e:
        success = 0
        spidername = Path(__file__).stem
        msg = 'spider-%s-%s' % (spidername, e)
    ret = {
        'success': success,
        'epgs': epgs,
        'msg': msg,
        'ban': 0
    }
    return ret


def default_day() -> str:
    return datetime.now(CN_TZ).strftime("%Y-%m-%d")


def default_timestamp() -> int:
    return int(datetime.now(CN_TZ).timestamp())


if __name__ == '__main__':
    asyncio.run(get_epgs_ysp_jce({'id': 'cctv_fyyy', 'name': 'CCTV风云音乐', 'id0': '600001859', 'source': 'YSP_JCE'}, datetime.now().date()))