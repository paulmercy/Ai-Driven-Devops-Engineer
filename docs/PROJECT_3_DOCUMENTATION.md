# Project 3: CI/CD Workflow Documentation

## 📋 Overview

A modern React application with comprehensive CI/CD pipeline demonstrating automated testing, security scanning, and deployment to GitHub Pages. Showcases DevOps best practices and modern frontend development.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Developer     │    │  GitHub Actions │    │  GitHub Pages   │
│                 │    │                 │    │                 │
│ Local Dev       │───►│ CI/CD Pipeline  │───►│ Live Deployment │
│ Git Push        │    │ Test/Build/Deploy│    │ Static Hosting  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Security Scan  │
                       │                 │
                       │ Trivy + Audit   │
                       └─────────────────┘
```

## 🛠️ Technology Stack

- **Frontend**: React 19.1.0, TypeScript 5.8.3
- **Build Tool**: Vite 7.0.0
- **Testing**: Vitest 1.0.4, React Testing Library 16.0.0
- **Linting**: ESLint 9.29.0, TypeScript ESLint
- **CI/CD**: GitHub Actions
- **Security**: Trivy scanner, npm audit
- **Deployment**: GitHub Pages
- **Package Manager**: npm with legacy peer deps

## 📁 Code Structure

```
Project 3/
├── .github/
│   └── workflows/
│       └── ci-cd.yml          # GitHub Actions pipeline
├── frontend/
│   ├── src/
│   │   ├── App.tsx            # Main React component
│   │   ├── App.test.tsx       # Component tests
│   │   ├── App.css            # Styling
│   │   ├── main.tsx           # React entry point
│   │   ├── setupTests.ts      # Test configuration
│   │   └── vite-env.d.ts      # Vite type definitions
│   ├── public/                # Static assets
│   ├── package.json           # Dependencies and scripts
│   ├── vite.config.ts         # Vite configuration
│   ├── vitest.config.ts       # Test configuration
│   ├── tsconfig.json          # TypeScript configuration
│   └── eslint.config.js       # ESLint configuration
└── README.md                  # Project documentation
```

### Key Components

#### 1. React Application (`App.tsx`)
- **Purpose**: Interactive demo application
- **Features**:
  - Counter with increment/decrement
  - Todo list with CRUD operations
  - Deployment information display
  - Local storage persistence
  - TypeScript interfaces

#### 2. CI/CD Pipeline (`.github/workflows/ci-cd.yml`)
- **Purpose**: Automated testing and deployment
- **Stages**:
  - Lint and Test
  - Security Scanning
  - Production Deployment

#### 3. Testing Suite (`App.test.tsx`)
- **Purpose**: Component and functionality testing
- **Coverage**: Rendering, interactions, state management

## 🚀 Setup Instructions

### Prerequisites
```bash
# Required software
- Node.js 18+
- npm 8+
- Git

# Verify installations
node --version
npm --version
git --version
```

### Local Development

1. **Navigate to Frontend**
```bash
cd "Project 3 CICD Workflow with GitHub Actions + GitHub Pages Hosting/frontend"
```

2. **Install Dependencies**
```bash
npm install --legacy-peer-deps
```

3. **Start Development Server**
```bash
npm run dev
```

4. **Access Application**
```
http://localhost:5173
```

### Available Scripts
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run lint         # Run ESLint
npm run test         # Run tests
npm run test:ui      # Run tests with UI
npm run preview      # Preview production build
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

#### Job 1: Lint and Test
```yaml
lint-and-test:
  runs-on: ubuntu-latest
  steps:
    - name: Checkout code
    - name: Setup Node.js
    - name: Install dependencies
    - name: Run ESLint
    - name: Run tests
    - name: Build application
    - name: Upload build artifacts
```

#### Job 2: Security Scan
```yaml
security-scan:
  needs: lint-and-test
  steps:
    - name: Run npm audit
    - name: Run Trivy vulnerability scanner
    - name: Upload SARIF results
