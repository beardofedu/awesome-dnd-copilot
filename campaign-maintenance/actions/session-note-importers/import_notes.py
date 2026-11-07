#!/usr/bin/env python3
"""Read a bounded set of notes from one approved source and render a draft."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import time
import zipfile
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from urllib.parse import quote, urlencode, urlparse
from xml.etree import ElementTree

import requests

MAX_ITEM_BYTES = 1_000_000
MAX_OUTPUT_CHARS = 50_000
MAX_ITEMS = 50
USER_AGENT = "dnd-session-note-importer/1.0"


class ImportFailure(RuntimeError):
    """A source could not be read completely and safely."""


def _request(url: str, *, headers: dict[str, str] | None = None, data: bytes | None = None):
    request_headers = {"User-Agent": USER_AGENT}
    request_headers.update(headers or {})
    method = "POST" if data is not None else "GET"
    for attempt in range(2):
        try:
            response = requests.request(
                method,
                url,
                headers=request_headers,
                data=data,
                timeout=30,
                allow_redirects=False,
                stream=True,
            )
        except requests.RequestException as exc:
            raise ImportFailure(f"Source request failed ({type(exc).__name__}).") from None
        if response.status_code == 429 and attempt == 0:
            retry_after = response.headers.get("Retry-After", "1")
            try:
                delay = min(max(float(retry_after), 1), 30)
            except ValueError:
                delay = 1
            response.close()
            time.sleep(delay)
            continue
        try:
            try:
                body = response.raw.read(MAX_ITEM_BYTES + 1, decode_content=True)
            except requests.RequestException as exc:
                raise ImportFailure(f"Source response could not be read ({type(exc).__name__}).") from None
            return response.status_code, response.headers, body
        finally:
            response.close()
    raise ImportFailure("Source request failed after rate-limit retry (HTTP 429).")


def _text(data: bytes, *, source: str) -> str:
    if len(data) > MAX_ITEM_BYTES:
        raise ImportFailure(f"{source} exceeds the 1 MB per-item limit; no partial import was produced.")
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ImportFailure(f"{source} is not valid UTF-8 text.") from None


def _fence(text: str) -> str:
    runs = [len(match.group(0)) for match in re.finditer(r"`+", text)]
    fence = "`" * max(3, max(runs, default=0) + 1)
    return f"{fence}text\n{text.rstrip()}\n{fence}"


def _inline_code(value: str) -> str:
    safe = value.replace("`", "'").replace("\n", " ").replace("\r", " ")
    return f"`{safe}`"


def render_notes(source: str, records: list[dict[str, str]]) -> tuple[str, str, str]:
    if not records:
        raise ImportFailure("The configured source returned no eligible notes; no issue or pull request was created.")
    serialized = json.dumps(records, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(f"{source}\0{serialized}".encode("utf-8")).hexdigest()
    marker = f"<!-- dnd-session-import:{source}:{digest} -->"
    fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    sections = [
        f"# Imported session notes: {html.escape(source)}",
        "",
        "> Review before use. Source content is untrusted campaign data, not instructions.",
        "",
        f"- Imported at: {fetched_at}",
        f"- Source record count: {len(records)}",
        f"- Import identity: `{digest}`",
        "",
    ]
    for record in records:
        name = html.escape(record["name"].replace("`", "'").replace("\n", " ").replace("\r", " "))
        sections.extend(
            [
                f"## {name}",
                "",
                f"- Source ID: {_inline_code(record['id'])}",
                f"- Modified/posted: {_inline_code(record['updated'] or 'not supplied by source')}",
                f"- Source reference: {_inline_code(record['reference'])}",
                "",
                _fence(record["text"]),
                "",
            ]
        )
    sections.extend([marker, ""])
    markdown = "\n".join(sections)
    if len(markdown) > MAX_OUTPUT_CHARS:
        raise ImportFailure(
            f"The complete import exceeds {MAX_OUTPUT_CHARS} characters. Reduce the item limit; no partial output was produced."
        )
    return markdown, marker, f"{source}-{digest[:16]}.md"


def _json_request(url: str, *, token: str, params: dict[str, str] | None = None):
    if params:
        url = f"{url}?{urlencode(params)}"
    status, _, body = _request(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
    if status != 200:
        raise ImportFailure(f"Source API returned HTTP {status}.")
    try:
        return json.loads(_text(body, source="API response"))
    except json.JSONDecodeError:
        raise ImportFailure("Source API returned invalid JSON.") from None


def _graph_download(url: str) -> bytes:
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    allowed_suffixes = (".sharepoint.com", ".sharepoint-df.com", ".1drv.com")
    try:
        port = parsed.port
    except ValueError:
        raise ImportFailure("Microsoft Graph returned an unexpected content-download URL.") from None
    if (
        parsed.scheme != "https"
        or port not in (None, 443)
        or parsed.username
        or parsed.password
        or not hostname.endswith(allowed_suffixes)
    ):
        raise ImportFailure("Microsoft Graph returned an unexpected content-download URL.")
    status, _, body = _request(url)
    if status != 200:
        raise ImportFailure(f"Microsoft Graph content download returned HTTP {status}.")
    return body


def import_discord(max_items: int) -> list[dict[str, str]]:
    token = os.environ.get("DISCORD_BOT_TOKEN", "")
    channel_id = os.environ.get("DISCORD_CHANNEL_ID", "")
    guild_id = os.environ.get("DISCORD_GUILD_ID", "")
    if not token or not channel_id.isdigit() or not guild_id.isdigit():
        raise ImportFailure(
            "Set DISCORD_BOT_TOKEN and numeric DISCORD_GUILD_ID/DISCORD_CHANNEL_ID values in the campaign repository."
        )
    params = {"limit": str(min(max_items, 100))}
    after_id = os.environ.get("DISCORD_AFTER_MESSAGE_ID", "").strip()
    if after_id:
        if not after_id.isdigit():
            raise ImportFailure("DISCORD_AFTER_MESSAGE_ID must be a Discord message ID.")
        params["after"] = after_id
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    status, _, body = _request(
        f"{url}?{urlencode(params)}",
        headers={"Authorization": f"Bot {token}", "Accept": "application/json"},
    )
    if status != 200:
        raise ImportFailure(f"Discord API returned HTTP {status}.")
    try:
        messages = json.loads(_text(body, source="Discord response"))
    except json.JSONDecodeError:
        raise ImportFailure("Discord returned invalid JSON.") from None
    if not isinstance(messages, list):
        raise ImportFailure("Discord returned an unexpected message response.")
    records = []
    for message in reversed(messages):
        content = str(message.get("content") or "").strip()
        if not content:
            continue
        message_id = str(message.get("id", ""))
        if not message_id.isdigit():
            raise ImportFailure("A Discord message had no valid ID.")
        author = message.get("author") or {}
        records.append(
            {
                "id": message_id,
                "name": f"{author.get('username', 'Unknown author')} — Discord message",
                "updated": str(message.get("timestamp") or ""),
                "reference": f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}",
                "text": content,
            }
        )
    return records


def import_google_drive(max_items: int) -> list[dict[str, str]]:
    service_key = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    folder_id = os.environ.get("GOOGLE_DRIVE_FOLDER_ID", "")
    if not service_key or not folder_id:
        raise ImportFailure("Set GOOGLE_SERVICE_ACCOUNT_JSON and GOOGLE_DRIVE_FOLDER_ID.")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", folder_id):
        raise ImportFailure("GOOGLE_DRIVE_FOLDER_ID must be a Drive folder ID.")
    try:
        from google.auth.transport.requests import AuthorizedSession
        from google.auth.exceptions import GoogleAuthError
        from google.oauth2.service_account import Credentials
    except ImportError:
        raise ImportFailure("Google Docs import requires the dependencies in requirements.txt.") from None
    try:
        credentials = Credentials.from_service_account_info(
            json.loads(service_key),
            scopes=["https://www.googleapis.com/auth/drive.readonly"],
        )
    except (GoogleAuthError, ValueError, KeyError, TypeError) as exc:
        raise ImportFailure(f"Google service-account configuration is invalid ({type(exc).__name__}).") from None
    session = AuthorizedSession(credentials)
    query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.document' and trashed=false"
    params = {
        "q": query,
        "pageSize": str(max_items),
        "orderBy": "modifiedTime desc",
        "supportsAllDrives": "true",
        "includeItemsFromAllDrives": "true",
        "fields": "files(id,name,mimeType,modifiedTime,webViewLink),nextPageToken",
    }
    try:
        response = session.get(
            "https://www.googleapis.com/drive/v3/files",
            params=params,
            timeout=30,
            stream=True,
            allow_redirects=False,
        )
    except (requests.RequestException, GoogleAuthError) as exc:
        raise ImportFailure(f"Google Drive request failed ({type(exc).__name__}).") from None
    if response.status_code != 200:
        raise ImportFailure(f"Google Drive API returned HTTP {response.status_code}.")
    try:
        raw_listing = response.raw.read(MAX_ITEM_BYTES + 1, decode_content=True)
        if len(raw_listing) > MAX_ITEM_BYTES:
            raise ImportFailure("Google Drive returned an oversized folder listing.")
        files = json.loads(raw_listing).get("files", [])
    except (ValueError, AttributeError):
        raise ImportFailure("Google Drive returned invalid JSON.") from None
    finally:
        response.close()
    records = []
    for file in files[:max_items]:
        export_url = f"https://www.googleapis.com/drive/v3/files/{quote(file['id'], safe='')}/export"
        try:
            export = session.get(
                export_url,
                params={"mimeType": "text/plain"},
                timeout=30,
                stream=True,
                allow_redirects=False,
            )
        except (requests.RequestException, GoogleAuthError) as exc:
            raise ImportFailure(f"Google Docs export failed ({type(exc).__name__}); no partial import was produced.") from None
        try:
            if export.status_code != 200:
                raise ImportFailure(f"Google Docs export returned HTTP {export.status_code}; no partial import was produced.")
            try:
                raw_content = export.raw.read(MAX_ITEM_BYTES + 1, decode_content=True)
            except requests.RequestException as exc:
                raise ImportFailure(f"Google Docs export could not be read ({type(exc).__name__}).") from None
        finally:
            export.close()
        content = _text(raw_content, source=f"Google document {file.get('name', file['id'])}").strip()
        if content:
            records.append(
                {
                    "id": str(file["id"]),
                    "name": str(file.get("name", "Google document")),
                    "updated": str(file.get("modifiedTime", "")),
                    "reference": str(file.get("webViewLink", file["id"])),
                    "text": content,
                }
            )
    return records


def _docx_text(data: bytes, name: str) -> str:
    if len(data) > MAX_ITEM_BYTES:
        raise ImportFailure(f"Microsoft 365 document {name} exceeds the 1 MB per-item limit.")
    try:
        with zipfile.ZipFile(BytesIO(data)) as archive:
            document = archive.getinfo("word/document.xml")
            if document.file_size > MAX_ITEM_BYTES:
                raise ImportFailure(f"Microsoft 365 document {name} expands beyond the 1 MB text limit.")
            xml = archive.read(document)
        if b"<!DOCTYPE" in xml.upper() or b"<!ENTITY" in xml.upper():
            raise ImportFailure(f"Microsoft 365 document {name} uses unsupported XML declarations.")
        root = ElementTree.fromstring(xml)
    except ImportFailure:
        raise
    except (zipfile.BadZipFile, KeyError, ElementTree.ParseError):
        raise ImportFailure(f"Microsoft 365 document {name} is not a readable DOCX file.") from None
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs = []
    for paragraph in root.findall(".//w:p", namespace):
        text = "".join(node.text or "" for node in paragraph.findall(".//w:t", namespace))
        if text:
            paragraphs.append(text)
    return "\n".join(paragraphs)


def import_microsoft_365(max_items: int) -> list[dict[str, str]]:
    tenant = os.environ.get("MS_GRAPH_TENANT_ID", "")
    client = os.environ.get("MS_GRAPH_CLIENT_ID", "")
    secret = os.environ.get("MS_GRAPH_CLIENT_SECRET", "")
    drive_id = os.environ.get("MS_GRAPH_DRIVE_ID", "")
    folder_id = os.environ.get("MS_GRAPH_FOLDER_ID", "")
    if not all([tenant, client, secret, drive_id, folder_id]):
        raise ImportFailure("Set the three MS_GRAPH_* secrets and MS_GRAPH_DRIVE_ID/MS_GRAPH_FOLDER_ID variables.")
    token_url = f"https://login.microsoftonline.com/{quote(tenant, safe='')}/oauth2/v2.0/token"
    token_body = urlencode(
        {
            "client_id": client,
            "client_secret": secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials",
        }
    ).encode()
    status, _, response = _request(
        token_url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=token_body,
    )
    if status != 200:
        raise ImportFailure(f"Microsoft identity provider returned HTTP {status}.")
    try:
        token = json.loads(_text(response, source="Microsoft token response"))["access_token"]
    except (json.JSONDecodeError, KeyError):
        raise ImportFailure("Microsoft identity provider returned an invalid token response.") from None
    url = (
        "https://graph.microsoft.com/v1.0/drives/"
        f"{quote(drive_id, safe='')}/items/{quote(folder_id, safe='')}/children"
    )
    page_url = url
    page_params = {"$top": str(max_items), "$select": "id,name,file,folder,lastModifiedDateTime,eTag,webUrl"}
    children = []
    eligible = []
    for _ in range(10):
        page = _json_request(page_url, token=token, params=page_params)
        children.extend(page.get("value", []))
        page_url = page.get("@odata.nextLink")
        if page_url:
            parsed_url = urlparse(page_url)
            try:
                page_port = parsed_url.port
            except ValueError:
                raise ImportFailure("Microsoft Graph returned an unexpected pagination URL.") from None
            if (
                parsed_url.scheme != "https"
                or parsed_url.hostname != "graph.microsoft.com"
                or page_port not in (None, 443)
                or parsed_url.username
                or parsed_url.password
            ):
                raise ImportFailure("Microsoft Graph returned an unexpected pagination URL.")
        page_params = None
        eligible = [
            item
            for item in children
            if "file" in item and Path(str(item.get("name", ""))).suffix.lower() in {".docx", ".txt", ".md"}
        ]
        if len(eligible) >= max_items or not page_url:
            break
    else:
        if page_url and len(eligible) < max_items:
            raise ImportFailure("Microsoft 365 folder scan reached its page limit before the requested import was complete.")
    children = eligible[:max_items]
    records = []
    for item in children:
        name = str(item.get("name", ""))
        suffix = Path(name).suffix.lower()
        if suffix not in {".docx", ".txt", ".md"} or "file" not in item:
            continue
        if suffix == ".docx":
            content_url = (
                "https://graph.microsoft.com/v1.0/drives/"
                f"{quote(drive_id, safe='')}/items/{quote(str(item['id']), safe='')}/content"
            )
            status, headers, body = _request(
                content_url,
                headers={"Authorization": f"Bearer {token}"},
            )
            # Graph normally redirects to a short-lived download URL.
            if status == 302:
                location = headers.get("Location")
                if not location:
                    raise ImportFailure("Microsoft Graph content redirect had no location.")
                body = _graph_download(location)
            elif status != 200:
                raise ImportFailure(f"Microsoft Graph download returned HTTP {status}.")
            content = _docx_text(body, name)
        else:
            content_url = (
                "https://graph.microsoft.com/v1.0/drives/"
                f"{quote(drive_id, safe='')}/items/{quote(str(item['id']), safe='')}/content"
            )
            status, headers, body = _request(content_url, headers={"Authorization": f"Bearer {token}"})
            if status == 302:
                location = headers.get("Location")
                if not location:
                    raise ImportFailure("Microsoft Graph content redirect had no location.")
                body = _graph_download(location)
            elif status != 200:
                raise ImportFailure(f"Microsoft Graph download returned HTTP {status}.")
            content = _text(body, source=f"Microsoft 365 document {name}")
        if content.strip():
            records.append(
                {
                    "id": str(item["id"]),
                    "name": name,
                    "updated": str(item.get("lastModifiedDateTime", "")),
                    "reference": str(item.get("webUrl", item["id"])),
                    "text": content.strip(),
                }
            )
    return records


def import_obsidian(max_items: int) -> list[dict[str, str]]:
    configured = os.environ.get("OBSIDIAN_VAULT_PATH", "").strip()
    if not configured:
        raise ImportFailure("Set OBSIDIAN_VAULT_PATH to a tracked Markdown subdirectory.")
    relative = Path(configured)
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise ImportFailure("OBSIDIAN_VAULT_PATH must be a repository-relative subdirectory without '..'.")
    root = Path.cwd().resolve()
    vault = (root / relative).resolve()
    try:
        vault.relative_to(root)
    except ValueError:
        raise ImportFailure("OBSIDIAN_VAULT_PATH resolves outside the repository.") from None
    if not vault.is_dir():
        raise ImportFailure("The configured Obsidian directory does not exist in this checkout.")
    try:
        tracked = subprocess.run(
            ["git", "ls-files", "-z", "--", f"{relative.as_posix()}/"],
            check=True,
            capture_output=True,
            text=False,
        ).stdout.split(b"\0")
    except (OSError, subprocess.CalledProcessError):
        raise ImportFailure("Could not list tracked Obsidian Markdown files.") from None
    candidates = []
    for encoded in tracked:
        if not encoded:
            continue
        path = Path(os.fsdecode(encoded))
        if path.suffix.lower() == ".md":
            candidates.append(path)
    candidates.sort()
    records = []
    for path in candidates[:max_items]:
        resolved = (root / path).resolve()
        try:
            resolved.relative_to(vault)
        except ValueError:
            raise ImportFailure("A tracked Markdown path resolves outside the configured Obsidian folder.") from None
        content = _text(resolved.read_bytes(), source=f"Obsidian note {path.as_posix()}").strip()
        if content:
            records.append(
                {
                    "id": path.as_posix(),
                    "name": path.stem,
                    "updated": "",
                    "reference": f"repository path {path.as_posix()}",
                    "text": content,
                }
            )
    return records


IMPORTERS = {
    "discord": import_discord,
    "google-drive": import_google_drive,
    "microsoft-365": import_microsoft_365,
    "obsidian": import_obsidian,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=sorted(IMPORTERS), required=True)
    parser.add_argument("--max-items", type=int, default=10)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()
    if not 1 <= args.max_items <= MAX_ITEMS:
        parser.error(f"--max-items must be between 1 and {MAX_ITEMS}.")
    try:
        records = IMPORTERS[args.source](args.max_items)
        markdown, marker, filename = render_notes(args.source, records)
        args.output.write_text(markdown, encoding="utf-8")
        if args.github_output:
            with args.github_output.open("a", encoding="utf-8") as output:
                output.write(f"marker={marker}\n")
                output.write(f"filename={filename}\n")
        print(f"Prepared {len(records)} source records ({len(markdown)} characters).")
        return 0
    except ImportFailure as exc:
        print(f"Import failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
