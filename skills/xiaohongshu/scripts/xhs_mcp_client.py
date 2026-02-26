#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""xhs_mcp_client.py

一个轻量的 xiaohongshu-mcp HTTP API 客户端（无第三方依赖）。

默认连接： http://localhost:18060

用法示例：
  python3 xhs_mcp_client.py health
  python3 xhs_mcp_client.py login-qrcode --out ./qrcode.png

说明：
- 该脚本面向“本机已启动 xiaohongshu-mcp 服务”的场景。
- 仅封装项目 docs/API.md 里公开的 HTTP API。
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional


DEFAULT_BASE_URL = "http://localhost:18060"


def _json_loads_maybe(value: Optional[str]) -> Any:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    return json.loads(value)


def _http_json(method: str, base_url: str, path: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    url = base_url.rstrip("/") + path
    data = None
    headers = {"Accept": "application/json"}

    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        data = body
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url=url, method=method.upper(), data=data, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} {e.reason}: {raw}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"连接失败：{url}，原因：{e}") from e


def cmd_health(args: argparse.Namespace) -> None:
    data = _http_json("GET", args.base_url, "/health")
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_login_status(args: argparse.Namespace) -> None:
    data = _http_json("GET", args.base_url, "/api/v1/login/status")
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_login_qrcode(args: argparse.Namespace) -> None:
    data = _http_json("GET", args.base_url, "/api/v1/login/qrcode")
    print(json.dumps({k: v for k, v in data.items() if k != "data"}, ensure_ascii=False, indent=2))

    img = (data.get("data") or {}).get("img")
    if not img:
        raise RuntimeError("响应中未包含 data.img（二维码）")

    # 可能是 data:image/png;base64,xxxx
    if "," in img:
        _, b64 = img.split(",", 1)
    else:
        b64 = img

    out = args.out
    if not out:
        out = "xhs_qrcode.png"

    png = base64.b64decode(b64)
    with open(out, "wb") as f:
        f.write(png)

    print(f"\n二维码已保存：{out}\n请用小红书 App 扫码登录，然后再运行 login-status 检查。")


