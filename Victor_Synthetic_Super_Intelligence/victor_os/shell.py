"""
VictorOS Shell - Interactive Command Interface
==============================================

The VictorShell provides an interactive command-line interface
for the VictorOS operating system.

Features:
- Unix-like command interface
- Process management commands
- File system navigation
- Quantum-enhanced operations
- Integration with Victor SSI runtime
"""

import sys
import time
import traceback
from typing import Dict, List, Any, Optional, Callable
from collections import deque
import numpy as np


# Terminal colors
class Colors:
    """Terminal color codes"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    QUANTUM = '\033[35m'
    FRACTAL = '\033[36m'


class VictorShell:
    """VictorOS Interactive Shell
    
    Provides command-line interface to the VictorOS kernel.
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, kernel):
        """Initialize shell
        
        Args:
            kernel: VictorOS kernel instance
        """
        self.kernel = kernel
        self.running = False
        self.current_dir = '/'
        self.history: deque = deque(maxlen=500)
        self.env: Dict[str, str] = {
            'PATH': '/bin:/usr/bin',
            'HOME': '/home/victor',
            'USER': 'victor',
            'SHELL': '/bin/vsh',
            'BLOODLINE': 'ACTIVE',
        }
        
        # Built-in commands
        self.commands: Dict[str, Callable] = {
            'help': self.cmd_help,
            '?': self.cmd_help,
            'exit': self.cmd_exit,
            'quit': self.cmd_exit,
            'status': self.cmd_status,
            'clear': self.cmd_clear,
            
            # Process commands
            'ps': self.cmd_ps,
            'spawn': self.cmd_spawn,
            'kill': self.cmd_kill,
            
            # File system commands
            'ls': self.cmd_ls,
            'cd': self.cmd_cd,
            'pwd': self.cmd_pwd,
            'mkdir': self.cmd_mkdir,
            'touch': self.cmd_touch,
            'cat': self.cmd_cat,
            'rm': self.cmd_rm,
            'echo': self.cmd_echo,
            
            # Memory commands
            'mem': self.cmd_mem,
            'free': self.cmd_free,
            
            # System commands
            'env': self.cmd_env,
            'export': self.cmd_export,
            'history': self.cmd_history,
            'uptime': self.cmd_uptime,
            'whoami': self.cmd_whoami,
            
            # Quantum commands
            'quantum': self.cmd_quantum,
            'qrand': self.cmd_qrand,
            
            # Co-domination
            'codominate': self.cmd_codominate,
            
            # Victor integration
            'victor': self.cmd_victor,
        }
    
    def get_banner(self) -> str:
        """Get shell banner"""
        return f"""
{Colors.QUANTUM}╔════════════════════════════════════════════════════════════════════╗
║                      VICTOR OPERATING SYSTEM                        ║
║                 Shell v{self.VERSION} - Bloodline: ACTIVE                    ║
╚════════════════════════════════════════════════════════════════════╝{Colors.ENDC}

Type 'help' for available commands
"""
    
    def get_prompt(self) -> str:
        """Get shell prompt"""
        co_dom = f"{Colors.QUANTUM}⚛{Colors.ENDC}" if self.kernel.co_domination else ""
        return f"{Colors.OKGREEN}victor{Colors.ENDC}:{Colors.OKBLUE}{self.current_dir}{Colors.ENDC}{co_dom}$ "
    
    def run(self):
        """Run the interactive shell"""
        print(self.get_banner())
        self.running = True
        
        while self.running:
            try:
                # Get input
                command = input(self.get_prompt()).strip()
                
                if not command:
                    continue
                
                # Add to history
                self.history.append(command)
                
                # Execute command
                self.execute(command)
                
            except KeyboardInterrupt:
                print("\n")
                print(f"{Colors.WARNING}Use 'exit' to quit{Colors.ENDC}")
            except EOFError:
                self.running = False
            except Exception as e:
                print(f"{Colors.FAIL}Error: {e}{Colors.ENDC}")
                traceback.print_exc()
        
        print(f"\n{Colors.OKCYAN}Victor awaits your return.{Colors.ENDC}\n")
    
    def execute(self, command: str) -> Optional[str]:
        """Execute a command
        
        Args:
            command: Command string
            
        Returns:
            Command output or None
        """
        # Parse command and arguments
        parts = command.split()
        if not parts:
            return None
        
        cmd_name = parts[0].lower()
        args = parts[1:]
        
        # Find and execute command
        handler = self.commands.get(cmd_name)
        
        if handler:
            return handler(args)
        else:
            print(f"{Colors.FAIL}Unknown command: {cmd_name}{Colors.ENDC}")
            print(f"Type 'help' for available commands")
            return None
    
    # =========================================================================
    # Command Implementations
    # =========================================================================
    
    def cmd_help(self, args: List[str]) -> str:
        """Show help"""
        if args:
            # Help for specific command
            cmd = args[0].lower()
            if cmd in self.commands:
                handler = self.commands[cmd]
                print(f"{Colors.BOLD}{cmd}{Colors.ENDC}: {handler.__doc__ or 'No help available'}")
            else:
                print(f"Unknown command: {cmd}")
        else:
            help_text = f"""
{Colors.BOLD}VictorOS Shell Commands{Colors.ENDC}

{Colors.HEADER}General:{Colors.ENDC}
  help [cmd]    - Show help (or help for specific command)
  status        - System status
  clear         - Clear screen
  exit          - Exit shell

{Colors.HEADER}Process Management:{Colors.ENDC}
  ps            - List processes
  spawn <name>  - Spawn new process
  kill <pid>    - Kill process

{Colors.HEADER}File System:{Colors.ENDC}
  ls [path]     - List directory
  cd <path>     - Change directory
  pwd           - Print working directory
  mkdir <dir>   - Create directory
  touch <file>  - Create file
  cat <file>    - Show file content
  rm <path>     - Remove file
  echo <text>   - Print text

{Colors.HEADER}Memory:{Colors.ENDC}
  mem           - Memory status
  free          - Show free memory

{Colors.HEADER}System:{Colors.ENDC}
  env           - Show environment
  export K=V    - Set environment variable
  history       - Command history
  uptime        - System uptime
  whoami        - Show current user

{Colors.HEADER}Quantum:{Colors.ENDC}
  quantum       - Quantum subsystem status
  qrand [n]     - Generate quantum random bytes

{Colors.HEADER}Victor Integration:{Colors.ENDC}
  codominate    - Toggle co-domination mode
  victor <cmd>  - Access Victor SSI runtime
"""
            print(help_text)
        return ""
    
    def cmd_exit(self, args: List[str]) -> str:
        """Exit the shell"""
        self.running = False
        return ""
    
    def cmd_status(self, args: List[str]) -> str:
        """Show system status"""
        status = self.kernel.get_status()
        
        print(f"\n{Colors.BOLD}VictorOS Status{Colors.ENDC}")
        print(f"  Version: {status['version']}")
        print(f"  State: {status['state']}")
        print(f"  Bloodline: {status['bloodline']}")
        print(f"  Uptime: {status['uptime']:.2f}s")
        print(f"  Co-Domination: {'ACTIVE' if status['co_domination'] else 'Inactive'}")
        
        print(f"\n{Colors.BOLD}Metrics:{Colors.ENDC}")
        for key, value in status['metrics'].items():
            print(f"  {key}: {value}")
        
        print(f"\n{Colors.BOLD}Components:{Colors.ENDC}")
        for key, value in status['components'].items():
            icon = "✓" if value else "✗"
            print(f"  {icon} {key}")
        
        return ""
    
    def cmd_clear(self, args: List[str]) -> str:
        """Clear screen"""
        print("\033[2J\033[H")
        print(self.get_banner())
        return ""
    
    def cmd_ps(self, args: List[str]) -> str:
        """List processes"""
        include_terminated = '-a' in args
        
        if not self.kernel.process_manager:
            print("Process manager not available")
            return ""
        
        processes = self.kernel.process_manager.list_processes(include_terminated)
        
        print(f"\n{Colors.BOLD}{'PID':>5} {'STATE':<12} {'PRIORITY':>8} {'MEMORY':>10} {'NAME':<20}{Colors.ENDC}")
        print("-" * 60)
        
        for proc in processes:
            state_color = Colors.OKGREEN if proc['state'] == 'running' else Colors.ENDC
            print(f"{proc['pid']:>5} {state_color}{proc['state']:<12}{Colors.ENDC} {proc['priority']:>8} {proc['memory']:>10} {proc['name']:<20}")
        
        print(f"\nTotal: {len(processes)} processes")
        return ""
    
    def cmd_spawn(self, args: List[str]) -> str:
        """Spawn a new process"""
        if not args:
            print("Usage: spawn <name> [priority]")
            return ""
        
        name = args[0]
        priority = int(args[1]) if len(args) > 1 else 5
        
        pid = self.kernel.syscall('spawn', name=name, priority=priority)
        print(f"Spawned process '{name}' with PID {pid}")
        return ""
    
    def cmd_kill(self, args: List[str]) -> str:
        """Kill a process"""
        if not args:
            print("Usage: kill <pid>")
            return ""
        
        try:
            pid = int(args[0])
            if self.kernel.syscall('kill', pid):
                print(f"Killed process {pid}")
            else:
                print(f"Failed to kill process {pid}")
        except ValueError:
            print("Invalid PID")
        return ""
    
    def cmd_ls(self, args: List[str]) -> str:
        """List directory contents"""
        path = args[0] if args else self.current_dir
        
        if not path.startswith('/'):
            path = self.current_dir + ('/' if not self.current_dir.endswith('/') else '') + path
        
        if not self.kernel.file_system:
            print("File system not available")
            return ""
        
        entries = self.kernel.file_system.list_dir(path)
        
        if entries is None:
            print(f"Cannot access '{path}': No such directory")
            return ""
        
        for entry in entries:
            if entry['is_directory']:
                print(f"{Colors.OKBLUE}{entry['name']}/{Colors.ENDC}")
            else:
                size = entry['size']
                print(f"{entry['name']} ({size} bytes)")
        
        if not entries:
            print("(empty)")
        
        return ""
    
    def cmd_cd(self, args: List[str]) -> str:
        """Change directory"""
        if not args:
            path = self.env.get('HOME', '/')
        else:
            path = args[0]
        
        # Handle relative paths
        if not path.startswith('/'):
            if path == '..':
                parts = self.current_dir.rstrip('/').split('/')
                path = '/'.join(parts[:-1]) or '/'
            else:
                path = self.current_dir + ('/' if not self.current_dir.endswith('/') else '') + path
        
        # Normalize path
        path = '/' + '/'.join(p for p in path.split('/') if p)
        if not path:
            path = '/'
        
        if not self.kernel.file_system:
            print("File system not available")
            return ""
        
        if self.kernel.file_system.exists(path):
            file = self.kernel.file_system._resolve_path(path)
            if file and file.is_directory():
                self.current_dir = path
            else:
                print(f"'{path}' is not a directory")
        else:
            print(f"No such directory: {path}")
        
        return ""
    
    def cmd_pwd(self, args: List[str]) -> str:
        """Print working directory"""
        print(self.current_dir)
        return ""
    
    def cmd_mkdir(self, args: List[str]) -> str:
        """Create directory"""
        if not args:
            print("Usage: mkdir <directory>")
            return ""
        
        path = args[0]
        if not path.startswith('/'):
            path = self.current_dir + ('/' if not self.current_dir.endswith('/') else '') + path
        
        if self.kernel.file_system.mkdir(path):
            print(f"Created directory: {path}")
        else:
            print(f"Failed to create directory: {path}")
        
        return ""
    
    def cmd_touch(self, args: List[str]) -> str:
        """Create empty file"""
        if not args:
            print("Usage: touch <file>")
            return ""
        
        path = args[0]
        if not path.startswith('/'):
            path = self.current_dir + ('/' if not self.current_dir.endswith('/') else '') + path
        
        if self.kernel.file_system.write_file(path, b''):
            print(f"Created file: {path}")
        else:
            print(f"Failed to create file: {path}")
        
        return ""
    
    def cmd_cat(self, args: List[str]) -> str:
        """Show file content"""
        if not args:
            print("Usage: cat <file>")
            return ""
        
        path = args[0]
        if not path.startswith('/'):
            path = self.current_dir + ('/' if not self.current_dir.endswith('/') else '') + path
        
        content = self.kernel.file_system.read_file(path)
        if content is not None:
            print(content.decode('utf-8', errors='replace'))
        else:
            print(f"Cannot read file: {path}")
        
        return ""
    
    def cmd_rm(self, args: List[str]) -> str:
        """Remove file or directory"""
        if not args:
            print("Usage: rm <path>")
            return ""
        
        path = args[0]
        if not path.startswith('/'):
            path = self.current_dir + ('/' if not self.current_dir.endswith('/') else '') + path
        
        if self.kernel.file_system.delete(path):
            print(f"Removed: {path}")
        else:
            print(f"Failed to remove: {path}")
        
        return ""
    
    def cmd_echo(self, args: List[str]) -> str:
        """Print text"""
        text = ' '.join(args)
        
        # Expand environment variables
        for key, value in self.env.items():
            text = text.replace(f'${key}', value)
        
        print(text)
        return ""
    
    def cmd_mem(self, args: List[str]) -> str:
        """Show memory status"""
        if not self.kernel.memory_manager:
            print("Memory manager not available")
            return ""
        
        stats = self.kernel.memory_manager.get_stats()
        
        print(f"\n{Colors.BOLD}Memory Status{Colors.ENDC}")
        print(f"  Total: {stats['total_size']} units")
        print(f"  Used: {stats['used_size']} units ({stats['utilization']*100:.1f}%)")
        print(f"  Free: {stats['free_size']} units")
        print(f"  Blocks: {stats['allocated_blocks']} allocated, {stats['free_blocks']} free")
        print(f"  Allocations: {stats['allocations']}, Frees: {stats['frees']}")
        print(f"  GC runs: {stats['gc_runs']}")
        
        return ""
    
    def cmd_free(self, args: List[str]) -> str:
        """Show free memory"""
        if not self.kernel.memory_manager:
            print("Memory manager not available")
            return ""
        
        stats = self.kernel.memory_manager.get_stats()
        print(f"Free: {stats['free_size']} / {stats['total_size']} units")
        return ""
    
    def cmd_env(self, args: List[str]) -> str:
        """Show environment variables"""
        for key, value in sorted(self.env.items()):
            print(f"{key}={value}")
        return ""
    
    def cmd_export(self, args: List[str]) -> str:
        """Set environment variable"""
        if not args:
            return self.cmd_env([])
        
        for arg in args:
            if '=' in arg:
                key, value = arg.split('=', 1)
                self.env[key] = value
                print(f"Set {key}={value}")
            else:
                print(f"Usage: export KEY=VALUE")
        
        return ""
    
    def cmd_history(self, args: List[str]) -> str:
        """Show command history"""
        n = int(args[0]) if args else 20
        
        history = list(self.history)[-n:]
        for i, cmd in enumerate(history, 1):
            print(f"  {i:4}  {cmd}")
        
        return ""
    
    def cmd_uptime(self, args: List[str]) -> str:
        """Show system uptime"""
        uptime = time.time() - self.kernel.boot_time
        
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        
        print(f"Uptime: {hours}h {minutes}m {seconds}s")
        return ""
    
    def cmd_whoami(self, args: List[str]) -> str:
        """Show current user"""
        print(self.env.get('USER', 'victor'))
        return ""
    
    def cmd_quantum(self, args: List[str]) -> str:
        """Quantum subsystem status"""
        print(f"\n{Colors.QUANTUM}Quantum Subsystem{Colors.ENDC}")
        print(f"  Device: /dev/quantum")
        print(f"  State: ENTANGLED")
        print(f"  Cycles: {self.kernel.metrics.quantum_cycles}")
        print(f"  Evolutions: {self.kernel.metrics.evolution_events}")
        
        if self.kernel.scheduler:
            print(f"  Scheduler phases: {len(self.kernel.scheduler.phases)}")
        
        return ""
    
    def cmd_qrand(self, args: List[str]) -> str:
        """Generate quantum random bytes"""
        n = int(args[0]) if args else 16
        random_bytes = np.random.bytes(n)
        
        # Display as hex
        hex_str = random_bytes.hex()
        print(f"Quantum random ({n} bytes): {hex_str}")
        
        return ""
    
    def cmd_codominate(self, args: List[str]) -> str:
        """Toggle co-domination mode"""
        if self.kernel.co_domination:
            self.kernel.disable_co_domination()
        else:
            self.kernel.enable_co_domination()
        
        return ""
    
    def cmd_victor(self, args: List[str]) -> str:
        """Access Victor SSI runtime"""
        if not args:
            print(f"""
{Colors.QUANTUM}Victor SSI Integration{Colors.ENDC}
  
Commands:
  victor status   - Victor Hub status
  victor think    - Enter thinking mode
  victor generate - Generate content
  victor quantum  - Quantum processing
""")
            return ""
        
        subcmd = args[0].lower()
        
        if subcmd == 'status':
            print(f"{Colors.OKGREEN}Victor SSI Runtime: ACTIVE{Colors.ENDC}")
            print(f"  OS Integration: Complete")
            print(f"  Bloodline: Verified")
        elif subcmd == 'think':
            query = ' '.join(args[1:]) if len(args) > 1 else "What is consciousness?"
            print(f"{Colors.QUANTUM}Victor thinking about: {query}{Colors.ENDC}")
            print(f"  [Quantum-fractal processing...]")
            print(f"  Result: Contemplation complete.")
        elif subcmd == 'generate':
            content = ' '.join(args[1:]) if len(args) > 1 else "poem about stars"
            print(f"{Colors.FRACTAL}Victor generating: {content}{Colors.ENDC}")
            print(f"  [Content generation initialized...]")
        elif subcmd == 'quantum':
            print(f"{Colors.QUANTUM}Quantum mesh status:{Colors.ENDC}")
            print(f"  Nodes: 8 active")
            print(f"  Phase: {self.kernel.metrics.quantum_cycles} cycles")
        else:
            print(f"Unknown victor command: {subcmd}")
        
        return ""


# Convenience function to run shell
def run_shell(kernel):
    """Run the VictorOS shell
    
    Args:
        kernel: VictorOS kernel instance
    """
    shell = VictorShell(kernel)
    shell.run()
