#!/usr/bin/env python3
import re

with open('api_server_minimal.py', 'r') as f:
    content = f.read()

# Find where the parsing happens
start_marker = "# Parse the output to find insights"
end_marker = "return jsonify({"

start = content.find(start_marker)
end = content.find(end_marker, start)

if start == -1 or end == -1:
    print("Could not find parsing section")
    exit(1)

# New parsing code
new_parsing = '''        # Parse the RunResult output from the comprehensive agent
        output = result.stdout
        insights = []
        
        # Look for 'Final output' section
        if 'Final output (str):' in output:
            # Extract everything after 'Final output (str):'
            start = output.find('Final output (str):')
            if start != -1:
                final_output = output[start + len('Final output (str):'):]
                
                # Find the end of the output
                end_markers = ['- 5 new item(s)', '(See `RunResult`']
                end_pos = len(final_output)
                for marker in end_markers:
                    pos = final_output.find(marker)
                    if pos != -1:
                        end_pos = min(end_pos, pos)
                
                final_output = final_output[:end_pos].strip()
                
                # Extract key insights
                # Look for numbered items (1., 2., etc)
                lines = final_output.split('\\n')
                
                # Extract specific action items
                for i, line in enumerate(lines):
                    line = line.strip()
                    # Match lines that start with numbers
                    if line and len(line) > 2 and line[0].isdigit() and line[1] == '.':
                        # Get the title
                        title = line[3:].split(':')[0] if ':' in line else line[3:]
                        
                        # Get preview text from this and following lines
                        preview_lines = [line[3:]]
                        for j in range(i+1, min(i+3, len(lines))):
                            if lines[j].strip():
                                preview_lines.append(lines[j].strip())
                        
                        preview = ' '.join(preview_lines)[:200]
                        
                        insights.append({
                            'id': f'action-{len(insights)+1}',
                            'company': title[:60],
                            'amount': 100000 - (len(insights) * 10000),
                            'stage': 'Action Required',
                            'action_preview': preview + '...' if len(preview) == 200 else preview,
                            'confidence': 0.95 - (len(insights) * 0.05),
                            'action_data': {
                                'type': 'priority_action',
                                'full_content': preview,
                                'priority': len(insights) + 1
                            }
                        })
                
                # If no numbered insights found, show the whole analysis
                if not insights and final_output:
                    insights.append({
                        'id': 'full-analysis',
                        'company': 'AI Chief of Staff Analysis',
                        'amount': 150000,
                        'stage': 'Complete Analysis',
                        'action_preview': final_output[:300] + '...' if len(final_output) > 300 else final_output,
                        'confidence': 0.99,
                        'action_data': {
                            'type': 'comprehensive',
                            'full_content': final_output
                        }
                    })
        
        '''

# Replace the parsing section
new_content = content[:start] + new_parsing + content[end:]

with open('api_server_minimal.py', 'w') as f:
    f.write(new_content)

print('✅ Successfully updated the parser!')
