#!/usr/bin/env python3
"""Git clean filter: sanitize collection YAML on git add (stdin -> stdout)."""

from __future__ import annotations

import re
import sys

ENV_ALLOWED = {
    "baseurl",
    "restaurantserviceurl",
    "userserviceurl",
    "orderserviceurl",
    "cartserviceurl",
    "courierserviceurl",
    "paymentserviceurl",
    "menuserviceurl",
    "authserverurl",
    "realm",
    "oauthclientid",
}

ENV_BLANK = {
    "username",
    "password",
    "userid",
    "customerid",
    "orderid",
    "restaurantid",
    "menuitemid",
    "paymentid",
    "courierid",
    "cartid",
    "stripepaymentintentid",
    "accesstoken",
    "clientsecret",
    "apikey",
    "email",
    "firstname",
    "lastname",
    "fullname",
    "displayname",
}

PARAM_BLANK_NAMES = ENV_BLANK | {
    "id",
    "paymentid",
    "stripepaymentintentid",
    "restaurantid",
    "menuitemid",
    "courierid",
    "cartid",
    "orderid",
    "customerid",
    "userid",
}

JWT_RE = re.compile(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")
BEARER_RE = re.compile(r"Bearer\s+[A-Za-z0-9._-]+", re.IGNORECASE)
UUID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)


def is_pass_through(text: str) -> bool:
    if text.lstrip().startswith("opencollection:"):
        return True
    return bool(re.search(r"^\s+type:\s*folder\s*$", text, re.MULTILINE))


def is_env_file(text: str) -> bool:
    return text.lstrip().startswith("name:") and "variables:" in text


def sanitize_env(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        name_match = re.match(r"^(\s+- name:\s*)(\S+)\s*$", line)
        if not name_match:
            out.append(JWT_RE.sub("", BEARER_RE.sub("", line)))
            i += 1
            continue

        prefix, var_name = name_match.group(1), name_match.group(2)
        key = var_name.lower()
        block_lines = [line]
        j = i + 1
        while j < len(lines) and not re.match(r"^\s+- name:\s*", lines[j]):
            block_lines.append(lines[j])
            j += 1

        if key in ENV_ALLOWED:
            out.extend(block_lines)
        elif key in ENV_BLANK or key == "password":
            out.append(f"{prefix}{var_name}")
            has_secret = any(re.match(r"^\s+secret:\s*true\s*$", b) for b in block_lines[1:])
            has_enabled = any(re.match(r"^\s+enabled:\s*", b) for b in block_lines[1:])
            if key == "password" or has_secret:
                out.append("    secret: true")
            else:
                out.append('    value: ""')
            if has_enabled:
                out.append("    enabled: true")
        else:
            sanitized_block = []
            for b in block_lines:
                b = JWT_RE.sub("", b)
                b = BEARER_RE.sub("", b)
                if UUID_RE.search(b) and re.match(r"^\s+value:\s*", b):
                    sanitized_block.append('    value: ""')
                elif re.match(r"^\s+value:\s*", b) and "@" in b:
                    sanitized_block.append('    value: ""')
                else:
                    sanitized_block.append(b)
            out.extend(sanitized_block)

        i = j

    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def sanitize_request(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    in_params = False
    current_name: str | None = None
    current_type: str | None = None

    for line in lines:
        line = JWT_RE.sub("", BEARER_RE.sub("", line))

        if re.match(r"^\s+params:\s*$", line):
            in_params = True
            out.append(line)
            continue

        if in_params:
            if re.match(r"^\s{2}\S", line) and not line.startswith("    "):
                in_params = False
                current_name = None
                current_type = None
            else:
                name_match = re.match(r"^\s+- name:\s*(\S+)\s*$", line)
                if name_match:
                    current_name = name_match.group(1)
                    current_type = None
                    out.append(line)
                    continue
                type_match = re.match(r"^\s+type:\s*(\S+)\s*$", line)
                if type_match and current_name:
                    current_type = type_match.group(1)
                    out.append(line)
                    continue
                value_match = re.match(r"^(\s+value:\s*)(.*)$", line)
                if value_match and current_name and current_type in {"path", "query"}:
                    raw = value_match.group(2).strip().strip("'\"")
                    name_key = current_name.lower()
                    should_blank = (
                        name_key in PARAM_BLANK_NAMES
                        or (
                            raw
                            and UUID_RE.fullmatch(raw)
                            and not raw.startswith("00000000-0000-0000-0000-")
                        )
                        or (
                            name_key in {"email", "username", "name"}
                            and raw
                            and "demo" not in raw.lower()
                        )
                    )
                    if should_blank and raw:
                        out.append(f'{value_match.group(1)}""')
                        continue

        out.append(line)

    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def sanitize(text: str) -> str:
    if is_pass_through(text):
        return text
    if is_env_file(text):
        return sanitize_env(text)
    return sanitize_request(text)


def main() -> int:
    text = sys.stdin.read()
    sys.stdout.write(sanitize(text))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
