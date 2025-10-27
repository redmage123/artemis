#!/usr/bin/env python3
"""
Clone Missing GitHub Repositories and Upload to RAG

Compares GitHub repos with local repos and clones missing ones.
"""

import json
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Set

# Paths
GITHUB_REPOS_JSON = '/tmp/github_repos.json'
LOCAL_REPOS_DIR = Path('/home/bbrelin/src/repos')
CLONE_LOG = '/tmp/clone_repos.log'


def get_local_repo_names() -> Set[str]:
    """Get set of local repository directory names"""
    if not LOCAL_REPOS_DIR.exists():
        return set()

    local_repos = set()
    for item in LOCAL_REPOS_DIR.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            # Normalize names
            local_repos.add(item.name.lower())

    return local_repos


def get_github_repos() -> List[Dict]:
    """Load GitHub repositories from JSON file"""
    with open(GITHUB_REPOS_JSON, 'r') as f:
        return json.load(f)


def find_missing_repos(github_repos: List[Dict], local_repos: Set[str]) -> List[Dict]:
    """Find repos that exist on GitHub but not locally"""
    missing = []

    for repo in github_repos:
        repo_name = repo['name'].lower()

        # Skip private repos
        if repo['isPrivate']:
            print(f"⏭️  Skipping private repo: {repo['name']}")
            continue

        # Skip forks (usually not original content)
        if repo['isFork']:
            print(f"⏭️  Skipping fork: {repo['name']}")
            continue

        # Check if missing locally
        if repo_name not in local_repos:
            missing.append(repo)

    return missing


def clone_repository(repo: Dict, target_dir: Path) -> bool:
    """Clone a single repository"""
    repo_name = repo['name']
    ssh_url = repo['sshUrl']
    target_path = target_dir / repo_name

    print(f"\n{'='*70}")
    print(f"📥 Cloning: {repo_name}")
    print(f"   URL: {ssh_url}")
    print(f"   Target: {target_path}")
    print(f"{'='*70}")

    try:
        # Clone with depth=1 for faster cloning (shallow clone)
        result = subprocess.run(
            ['git', 'clone', '--depth', '1', ssh_url, str(target_path)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode == 0:
            print(f"✅ Successfully cloned: {repo_name}")
            return True
        else:
            print(f"❌ Failed to clone {repo_name}: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print(f"❌ Timeout cloning {repo_name}")
        return False
    except Exception as e:
        print(f"❌ Error cloning {repo_name}: {e}")
        return False


def main():
    """Main execution"""
    print("\n" + "="*70)
    print("CLONE MISSING GITHUB REPOSITORIES")
    print("="*70)

    # Load data
    print("\n📊 Loading repository lists...")
    github_repos = get_github_repos()
    local_repos = get_local_repo_names()

    print(f"   GitHub repositories: {len(github_repos)}")
    print(f"   Local repositories: {len(local_repos)}")

    # Find missing
    print("\n🔍 Finding missing repositories...")
    missing_repos = find_missing_repos(github_repos, local_repos)

    print(f"\n📋 Found {len(missing_repos)} repositories to clone:")
    for repo in missing_repos:
        print(f"   - {repo['name']} (updated: {repo['updatedAt'][:10]})")

    if not missing_repos:
        print("\n✅ All repositories are already cloned!")
        return

    # Auto-proceed (no user confirmation needed)
    print(f"\n🚀 Proceeding to clone {len(missing_repos)} repositories to {LOCAL_REPOS_DIR}")

    # Clone repositories
    print("\n🚀 Starting clone operations...")
    cloned = []
    failed = []

    for i, repo in enumerate(missing_repos, 1):
        print(f"\n[{i}/{len(missing_repos)}]", end=' ')
        if clone_repository(repo, LOCAL_REPOS_DIR):
            cloned.append(repo['name'])
        else:
            failed.append(repo['name'])

    # Summary
    print("\n" + "="*70)
    print("CLONE SUMMARY")
    print("="*70)
    print(f"✅ Successfully cloned: {len(cloned)}")
    print(f"❌ Failed: {len(failed)}")

    if cloned:
        print("\n📁 Cloned repositories:")
        for name in cloned:
            print(f"   ✓ {name}")

    if failed:
        print("\n❌ Failed repositories:")
        for name in failed:
            print(f"   ✗ {name}")

    print("\n💾 Clone log saved to:", CLONE_LOG)
    print("="*70)

    # Save results
    with open(CLONE_LOG, 'w') as f:
        f.write(f"Cloned: {len(cloned)}\n")
        f.write(f"Failed: {len(failed)}\n\n")
        f.write("Cloned repositories:\n")
        for name in cloned:
            f.write(f"  {name}\n")
        if failed:
            f.write("\nFailed repositories:\n")
            for name in failed:
                f.write(f"  {name}\n")


if __name__ == "__main__":
    main()
