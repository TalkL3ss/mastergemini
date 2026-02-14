import sys
import re
import subprocess
import os

def execute_codex(file_path):
    """
    Reads a markdown file, finds code blocks to execute, runs them, and appends the output to the file.
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    last_codex_done_index = content.rfind("codex done")
    if last_codex_done_index != -1:
        content_to_parse = content[last_codex_done_index + len("codex done"):]
    else:
        content_to_parse = content
    
    # Fixed regex pattern to properly capture bash code blocks
    commands = re.findall(r'```bash\n(.*?)```', content_to_parse, re.DOTALL)
    
    if not commands:
        print("No new commands found to execute.")
        return
    
    full_output = ""
    all_commands_successful = True
    
    for i, command_block in enumerate(commands):
        print(f"Executing command block {i+1}/{len(commands)}:")
        print(f"{command_block[:100]}...")  # Print first 100 chars
        
        try:
            # Execute commands relative to the directory of the plan file
            # This is important for commands that reference local files or scripts.
            result = subprocess.run(
                command_block,
                shell=True,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(file_path))
            )
            
            output = result.stdout + result.stderr
            full_output += f"\n### Command Block {i+1} Output:\n```\n{output}\n```\n"
            
            if result.returncode != 0:
                full_output += f"\n**Error:** Command block {i+1} failed with exit code {result.returncode}.\n\n**Command:**\n```bash\n{command_block}\n```\n"
                all_commands_successful = False
                break  # Stop execution on first failure
                
        except Exception as e:
            full_output += f"\n**Error executing command block {i+1}:** {e}\n\n**Command:**\n```bash\n{command_block}\n```\n"
            all_commands_successful = False
            break
    
    with open(file_path, 'a') as f:
        f.write("\n\n## Results\n")
        f.write(full_output)
        if all_commands_successful:
            f.write("\n\ncodex done\n")
        else:
            f.write("\n\ncodex failed\n")
    
    print("Execution complete. Results appended.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Default to instructions.md if not provided
        target_file = "instructions.md"
    else:
        target_file = sys.argv[1]
    
    execute_codex(target_file)
