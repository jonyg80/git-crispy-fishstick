import xml.etree.ElementTree as ET
import os

# Parse the XML file
tree = ET.parse('android.xml')
root = tree.getroot()

# Find all project elements and extract their names
project_names = [p.get('name') for p in root.findall('project')]

# Print the list of project names
# print(project_names)

minute = 0
hour = 0

# Create yml files using project names as variable
for repo_name in project_names:
    # change / to _ in repo_name
    file_name = repo_name.replace('/', '_')
    with open(file_name + '.yml', 'w', encoding='utf-8') as f:
        f.write(f'''name: {repo_name} Clone and Push

on:
  schedule:
    - cron: '{minute} {hour} * * *' # Runs every day

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout
      uses: actions/checkout@v2

    - name: Git clone
      run: git clone --mirror https://android.googlesource.com/{repo_name} {repo_name}

    - name: Push
      run: |
        cd {repo_name}
        git config --global user.email "you@example.com"
        git config --global user.name "Your Name"
        git push --mirror https://${{{{ secrets.GitURL }}}}/{repo_name}.git''')
    # Increment minute and hour

    if minute >=59 and hour >= 23:
        minute = 0
        hour = 0
    elif minute >= 59:
      minute = 0
      hour += 1
    else:
        minute += 1




# Print confirmation message
print('Text files created successfully!')