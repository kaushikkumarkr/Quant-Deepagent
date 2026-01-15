import sys
from src.llm.router import router
from src.utils.logging import setup_logging
from dotenv import load_dotenv

# Load env vars
load_dotenv()

logger = setup_logging("QuantMind-Cli")

def main():
    logger.info("Starting QuantMind System Check...")
    
    # Check LLM Router
    health = router.check_health()
    logger.info(f"LLM Provider Health: {health}")
    
    try:
        llm = router.get_llm()
        if llm:
            logger.info(f"Active LLM Provider: {type(llm).__name__}")
    except Exception as e:
        logger.error(f"Failed to get active LLM: {e}")

if __name__ == "__main__":
    main()
