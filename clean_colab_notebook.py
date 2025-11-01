#!/usr/bin/env python3
"""
Clean Colab Notebook Utility
=============================
Removes widget metadata and references from Google Colab notebooks
to make them compatible with other Jupyter environments.

Usage:
    python clean_colab_notebook.py <notebook_file>
    python clean_colab_notebook.py *.ipynb  (for multiple files)
"""

import json
import sys
import os
from pathlib import Path


def clean_notebook(notebook_path):
    """Remove widget metadata and references from a Jupyter notebook."""
    try:
        # Read the notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        changes_made = []
        
        # 1. Remove widgets metadata from top-level metadata
        if 'widgets' in data.get('metadata', {}):
            del data['metadata']['widgets']
            changes_made.append("Removed 'widgets' from metadata")
        
        # 2. Remove widget outputs from cells
        widgets_removed = 0
        for cell in data.get('cells', []):
            if 'outputs' in cell:
                new_outputs = []
                for output in cell['outputs']:
                    # Check if output contains widget data
                    if 'data' in output and 'application/vnd.jupyter.widget-view+json' in output['data']:
                        widgets_removed += 1
                        # Keep other data formats if they exist (like text/plain)
                        output_copy = output.copy()
                        del output_copy['data']['application/vnd.jupyter.widget-view+json']
                        
                        # Remove widget metadata if it exists
                        if 'metadata' in output_copy:
                            output_copy['metadata'].pop('application/vnd.jupyter.widget-view+json', None)
                        
                        # Only keep if there's still data left
                        if output_copy.get('data'):
                            new_outputs.append(output_copy)
                    else:
                        new_outputs.append(output)
                
                cell['outputs'] = new_outputs
        
        if widgets_removed > 0:
            changes_made.append(f"Removed {widgets_removed} widget output reference(s)")
        
        # 3. Clean up Colab-specific metadata that might cause issues
        colab_keys_removed = []
        if 'colab' in data.get('metadata', {}):
            colab_meta = data['metadata']['colab']
            # Keep colab metadata but remove problematic keys
            if 'toc_visible' in colab_meta:
                del colab_meta['toc_visible']
                colab_keys_removed.append('toc_visible')
        
        if colab_keys_removed:
            changes_made.append(f"Cleaned Colab metadata: {', '.join(colab_keys_removed)}")
        
        # Save the cleaned notebook
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=1, ensure_ascii=False)
        
        return True, changes_made
    
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]
    except Exception as e:
        return False, [f"Error: {e}"]


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nError: Please provide at least one notebook file.")
        print("\nExamples:")
        print("  python clean_colab_notebook.py my_notebook.ipynb")
        print("  python clean_colab_notebook.py notebook1.ipynb notebook2.ipynb")
        sys.exit(1)
    
    notebook_files = sys.argv[1:]
    
    # Expand wildcards if any
    expanded_files = []
    for pattern in notebook_files:
        if '*' in pattern or '?' in pattern:
            expanded_files.extend(Path('.').glob(pattern))
        else:
            expanded_files.append(Path(pattern))
    
    if not expanded_files:
        print("Error: No notebook files found.")
        sys.exit(1)
    
    print("=" * 70)
    print("Cleaning Google Colab Notebooks")
    print("=" * 70)
    
    success_count = 0
    total_count = len(expanded_files)
    
    for notebook_path in expanded_files:
        if not notebook_path.exists():
            print(f"\n[X] {notebook_path}: File not found")
            continue
        
        if not str(notebook_path).endswith('.ipynb'):
            print(f"\n[!] {notebook_path}: Skipping (not a .ipynb file)")
            continue
        
        print(f"\n[*] Processing: {notebook_path}")
        success, changes = clean_notebook(notebook_path)
        
        if success:
            if changes:
                print(f"    [OK] Cleaned successfully!")
                for change in changes:
                    print(f"         - {change}")
                success_count += 1
            else:
                print(f"    [OK] Already clean (no changes needed)")
                success_count += 1
        else:
            print(f"    [ERROR] Failed:")
            for error in changes:
                print(f"            - {error}")
    
    print("\n" + "=" * 70)
    print(f"Results: {success_count}/{total_count} notebooks processed successfully")
    print("=" * 70)
    
    if success_count == total_count:
        print("\n[SUCCESS] All notebooks are now compatible with Jupyter/VS Code/Cursor!")
    else:
        print(f"\n[WARNING] {total_count - success_count} notebook(s) had errors.")


if __name__ == "__main__":
    main()

