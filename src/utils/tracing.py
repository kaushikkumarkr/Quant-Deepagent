import os
import phoenix as px
from phoenix.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor
from src.utils.logging import setup_logging

logger = setup_logging(__name__)

def setup_tracing():
    """
    Initialize Arize Phoenix tracing for LangChain.
    Returns the session URL if successful.
    """
    try:
        collector_endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT")
        
        if collector_endpoint:
            # Docker Mode: Connect to external Phoenix service
            logger.info(f"Connecting to remote Phoenix collector at: {collector_endpoint}")
            # Instrument LangChain to send traces to the collector
            tracer_provider = register(
                project_name=os.getenv("PHOENIX_PROJECT_NAME", "quantmind-docker"),
                endpoint=f"{collector_endpoint}/v1/traces"
            )
            LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
            return collector_endpoint # Return the collector URL (UI is usually on port 6006 of that host)
            
        else:
            # Local Mode: Launch local instance
            session = px.launch_app()
            logger.info(f"Phoenix running locally at: {session.url}")
            LangChainInstrumentor().instrument()
            return session.url
            
    except Exception as e:
        logger.warning(f"Failed to initialize Phoenix tracing: {e}")
        return None
