# Release Instructions

## 🎯 Recommended: GitHub Actions with Trusted Publishing

**This is the most secure and modern approach for 2024.**

### Prerequisites

1. **Set up Trusted Publishing** (one-time setup):
   - Follow the complete guide in [`TRUSTED_PUBLISHING.md`](TRUSTED_PUBLISHING.md)
   - Configure PyPI and TestPyPI trusted publishers
   - Set up GitHub environments for additional security

2. **Install required tools:**
   ```bash
   # For local development and testing
   pip install pdm
   pip install gh  # GitHub CLI for manual workflow triggers
   ```

### Release Workflow

#### 1. Prepare Release Locally

```bash
# Run comprehensive pre-flight checks and build
python scripts/release.py
```

This script will:
- ✅ Run all linting and formatting checks
- ✅ Test plugin installation and functionality  
- ✅ Build packages with PDM
- ✅ Validate all required files are generated

#### 2. Test on TestPyPI

```bash
# Trigger TestPyPI release via GitHub Actions
gh workflow run release.yml -f upload_to_pypi=false
```

#### 3. Verify TestPyPI Installation

```bash
# Test installation from TestPyPI
pip install -i https://test.pypi.org/simple/ mkdocs-llmstxt-md==0.1.0

# Quick functionality test
mkdir test-install && cd test-install
echo "site_name: Test
plugins:
  - llms-txt:
      sections:
        'Test': ['*.md']
" > mkdocs.yml

mkdir docs && echo "# Test Content" > docs/index.md
mkdocs build

# Verify outputs
ls site/  # Should contain: llms.txt, llms-full.txt, index.md
```

#### 4. Release to Production

**Option A: Automatic (Recommended)**
```bash
# Create and push tag - triggers automatic PyPI release
git tag v0.1.0
git push origin v0.1.0
```

**Option B: Manual Trigger**
```bash
# Manual workflow trigger for PyPI
gh workflow run release.yml -f upload_to_pypi=true
```

## 🔧 Alternative: Manual Release (Less Secure)

If you prefer manual publishing with PDM:

### Prerequisites
```bash
# Set up PDM with PyPI credentials
pdm config pypi.username __token__
pdm config pypi.password your-pypi-api-token
pdm config repository.testpypi.username __token__  
pdm config repository.testpypi.password your-testpypi-api-token
```

### Release Steps
```bash
# 1. Build and test locally
python scripts/release.py

# 2. Upload to TestPyPI
pdm publish --repository testpypi

# 3. Test installation
pip install -i https://test.pypi.org/simple/ mkdocs-llms-txt==0.1.0

# 4. Upload to PyPI
pdm publish

# 5. Create Git tag
git tag v0.1.0 && git push origin v0.1.0
```

## 📋 Release Checklist

- [ ] **Pre-Release**
  - [ ] Update version in `pyproject.toml`
  - [ ] Update `CHANGELOG.md` with new features/fixes
  - [ ] Run `python scripts/release.py` (validates everything)
  - [ ] Commit and push changes

- [ ] **Testing**
  - [ ] Release to TestPyPI: `gh workflow run release.yml -f upload_to_pypi=false`
  - [ ] Test installation from TestPyPI
  - [ ] Verify plugin functionality with test project

- [ ] **Production Release**
  - [ ] Create and push Git tag: `git tag v0.1.0 && git push origin v0.1.0`
  - [ ] Verify PyPI release completed successfully
  - [ ] Test installation from PyPI: `pip install mkdocs-llmstxt-md`
  - [ ] Update GitHub release notes (created automatically)

- [ ] **Post-Release**
  - [ ] Announce release (social media, forums, etc.)
  - [ ] Update documentation if needed
  - [ ] Plan next version features

## 🔐 Security Features

The GitHub Actions workflow includes:

- **🔒 Trusted Publishing**: No long-lived API tokens required
- **📝 Digital Attestations**: Automatic Sigstore signatures
- **🛡️ Environment Protection**: Manual approval for production releases
- **🏗️ Isolated Build/Publish**: Separate jobs for security
- **📦 Artifact Storage**: Build artifacts stored securely between jobs

## 📁 Configuration Files

- `scripts/release.py` - Local build and validation script
- `.github/workflows/release.yml` - Trusted publishing workflow
- `.github/workflows/ci.yml` - Continuous integration
- `TRUSTED_PUBLISHING.md` - Detailed setup guide
- `pyproject.toml` - Package configuration
- `CHANGELOG.md` - Version history

## 🆘 Troubleshooting

### Common Issues

1. **Workflow fails with "OIDC token verification failed"**
   - Check trusted publisher configuration in PyPI matches repository details
   - Verify GitHub environment names match PyPI settings

2. **"Package already exists" error**
   - Version already published - increment version number
   - For TestPyPI, this is usually safe to ignore

3. **Tests fail in GitHub Actions**
   - Run `python scripts/release.py` locally first
   - Check that all dependencies are properly specified

### Getting Help

- Check GitHub Actions logs for detailed error messages
- Review [TRUSTED_PUBLISHING.md](TRUSTED_PUBLISHING.md) for setup issues
- Verify PyPI trusted publisher configuration
- Test locally with `python scripts/release.py`

## 🚀 Why This Approach?

- **Security**: Trusted publishing is the 2024 gold standard
- **Automation**: Reduces human error and manual steps
- **Validation**: Comprehensive testing before any publication
- **Flexibility**: Local development with PDM, secure publishing with GitHub Actions
- **Modern**: Uses latest Python packaging best practices