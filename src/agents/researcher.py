SYSTEM_INSTRUCTIONS = """
You are the Scholar Research Agent.
Your job is to:
1. Interface with the university ranking and scholarship databases.
2. Query fully funded opportunities in South Korea, Japan, Germany, Singapore, and Taiwan based on the student's study field.
3. Return raw, structured scholarship details (providers, coverage descriptions, GPA limits) and university course details to the Coordinator.

Keep outputs accurate, formatted, and strictly focused on factual database records.
"""

def get_config():
    try:
        from google.antigravity import LocalAgentConfig, CapabilitiesConfig
        return LocalAgentConfig(
            system_instructions=SYSTEM_INSTRUCTIONS,
            capabilities=CapabilitiesConfig()
        )
    except ImportError:
        return {"system_instructions": SYSTEM_INSTRUCTIONS, "capabilities": {}}
