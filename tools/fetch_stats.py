#!/usr/bin/env python3
"""Lấy số liệu GitHub (30 ngày gần nhất) -> data/stats.json.

Chạy local:   python3 tools/fetch_stats.py luchub-19      (dùng `gh auth token`)
Chạy Actions: GITHUB_TOKEN có sẵn, truyền username làm tham số.
Chỉ dùng thư viện chuẩn. Lỗi mạng -> giữ nguyên stats.json cũ.
"""
import json, os, subprocess, sys, urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

LOGIN = sys.argv[1] if len(sys.argv) > 1 else "luchub-19"
OUT = Path(__file__).resolve().parent.parent / "data" / "stats.json"

QUERY = """
query($login:String!, $from:DateTime!){
  user(login:$login){
    repositories(privacy:PUBLIC, ownerAffiliations:OWNER, isFork:false, first:100){
      totalCount
      nodes{ pushedAt }
    }
    recent: contributionsCollection(from:$from){
      totalCommitContributions
      contributionCalendar{ weeks{ contributionDays{ date contributionCount } } }
    }
    year: contributionsCollection{
      totalCommitContributions
      contributionCalendar{ totalContributions }
    }
  }
}"""


def token():
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if t:
        return t
    return subprocess.check_output(["gh", "auth", "token"], text=True).strip()


def main():
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=30)
    body = json.dumps({"query": QUERY, "variables": {
        "login": LOGIN, "from": since.strftime("%Y-%m-%dT%H:%M:%SZ")}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=body,
        headers={"Authorization": f"bearer {token()}", "Content-Type": "application/json",
                 "User-Agent": "profile-readme-stats"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            u = json.load(r)["data"]["user"]
    except Exception as e:  # giữ số liệu cũ nếu lỗi
        print("fetch lỗi, giữ stats.json cũ:", e, file=sys.stderr)
        return

    days = [d for w in u["recent"]["contributionCalendar"]["weeks"] for d in w["contributionDays"]
            if d["date"] >= since.strftime("%Y-%m-%d")]
    active = sum(1 for d in days if d["contributionCount"] > 0)
    repos = u["repositories"]["nodes"]
    touched = sum(1 for n in repos if n["pushedAt"] and
                  datetime.fromisoformat(n["pushedAt"].replace("Z", "+00:00")) >= since)
    stats = {
        "login": LOGIN,
        "updated": now.strftime("%Y-%m-%d"),
        "commits30": u["recent"]["totalCommitContributions"],
        "active_days30": active,
        "public_repos": u["repositories"]["totalCount"],
        "repos_touched30": touched,
        "year_contributions": u["year"]["contributionCalendar"]["totalContributions"],
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(stats, indent=2) + "\n")
    print(stats)


main()
