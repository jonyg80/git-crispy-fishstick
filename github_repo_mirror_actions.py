import xml.etree.ElementTree as ET
import os

# Parse the XML file
tree = ET.parse("manifest/default.xml")
root = tree.getroot()

# Find all project elements and extract their names
project_names = [p.get("name") for p in root.findall("project")]

# Print the list of project names
# print(project_names)


hour = 0
week = 0

def create_matrix_array(project_names, start):
  matrix_array = []
  for j in range(start, start+110):
    matrix_array.append(project_names[j])
    if j == len(project_names)-1:
      break

  return matrix_array


# Create yml files using project names as variable
# for repo_name in project_names:
for i in range(0,len(project_names),110):
    # change / to _ in repo_name
    # file_name = repo_name.replace("/", "_")
    with open(".github/workflows/"+ str(i) + ".yml", "w", encoding="utf-8") as f:
        f.write(
            f"""name: {i} Clone and Push

on:
  schedule:
    - cron: '0 {hour} * * *' # Runs every week
  workflow_dispatch:



jobs:
  build:
    runs-on: ubuntu-latest
    continue-on-error: true
    strategy:
      max-parallel: 5
      matrix:
        repo_name: {create_matrix_array(project_names, i)}

    steps:
      - name: Maximize build space
        uses: easimon/maximize-build-space@master
        with:
          root-reserve-mb: 512
          swap-size-mb: 1024
          remove-dotnet: 'true'
          remove-haskell: 'true'
          remove-android: 'true'
          
      - name: Checkout
        uses: actions/checkout@v4

      - name: Git clone
        run: git clone --mirror https://android.googlesource.com/${{{{ matrix.repo_name }}}} ${{{{ matrix.repo_name }}}}

      - name: Push
        run: |
          cd ${{{{ matrix.repo_name }}}}
          git config --global user.email "you@example.com"
          git config --global user.name "Your Name"
          git push --mirror https://${{{{ secrets.GitUsername }}}}:${{{{ secrets.GitToken }}}}@${{{{ secrets.GitURL }}}}/${{{{ matrix.repo_name }}}}.git
""")

    # # Increment hour and week
    # if hour >= 23 and week >= 6:
    #     hour = 0
    #     week = 0
    # elif hour >= 23:
    #     hour = 0
    #     week += 1
    # else:
    #     hour += 1

    if hour >= 23:
      hour = 0
    else:
      hour += 1


# Print confirmation message
print("Text files created successfully!")

