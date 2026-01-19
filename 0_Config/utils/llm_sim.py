import os
import google.generativeai as genai
import time
import threading
import collections

# Initialize locks and history for thread-safe rate limiting
rate_limit_lock = threading.Lock()
request_timestamps = collections.deque() # For RPM: stores timestamps of successful requests
token_usage_history = collections.deque() # For TPM: stores (timestamp, token_count) tuples

RPM_LIMIT = 10 # Requests Per Minute
TPM_LIMIT = 200000 # Tokens Per Minute

# Calculate intervals
RPM_WINDOW_SECONDS = 60 # 1 minute window for RPM
TPM_WINDOW_SECONDS = 60 # 1 minute window for TPM

def llm_call(prompt: str, api_key: str = None) -> str:
    """
    Calls the Gemini API using the SDK and returns its output.
    Enforces local rate limits of 10 RPM and 250k TPM.
    Accepts an optional api_key parameter which overrides the environment variable.
    """
    global request_timestamps, token_usage_history

    # Configure API key
    if api_key:
        genai.configure(api_key=api_key)
    else:
        env_api_key = os.environ.get("GEMINI_API_KEY")
        if not env_api_key:
            return "Error: GEMINI_API_KEY environment variable not set and no API key provided."
        genai.configure(api_key=env_api_key)


    # Use the correct model name as identified from genai.list_models()
    model_name = "models/gemini-2.5-flash"
    model = genai.GenerativeModel(model_name)

    with rate_limit_lock:
        current_time = time.time()

        # --- RPM Enforcement ---
        # Remove requests older than 1 minute
        while request_timestamps and request_timestamps[0] <= current_time - RPM_WINDOW_SECONDS:
            request_timestamps.popleft()

        time_to_wait_rpm = 0
        if len(request_timestamps) >= RPM_LIMIT:
            # Calculate when the oldest request will "expire"
            time_to_wait_rpm = request_timestamps[0] + RPM_WINDOW_SECONDS - current_time
        
        # --- TPM Enforcement ---
        prompt_token_count = 0
        try:
            # Use count_tokens for accurate estimation of tokens *before* sending
            prompt_token_count = model.count_tokens(prompt).total_tokens
        except Exception as e:
            return f"Error counting tokens for prompt: {e}"

        # Remove token usages older than 1 minute
        while token_usage_history and token_usage_history[0][0] <= current_time - TPM_WINDOW_SECONDS:
            token_usage_history.popleft()
        
        current_token_sum = sum(item[1] for item in token_usage_history)

        time_to_wait_tpm = 0
        if current_token_sum + prompt_token_count > TPM_LIMIT:
            # We need to wait until enough tokens expire
            needed_to_expire = (current_token_sum + prompt_token_count) - TPM_LIMIT
            
            expired_tokens_needed = 0
            for timestamp, tokens in token_usage_history:
                expired_tokens_needed += tokens
                if expired_tokens_needed >= needed_to_expire:
                    # This timestamp is the one whose expiry will free enough tokens
                    time_to_wait_tpm = timestamp + TPM_WINDOW_SECONDS - current_time
                    break
            # If after iterating, we still need to wait (e.g., all tokens are new), wait for a full window from now
            if time_to_wait_tpm <= 0 and current_token_sum + prompt_token_count > TPM_LIMIT:
                time_to_wait_tpm = TPM_WINDOW_SECONDS # Wait for a full minute to reset (approx)
        
        # Ensure wait times are not negative
        time_to_wait_rpm = max(0, time_to_wait_rpm)
        time_to_wait_tpm = max(0, time_to_wait_tpm)
        
        # Wait for the longest required time from either RPM or TPM
        time_to_wait = max(time_to_wait_rpm, time_to_wait_tpm)
        if time_to_wait > 0:
            time.sleep(time_to_wait)
        
        # Recalculate current_time after waiting
        current_time = time.time()

        try:
            response = model.generate_content(prompt)
            # Record successful request (after potential waiting and actual API call)
            request_timestamps.append(current_time)
            token_usage_history.append((current_time, prompt_token_count)) # Use prompt_token_count for tokens sent

            # The API response structure can vary, check for common attributes
            if hasattr(response, 'text'):
                return response.text.strip()
            elif hasattr(response, 'parts') and response.parts:
                return "".join(part.text for part in response.parts if hasattr(part, 'text')).strip()
            else:
                return f"Error: Unexpected API response format: {response}"
        except Exception as e:
            # Even if API call fails, we still consider it a request for RPM/TPM purposes as the tokens were sent
            request_timestamps.append(current_time) 
            token_usage_history.append((current_time, prompt_token_count)) # Still count tokens as they were sent
            return f"Error calling Gemini API: {e}"