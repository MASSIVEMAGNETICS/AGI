#!/usr/bin/env python3
"""
Victor Personal Runtime - Main Entry Point
===========================================

Run with: python -m victor_runtime
"""

import asyncio
import sys
import argparse
from pathlib import Path

def main():
    """Main entry point for Victor Personal Runtime"""
    parser = argparse.ArgumentParser(
        description='Victor Personal Runtime - Cross-Platform Personal AI Assistant'
    )
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to configuration file'
    )
    parser.add_argument(
        '--data-dir', '-d',
        type=str,
        help='Path to data directory'
    )
    parser.add_argument(
        '--version', '-v',
        action='store_true',
        help='Show version and exit'
    )
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show runtime status and exit'
    )
    
    args = parser.parse_args()
    
    if args.version:
        from victor_runtime import __version__
        print(f"Victor Personal Runtime v{__version__}")
        return 0
    
    from victor_runtime.core.runtime import VictorPersonalRuntime, run_victor_runtime
    
    if args.status:
        # Quick status check
        runtime = VictorPersonalRuntime(
            config_path=args.config,
            data_dir=args.data_dir
        )
        status = runtime.get_status()
        print("Victor Personal Runtime Status:")
        print(f"  Version: {status['version']}")
        print(f"  State: {status['state']}")
        print(f"  Data Directory: {runtime.data_dir}")
        return 0
    
    # Print welcome banner
    print("""
╔═══════════════════════════════════════════════════════════════╗
║          VICTOR PERSONAL RUNTIME v1.0.0                       ║
║     Cross-Platform Personal AI Assistant                      ║
║                                                               ║
║     Privacy-First • User-Controlled • Local Learning          ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    print("Initializing Victor Personal Runtime...")
    print("Press Ctrl+C to shutdown\n")
    
    try:
        asyncio.run(run_victor_runtime(config_path=args.config))
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"\nError: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
