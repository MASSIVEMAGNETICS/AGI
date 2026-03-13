"""
Victor Hub with Visual Engine Integration Example

Demonstrates how to run Victor Hub with the Visual Engine enabled.
This example shows the complete integration between reasoning and visualization.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))

from visual_engine.backend.victor_visual_server import VictorVisualServer
from visual_engine.backend.victor_visual_bridge import VictorVisualBridge
from victor_hub.victor_boot import VictorHub, Task


async def run_victor_with_visual():
    """Run Victor Hub with Visual Engine integration"""
    
    print("=" * 60)
    print("VICTOR HUB + VISUAL ENGINE INTEGRATION")
    print("=" * 60)
    print()
    
    # 1. Initialize Visual Server
    print("[1/3] Starting Visual Engine Server...")
    visual_server = VictorVisualServer(host="127.0.0.1", port=8765)
    server_task = asyncio.create_task(visual_server.start())
    await asyncio.sleep(1)
    print("✓ Visual Server running on ws://127.0.0.1:8765")
    print()
    
    # 2. Initialize Victor Hub
    print("[2/3] Initializing Victor Hub...")
    hub = VictorHub(config_path="victor_hub/config.yaml")
    print("✓ Victor Hub initialized")
    print()
    
    # 3. Create Integration Bridge
    print("[3/3] Creating Visual Bridge...")
    bridge = VictorVisualBridge(visual_server)
    print("✓ Bridge connected")
    print()
    
    print("=" * 60)
    print("SYSTEM ONLINE - Victor is now visible")
    print("=" * 60)
    print()
    print("Instructions:")
    print("1. Open Godot project: visual_engine/godot_project/project.godot")
    print("2. Press F5 to run the visual scene")
    print("3. You should see Victor's visual presence")
    print()
    print("Running demo task sequence...")
    print()
    
    # Show idle state
    await bridge.show_idle()
    await asyncio.sleep(3)
    
    # Demo: Execute tasks with visual feedback
    demo_tasks = [
        {
            "description": "Analyze system performance",
            "type": "analysis",
            "emotion": "analyzing",
            "energy": 0.8
        },
        {
            "description": "Generate creative content",
            "type": "creative",
            "emotion": "creative",
            "energy": 0.7
        },
        {
            "description": "Research quantum computing",
            "type": "research",
            "emotion": "thinking",
            "energy": 0.75
        },
    ]
    
    for i, task_data in enumerate(demo_tasks, 1):
        print(f"\n--- Task {i}/{len(demo_tasks)} ---")
        print(f"Task: {task_data['description']}")
        
        # Show thinking state
        await bridge.show_thinking(f"Processing: {task_data['description']}")
        await asyncio.sleep(3)
        
        # Create and execute task
        task = Task(
            id=f"demo_task_{i}",
            type=task_data['type'],
            description=task_data['description']
        )
        
        # Execute task (this would normally be async)
        result = hub.execute_task(task)
        
        # Show result
        if result.status == "success":
            await bridge.show_success(f"✓ Completed: {task_data['description']}")
            print(f"Status: SUCCESS")
        else:
            await bridge.show_error(f"✗ Error: {result.error}")
            print(f"Status: FAILED - {result.error}")
        
        await asyncio.sleep(3)
    
    # Return to idle
    await bridge.show_idle()
    
    print("\n" + "=" * 60)
    print("Demo sequence complete")
    print("Server will continue running. Press Ctrl+C to stop.")
    print("=" * 60)
    
    # Keep server running
    await server_task


async def run_interactive_mode():
    """Run in interactive mode with visual feedback"""
    
    print("=" * 60)
    print("VICTOR HUB - INTERACTIVE MODE WITH VISUAL ENGINE")
    print("=" * 60)
    print()
    
    # Start visual server
    print("Starting Visual Engine...")
    visual_server = VictorVisualServer(host="127.0.0.1", port=8765)
    server_task = asyncio.create_task(visual_server.start())
    await asyncio.sleep(1)
    
    # Initialize hub and bridge
    hub = VictorHub(config_path="victor_hub/config.yaml")
    bridge = VictorVisualBridge(visual_server)
    
    await bridge.show_idle()
    
    print("\nVictor Visual Engine is ready!")
    print("Open Godot project and press F5 to see Victor")
    print("\nType commands (or 'exit' to quit):")
    print()
    
    # Interactive loop
    while True:
        try:
            command = input("Victor> ").strip()
            
            if command == "exit":
                print("Shutting down...")
                break
            
            if not command:
                continue
            
            # Process command with visual feedback
            await bridge.show_thinking("Processing your request...")
            await asyncio.sleep(1)
            
            response = hub.process_command(command)
            
            await bridge.show_success(response[:100])  # Show first 100 chars
            print(response)
            
            await asyncio.sleep(2)
            await bridge.show_idle()
            
        except KeyboardInterrupt:
            print("\nShutting down...")
            break
        except Exception as e:
            await bridge.show_error(f"Error: {str(e)}")
            print(f"Error: {e}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Victor Hub with Visual Engine Integration"
    )
    parser.add_argument(
        "--mode",
        choices=["demo", "interactive"],
        default="demo",
        help="Run mode: demo (automated) or interactive (CLI)"
    )
    
    args = parser.parse_args()
    
    try:
        if args.mode == "demo":
            asyncio.run(run_victor_with_visual())
        else:
            asyncio.run(run_interactive_mode())
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
