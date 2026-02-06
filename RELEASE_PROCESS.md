# Release Process for forge-cli

This document describes how to create and publish new releases of the forge-cli package.

## Prerequisites

Before creating a release, ensure:

1. **All tests pass** - CI must be green on main branch
2. **Version updated** - Update version in `pyproject.toml`
3. **Changelog updated** - Document changes in CHANGELOG.md (optional but recommended)
4. **PyPI credentials configured** - Set up trusted publishing (see below)

## PyPI Trusted Publishing Setup (One-Time)

Configure PyPI to accept releases from GitHub Actions:

1. Go to [PyPI](https://pypi.org/) and log in
2. Navigate to your account settings
3. Go to "Publishing" → "Add a new publisher"
4. Fill in the form:
   - **PyPI Project Name**: `forge-cli`
   - **Owner**: `jpoutrin`
   - **Repository name**: `product-forge`
   - **Workflow name**: `release.yml`
   - **Environment name**: (leave blank)

This allows GitHub Actions to publish without API tokens using OIDC authentication.

## Release Steps

### 1. Update Version

Edit `pyproject.toml`:

```toml
[project]
name = "forge-cli"
version = "0.3.0"  # Update this
```

### 2. Create Changelog Entry (Optional)

Create or update `CHANGELOG.md`:

```markdown
## [0.3.0] - 2026-02-06

### Added
- GitHub Actions CI/CD workflow
- Code quality tools (ruff, mypy)
- Comprehensive test suite

### Fixed
- Type checking non-blocking in CI

### Changed
- Updated dependencies
```

### 3. Commit and Push

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore(release): bump version to 0.3.0"
git push origin main
```

### 4. Create and Push Tag

```bash
# Create annotated tag
git tag -a v0.3.0 -m "Release version 0.3.0"

# Push tag to trigger release workflow
git push origin v0.3.0
```

### 5. Monitor Release

The release workflow will automatically:

1. ✅ Build the package (`uv build`)
2. ✅ Publish to PyPI
3. ✅ Create GitHub Release with auto-generated notes
4. ✅ Attach distribution files to release

Monitor progress at:
```
https://github.com/jpoutrin/product-forge/actions
```

## Release Workflow Details

The `.github/workflows/release.yml` workflow:

- **Trigger**: Pushing a tag matching `v*` (e.g., `v0.3.0`, `v1.0.0`)
- **Permissions**:
  - `contents: write` - Create GitHub releases
  - `id-token: write` - OIDC authentication for PyPI
- **Steps**:
  1. Checkout code
  2. Install uv package manager
  3. Set up Python 3.12
  4. Build package (creates wheel and sdist in `dist/`)
  5. Publish to PyPI using trusted publishing
  6. Create GitHub release with auto-generated notes

## Versioning Scheme

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.3.0): New features, backward compatible
- **PATCH** (0.2.1): Bug fixes, backward compatible

## Testing a Release Locally

Before creating a real release, test the build:

```bash
# Build the package
uv build

# Check dist/ contents
ls -lh dist/

# Install locally to test
pip install dist/forge_cli-0.3.0-py3-none-any.whl

# Verify installation
forge --help
```

## PyPI Test Instance

For testing releases without publishing to production PyPI:

1. Create account at [TestPyPI](https://test.pypi.org/)
2. Update workflow to use TestPyPI:
   ```yaml
   - name: Publish to TestPyPI
     uses: pypa/gh-action-pypi-publish@release/v1
     with:
       repository-url: https://test.pypi.org/legacy/
   ```
3. Set up trusted publishing at TestPyPI

## Manual Release (Fallback)

If the automated workflow fails:

```bash
# Build package
uv build

# Publish manually (requires API token)
uv publish

# Or with twine
pip install twine
twine upload dist/*
```

## Troubleshooting

### "Project not found on PyPI"

**First release only**: You must manually create the project on PyPI:

```bash
# Register project (first time only)
uv publish --no-build
```

Or upload the first release manually through the PyPI web interface.

### "Invalid or non-existent authentication"

- Verify trusted publishing is configured correctly on PyPI
- Check repository name, owner, and workflow name match exactly
- Ensure workflow has `id-token: write` permission

### "Version already exists"

You cannot overwrite existing versions on PyPI. You must:

1. Delete the local tag: `git tag -d v0.3.0`
2. Delete the remote tag: `git push origin :refs/tags/v0.3.0`
3. Bump version in `pyproject.toml`
4. Create new tag with updated version

## Post-Release Checklist

After successful release:

- [ ] Verify package on PyPI: https://pypi.org/project/forge-cli/
- [ ] Test installation: `pip install forge-cli`
- [ ] Check GitHub release: https://github.com/jpoutrin/product-forge/releases
- [ ] Update documentation if needed
- [ ] Announce release (if applicable)

## Example Release Commands

```bash
# Complete release example
VERSION="0.3.0"

# Update version in pyproject.toml
sed -i '' "s/version = \".*\"/version = \"$VERSION\"/" pyproject.toml

# Commit version bump
git add pyproject.toml
git commit -m "chore(release): bump version to $VERSION"

# Create and push tag
git tag -a "v$VERSION" -m "Release version $VERSION"
git push origin main
git push origin "v$VERSION"

# Watch the release
open "https://github.com/jpoutrin/product-forge/actions"
```

## Security Notes

- **Never commit PyPI tokens** to the repository
- Use **trusted publishing** (OIDC) instead of API tokens when possible
- Regularly rotate any API tokens if used
- Review release notes before publishing
- Tag releases from the main branch only

## Release Automation Future Enhancements

Potential improvements:

1. **Automated version bumping** - Use bump2version or similar
2. **Changelog automation** - Generate from conventional commits
3. **Pre-release testing** - Deploy to TestPyPI first
4. **Release candidates** - Support rc1, rc2 tags
5. **Branch protection** - Require PR reviews before merging to main
