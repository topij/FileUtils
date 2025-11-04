# GitHub Actions Workflow Troubleshooting

If your workflow didn't trigger, check these common issues:

## 1. Verify GitHub Actions is Enabled
- Go to your repository: https://github.com/topij/FileUtils
- Click on **Settings** → **Actions** → **General**
- Ensure "Allow all actions and reusable workflows" is selected
- Check that "Workflow permissions" allows read and write permissions

## 2. Check Workflow File Location
The workflow file should be at:
```
.github/workflows/ci.yml
```

## 3. Verify Branch Name
The workflow triggers on pushes to `main` or `develop`. Make sure:
- Your default branch is `main` (not `master`)
- You pushed to the correct branch

## 4. Manual Trigger Test
You can manually trigger the workflow:
- Go to **Actions** tab in your repository
- Click on "CI" workflow
- Click "Run workflow" button
- Select branch and click "Run workflow"

## 5. Check Workflow Syntax
The workflow file should be valid YAML. Common issues:
- Indentation (must be spaces, not tabs)
- Missing quotes around special characters
- Invalid expressions in conditional statements

## 6. Push a New Commit
Sometimes workflows need a fresh push to trigger:
```bash
git commit --allow-empty -m "Trigger CI workflow"
git push
```

## 7. Check Repository Settings
- Ensure GitHub Actions is not disabled for your repository
- Check if there are any branch protection rules blocking workflows
- Verify you have push permissions to the repository

## Current Workflow Configuration
- Triggers on: push to `main` or `develop`, PRs to `main` or `develop`
- File location: `.github/workflows/ci.yml` ✅
- YAML syntax: Valid ✅

