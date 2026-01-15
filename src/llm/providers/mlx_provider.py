from typing import Optional, Any
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from pydantic import Field
import mlx_lm
from src.config import settings
from src.utils.logging import setup_logging

logger = setup_logging(__name__)

# Custom LangChain wrapper for MLX since one doesn't exist yet standardly
class ChatMLX(BaseChatModel):
    model_path: str = Field(..., description="Path to the MLX model")
    model: Any = Field(None, exclude=True) # Exclude from serialization
    tokenizer: Any = Field(None, exclude=True)
    temperature: float = Field(0.0, description="Sampling temperature")
    
    # Removed __init__ to rely on Pydantic initialization logic
    
    def _load_model(self):
        if self.model is None:
            logger.info(f"Loading MLX model: {self.model_path}...")
            self.model, self.tokenizer = mlx_lm.load(self.model_path)
            logger.info("MLX model loaded successfully.")

    def _generate(self, messages: list[BaseMessage], stop: Optional[list[str]] = None, run_manager: Optional[Any] = None, **kwargs: Any) -> ChatResult:
        self._load_model()
        
        # Convert messages to prompt
        # Simple chat template handling
        prompt = ""
        for msg in messages:
            if isinstance(msg, SystemMessage):
                prompt += f"<|system|>\n{msg.content}\n"
            elif isinstance(msg, HumanMessage):
                prompt += f"<|user|>\n{msg.content}\n"
            elif isinstance(msg, AIMessage):
                prompt += f"<|assistant|>\n{msg.content}\n"
        
        # Render tools if present in kwargs (from bind_tools)
        tools = kwargs.get("tools", [])
        if tools:
            tool_desc = "\n".join([f"- {t.name}: {t.description}" for t in tools])
            prompt += f"\n[AVAILABLE TOOLS]\n{tool_desc}\n\n"
            prompt += "INSTRUCTION: You must call a tool to proceed. Respond ONLY with a valid JSON object used to call a tool.\n"
            prompt += "FORMAT: {\"tool\": \"tool_name\", \"args\": {\"arg_name\": \"value\"}}\n"

        prompt += "<|assistant|>\n"
        
        response = mlx_lm.generate(
            self.model, 
            self.tokenizer, 
            prompt=prompt, 
            verbose=False, 
            max_tokens=1024
        )
        
        # Parse tool calls if JSON present
        import json
        tool_calls = []
        clean_content = response
        
        if tools: # Only attempt to parse if tools were actually offered
            try:
                # Naive extraction of JSON
                if "{" in response and "}" in response:
                    # Look for the JSON-like object (Greedy approach)
                    # We look for the first '{' and last '}'
                    start = response.find("{")
                    end = response.rfind("}") + 1
                    json_str = response[start:end]
                    
                    data = None
                    try:
                        data = json.loads(json_str)
                    except json.JSONDecodeError:
                        # Attempt cleanup: convert {'tool': ...} to {"tool": ...}
                        try:
                            # Simple heuristic for single quotes
                            fixed_json = json_str.replace("'", '"')
                            data = json.loads(fixed_json)
                        except:
                            # Verify if it really looks like a tool call before warning
                            if "tool" in json_str:
                                logger.warning(f"Failed to parse likely tool call: {json_str}")
                            pass

                    if data and isinstance(data, dict) and "tool" in data and "args" in data:
                        tool_calls.append({
                            "name": data["tool"],
                            "args": data["args"],
                            "id": f"call_{len(tool_calls)}", # Dummy ID
                            "type": "tool_call"
                        })
                        # Content might be empty or explanation
                        clean_content = response[:start].strip()
            except Exception as e:
                # Fallback to text
                pass
        
        msg = AIMessage(content=clean_content, tool_calls=tool_calls)
        generation = ChatGeneration(message=msg)
        return ChatResult(generations=[generation])

    def bind_tools(self, tools: list[Any], **kwargs: Any) -> Any:
        """Bind tools to the model. Returns a RunnableBinding."""
        # This allows DeepAgents to attach tools without crashing.
        # We return a new instance or binding. 
        # Standard LangChain way: return self.bind(tools=tools, **kwargs)
        return self.bind(tools=tools, **kwargs)

    @property
    def _llm_type(self) -> str:
        return "mlx-chat"

class MLXProvider:
    def __init__(self):
        self.model_path = settings.mlx_model

    def is_available(self) -> bool:
        # Check if running on macOS with Apple Silicon AND mlx_lm installed
        try:
            import mlx.core as mx
            import mlx_lm
            return mx.metal.is_available()
        except ImportError:
            return False

    def get_llm(self) -> Optional[BaseChatModel]:
        if not self.is_available():
            logger.warning("MLX (Apple Silicon) not available on this system.")
            return None
            
        try:
            logger.info(f"Initializing MLX LLM with model: {self.model_path}")
            # Fix: Pydantic models expect arguments or valid defaults. 
            # ChatMLX inherits from BaseChatModel (Pydantic V1/V2 hybrid in LangChain).
            # We must pass fields by name.
            return ChatMLX(model_path=self.model_path)
        except Exception as e:
            logger.error(f"Failed to initialize MLX LLM: {str(e)}")
            return None
