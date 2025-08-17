#!/usr/bin/env python3
"""
Python code execution script for the coding challenge platform.
Safely executes user-submitted Python code with resource limits.
"""

import os
import sys
import json
import time
import signal
import resource
import subprocess
import tempfile
from pathlib import Path

class CodeExecutor:
    def __init__(self):
        self.time_limit = int(os.environ.get('TIME_LIMIT', 10))  # seconds
        self.memory_limit = int(os.environ.get('MEMORY_LIMIT', 256)) * 1024 * 1024  # bytes
        
    def set_limits(self):
        """Set resource limits for the execution."""
        # Set memory limit
        resource.setrlimit(resource.RLIMIT_AS, (self.memory_limit, self.memory_limit))
        
        # Set CPU time limit
        resource.setrlimit(resource.RLIMIT_CPU, (self.time_limit, self.time_limit))
        
        # Limit number of processes
        resource.setrlimit(resource.RLIMIT_NPROC, (1, 1))
        
        # Disable core dumps
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    
    def execute_code(self, code, input_data):
        """Execute Python code with given input."""
        result = {
            'status': 'Unknown',
            'output': '',
            'error': '',
            'runtime': 0,
            'memory_used': 0
        }
        
        start_time = time.time()
        
        try:
            # Create temporary file for code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                code_file = f.name
            
            # Execute code with timeout
            process = subprocess.Popen(
                [sys.executable, code_file],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=self.set_limits
            )
            
            try:
                stdout, stderr = process.communicate(
                    input=input_data,
                    timeout=self.time_limit
                )
                
                runtime = time.time() - start_time
                result['runtime'] = int(runtime * 1000)  # milliseconds
                
                if process.returncode == 0:
                    result['status'] = 'Success'
                    result['output'] = stdout.strip()
                else:
                    result['status'] = 'Runtime Error'
                    result['error'] = stderr.strip()
                    
            except subprocess.TimeoutExpired:
                process.kill()
                result['status'] = 'Time Limit Exceeded'
                result['error'] = f'Execution timed out after {self.time_limit} seconds'
                
        except MemoryError:
            result['status'] = 'Memory Limit Exceeded'
            result['error'] = 'Memory limit exceeded'
            
        except Exception as e:
            result['status'] = 'System Error'
            result['error'] = str(e)
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(code_file)
            except:
                pass
        
        return result

def main():
    """Main execution function."""
    try:
        # Read input from environment or stdin
        code = os.environ.get('USER_CODE', '')
        input_data = os.environ.get('INPUT_DATA', '')
        
        if not code:
            # Read from stdin if not in environment
            data = json.loads(sys.stdin.read())
            code = data.get('code', '')
            input_data = data.get('input', '')
        
        if not code:
            print(json.dumps({
                'status': 'Error',
                'error': 'No code provided'
            }))
            return
        
        executor = CodeExecutor()
        result = executor.execute_code(code, input_data)
        
        # Output result as JSON
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({
            'status': 'System Error',
            'error': str(e)
        }))

if __name__ == '__main__':
    main()