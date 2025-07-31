#!/usr/bin/env python3
"""Release automation script for mkdocs-llms-txt - Local build with GitHub Actions publishing."""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, check=check)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result


def main():
    """Local build and release preparation workflow."""
    print("🚀 Starting mkdocs-llms-txt local build process...")

    # Ensure we're in the project root
    project_root = Path(__file__).parent.parent

    print("\n🔍 Pre-flight checks...")
    try:
        # Check if PDM is available
        run_command(["pdm", "--version"], check=True)

        # Install dependencies
        print("📦 Installing dependencies...")
        run_command(["pdm", "install"], check=True)

        # Run linting
        print("🔍 Running linting...")
        run_command(["pdm", "run", "ruff", "check"], check=True)
        run_command(["pdm", "run", "ruff", "format", "--check"], check=True)

        # Test plugin installation
        print("🧪 Testing plugin installation...")
        run_command(["pdm", "install", "-e", "."], check=True)

        # Test with example site
        print("🏗️  Testing with example site...")
        run_command(["pdm", "run", "mkdocs", "build"], check=True)

        # Verify expected files exist
        site_dir = project_root / "test-site" / "site"
        required_files = [
            "llms.txt",
            "llms-full.txt",
            "index.md",
            "quickstart/index.md",
        ]
        for file in required_files:
            file_path = site_dir / file
            if not file_path.exists():
                raise FileNotFoundError(f"Required file not found: {file}")
        print("✅ All tests passed!")

    except subprocess.CalledProcessError as e:
        print(f"❌ Pre-flight checks failed: {e}")
        return 1
    except FileNotFoundError as e:
        print(f"❌ Test validation failed: {e}")
        return 1

    print("\n📦 Building package...")
    try:
        # Clean previous builds
        build_dirs = [project_root / "dist", project_root / "build"]
        for build_dir in build_dirs:
            if build_dir.exists():
                import shutil

                shutil.rmtree(build_dir)
                print(f"Cleaned {build_dir}")

        # Build with PDM
        run_command(["pdm", "build"], check=True)
        print("✅ Package built successfully!")

    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return 1

    print("\n📋 Built files:")
    dist_dir = project_root / "dist"
    if dist_dir.exists():
        for file in dist_dir.iterdir():
            print(f"  - {file.name}")

    print("\n🎯 RECOMMENDED: Use GitHub Actions for Publishing")
    print("=" * 50)
    print("For maximum security, use GitHub Actions with Trusted Publishing:")
    print()
    print("1. 🧪 Test on TestPyPI:")
    print("   gh workflow run release.yml -f upload_to_pypi=false")
    print()
    print("2. ✅ Test installation:")
    print("   pip install -i https://test.pypi.org/simple/ mkdocs-llms-txt")
    print()
    print("3. 🚀 Release to PyPI (creates tag automatically):")
    print("   git tag v0.1.0 && git push origin v0.1.0")
    print()
    print("4. 🏷️  Or manual trigger:")
    print("   gh workflow run release.yml -f upload_to_pypi=true")

    print("\n📝 Alternative: Manual Publishing (less secure)")
    print("=" * 50)
    print("If you prefer manual publishing (requires API tokens):")
    print("1. pdm publish --repository testpypi  # Test first")
    print("2. pdm publish                        # Then production")

    print("\n🔧 Setup Required:")
    print("- Configure PyPI Trusted Publisher (see TRUSTED_PUBLISHING.md)")
    print("- Set up GitHub environments: 'testpypi' and 'pypi'")
    print("- Install GitHub CLI: brew install gh")

    return 0


if __name__ == "__main__":
    sys.exit(main())
