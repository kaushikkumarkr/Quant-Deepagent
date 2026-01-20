
import asyncio
import logging
import os
import time
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from phoenix.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_minimal_test():
    print("🚀 Starting Minimal Tracing Test (Forced Mode)...")
    
    collector_endpoint = "http://phoenix:6006/v1/traces"
    print(f"📡 Tracing configured for: {collector_endpoint}")

    # Set Project Name Environment Variable for this process
    os.environ["PHOENIX_PROJECT_NAME"] = "quantmind-docker"
    
    # Instrument via OpenTelemetry (New Standard)
    print("🔧 Instrumenting LangChain with OpenInference...")
    tracer_provider = register(
        project_name="quantmind-docker",
        endpoint=collector_endpoint
    )
    LangChainInstrumentor().instrument(tracer_provider=tracer_provider)

    # Setup Simple LLM
    lm_studio_url = os.getenv("LM_STUDIO_URL", "http://host.docker.internal:1234/v1")
    logger.info(f"🤖 Connecting to LLM at: {lm_studio_url}")
    
    llm = ChatOpenAI(
        base_url=lm_studio_url,
        api_key="lm-studio",
        model="local-model",
        temperature=0
    )
    
    # Send multiple messages to ensure buffer flush
    for i in range(3):
        print(f"💬 Sending Message {i+1}...")
        try:
            response = await llm.ainvoke([HumanMessage(content=f"Say 'Trace {i+1}'")])
            print(f"✅ Response {i+1}: {response.content}")
        except Exception as e:
            print(f"❌ Failed: {e}")
            
    print("⏳ Waiting 5 seconds for traces to flush...")
    time.sleep(5)
    print("✅ Done.")

if __name__ == "__main__":
    asyncio.run(run_minimal_test())
