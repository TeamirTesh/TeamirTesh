import requests
import json
import datetime
import os

# --- CONFIG ---
USERNAME = "TeamirT"
SOLUTIONS_DIR = "solutions"
README_FILE = "README.md"

# --- Ensure folders exist ---
os.makedirs(SOLUTIONS_DIR, exist_ok=True)

# --- GraphQL query for LeetCode stats ---
query = f'''
{{
  matchedUser(username: "{USERNAME}") {{
    submitStatsGlobal {{
      acSubmissionNum {{
        difficulty
        count
      }}
    }}
  }}
}}
'''


# --- Headers to make LeetCode treat this as a browser request ---
headers = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json",
}

# --- Fetch LeetCode data safely ---
data = None
try:
    res = requests.post("https://leetcode.com/graphql", headers=headers, json={"query": query})
    res.raise_for_status()
    
    try:
        response_json = res.json()
    except json.JSONDecodeError:
        print("LeetCode returned non-JSON response:")
        print(res.text)
    else:
        data = response_json.get("data", {}).get("matchedUser")
        if not data:
            print("No matchedUser found in API response:", response_json)
except Exception as e:
    print("Error fetching LeetCode data:", e)

# --- Save progress if data exists ---
if data:
    # Save progress.json
    with open("progress.json", "w") as f:
        json.dump(data["submitStatsGlobal"], f, indent=2)

    # Update daily log
    with open("daily_log.txt", "a") as f:
        f.write(f"{datetime.date.today()} - Synced LeetCode progress\n")

    # Create placeholder files for recent solutions
    recent = data.get("recentSubmissionList", [])
    for sub in recent:
        filename = f"{SOLUTIONS_DIR}/{sub['title'].replace(' ', '_')}.py"
        if not os.path.exists(filename):
            with open(filename, "w") as f:
                f.write(f"# {sub['title']} (status: {sub['statusDisplay']})\n# TODO: Add code\n")

# --- Update README placeholders ---
if os.path.exists(README_FILE) and data:
    # Total problems solved
    total_solved = sum(item["count"] for item in data["submitStatsGlobal"]["acSubmissionNum"])

    # Recent solution links (last 5)
    solution_files = os.listdir(SOLUTIONS_DIR)
    solution_files.sort(reverse=True)
    recent_files = solution_files[:5]
    recent_links = "\n".join([f"- [{file}]({SOLUTIONS_DIR}/{file})" for file in recent_files])

    # Read and update README
    with open(README_FILE, "r") as f:
        readme = f.read()

    readme = readme.replace("SOLVED_COUNT", str(total_solved))
    readme = readme.replace("RECENT_SOLUTIONS", recent_links)

    with open(README_FILE, "w") as f:
        f.write(readme)

print("LeetCode sync complete.")
