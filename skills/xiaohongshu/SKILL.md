---
name: 小红书运营（xiaohongshu-mcp）
description: "基于开源项目 xpzouying/xiaohongshu-mcp 的小红书自动化运营 Skill。用于：发布图文/视频笔记、搜索与获取推荐流、读取笔记详情与评论、获取用户主页、发表评论/回复、检查登录与获取登录二维码、重置 Cookies 等。用户提供小红书关键词或链接并要求发布/搜索/阅读内容时使用。"
---

# 小红书运营（xiaohongshu-mcp）

本 Skill 不会把 xiaohongshu-mcp 的二进制文件“打包进 Skill 文件”，而是把**可复用的操作流程 + 本地脚本客户端**打包进 Skill，方便你在本机/服务器启动 xiaohongshu-mcp 后，用统一方式完成常见小红书运营动作。

## 0. 前置：启动 xiaohongshu-mcp 服务（一次性）

你需要先把开源项目跑起来（推荐 Docker）：

```bash
# 方式 A：Docker Compose（推荐）
wget https://raw.githubusercontent.com/xpzouying/xiaohongshu-mcp/main/docker/docker-compose.yml
mkdir -p ./xhs-mcp && mv docker-compose.yml ./xhs-mcp/
cd ./xhs-mcp

docker compose up -d

docker compose logs -f
```

服务默认地址：
- HTTP API: `http://localhost:18060`
- MCP: `http://localhost:18060/mcp`

> 也可以用 Release 二进制或源码运行，详见项目 README。

## 1. 快速自检

```bash
python3 .continue/skills/xiaohongshu-mcp/scripts/xhs_mcp_client.py health
python3 .continue/skills/xiaohongshu-mcp/scripts/xhs_mcp_client.py login-status
```

## 2. 登录（扫码一次，后续复用 cookies）

获取二维码并保存为图片：

```bash
python3 .continue/skills/xiaohongshu-mcp/scripts/xhs_mcp_client.py login-qrcode --out ./xhs_qrcode.png
```

打开 `./xhs_qrcode.png` 用小红书 App 扫码登录；登录完成后再检查：

```bash
python3 .continue/skills/xiaohongshu-mcp/scripts/xhs_mcp_client.py login-status
```

如需重置登录（删除 cookies）：

```bash
python3 .continue/skills/xiaohongshu-mcp/scripts/xhs_mcp_client.py login-reset
```

## 3. 发布

### 3.1 发布图文

```bash
python3 .continue/skills/xiaohongshu-mcp/scripts/xhs_mcp_client.py publish-note \
  --title "标题（建议<=20字）" \
  --content "正文（建议<=1000字）" \
  --images '["/绝对路径/1.jpg","/绝对路径/2.png"]' \
  --tags '["标签1","标签2"]'
```

> images 支持 HTTP/HTTPS 链接，但更推荐本地绝对路径（更稳、更快）。

### 3.2 发布视频

```bash
python3 .continue/skills/xiaohongshu-mcp/scripts/xhs_mcp_client.py publish-video \
  --title "视频标题" \
  --content "视频描述" \
  --video "/绝对路径/video.mp4" \
  --tags '["标签1","标签2"]'
```

## 4. 搜索 / 推荐流 / 读取内容

### 4.1 获取推荐流（feeds list）

```bash
python3 .continue/skills/xiaohongshu-mcp/scripts/xhs_mcp_client.py feeds-list
```

### 4.2 搜索

```bash
python3 .continue/skills/xiaohongshu-mcp/scripts/xhs_mcp_client.py feeds-search --keyword "搜索关键词"
```

### 4.3 读取笔记详情与评论

⚠️ 读取详情需要 `feed_id` + `xsec_token`。
- 通常可从 `feeds-list` / `feeds-search` 的返回结果里拿到：`id` + `xsecToken`
- 如果用户只给了小红书链接，但链接里不带 `xsec_token`，就需要先搜索或让用户提供 `xsec_token`

```bash
python3 .continue/skills/xiaohongshu-mcp/scripts/xhs_mcp_client.py feed-detail \
  --feed-id "xxxx" --xsec-token "yyyy" \
  --max-comment-items 50
```

## 5. 用户主页 / 评论互动

### 5.1 获取当前登录用户主页

```bash
python3 .continue/skills/xiaohongshu-mcp/scripts/xhs_mcp_client.py user-me
```

### 5.2 获取指定用户主页

```bash
python3 .continue/skills/xiaohongshu-mcp/scripts/xhs_mcp_client.py user-profile --user-id "xxxx" --xsec-token "yyyy"
```

### 5.3 发表评论

```bash
python3 .continue/skills/xiaohongshu-mcp/scripts/xhs_mcp_client.py comment \
  --feed-id "xxxx" --xsec-token "yyyy" --content "评论内容"
```

### 5.4 回复评论

```bash
python3 .continue/skills/xiaohongshu-mcp/scripts/xhs_mcp_client.py comment-reply \
  --feed-id "xxxx" --xsec-token "yyyy" --comment-id "comment_id" \
  --content "回复内容"
```

## 6. 使用建议与风险提示（务必遵守平台规则）

- 控制频率与批量操作，避免高频发布/评论造成账号风控。
- 遵守小红书社区规范与法律法规，不做刷量/引流/搬运等违规行为。
- 同一账号避免在多个网页端同时登录（项目 README 有明确提示），以免互相“踢下线”。

## 参考

- 项目主页： https://github.com/xpzouying/xiaohongshu-mcp
- HTTP API 文档（项目自带）：https://raw.githubusercontent.com/xpzouying/xiaohongshu-mcp/main/docs/API.md
