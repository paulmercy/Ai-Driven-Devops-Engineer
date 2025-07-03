# CI/CD Demo Application

This project demonstrates a complete CI/CD pipeline using GitHub Actions and GitHub Pages hosting.

## 🚀 Features

- **React + TypeScript** - Modern frontend development
- **Automated Testing** - Unit tests with Vitest and React Testing Library
- **Code Quality** - ESLint for code linting
- **Security Scanning** - Vulnerability scanning with Trivy
- **Automated Deployment** - Deploy to GitHub Pages on every push to main
- **Environment Variables** - Build-time injection of commit hash and build time

## 🛠️ Local Development

### Prerequisites
- Node.js 18 or higher
- npm

### Setup
```bash
cd frontend
npm install
npm run dev
```

### Available Scripts
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run lint` - Run ESLint
- `npm run test` - Run tests
- `npm run test:ui` - Run tests with UI
- `npm run preview` - Preview production build

## 🔄 CI/CD Pipeline

The GitHub Actions workflow includes:

### 1. **Lint and Test** Job
- Code checkout
- Node.js setup with caching
- Dependency installation
- ESLint code linting
- Unit test execution
- Production build
- Artifact upload

### 2. **Security Scan** Job
- npm audit for dependency vulnerabilities
- Trivy filesystem scanning
- SARIF report upload to GitHub Security tab

### 3. **Deploy** Job (main branch only)
- Production build with environment variables
- GitHub Pages deployment
- Automatic URL generation

## 📦 Deployment

The application is automatically deployed to GitHub Pages when code is pushed to the main branch.

**Live Demo**: [Your GitHub Pages URL will appear here]

## 🧪 Testing

The project includes comprehensive tests for:
- Component rendering
- User interactions
- State management
- Todo functionality

Run tests locally:
```bash
cd frontend
npm run test
```

## 🔒 Security

- Automated dependency vulnerability scanning
- Code quality enforcement
- Security-focused CI/CD pipeline

## 📊 Pipeline Status

Check the Actions tab in GitHub to see:
- ✅ Build status
- ✅ Test results
- ✅ Security scan results
- ✅ Deployment status

## 🎯 Demo Features

The deployed application demonstrates:
- Interactive counter with increment/decrement
- Todo list with add/toggle/delete functionality
- Real-time deployment information display
- Responsive design
- Local storage persistence
