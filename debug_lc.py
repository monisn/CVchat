import langchain
import pkgutil
import sys

print(f"Langchain path: {langchain.__path__}")

def find_module(module_name, path=None):
    if path is None:
        path = sys.path
    
    found = False
    for loader, name, is_pkg in pkgutil.walk_packages(path):
        if name == module_name:
            print(f"Found {name}")
            return

try:
    import langchain.chains
    print("langchain.chains imported successfully")
except ImportError as e:
    print(f"Error importing langchain.chains: {e}")

try:
    from langchain.chains import create_history_aware_retriever
    print("Found create_history_aware_retriever")
except ImportError:
    print("Could not import create_history_aware_retriever from langchain.chains")

# Try to look into langchain_core or community
try:
    import langchain_core
    print(f"langchain_core version: {langchain_core.__version__}")
except ImportError:
    print("langchain_core not found")
