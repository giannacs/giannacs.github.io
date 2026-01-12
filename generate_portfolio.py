import json
from pathlib import Path
from datetime import datetime
import pytz

utc_tz = pytz.utc
utc_time = datetime.now(utc_tz)

from jinja2 import Environment, FileSystemLoader

# Load JSON data
with Path("portfolio-christos.json").open(encoding="utf-8") as f:
    data = json.load(f)

# Add any extra context if needed
data["current_year"] = utc_time.year

# Compute resume file metadata if resume_url points to a local file
def _human_readable_size(num, suffix='B'):
    for unit in ['','K','M','G','T','P']:
        if num < 1024.0:
            return f"{num:.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}P{suffix}"

resume_url = data.get("resume_url")
if resume_url:
    resume_path = Path(resume_url.lstrip('/'))
    if resume_path.exists():
        st = resume_path.stat()
        # data["resume_file_size"] = _human_readable_size(st.st_size)
        data["resume_last_modified"] = datetime.fromtimestamp(st.st_mtime, utc_tz).strftime('%Y-%m-%d')
    else:
        # If path doesn't exist locally, leave metadata blank
        # data["resume_file_size"] = None
        data["resume_last_modified"] = None

if "social_links" in data:
    for link in data["social_links"]:
        if link.get("svg_path"):
            with Path(link["svg_path"]).open(encoding="utf-8") as svg_file:
                link["svg_data"] = svg_file.read()

# Set up Jinja environment
env = Environment(loader=FileSystemLoader("."), autoescape=True)
index_template = env.get_template("templates/index_template.html")
resume_template = env.get_template("templates/resume_template.html")

# Render the template with the data
html_output = index_template.render(**data)
resume_output = resume_template.render(**data)

# This is equivalent to...
# html_output = index_template.render(name=data["name"], label=data["label"]...)
# resume_output = resume_template.render(name=data["name"], label=data["label"]...)

# Write the output to an HTML file
with Path("index.html").open("w", encoding="utf-8") as f:
    f.write(html_output)

with Path("templates/resume.html").open("w", encoding="utf-8") as f:
    f.write(resume_output)

print("HTML file generated successfully!")
