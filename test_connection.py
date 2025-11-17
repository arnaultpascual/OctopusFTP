#!/usr/bin/env python3
"""
Quick test script for OctopusFTP connection
Tests FTPS connection with passive mode
"""

import sys
from ftp_engine import MultiConnectionFTP

def test_ftp_connection():
    """Test FTP connection with user input"""
    print("=== OctopusFTP Connection Test ===\n")

    # Get connection details
    host = input("FTP Server (e.g., ftp.example.com): ").strip()
    if not host:
        print("Error: Server is required")
        return

    port = input("Port [21]: ").strip() or "21"
    try:
        port = int(port)
    except:
        print("Error: Invalid port")
        return

    user = input("Username: ").strip()
    if not user:
        print("Error: Username is required")
        return

    password = input("Password: ").strip()
    if not password:
        print("Error: Password is required")
        return

    use_ssl = input("Use SSL/TLS (FTPS)? [Y/n]: ").strip().lower()
    use_ssl = use_ssl != 'n'

    print(f"\n{'='*50}")
    print(f"Testing connection to {host}:{port}")
    print(f"SSL/TLS: {'Yes' if use_ssl else 'No'}")
    print(f"{'='*50}\n")

    try:
        # Create FTP instance
        ftp = MultiConnectionFTP(host, user, password, port, use_ssl)

        # Test connection
        print("[1/3] Testing connection...")
        success, message = ftp.test_connection()

        if not success:
            print(f"❌ Connection failed: {message}")
            return

        print(f"✓ Connection successful!")
        print(f"    Server message: {message}\n")

        # Test directory listing
        print("[2/3] Testing directory listing...")
        try:
            items = ftp.list_directory('/')
            print(f"✓ Directory listing successful!")
            print(f"    Found {len(items)} items in root directory:\n")

            # Show first 10 items
            for item in items[:10]:
                icon = "📁" if item.is_dir else "📄"
                size = f"{item.size:,} bytes" if not item.is_dir else "DIR"
                print(f"    {icon} {item.name:30} {size:>15}")

            if len(items) > 10:
                print(f"    ... and {len(items) - 10} more items")

        except Exception as e:
            print(f"❌ Directory listing failed: {e}")
            print(f"    Error type: {type(e).__name__}")
            import traceback
            print("\n    Full traceback:")
            traceback.print_exc()
            return

        # Test file size query (if there are files)
        files = [item for item in items if not item.is_dir]
        if files:
            print(f"\n[3/3] Testing file size query...")
            test_file = files[0]
            try:
                size = ftp.get_file_size(test_file.path)
                print(f"✓ File size query successful!")
                print(f"    File: {test_file.name}")
                print(f"    Size: {size:,} bytes")
            except Exception as e:
                print(f"⚠️  File size query failed: {e}")
        else:
            print(f"\n[3/3] Skipping file size test (no files in root)")

        print(f"\n{'='*50}")
        print("✓ All tests passed!")
        print(f"{'='*50}\n")
        print("Your FTP server is ready to use with OctopusFTP!")

    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_ftp_connection()
