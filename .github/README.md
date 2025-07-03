# GitHub Actions CI/CD Setup

This repository contains comprehensive GitHub Actions workflows for the AI-Driven DevOps Engineer projects.

## 🚀 Available Workflows

### 1. **Main CI/CD Pipeline** (`main-ci-cd.yml`)
- **Triggers**: Push to main/develop, Pull Requests, Manual dispatch
- **Purpose**: Orchestrates all project workflows based on changes detected
- **Features**:
  - Automatic change detection
  - Manual project selection
  - Parallel execution
  - Comprehensive summary

### 2. **Project 2 - AI Web App** (`project2-ci-cd.yml`)
- **Triggers**: Changes to Project 2 directory, Manual dispatch
- **Features**:
  - Python dependency installation
  - C++ extension building with pybind11
  - FastAPI application testing
  - Security scanning with bandit
  - Docker image building and testing

### 3. **Project 3 - CI/CD Demo** (`project3-ci-cd.yml`)
- **Triggers**: Changes to Project 3 directory, Manual dispatch
- **Features**:
  - React + TypeScript building
  - ESLint code quality checks
  - Unit testing with Vitest
  - Security scanning with Trivy
  - **GitHub Pages deployment** (main branch only)

### 4. **Project 5 - DevSecOps Dashboard** (`project5-ci-cd.yml`)
- **Triggers**: Changes to Project 5 directory, Manual dispatch
- **Features**:
  - Docker Compose validation
  - FastAPI application testing
  - Prometheus/Grafana configuration validation
  - Security scanning
  - Integration testing with Docker stack

## 🎯 How to Trigger Workflows

### Automatic Triggers
Workflows automatically run when you:
1. **Push to main or develop branch**
2. **Create a Pull Request to main**
3. **Make changes to specific project directories**

### Manual Triggers
You can manually trigger workflows from GitHub:
1. Go to **Actions** tab in your repository
2. Select the workflow you want to run
3. Click **"Run workflow"**
4. Choose options (for main workflow, select specific project)

## 📋 Setup Requirements

### Repository Settings
1. **Enable GitHub Actions** in repository settings
2. **Enable GitHub Pages** for Project 3 deployment:
   - Go to Settings → Pages
   - Source: GitHub Actions
   - No additional configuration needed

### Secrets (if needed)
Add these secrets in repository settings if using external services:
- `OPENAI_API_KEY` (for Project 2 AI features)
- `GEMINI_API_KEY` (for Project 2 Gemini support)

### Permissions
The workflows require these permissions (automatically granted):
- `contents: read` - Read repository content
- `pages: write` - Deploy to GitHub Pages (Project 3)
- `id-token: write` - GitHub Pages deployment
- `security-events: write` - Upload security scan results

## 🔄 Workflow Execution Flow

### Main Workflow (`main-ci-cd.yml`)
```
1. Detect Changes → 2. Run Project Workflows → 3. Generate Summary
                     ├── Project 2 (if changed)
                     ├── Project 3 (if changed)
                     └── Project 5 (if changed)
```

### Individual Project Workflows
```
Project 2: Test → Security Scan → Docker Build
Project 3: Lint/Test → Security Scan → Deploy to Pages
Project 5: Validate → Security Scan → Integration Test
```

## 📊 Monitoring and Results

### GitHub Actions Tab
- View all workflow runs
- See detailed logs for each step
- Download artifacts (build files, security reports)

### GitHub Pages (Project 3)
- Automatic deployment URL in workflow summary
- Live demo accessible after successful deployment

### Security Tab
- SARIF reports from Trivy scans
- Vulnerability alerts and recommendations

## 🛠️ Customization

### Adding New Projects
1. Create new workflow file: `.github/workflows/projectX-ci-cd.yml`
2. Update `main-ci-cd.yml` to include the new project
3. Add path detection logic

### Modifying Triggers
Edit the `on:` section in workflow files:
```yaml
on:
  push:
    branches: [ main, develop ]
    paths: [ 'your-project-path/**' ]
  workflow_dispatch:
```

### Environment Variables
Add environment variables in workflow steps:
```yaml
env:
  NODE_ENV: production
  CUSTOM_VAR: value
```

## 🔧 Troubleshooting

### Common Issues
1. **Workflow not triggering**: Check path filters and branch names
2. **Permission errors**: Verify repository settings and workflow permissions
3. **Build failures**: Check logs in Actions tab for specific error messages
4. **GitHub Pages not deploying**: Ensure Pages is enabled and workflow has correct permissions

### Debug Tips
- Use `workflow_dispatch` for manual testing
- Add debug steps with `echo` commands
- Check artifact uploads for build outputs
- Review security scan results for vulnerabilities

## 📈 Best Practices

1. **Keep workflows focused**: Each project has its own workflow
2. **Use caching**: Node.js and Python dependencies are cached
3. **Parallel execution**: Independent jobs run in parallel
4. **Security first**: All projects include security scanning
5. **Artifact management**: Important files are uploaded as artifacts
6. **Clear naming**: Workflows and jobs have descriptive names
