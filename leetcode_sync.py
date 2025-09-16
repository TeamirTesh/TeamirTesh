import requests, json, datetime, os

USERNAME = "TeamirT"

# --- Ensure folders exist ---
os.makedirs("solutions", exist_ok=True)

# --- Safe API fetch ---
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
try:
    res = requests.post("https://leetcode.com/graphql", json={"query": query})
    data = res.json()["data"]["matchedUser"]
except Exception as e:
    print("Error fetching from LeetCode API:", e)
    data = None

# --- Save progress if data exists ---
if data:
    with open("progress.json", "w") as f:
        json.dump(data["submitStatsGlobal"], f, indent=2)

    # Daily log
    with open("daily_log.txt", "a") as f:
        f.write(f"{datetime.date.today()} - Synced LeetCode progress\n")

    # Create placeholder for most recent solution
    recent = data.get("recentSubmissionList", [])
    if recent:
        sub = recent[0]
        filename = f"solutions/{sub['title'].replace(' ', '_')}.py"
        with open(filename, "w") as f:
            f.write(f"# {sub['title']} (status: {sub['statusDisplay']})\n# TODO: Add code\n")
