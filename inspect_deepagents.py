from deepagents import create_deep_agent, SubAgent
import inspect

print("FUNCTION: create_deep_agent")
try:
    print(inspect.signature(create_deep_agent))
except Exception as e:
    print(f"Could not get signature: {e}")
print(create_deep_agent.__doc__)

print("\nCLASS: SubAgent")
try:
    print(inspect.signature(SubAgent))
except Exception as e:
    print(f"Could not get signature: {e}")
print(SubAgent.__doc__)
