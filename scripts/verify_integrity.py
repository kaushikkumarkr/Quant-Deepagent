import os
import sys
import importlib
import pkgutil
import traceback

def verify_directory(start_dir):
    print(f"🔍 Verifying integrity of modules in {start_dir}...")
    
    success_count = 0
    error_count = 0
    
    # Walk through logical packages
    # We assume 'src' is a package or contains packages
    
    # Add root to path
    sys.path.insert(0, os.getcwd())
    
    for root, dirs, files in os.walk(start_dir):
        if '__pycache__' in root:
            continue
            
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                # Construct module name
                rel_path = os.path.relpath(os.path.join(root, file), os.getcwd())
                module_name = rel_path.replace(os.sep, ".").replace(".py", "")
                
                try:
                    importlib.import_module(module_name)
                    print(f"✅ Loaded: {module_name}")
                    success_count += 1
                except Exception as e:
                    print(f"❌ FAILED: {module_name}")
                    print(f"   Error: {str(e)}")
                    # traceback.print_exc()
                    error_count += 1
            elif file == "__init__.py":
                # Import package
                rel_path = os.path.relpath(root, os.getcwd())
                module_name = rel_path.replace(os.sep, ".")
                if module_name == ".": continue
                
                try:
                    importlib.import_module(module_name)
                    print(f"✅ Loaded Pkg: {module_name}")
                    success_count += 1
                except Exception as e:
                    print(f"❌ FAILED Pkg: {module_name}")
                    print(f"   Error: {str(e)}")
                    error_count += 1

    print("-" * 40)
    print(f"Verification Complete.")
    print(f"Successful: {success_count}")
    print(f"Failed:     {error_count}")
    
    if error_count > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    verify_directory("src")