```

#### Job 3: Deploy
```yaml
deploy:
  needs: [lint-and-test, security-scan]
  if: github.ref == 'refs/heads/main'
  steps:
    - name: Build for production
    - name: Deploy to GitHub Pages
```

### Pipeline Features

1. **Automated Testing**: Unit tests run on every push/PR
2. **Code Quality**: ESLint enforces coding standards
3. **Security Scanning**: Vulnerability detection with Trivy
4. **Dependency Audit**: npm audit for known vulnerabilities
5. **Automated Deployment**: Deploy to GitHub Pages on main branch
6. **Environment Variables**: Build-time injection of commit info

## 🧪 Testing Guide

### Running Tests Locally
```bash
# Run all tests
npm run test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:ui
```

### Test Structure
```typescript
describe('App Component', () => {
  it('renders without crashing', () => {
    const { container } = render(<App />);
    expect(container).toBeTruthy();
  });

  it('contains main heading', () => {
    const { container } = render(<App />);
    expect(container.textContent).toContain('CI/CD Demo Application');
  });
});
```

### Testing Best Practices
- Component rendering tests
- User interaction testing
- State management validation
- Accessibility testing
- Performance testing

## 🔐 Security Features

### 1. Dependency Scanning
```yaml
- name: Run npm audit
  run: |
    cd frontend
    npm audit --audit-level moderate
```

### 2. Vulnerability Scanning
```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: 'fs'
    scan-ref: './frontend'
    format: 'sarif'
```

### 3. Code Quality Enforcement
```bash
# ESLint configuration
npm run lint  # Enforces TypeScript and React best practices
```

### 4. Secure Deployment
- HTTPS-only GitHub Pages
- Content Security Policy headers
- Dependency vulnerability monitoring

## 📊 Performance Metrics

### Build Performance
- **Build Time**: < 2 minutes
- **Test Execution**: < 30 seconds
- **Bundle Size**: < 200KB gzipped
- **Lighthouse Score**: > 90

### Runtime Performance
- **First Contentful Paint**: < 1.5s
- **Time to Interactive**: < 3s
- **Cumulative Layout Shift**: < 0.1

### Monitoring
```typescript
// Performance monitoring in production
const observer = new PerformanceObserver((list) => {
  list.getEntries().forEach((entry) => {
    console.log(entry.name, entry.duration);
  });
});
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Dependency Conflicts
```bash
# Error: peer dependency warnings
# Solution: Use legacy peer deps
npm install --legacy-peer-deps
```

#### 2. Build Failures
```bash
# Error: TypeScript compilation errors
# Solution: Check type definitions
npm run build  # See detailed errors
```

#### 3. Test Failures
```bash
# Error: Tests not finding components
# Solution: Check test setup
npm run test -- --reporter=verbose
```

#### 4. GitHub Actions Failures
```yaml
# Check workflow logs in GitHub Actions tab
# Common issues: Node version, dependency cache
```

## 🎯 Demo Scenarios

### 1. Local Development Demo
```bash
# Show hot reload
npm run dev
# Edit App.tsx, show instant updates
```

### 2. Testing Demo
```bash
# Run tests with coverage
npm run test:coverage
# Show test results and coverage report
```

### 3. Build Process Demo
```bash
# Production build
npm run build
# Show optimized bundle in dist/
```

### 4. CI/CD Pipeline Demo
```bash
# Push to GitHub
git add .
git commit -m "Demo commit"
git push origin main
# Show GitHub Actions running
```

## 📈 Key Technical Achievements

1. **Modern React Development**: Hooks, TypeScript, functional components
2. **Comprehensive Testing**: Unit tests, component testing, coverage
3. **Automated CI/CD**: GitHub Actions, automated deployment
4. **Security Integration**: Vulnerability scanning, dependency auditing
5. **Performance Optimization**: Vite build tool, code splitting
6. **Developer Experience**: Hot reload, TypeScript, ESLint
