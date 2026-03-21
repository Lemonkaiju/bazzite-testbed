#!/usr/bin/env python3
"""
Example usage of AI Facilitator
Demonstrates how to integrate with AI assistants
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_facilitator.server import AIFacilitatorServer


def example_install_flatpak():
    """Example: Install a Flatpak application"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Install Flatpak Application")
    print("="*60)
    
    server = AIFacilitatorServer()
    server.start()
    
    print("\nAttempting to install Firefox via Flatpak...")
    print("(This will request user approval)")
    
    result = server.execute_command("flatpak_install", {
        "app_name": "org.mozilla.firefox",
        "remote": "flathub",
        "system": False
    })
    
    print(f"\nResult: {result['status']}")
    if result['status'] == 'success':
        print(f"Transaction ID: {result['transaction_id']}")
        print("Firefox installed successfully!")
    elif result['status'] == 'rejected':
        print(f"Reason: {result['reason']}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    server.stop()


def example_create_distrobox():
    """Example: Create a Distrobox container"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Create Distrobox Container")
    print("="*60)
    
    server = AIFacilitatorServer()
    server.start()
    
    print("\nCreating development Distrobox...")
    print("(This will request user approval)")
    
    result = server.execute_command("distrobox_create", {
        "name": "dev-env",
        "distro": "fedora:39",
        "additional_packages": ["git", "python3", "nodejs"]
    })
    
    print(f"\nResult: {result['status']}")
    if result['status'] == 'success':
        print(f"Container '{result['result']['container_name']}' created!")
        print("Enter with: distrobox enter dev-env")
    
    server.stop()


def example_rollback_system():
    """Example: Rollback system (for 'something feels broken')"""
    print("\n" + "="*60)
    print("EXAMPLE 3: System Rollback")
    print("="*60)
    
    server = AIFacilitatorServer()
    server.start()
    
    print("\nRolling back to previous deployment...")
    print("(This will request user approval)")
    
    result = server.execute_command("rpm_ostree_rollback", {
        "reboot": False
    })
    
    print(f"\nResult: {result['status']}")
    if result['status'] == 'success':
        print("System rolled back successfully!")
        if result['result'].get('requires_reboot'):
            print("Reboot required to activate previous deployment")
    
    server.stop()


def example_view_history():
    """Example: View command history"""
    print("\n" + "="*60)
    print("EXAMPLE 4: View Command History")
    print("="*60)
    
    server = AIFacilitatorServer()
    
    history = server.get_history(limit=10)
    
    if history:
        print(f"\nShowing last {len(history)} transactions:\n")
        for tx in history:
            status_icon = "✓" if tx['status'] == 'success' else "✗"
            print(f"{status_icon} {tx['timestamp']}")
            print(f"  Command: {tx['command']}")
            print(f"  Status: {tx['status']}")
            if tx.get('undone'):
                print(f"  [UNDONE at {tx.get('undo_timestamp')}]")
            print()
    else:
        print("\nNo transaction history yet")


def example_undo_action():
    """Example: Undo last action"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Undo Last Action")
    print("="*60)
    
    server = AIFacilitatorServer()
    server.start()
    
    print("\nUndoing last action...")
    
    try:
        result = server.undo_last_action()
        
        print(f"\nResult: {result['status']}")
        if result['status'] == 'success':
            print("Last action undone successfully!")
            print(f"Details: {result['result']}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"Cannot undo: {e}")
    
    server.stop()


def example_ai_assistant_integration():
    """Example: How an AI assistant would use this"""
    print("\n" + "="*60)
    print("EXAMPLE 6: AI Assistant Integration")
    print("="*60)
    
    print("\nScenario: User says 'Install Steam for gaming'")
    print("\nAI Assistant logic:")
    print("1. Recognize intent: Install application")
    print("2. Identify tool: Flatpak (preferred for GUI apps)")
    print("3. Find app ID: com.valvesoftware.Steam")
    print("4. Execute via AI Facilitator")
    
    server = AIFacilitatorServer()
    server.start()
    
    # Check if user is present
    status = server.get_status()
    if not status['user_present']:
        print("\n⚠️  User not present - cannot execute")
        print("   Waiting for USB sentinel or mobile dashboard activation...")
        server.stop()
        return
    
    print("\n✓ User present - proceeding with installation")
    print("\nRequesting approval...")
    
    result = server.execute_command("flatpak_install", {
        "app_name": "com.valvesoftware.Steam",
        "remote": "flathub"
    })
    
    # AI would then respond to user based on result
    if result['status'] == 'success':
        ai_response = "I've installed Steam for you! You can launch it from your applications menu."
    elif result['status'] == 'rejected':
        ai_response = "I understand you don't want to install Steam right now. Let me know if you change your mind!"
    else:
        ai_response = f"I encountered an issue installing Steam: {result.get('error', 'Unknown error')}. Would you like me to try a different approach?"
    
    print(f"\nAI Response to User: {ai_response}")
    
    server.stop()


def main():
    """Run examples"""
    print("\n" + "="*60)
    print("AI FACILITATOR - USAGE EXAMPLES")
    print("="*60)
    print("\nThese examples demonstrate how to use the AI Facilitator")
    print("in various scenarios. Each example shows:")
    print("  • How to initialize the server")
    print("  • How to execute commands")
    print("  • How to handle results")
    print("\nNote: Some examples require user approval via notification")
    
    examples = [
        ("View History", example_view_history),
        ("Install Flatpak", example_install_flatpak),
        ("Create Distrobox", example_create_distrobox),
        ("System Rollback", example_rollback_system),
        ("Undo Action", example_undo_action),
        ("AI Assistant Integration", example_ai_assistant_integration)
    ]
    
    print("\n\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\nRun specific example: python example_usage.py <number>")
    print("Run all examples: python example_usage.py all")
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg == "all":
            for name, func in examples:
                func()
                time.sleep(2)
        else:
            try:
                idx = int(arg) - 1
                if 0 <= idx < len(examples):
                    examples[idx][1]()
                else:
                    print(f"\nInvalid example number: {arg}")
            except ValueError:
                print(f"\nInvalid argument: {arg}")
    else:
        # Default: show view history
        example_view_history()


if __name__ == "__main__":
    main()
