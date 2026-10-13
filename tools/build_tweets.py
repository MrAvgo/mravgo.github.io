#!/usr/bin/env python3
"""从 tools/input/tweets.json 生成 tweets.html（我的推文主页）。

用法: python3 tools/build_tweets.py
输入: tools/input/tweets.json（含 profile + tweets 数组，时间倒序）
输出: tweets.html（站根目录）
只收 2026-09-28 及之后的推文；每条推文保留 X 原帖链接。
"""
import html as htmlmod
import json
import os
import re

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT = os.path.join(SITE, "tools", "input", "tweets.json")
OUT = os.path.join(SITE, "tweets.html")
SITE_URL = "https://avgo.pages.dev"
CUTOFF = "2026-09-28"
CSS_VER = "20261013"

URL_RE = re.compile(r"https?://[^\s<>\"]+")

TYPE_LABEL = {"original": "原创", "quote": "引用", "reply": "回复"}


def linkify(text):
    """转义 HTML 后把 URL 变成链接，保留换行。"""
    parts = []
    last = 0
    for m in URL_RE.finditer(text):
        parts.append(htmlmod.escape(text[last:m.start()]))
        url = m.group(0)
        parts.append('<a href="%s" target="_blank" rel="noopener">%s</a>'
                     % (htmlmod.escape(url, quote=True), htmlmod.escape(url)))
        last = m.end()
    parts.append(htmlmod.escape(text[last:]))
    return "<br>".join("".join(parts).split("\n"))


def tweet_card(t):
    ttype = t.get("type", "original")
    label = TYPE_LABEL.get(ttype, "原创")
    time = htmlmod.escape(t.get("time", ""))
    text_html = linkify(t.get("text", ""))
    url = t.get("url", "")
    card = ['<article class="brief-card tweet-card">',
            '  <div class="tweet-meta"><span class="tweet-badge tweet-%s">%s</span>'
            % (ttype, label),
            '  <span class="tweet-time">%s</span></div>' % time,
            '  <p class="tweet-text">%s</p>' % text_html]
    ref_url = t.get("ref_url")
    ref_author = t.get("ref_author")
    if ttype in ("quote", "reply") and ref_url:
        verb = "引用" if ttype == "quote" else "回复"
        author = htmlmod.escape(ref_author or "")
        card.append('  <p class="tweet-ref">%s <a href="%s" target="_blank" rel="noopener">%s 的帖子</a></p>'
                    % (verb, htmlmod.escape(ref_url, quote=True), author))
    if url:
        card.append('  <p class="tweet-link"><a href="%s" target="_blank" rel="noopener">在 𝕏 上查看 →</a></p>'
                    % htmlmod.escape(url, quote=True))
    card.append("</article>")
    return "\n".join(card)


