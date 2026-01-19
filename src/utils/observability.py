import os
import logging
import phoenix as px
from phoenix.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor

logger = logging.getLogger(__name__)

def setup_observability():
    """
    Launches Arize Phoenix observability server and instruments LangChain.
    
    This allows local tracing of all agent activities, tool calls, and RAG retrieval.
    The UI will be available at http://localhost:6006
    """
    try:
        # Launch Phoenix Server
        session = px.launch_app(host="localhost", port=6006, run_in_thread=True)
        logger.info(f"🦚 Arize Phoenix Observability running at: {session.url}")
        
        # Configure OpenTelemetry Tracer provider connected to Phoenix
        tracer_provider = register(project_name="quant-deepagent")
        
        # Instrument LangChain (DeepAgents)
        LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
        logger.info("🔭 LangChain Auto-Instrumentation enabled (OpenInference).")
        
    except Exception as e:
        logger.warning(f"Failed to start observability: {e}")
