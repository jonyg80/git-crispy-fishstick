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
day = 1

def create_matrix_array(project_names, start):
  matrix_array = []
  for j in range(start, start+10):
    matrix_array.append(project_names[j])
    if j == len(project_names)-1:
      break

  return matrix_array


# Create yml files using project names as variable
# for repo_name in project_names:
for i in range(0, len(project_names), 10):
    # change / to _ in repo_name
    # file_name = repo_name.replace("/", "_")
    with open(".github/workflows/"+ str(i) + ".yml", "w", encoding="utf-8") as f:
        f.write(
            f"""name: {i} Clone and Push

on:
  schedule:
    - cron: '0 {hour} {day} * *' # Runs monthly, every 2 hours, incrementing day when hour resets
  workflow_dispatch:



jobs:
  build:
    runs-on: ubuntu-latest
    continue-on-error: true
    strategy:
      max-parallel: 1
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

      - name: Increase Git buffer size
        run: git config --global http.postBuffer 157286400

      - name: Push with retry
        run: |
          cd ${{{{ matrix.repo_name }}}}
          git config --global user.email "you@example.com"
          git config --global user.name "Your Name"
          for i in {{1..3}}; do
            git push --mirror https://${{{{ secrets.GitUsername }}}}:${{{{ secrets.GitToken }}}}@${{{{ secrets.GitURL }}}}/${{{{ matrix.repo_name }}}}.git && break || sleep 30;
          done

      - name: Notify Slack on failure
        if: failure()
        uses: slackapi/slack-github-action@v2
        with:
          webhook: ${{{{ secrets.SLACK_WEBHOOK_URL }}}}
          webhook-type: incoming-webhook
          payload: |
            text: "❌ GitHub Actions Workflow Failed"
            blocks:
              - type: section
                text:
                  type: mrkdwn
                  text: "*Workflow Failure Details:*"
              - type: section
                text:
                  type: mrkdwn
                  text: "Job *${{{{ github.job }}}}* failed in workflow *${{{{ github.workflow }}}}*"
                fields:
                  - type: mrkdwn
                    text: "*Repository*\n${{{{ github.repository }}}}"
                  - type: mrkdwn
                    text: "*Branch*\n${{{{ github.ref_name }}}}"
              - type: section
                text:
                  type: mrkdwn
                  text: "<${{{{ github.server_url }}}}/${{{{ github.repository }}}}/actions/runs/${{{{ github.run_id }}}}|View Job Details> :warning:"
""")

    # Increment hour by 2 for each workflow, reset to 0 if hour >= 24, and increment day
    hour += 2
    if hour >= 24:
        hour = 0
        day += 1

# Print confirmation message
print("Text files created successfully!")