def build():
    with open(INPUT, encoding="utf-8") as f:
        data = json.load(f)
    tweets = [t for t in data.get("tweets", [])
              if t.get("time", "") >= CUTOFF and t.get("url")]
    tweets.sort(key=lambda t: t["time"], reverse=True)

    profile = data
    name = htmlmod.escape(profile.get("name", "@AVGO_X_"))
    handle = htmlmod.escape(profile.get("handle", "@AVGO_X_"))
    bio = htmlmod.escape(profile.get("bio", ""))
    followers = htmlmod.escape(str(profile.get("followers", "–")))
    following = htmlmod.escape(str(profile.get("following", "–")))
    avatar = htmlmod.escape(profile.get("avatar", "assets/x-avatar.jpg"))
    profile_url = htmlmod.escape(profile.get("profile_url", "https://x.com/AVGO_X_"),
                                 quote=True)
    updated = htmlmod.escape(data.get("updated", ""))

    cards = "\n".join(tweet_card(t) for t in tweets)

    page = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>我的推文 | AVGO 每日追踪</title>
  <meta name="description" content="$AVGO Observer（@AVGO_X_）在 X 上的全部推文：原创、引用、回复，按时间倒序展示。">
  <link rel="canonical" href="%s/tweets">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="AVGO 每日追踪">
  <meta property="og:title" content="我的推文 | AVGO 每日追踪">
  <meta property="og:description" content="$AVGO Observer（@AVGO_X_）在 X 上的全部推文：原创、引用、回复，按时间倒序。">
  <meta property="og:url" content="%s/tweets">
  <meta property="og:image" content="%s/assets/avgo-emblem.webp">
  <meta name="twitter:card" content="summary">
  <link rel="icon" href="favicon.ico" type="image/x-icon">
  <link rel="apple-touch-icon" href="apple-touch-icon.png">
  <link rel="stylesheet" href="styles.css?v=%s">
  <script>(function(){try{var m=localStorage.getItem("avgo-theme")||"system";var t=(m==="dark"||m==="light")?m:((window.matchMedia&&window.matchMedia("(prefers-color-scheme: dark)").matches)?"dark":"light");document.documentElement.setAttribute("data-theme",t);document.documentElement.setAttribute("data-theme-mode",m);}catch(e){}})();</script>
  <style>
    .profile-card{display:flex;gap:16px;align-items:center;flex-wrap:wrap}
    .profile-avatar{width:72px;height:72px;border-radius:50%%;flex:none}
    .profile-info{flex:1;min-width:200px}
    .profile-name{font-size:1.25em;font-weight:700;margin:0}
    .profile-handle{color:var(--muted,#888);margin:2px 0 6px}
    .profile-bio{margin:6px 0;font-size:.92em}
    .profile-stats{display:flex;gap:16px;font-size:.9em;color:var(--muted,#888);margin:6px 0}
    .profile-stats b{color:inherit}
    .tweet-card{margin-bottom:14px}
    .tweet-meta{display:flex;align-items:center;gap:10px;margin-bottom:8px}
    .tweet-badge{font-size:.78em;font-weight:700;padding:2px 10px;border-radius:999px;color:#fff}
    .tweet-original{background:#1d9bf0}
    .tweet-quote{background:#7c3aed}
    .tweet-reply{background:#0f9d58}
    .tweet-time{font-size:.85em;color:var(--muted,#888)}
    .tweet-text{margin:0 0 8px;line-height:1.65;word-break:break-word}
    .tweet-ref{font-size:.88em;color:var(--muted,#888);margin:0 0 6px}
    .tweet-link{margin:0;font-size:.88em}
  </style>
</head>
<body>

<header class="site-header">
  <div class="wrap">
    <div class="brand">
      <a class="brand-logo-link" href="/" aria-label="AVGO 投资简报首页"><img class="brand-logo" src="assets/avgo-emblem.webp" alt="$AVGO"></a>
      <div>
        <h1>AVGO 每日追踪</h1>
        <p class="subtitle">每日更新的 Broadcom (NASDAQ: AVGO) 中文投资资讯站</p>
      </div>
    </div>
    <button class="menu-toggle" type="button" aria-label="打开菜单" aria-expanded="false" aria-controls="site-nav">
    <svg class="icon-menu" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
    <svg class="icon-close" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>
    </button>
    <nav class="nav" id="site-nav">
      <a href="./">← 返回首页</a>
      <a href="#profile">𝕏 主页</a>
      <a href="#tweets">推文列表</a>
    </nav>
  </div>
</header>

<main class="wrap">

  <a class="back-link" href="./">← 返回首页</a>

  <div class="section-head">
    <h2>𝕏 我的推文</h2>
    <span class="date-tag">更新于 %s · 共 %d 条（2026-09-28 起）</span>
  </div>

  <section id="profile">
    <article class="brief-card profile-card">
      <img class="profile-avatar" src="%s" alt="%s">
      <div class="profile-info">
        <p class="profile-name">%s</p>
        <p class="profile-handle">%s</p>
        <p class="profile-bio">%s</p>
        <div class="profile-stats"><span><b>%s</b> 关注者</span><span><b>%s</b> 正在关注</span></div>
      </div>
      <a class="btn" href="%s" target="_blank" rel="noopener">𝕏 关注我</a>
    </article>
  </section>

  <section id="tweets">
%s
  </section>

</main>

<script src="app.js?v=%s" defer></script>
</body>
</html>
""" % (SITE_URL, SITE_URL, SITE_URL, CSS_VER,
        updated, len(tweets),
        avatar, name, name, handle, bio, followers, following,
        profile_url, cards, CSS_VER)

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print("wrote %s (%d tweets)" % (OUT, len(tweets)))


if __name__ == "__main__":
    build()
