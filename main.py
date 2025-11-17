#!/usr/bin/env python3
"""
🐙 OctopusFTP - Multi-Connection FTP/FTPS Downloader
Entry point for the application
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ftp_gui import FTPDownloaderGUI

def main():
    """Main entry point for the application"""
    try:
        app = FTPDownloaderGUI()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication closed by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
