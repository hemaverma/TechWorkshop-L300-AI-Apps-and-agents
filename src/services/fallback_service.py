import time
import logging
from opentelemetry import trace
from azure.ai.agents.telemetry import trace_function
from utils.log_utils import log_timing

# Configure logging
logger = logging.getLogger(__name__)

# Get tracer for telemetry
tracer = trace.get_tracer(__name__)

def call_fallback(llm_client, fallback_prompt: str, gpt_deployment = "gpt-5-mini"):
    """Call the fallback model and return its reply."""
    start_time = time.time()
    
    chat_prompt = [    
        {
            "role": "system",      
            "content": 
            [           
                {               
                    "type": "text",               
                    "text": fallback_prompt           
                }       
            ]   
        }]

    messages = chat_prompt
    completion = llm_client.chat.completions.create(
        model=gpt_deployment,
        messages=messages,
        temperature=0.7,
        stream=False)
    result = completion.choices[0].message.content
    log_timing("Fallback Call", start_time, f"Model: {gpt_deployment}")
    return result

@trace_function
def cora_fallback(llm_client, fallback_prompt: str, gpt_deployment = "Phi-4"):
    """Call the fallback model for cora and return its reply."""
    start_time = time.time()
    logger.info(f"Calling Cora fallback with phi-4 model (deployment: {gpt_deployment})")
    
    chat_prompt = [    
        {
            "role": "system",      
            "content": 
            [           
                {               
                    "type": "text",               
                    "text": fallback_prompt           
                }       
            ]   
        }]

    messages = chat_prompt
    completion = llm_client.chat.completions.create(
        model=gpt_deployment,
        messages=messages,
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        stream=False)
    result = completion.choices[0].message.content
    
    # Log structured data about the phi-4 call
    execution_time = time.time() - start_time
    logger.info(
        f"Phi-4 Cora fallback completed",
        extra={
            "model": gpt_deployment,
            "execution_time_seconds": execution_time,
            "prompt_tokens": completion.usage.prompt_tokens if completion.usage else None,
            "completion_tokens": completion.usage.completion_tokens if completion.usage else None,
            "total_tokens": completion.usage.total_tokens if completion.usage else None,
            "temperature": 0.7,
            "top_p": 0.95,
        }
    )
    
    log_timing("Cora Fallback Call", start_time, f"Model: {gpt_deployment}")
    return result