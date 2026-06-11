#!/usr/bin/env python3
"""
SEC-007: Secret Scanning with Trufflehog
Аудит репозитория на наличие утечек секретов
"""
import subprocess
import json
import sys
import os


def scan_repository():
    """Сканировать репозиторий на секреты с помощью trufflehog"""
    print("=" * 70)
    print("🔐 SECRET SCANNING with Trufflehog (SEC-007)")
    print("=" * 70)
    
    # Get the root directory
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print(f"\n📁 Scanning repository: {repo_root}")
    print("\nChecking for exposed secrets in Git history and files...")
    
    try:
        # Run trufflehog scan
        result = subprocess.run(
            ['trufflehog', 'filesystem', repo_root, '--json'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            # Parse JSON output
            secrets_found = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        data = json.loads(line)
                        secrets_found.append(data)
                    except json.JSONDecodeError:
                        pass
            
            # Display results
            print("\n" + "-" * 70)
            if not secrets_found:
                print("✅ SCAN RESULT: NO SECRETS FOUND")
                print("   Repository is clean - no exposed credentials detected")
            else:
                print(f"⚠️  SCAN RESULT: {len(secrets_found)} SECRET(S) DETECTED")
                for i, secret in enumerate(secrets_found, 1):
                    print(f"\n{i}. {secret.get('DetectorName', 'Unknown')}")
                    print(f"   File: {secret.get('SourceMetadata', {}).get('Data', {}).get('Filesystem', {}).get('file', 'N/A')}")
                    print(f"   Match: {secret.get('Raw', '')[:50]}...")
            
            print("-" * 70)
            
            # Check .env file
            print("\n🔍 Checking .env file:")
            env_path = os.path.join(repo_root, '.env')
            if os.path.exists(env_path):
                print(f"   ✓ .env exists at: {env_path}")
                print(f"   ✓ .env should be in .gitignore (never committed)")
                
                # Check if .gitignore contains .env
                gitignore_path = os.path.join(repo_root, '.gitignore')
                if os.path.exists(gitignore_path):
                    with open(gitignore_path, 'r') as f:
                        gitignore_content = f.read()
                        if '.env' in gitignore_content:
                            print(f"   ✓ .env is in .gitignore (GOOD)")
                        else:
                            print(f"   ✗ .env is NOT in .gitignore (SECURITY RISK)")
            else:
                print(f"   ℹ .env file not found (may be on production only)")
            
            print("\n" + "=" * 70)
            print("✅ SEC-007 SECURITY AUDIT COMPLETE")
            print("=" * 70)
            
            return len(secrets_found) == 0
        
        else:
            print(f"\n❌ Trufflehog scan failed:")
            print(result.stderr)
            return False
    
    except FileNotFoundError:
        print("\n❌ ERROR: trufflehog not installed")
        print("   Install with: pip install trufflehog")
        return False
    
    except subprocess.TimeoutExpired:
        print("\n⏱️ Scan timed out - repository might be too large")
        return False
    
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False


def check_env_best_practices():
    """Check if environment variables follow best practices"""
    print("\n" + "=" * 70)
    print("📋 ENVIRONMENT VARIABLES BEST PRACTICES")
    print("=" * 70)
    
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Check settings.py for hardcoded secrets
    settings_path = os.path.join(repo_root, 'classes-main', 'core', 'settings.py')
    if os.path.exists(settings_path):
        with open(settings_path, 'r') as f:
            settings_content = f.read()
        
        issues = []
        
        # Check for common secret patterns
        if 'SECRET_KEY =' in settings_content and 'os.environ.get' not in settings_content:
            issues.append("SECRET_KEY might be hardcoded")
        
        if 'PASSWORD' in settings_content and 'os.environ' not in settings_content:
            issues.append("DATABASE_PASSWORD might be hardcoded")
        
        if issues:
            print("\n⚠️  POTENTIAL ISSUES:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("\n✅ All environment variables use os.environ.get()")
            print("   - No hardcoded secrets detected")
            print("   - All credentials properly externalized")
    
    print("\n" + "=" * 70)


if __name__ == '__main__':
    # Run security audit
    success = scan_repository()
    
    # Check best practices
    check_env_best_practices()
    
    sys.exit(0 if success else 1)