def cmd_login_reset(args: argparse.Namespace) -> None:
    data = _http_json("DELETE", args.base_url, "/api/v1/login/cookies")
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_publish_note(args: argparse.Namespace) -> None:
    payload: Dict[str, Any] = {
        "title": args.title,
        "content": args.content,
        "images": _json_loads_maybe(args.images) or [],
    }
    tags = _json_loads_maybe(args.tags)
    if tags is not None:
        payload["tags"] = tags

    data = _http_json("POST", args.base_url, "/api/v1/publish", payload)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_publish_video(args: argparse.Namespace) -> None:
    payload: Dict[str, Any] = {
        "title": args.title,
        "content": args.content,
        "video": args.video,
    }
    tags = _json_loads_maybe(args.tags)
    if tags is not None:
        payload["tags"] = tags

    data = _http_json("POST", args.base_url, "/api/v1/publish_video", payload)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_feeds_list(args: argparse.Namespace) -> None:
    data = _http_json("GET", args.base_url, "/api/v1/feeds/list")
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_feeds_search(args: argparse.Namespace) -> None:
    if args.use_post:
        payload: Dict[str, Any] = {"keyword": args.keyword}
        if args.filters:
            payload["filters"] = _json_loads_maybe(args.filters)
        data = _http_json("POST", args.base_url, "/api/v1/feeds/search", payload)
    else:
        query = urllib.parse.urlencode({"keyword": args.keyword})
        data = _http_json("GET", args.base_url, f"/api/v1/feeds/search?{query}")

    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_feed_detail(args: argparse.Namespace) -> None:
    payload: Dict[str, Any] = {
        "feed_id": args.feed_id,
        "xsec_token": args.xsec_token,
    }

    if args.load_all_comments:
        payload["load_all_comments"] = True

    if args.max_comment_items is not None:
        payload["comment_config"] = {
            "max_comment_items": args.max_comment_items,
        }

    data = _http_json("POST", args.base_url, "/api/v1/feeds/detail", payload)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_user_profile(args: argparse.Namespace) -> None:
    payload = {"user_id": args.user_id, "xsec_token": args.xsec_token}
    data = _http_json("POST", args.base_url, "/api/v1/user/profile", payload)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_user_me(args: argparse.Namespace) -> None:
    data = _http_json("GET", args.base_url, "/api/v1/user/me")
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_comment(args: argparse.Namespace) -> None:
    payload = {"feed_id": args.feed_id, "xsec_token": args.xsec_token, "content": args.content}
    data = _http_json("POST", args.base_url, "/api/v1/feeds/comment", payload)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_comment_reply(args: argparse.Namespace) -> None:
    payload: Dict[str, Any] = {
        "feed_id": args.feed_id,
        "xsec_token": args.xsec_token,
        "content": args.content,
    }
    if args.comment_id:
        payload["comment_id"] = args.comment_id
    if args.user_id:
        payload["user_id"] = args.user_id

    data = _http_json("POST", args.base_url, "/api/v1/feeds/comment/reply", payload)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="xiaohongshu-mcp HTTP API client")
    p.add_argument("--base-url", default=DEFAULT_BASE_URL, help=f"默认：{DEFAULT_BASE_URL}")

    sub = p.add_subparsers(dest="cmd", required=True)

    sub_health = sub.add_parser("health", help="健康检查")
    sub_health.set_defaults(func=cmd_health)

    sub_status = sub.add_parser("login-status", help="检查登录状态")
    sub_status.set_defaults(func=cmd_login_status)

    sub_qr = sub.add_parser("login-qrcode", help="获取登录二维码并保存")
    sub_qr.add_argument("--out", default="xhs_qrcode.png", help="输出 PNG 路径")
    sub_qr.set_defaults(func=cmd_login_qrcode)

    sub_reset = sub.add_parser("login-reset", help="删除 cookies（重置登录）")
    sub_reset.set_defaults(func=cmd_login_reset)

    sub_pub = sub.add_parser("publish-note", help="发布图文")
    sub_pub.add_argument("--title", required=True)
    sub_pub.add_argument("--content", required=True)
    sub_pub.add_argument("--images", required=True, help='JSON 数组，如 ["/abs/1.jpg","/abs/2.png"]')
    sub_pub.add_argument("--tags", default=None, help='可选 JSON 数组，如 ["标签1","标签2"]')
    sub_pub.set_defaults(func=cmd_publish_note)

    sub_vid = sub.add_parser("publish-video", help="发布视频")
    sub_vid.add_argument("--title", required=True)
    sub_vid.add_argument("--content", required=True)
    sub_vid.add_argument("--video", required=True, help="本地视频绝对路径")
    sub_vid.add_argument("--tags", default=None, help='可选 JSON 数组，如 ["标签1","标签2"]')
    sub_vid.set_defaults(func=cmd_publish_video)

    sub_list = sub.add_parser("feeds-list", help="获取推荐流/feeds 列表")
    sub_list.set_defaults(func=cmd_feeds_list)

    sub_search = sub.add_parser("feeds-search", help="搜索 feeds")
    sub_search.add_argument("--keyword", required=True)
    sub_search.add_argument("--use-post", action="store_true", help="使用 POST（支持 filters JSON）")
    sub_search.add_argument("--filters", default=None, help='filters JSON，参考 docs/API.md')
    sub_search.set_defaults(func=cmd_feeds_search)

    sub_detail = sub.add_parser("feed-detail", help="获取 feed 详情（含评论）")
    sub_detail.add_argument("--feed-id", required=True)
    sub_detail.add_argument("--xsec-token", required=True)
    sub_detail.add_argument("--load-all-comments", action="store_true")
    sub_detail.add_argument("--max-comment-items", type=int, default=None, help="最大评论数（0=全部）")
    sub_detail.set_defaults(func=cmd_feed_detail)

    sub_user = sub.add_parser("user-profile", help="获取指定用户主页")
    sub_user.add_argument("--user-id", required=True)
    sub_user.add_argument("--xsec-token", required=True)
    sub_user.set_defaults(func=cmd_user_profile)

    sub_me = sub.add_parser("user-me", help="获取当前登录用户主页")
    sub_me.set_defaults(func=cmd_user_me)

    sub_c = sub.add_parser("comment", help="发表评论")
    sub_c.add_argument("--feed-id", required=True)
    sub_c.add_argument("--xsec-token", required=True)
    sub_c.add_argument("--content", required=True)
    sub_c.set_defaults(func=cmd_comment)

    sub_r = sub.add_parser("comment-reply", help="回复评论")
    sub_r.add_argument("--feed-id", required=True)
    sub_r.add_argument("--xsec-token", required=True)
    sub_r.add_argument("--content", required=True)
    sub_r.add_argument("--comment-id", default=None)
    sub_r.add_argument("--user-id", default=None)
    sub_r.set_defaults(func=cmd_comment_reply)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
