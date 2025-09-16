import requests, json, datetime, os

USERNAME = "TeamirT" 

# GraphQL query: fetch submission stats + most recent submission
query = f"""
{{
  matchedUser(username: "{USERNAME}") {{
    submitStatsGlobal {{
      acSubmissionNum {{
        difficulty
        count
      }}
    }}
    recentSubmissionList(limit: 1) {{
      title
      titleSlug
      timestamp
      lang
      statusDisplay
    }}
  }}
}}
"""

res = requests.post("https://leetcode.com/graphql", json={"query": query})
data = res.json()["data"]["matchedUser"]

# --- Save global progress ---
with open("progress.json", "w") as f:
    json.dump(data["submitStatsGlobal"], f, indent=2)

# --- Save most recent solution (stub file) ---
if data["recentSubmissionList"]:
    submission = data["recentSubmissionList"][0]
    title = submission["title"].replace(" ", "_")  # filename friendly
    lang = submission["lang"].lower()
    ext_map = {
        "python3": "py",
        "cpp": "cpp",
        "java": "java",
        "c": "c"
    }
    ext = ext_map.get(lang, "txt")
    filename = f"solutions/{title}.{ext}"

    os.makedirs("solutions", exist_ok=True)

    with open(filename, "w") as f:
        f.write(f"# {submission['title']}\n")
        f.write(f"# Solved on {datetime.date.today()}\n")
        f.write(f"# Status: {submission['statusDisplay']}\n\n")
        f.write("# TODO: Insert actual code (LeetCode API doesn’t return full code)\n")

# --- Keep daily log for commit activity ---
with open("daily_log.txt", "a") as f:
    f.write(f"{datetime.date.today()} - Synced LeetCode progress, latest: {submission['title']}\n")


# Update Leetcode Stats in ReadMe
with open("progress.json") as f:
    stats = json.load(f)

# total problems solved
total_solved = sum([item['count'] for item in stats['acSubmissionNum']])

# recent solutions
solution_files = os.listdir("solutions")
solution_files.sort(reverse=True)
recent_files = solution_files[:5]  # show last 5
recent_links = "\n".join([f"- [{file}](solutions/{file})" for file in recent_files])

# read current README
with open("README.md", "r") as f:
    readme = f.read()

# replace placeholders
readme = readme.replace("SOLVED_COUNT", str(total_solved))
readme = readme.replace("RECENT_SOLUTIONS", recent_links)

# write updated README
with open("README.md", "w") as f:
    f.write(readme)

