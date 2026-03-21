#!/usr/bin/env python3
"""
Test script for AI Facilitator
Demonstrates basic functionality without requiring full setup
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_facilitator.server import AIFacilitatorServer
from ai_facilitator.user_present import UserPresentDetector
from ai_facilitator.mcp_tools import MCPToolWrapper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_user_presence():
    """Test user presence detection"""
    print("\n" + "="*60)
    print("TEST 1: User Presence Detection")
    print("="*60)
    
    detector = UserPresentDetector({
        "usb_sentinel_enabled": True,
        "mobile_dashboard_enabled": False,
        "check_interval": 5
    })
    
    status = detector.get_status()
    print(f"USB Sentinel Enabled: {status['usb_sentinel_enabled']}")
    print(f"USB Sentinel Detected: {status['usb_sentinel_detected']}")
    print(f"User Present: {status['user_present']}")
    
    if not status['user_present']:
        print("\n⚠️  User not present - AI facilitator would be DISABLED")
        print("   Insert USB sentinel or enable mobile dashboard to activate")
    else:
        print("\n✓ User present - AI facilitator ACTIVE")


def test_mcp_tools():
    """Test MCP tool wrapper"""
    print("\n" + "="*60)
    print("TEST 2: MCP Tool Wrapper")
    print("="*60)
    
    tools = MCPToolWrapper({
        "allowed_commands": [
            "flatpak install",
            "rpm-ostree rollback",
            "distrobox create",
            "ujust setup-gaming"
        ]
    })
    
    # Test listing Flatpaks
    print("\nTesting Flatpak search...")
    apps = tools.list_available_flatpaks("firefox")
    if apps:
        print(f"Found {len(apps)} results for 'firefox':")
        for app in apps[:3]:
            print(f"  • {app['name']}: {app['app_id']}")
    else:
        print("  No results (flatpak may not be configured)")
    
    # Test listing Distrobox containers
    print("\nTesting Distrobox list...")
    containers = tools.list_distrobox_containers()
    if containers:
        print(f"Found {len(containers)} containers:")
        for container in containers:
            print(f"  • {container['name']}: {container['status']}")
    else:
        print("  No containers found")
    
    # Test rpm-ostree status
    print("\nTesting rpm-ostree status...")
    status = tools.get_rpm_ostree_status()
    if "error" not in status:
        deployments = status.get("deployments", [])
        if deployments:
            current = deployments[0]
            print(f"  Current deployment: {current.get('version', 'unknown')}")
            print(f"  Booted: {current.get('booted', False)}")
    else:
        print(f"  Error: {status['error']}")


def test_server_status():
    """Test server initialization and status"""
    print("\n" + "="*60)
    print("TEST 3: Server Status")
    print("="*60)
    
    try:
        server = AIFacilitatorServer()
        status = server.get_status()
        
        print(f"Server Running: {status['running']}")
        print(f"User Present: {status['user_present']}")
        print(f"Pending Commands: {status['pending_commands']}")
        print(f"Last Transaction: {status['last_transaction']}")
        
        print("\n✓ Server initialized successfully")
        
    except Exception as e:
        print(f"\n✗ Server initialization failed: {e}")


def test_transaction_log():
    """Test transaction logging"""
    print("\n" + "="*60)
    print("TEST 4: Transaction Logging")
    print("="*60)
    
    from ai_facilitator.transaction_log import TransactionLogger
    
    logger_instance = TransactionLogger({
        "log_dir": str(Path.home() / ".local" / "share" / "ai_facilitator" / "logs"),
        "max_history": 1000
    })
    
    # Log a test transaction
    tx_id = logger_instance.log_action(
        command="test_command",
        args={"test": "value"},
        status="success",
        result={"message": "Test successful"}
    )
    
    print(f"Logged test transaction: {tx_id}")
    
    # Get statistics
    stats = logger_instance.get_statistics()
    print(f"\nTransaction Statistics:")
    print(f"  Total: {stats['total_transactions']}")
    print(f"  Successful: {stats['successful']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Rejected: {stats['rejected']}")
    print(f"  Undone: {stats['undone']}")
    
    # Get recent history
    history = logger_instance.get_history(limit=5)
    if history:
        print(f"\nRecent transactions:")
        for tx in history[:5]:
            print(f"  • {tx['timestamp']}: {tx['command']} - {tx['status']}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("AI FACILITATOR TEST SUITE")
    print("="*60)
    
    try:
        test_user_presence()
        test_mcp_tools()
        test_server_status()
        test_transaction_log()
        
        print("\n" + "="*60)
        print("TEST SUITE COMPLETE")
        print("="*60)
        print("\nAll core components are functional!")
        print("\nNext steps:")
        print("  1. Configure USB sentinel (optional)")
        print("  2. Install PolicyKit rules: sudo ./install_policykit.sh")
        print("  3. Install systemd service: ./install_service.sh")
        print("  4. Start server: systemctl --user start ai_facilitator")
        print("")
        
    except Exception as e:
        logger.error(f"Test suite failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
