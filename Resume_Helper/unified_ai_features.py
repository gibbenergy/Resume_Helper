"""
Unified AI Features - A class that provides AI-powered features using different providers.

This module combines the functionality of OpenAI and Google Gemini APIs into a single class.
"""

import os
import json
import logging
import uuid
import re
import requests
from typing import Dict, List, Optional, Union, Any, Tuple
from dotenv import load_dotenv
from enum import Enum

# OpenAI imports
import openai
from openai import OpenAI
from openai.types.chat import ChatCompletion
from openai import APIError, AuthenticationError, RateLimitError, APIConnectionError

from Resume_Helper.base_ai_provider import BaseAIProvider

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIProvider(Enum):
    """Enum for supported AI providers."""
    OPENAI = "openai"
    GEMINI = "gemini"

class UnifiedAIFeatures(BaseAIProvider):
    """
    A class that provides AI-powered features for resume optimization using different AI providers.
    """
    
    # OpenAI constants
    OPENAI_DEFAULT_MODEL = "gpt-4o"
    OPENAI_AVAILABLE_MODELS = [
        "gpt-4o",
        "gpt-4o-mini-2024-07-18",
        "gpt-4.1-2025-04-14",
        "o3-2025-04-16"
    ]
    
    # Gemini constants
    GEMINI_DEFAULT_MODEL = "Gemini 2.0 Flash"
    GEMINI_AVAILABLE_MODELS = [
        "Gemini 2.0 Flash", 
        "Gemini 2.0 Flash Lite",
        "Gemini 2.0 Pro",
        "Gemini 1.5 Pro",
        "Gemini 1.5 Flash"
    ]
    GEMINI_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
    
    # Gemini model mapping to API endpoints
    GEMINI_MODEL_MAPPING = {
        "Gemini 2.0 Flash": "gemini-2.0-flash",
        "Gemini 2.0 Flash Lite": "gemini-2.0-flash-lite",
        "Gemini 2.0 Pro": "gemini-2.0-pro",
        "Gemini 1.5 Pro": "gemini-1.5-pro",
        "Gemini 1.5 Flash": "gemini-1.5-flash"
    }
    
    def __init__(self, provider: str = "gemini", api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the UnifiedAIFeatures class.
        
        Args:
            provider: The AI provider to use ("openai" or "gemini").
            api_key: API key for the selected provider. If None, tries to get it from environment variables.
            model: The model to use for the selected provider.
        """
        self.provider = AIProvider(provider.lower()) if isinstance(provider, str) else provider
        
        # Set default model based on provider
        if model is None:
            self.model = self.OPENAI_DEFAULT_MODEL if self.provider == AIProvider.OPENAI else self.GEMINI_DEFAULT_MODEL
        else:
            self.model = model
        
        # Set API key based on provider
        if api_key is None:
            if self.provider == AIProvider.OPENAI:
                self.api_key = os.getenv("OPENAI_API_KEY", "")
            else:  # GEMINI
                self.api_key = os.getenv("GEMINI_API_KEY", "")
        else:
            self.api_key = api_key
        
        # Initialize clients
        self.openai_client = None
        
        # Set up client if API key is available
        if self.api_key:
            if self.provider == AIProvider.OPENAI:
                self.setup_openai_client()
    
    def setup_openai_client(self):
        """Set up the OpenAI client with the current API key."""
        try:
            self.openai_client = OpenAI(api_key=self.api_key)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {str(e)}")
            self.openai_client = None
    
    def set_provider(self, provider: str) -> str:
        """
        Set the AI provider to use.
        
        Args:
            provider: The provider to use ("openai" or "gemini").
            
        Returns:
            A message indicating success or failure.
        """
        try:
            self.provider = AIProvider(provider.lower())
            
            # Update model to default for the new provider if current model isn't compatible
            if self.provider == AIProvider.OPENAI and self.model not in self.OPENAI_AVAILABLE_MODELS:
                self.model = self.OPENAI_DEFAULT_MODEL
            elif self.provider == AIProvider.GEMINI and self.model not in self.GEMINI_AVAILABLE_MODELS:
                self.model = self.GEMINI_DEFAULT_MODEL
                
            logger.info(f"Provider set to {self.provider.value}")
            return f"Provider set to {self.provider.value}"
        except ValueError:
            logger.error(f"Invalid provider: {provider}")
            return f"Invalid provider: {provider}. Available providers: openai, gemini"
    
    def set_api_key(self, api_key: str) -> str:
        """
        Set the API key for the current provider.
        
        Args:
            api_key: The API key to use.
            
        Returns:
            A message indicating success or failure.
        """
        self.api_key = api_key
        
        if self.provider == AIProvider.OPENAI:
            self.setup_openai_client()
            # Test the API key
            return self.test_api_key(api_key, self.model)
        else:  # GEMINI
            # Test the API key with a simple request
            return self.test_api_key(api_key, self.model)
    
    def get_provider_name(self) -> str:
        """
        Get the name of the current AI provider.
        
        Returns:
            The name of the current AI provider.
        """
        return self.provider.value
    
    def get_available_models(self) -> List[str]:
        """
        Get a list of available models for the current provider.
        
        Returns:
            A list of model names.
        """
        if self.provider == AIProvider.OPENAI:
            return self.OPENAI_AVAILABLE_MODELS
        else:  # GEMINI
            return self.GEMINI_AVAILABLE_MODELS
    
    def set_model(self, model_name: str) -> str:
        """
        Set the model to use for the current provider.
        
        Args:
            model_name: The name of the model to use.
            
        Returns:
            A message indicating success or failure.
        """
        # Check if the model is available for the current provider
        available_models = self.get_available_models()
        if model_name not in available_models:
            logger.error(f"Model {model_name} not available for provider {self.provider.value}")
            return f"Model {model_name} not available for provider {self.provider.value}. Available models: {', '.join(available_models)}"
        
        self.model = model_name
        logger.info(f"Model set to {model_name}")
        return f"Model set to {model_name}"
    
    def test_api_key(self, api_key: str, model: str) -> str:
        """
        Test if an API key is valid by making a simple API call.
        
        Args:
            api_key: The API key to test.
            model: The model to use for testing.
            
        Returns:
            A message indicating if the API key is valid.
        """
        request_id = str(uuid.uuid4())
        logger.info(f"[Request {request_id}] Testing API key for provider {self.provider.value}")
        
        if self.provider == AIProvider.OPENAI:
            # Create a temporary client with the provided API key
            temp_client = self.openai_client
            self.openai_client = OpenAI(api_key=api_key)
            
            # Test with a simple completion
            messages = [{"role": "user", "content": "Hello"}]
            
            # Call the OpenAI API
            response, error = self._call_openai_chat_completion(
                messages=messages, 
                request_id=request_id,
                max_tokens=5
            )
            
            # Restore the original client if there was an error
            if not response:
                self.openai_client = temp_client
                logger.error(f"[Request {request_id}] Invalid API key: {error}")
                return f"Invalid API key: {error}"
            
            # If successful, update the instance with the new API key
            self.api_key = api_key
            logger.info(f"[Request {request_id}] API key validated successfully")
            
            # Save API key to .env file
            try:
                with open(".env", "w") as f:
                    f.write(f"OPENAI_API_KEY={api_key}")
                logger.info(f"[Request {request_id}] API key saved to .env file")
                return "API key is valid and has been saved!"
            except Exception as e:
                logger.error(f"[Request {request_id}] Error saving API key to .env file: {str(e)}")
                return "API key is valid but could not be saved to .env file."
        
        else:  # GEMINI
            # Test with a simple request
            try:
                # Get the API model name
                api_model = self.GEMINI_MODEL_MAPPING.get(model, "gemini-2.0-flash")
                
                # Construct the API URL
                url = f"{self.GEMINI_API_BASE_URL}/{api_model}:generateContent?key={api_key}"
                
                # Prepare the request payload
                payload = {
                    "contents": [
                        {
                            "parts": [
                                {"text": "Hello, can you respond with a simple 'Hello, I'm working!' to verify the API is working?"}
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.2,
                        "maxOutputTokens": 10
                    }
                }
                
                # Make the API request
                response = requests.post(url, json=payload)
                
                # Check the response
                if response.status_code == 200:
                    # API key is valid
                    self.api_key = api_key
                    logger.info(f"[Request {request_id}] Gemini API key validated successfully")
                    
                    # Save API key to .env file
                    try:
                        with open(".env", "w") as f:
                            f.write(f"GEMINI_API_KEY={api_key}")
                        logger.info(f"[Request {request_id}] API key saved to .env file")
                        return "API key is valid and has been saved!"
                    except Exception as e:
                        logger.error(f"[Request {request_id}] Error saving API key to .env file: {str(e)}")
                        return "API key is valid but could not be saved to .env file."
                
                elif response.status_code == 400:
                    logger.error(f"[Request {request_id}] Bad request: {response.text}")
                    return f"Invalid request: {response.text}"
                
                elif response.status_code == 401:
                    logger.error(f"[Request {request_id}] Unauthorized: Invalid API key")
                    return "Invalid API key. Please check your API key and try again."
                
                elif response.status_code == 403:
                    logger.error(f"[Request {request_id}] Forbidden: {response.text}")
                    return f"Access denied: {response.text}"
                
                elif response.status_code == 404:
                    logger.error(f"[Request {request_id}] Model not found: {response.text}")
                    return f"Model not found: {response.text}"
                
                elif response.status_code == 429:
                    logger.error(f"[Request {request_id}] Rate limit exceeded: {response.text}")
                    return "Rate limit exceeded. Please try again later."
                
                else:
                    logger.error(f"[Request {request_id}] API error: {response.status_code} - {response.text}")
                    return f"API error: {response.status_code} - {response.text}"
                
            except Exception as e:
                logger.error(f"[Request {request_id}] Error testing API key: {str(e)}")
                return f"Error testing API key: {str(e)}"
    
    #######################
    # OpenAI API Methods #
    #######################
    
    def _call_openai_chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        request_id: str,
        model: Optional[str] = None,
        response_format: Optional[Dict[str, str]] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Tuple[Optional[ChatCompletion], Optional[str]]:
        """
        Call the OpenAI Chat Completion API with error handling.
        
        Args:
            messages: List of message dictionaries to send to the API.
            request_id: Unique identifier for tracking this specific request.
            model: The model to use (overrides instance model if provided).
            response_format: Format specification for the response.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature (0-2).
            
        Returns:
            A tuple containing (response, error) where response is the API response object
            and error is an error message string (or None if successful).
        """
        if not self.openai_client:
            if not self.api_key:
                return None, "OpenAI API key not provided"
            self.setup_openai_client()
            if not self.openai_client:
                return None, "Failed to initialize OpenAI client"
        
        # Use provided model or fall back to instance model
        model_to_use = model or self.model
        
        # Ensure we're using an OpenAI model
        if model_to_use not in self.OPENAI_AVAILABLE_MODELS:
            model_to_use = self.OPENAI_DEFAULT_MODEL
        
        try:
            # Prepare the API call parameters
            params = {
                "model": model_to_use,
                "messages": messages
            }
            
            # Add optional parameters if provided
            if response_format:
                params["response_format"] = response_format
            if max_tokens:
                params["max_tokens"] = max_tokens
            if temperature is not None:
                params["temperature"] = temperature
            
            # Log the API call
            logger.info(f"[Request {request_id}] Calling OpenAI API with model: {model_to_use}")
            
            # Make the API call
            response = self.openai_client.chat.completions.create(**params)
            
            # Log success
            logger.info(f"[Request {request_id}] OpenAI API call successful")
            
            return response, None
            
        except AuthenticationError as e:
            error_msg = f"Authentication error: {str(e)}"
            logger.error(f"[Request {request_id}] {error_msg}")
            return None, error_msg
            
        except RateLimitError as e:
            error_msg = f"Rate limit exceeded: {str(e)}"
            logger.error(f"[Request {request_id}] {error_msg}")
            return None, error_msg
            
        except APIConnectionError as e:
            error_msg = f"API connection error: {str(e)}"
            logger.error(f"[Request {request_id}] {error_msg}")
            return None, error_msg
            
        except APIError as e:
            error_msg = f"API error: {str(e)}"
            logger.error(f"[Request {request_id}] {error_msg}")
            return None, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"[Request {request_id}] {error_msg}")
            return None, error_msg
    
    def openai_prompt_function(
        self,
        messages: List[Dict[str, str]],
        request_id: Optional[str] = None,
        model: Optional[str] = None,
        response_format: Optional[Dict[str, str]] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Dict:
        """
        Execute a prompt function that expects a JSON response from OpenAI.
        
        Args:
            messages: List of message dictionaries to send to the API.
            request_id: Unique identifier for tracking this specific request.
            model: The model to use (overrides instance model if provided).
            response_format: Format specification for the response.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature (0-2).
            
        Returns:
            If successful, returns the parsed JSON response as a dictionary.
            If failed, returns a dictionary with an "error" key containing the error message.
        """
        # Generate a request ID if not provided
        req_id = request_id or str(uuid.uuid4())
        logger.info(f"[Request {req_id}] Starting OpenAI prompt function execution")
        
        # Call the OpenAI API
        response, error = self._call_openai_chat_completion(
            messages=messages,
            request_id=req_id,
            model=model or self.model,
            response_format=response_format,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Handle errors
        if error:
            logger.error(f"[Request {req_id}] Error in prompt_function: {error}")
            return {"error": error, "request_id": req_id}
        
        # Extract the response content
        try:
            content = response.choices[0].message.content
            
            # If we expect a JSON response, parse it
            if response_format and response_format.get("type") == "json_object":
                try:
                    # Parse the JSON response
                    result = json.loads(content)
                    logger.info(f"[Request {req_id}] Successfully parsed JSON response")
                    
                    # Add request_id to the result
                    if isinstance(result, dict):
                        result["request_id"] = req_id
                    
                    return result
                except json.JSONDecodeError as e:
                    logger.error(f"[Request {req_id}] Error parsing JSON response: {str(e)}")
                    return {"error": f"Error parsing JSON response: {str(e)}", "request_id": req_id}
            
            # If we don't expect a JSON response, return the content as is
            logger.info(f"[Request {req_id}] Successfully retrieved text response")
            return {"result": content, "request_id": req_id}
            
        except Exception as e:
            logger.error(f"[Request {req_id}] Error extracting response content: {str(e)}")
            return {"error": f"Error extracting response content: {str(e)}", "request_id": req_id}
    
    ######################
    # Gemini API Methods #
    ######################
    
    def _call_gemini_api(
        self,
        prompt: Union[str, List[Dict[str, str]]],
        request_id: str,
        model: Optional[str] = None,
        json_response: bool = False,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Call the Gemini API with error handling.
        
        Args:
            prompt: The prompt to send to the API. Can be a string or a list of message dictionaries.
            request_id: Unique identifier for tracking this specific request.
            model: The model to use (overrides instance model if provided).
            json_response: Whether to expect a JSON response.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature (0-1).
            
        Returns:
            A tuple containing (response_data, error) where response_data is the API response data
            and error is an error message string (or None if successful).
        """
        if not self.api_key:
            return None, "Gemini API key not provided"
        
        # Use provided model or fall back to instance model
        model_to_use = model or self.model
        
        # Get the API model name
        api_model = self.GEMINI_MODEL_MAPPING.get(model_to_use, "gemini-2.0-flash")
        
        # Construct the API URL
        url = f"{self.GEMINI_API_BASE_URL}/{api_model}:generateContent?key={self.api_key}"
        
        # Prepare the request payload
        if isinstance(prompt, str):
            # If prompt is a string, use it directly
            contents = [{"parts": [{"text": prompt}]}]
        else:
            # If prompt is a list of message dictionaries, convert it to Gemini format
            contents = []
            system_content = None
            
            # Extract system message if present
            for message in prompt:
                if message.get("role") == "system":
                    system_content = message.get("content")
                    break
            
            # Create a single content with all messages
            parts = []
            
            # Add system instruction as a user message if present
            if system_content:
                parts.append({"text": f"System instruction: {system_content}\n\n"})
            
            # Add user messages
            for message in prompt:
                if message.get("role") == "user":
                    parts.append({"text": f"User: {message.get('content')}\n\n"})
                elif message.get("role") == "assistant":
                    parts.append({"text": f"Assistant: {message.get('content')}\n\n"})
            
            # Add the parts to a single content
            contents.append({"role": "user", "parts": parts})
        
        # Prepare the generation config
        generation_config = {}
        if max_tokens:
            generation_config["maxOutputTokens"] = max_tokens
        if temperature is not None:
            generation_config["temperature"] = temperature
        
        # Add JSON instruction if needed
        if json_response:
            # Add JSON instruction to the prompt
            if contents and "parts" in contents[0]:
                # Insert JSON instruction at the beginning of the parts
                json_instruction = {"text": "You are an AI assistant that always responds in valid JSON format. Your responses must be valid JSON objects that can be parsed by JSON.parse().\n\n"}
                contents[0]["parts"].insert(0, json_instruction)
        
        # Prepare the final payload
        payload = {"contents": contents}
        if generation_config:
            payload["generationConfig"] = generation_config
        
        try:
            # Log the API call
            logger.info(f"[Request {request_id}] Calling Gemini API with model: {api_model}")
            
            # Make the API request
            response = requests.post(url, json=payload)
            
            # Check the response
            if response.status_code == 200:
                # Parse the response
                response_data = response.json()
                
                # Log success
                logger.info(f"[Request {request_id}] Gemini API call successful")
                
                return response_data, None
                
            elif response.status_code == 400:
                error_msg = f"Bad request: {response.text}"
                logger.error(f"[Request {request_id}] {error_msg}")
                return None, error_msg
                
            elif response.status_code == 401:
                error_msg = "Unauthorized: Invalid API key"
                logger.error(f"[Request {request_id}] {error_msg}")
                return None, error_msg
                
            elif response.status_code == 403:
                error_msg = f"Forbidden: {response.text}"
                logger.error(f"[Request {request_id}] {error_msg}")
                return None, error_msg
                
            elif response.status_code == 404:
                error_msg = f"Model not found: {response.text}"
                logger.error(f"[Request {request_id}] {error_msg}")
                return None, error_msg
                
            elif response.status_code == 429:
                error_msg = f"Rate limit exceeded: {response.text}"
                logger.error(f"[Request {request_id}] {error_msg}")
                return None, error_msg
                
            else:
                error_msg = f"API error: {response.status_code} - {response.text}"
                logger.error(f"[Request {request_id}] {error_msg}")
                return None, error_msg
                
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"[Request {request_id}] {error_msg}")
            return None, error_msg
    
    def gemini_prompt_function(
        self,
        messages: List[Dict[str, str]],
        request_id: Optional[str] = None,
        model: Optional[str] = None,
        response_format: Optional[Dict[str, str]] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Dict:
        """
        Execute a prompt function that expects a JSON response from Gemini.
        
        Args:
            messages: List of message dictionaries to send to the API.
            request_id: Unique identifier for tracking this specific request.
            model: The model to use (overrides instance model if provided).
            response_format: Format specification for the response (ignored for Gemini).
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature (0-1).
            
        Returns:
            If successful, returns the parsed JSON response as a dictionary.
            If failed, returns a dictionary with an "error" key containing the error message.
        """
        # Generate a request ID if not provided
        req_id = request_id or str(uuid.uuid4())
        logger.info(f"[Request {req_id}] Starting Gemini prompt function execution")
        
        # Determine if we expect a JSON response
        expect_json = response_format is not None and response_format.get("type") == "json_object"
        
        # Call the Gemini API
        response_data, error = self._call_gemini_api(
            prompt=messages,
            request_id=req_id,
            model=model or self.model,
            json_response=expect_json,
            max_tokens=max_tokens,
            temperature=temperature or 0.7
        )
        
        # Handle errors
        if error:
            logger.error(f"[Request {req_id}] Error in prompt_function: {error}")
            return {"error": error, "request_id": req_id}
        
        # Extract the response content
        try:
            # Navigate the Gemini response structure to get the text
            content = response_data["candidates"][0]["content"]["parts"][0]["text"]
            
            # If we expect a JSON response, parse it
            if expect_json:
                try:
                    # Try to extract JSON from the response
                    # First, try to find JSON within triple backticks
                    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
                    if json_match:
                        json_str = json_match.group(1)
                    else:
                        # If no triple backticks, use the whole response
                        json_str = content
                    
                    # Clean up the JSON string
                    json_str = json_str.strip()
                    
                    # Parse the JSON
                    result = json.loads(json_str)
                    logger.info(f"[Request {req_id}] Successfully parsed JSON response")
                    
                    # Add request_id to the result
                    if isinstance(result, dict):
                        result["request_id"] = req_id
                    
                    return result
                    
                except json.JSONDecodeError as e:
                    logger.error(f"[Request {req_id}] Error parsing JSON response: {str(e)}")
                    return {"error": f"Error parsing JSON response: {str(e)}", "content": content, "request_id": req_id}
            
            # If we don't expect a JSON response, return the content as is
            logger.info(f"[Request {req_id}] Successfully retrieved text response")
            return {"result": content, "request_id": req_id}
            
        except Exception as e:
            logger.error(f"[Request {req_id}] Error extracting response content: {str(e)}")
            return {"error": f"Error extracting response content: {str(e)}", "request_id": req_id}
    
    def prompt_function(
        self,
        messages: List[Dict[str, str]],
        request_id: Optional[str] = None,
        model: Optional[str] = None,
        response_format: Optional[Dict[str, str]] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Dict:
        """
        Execute a prompt function using the current provider.
        
        Args:
            messages: List of message dictionaries to send to the API.
            request_id: Unique identifier for tracking this specific request.
            model: The model to use (overrides instance model if provided).
            response_format: Format specification for the response.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature.
            
        Returns:
            If successful, returns the parsed response as a dictionary.
            If failed, returns a dictionary with an "error" key containing the error message.
        """
        if self.provider == AIProvider.OPENAI:
            return self.openai_prompt_function(
                messages=messages,
                request_id=request_id,
                model=model,
                response_format=response_format,
                max_tokens=max_tokens,
                temperature=temperature
            )
        else:  # GEMINI
            return self.gemini_prompt_function(
                messages=messages,
                request_id=request_id,
                model=model,
                response_format=response_format,
                max_tokens=max_tokens,
                temperature=temperature
            )
    
    #######################
    # Core AI Features    #
    #######################
    
    def analyze_job_description(self, job_description: str, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a job description to extract key information.
        
        Args:
            job_description: The job description text to analyze.
            model: Optional model override for this specific call.
            
        Returns:
            A dictionary containing the analysis results or an error message.
        """
        # Generate a unique request ID for this analysis
        request_id = str(uuid.uuid4())
        logger.info(f"[Request {request_id}] Analyzing job description")
        
        messages = [
            {"role": "system", "content": "You are a professional resume analyzer. Extract key information from job descriptions."},
            {"role": "user", "content": f"""
                Analyze this job description and extract the following information:
                1) Company name (CRITICAL - extract this precisely)
                2) Job position/title (CRITICAL - extract this precisely)
                3) Required skills
                4) Preferred skills
                5) Key responsibilities
                6) Required experience
                7) Keywords for ATS optimization
                
                Format the response as a JSON object with the following structure:
                {{
                    "company_name": "Extracted company name",
                    "job_position": "Extracted job position/title",
                    "required_skills": ["skill1", "skill2", ...],
                    "preferred_skills": ["skill1", "skill2", ...],
                    "key_responsibilities": ["responsibility1", "responsibility2", ...],
                    "required_experience": ["experience1", "experience2", ...],
                    "keywords": ["keyword1", "keyword2", ...]
                }}
                
                IMPORTANT INSTRUCTIONS FOR COMPANY NAME AND JOB POSITION:
                - For company_name: Extract the exact company name. Look for phrases like "at [Company]", "[Company] is looking for", etc.
                - For job_position: Extract the exact job title/position. Look for phrases like "seeking a [Position]", "hiring a [Position]", etc.
                - If you cannot determine with certainty, use "Unknown Company" or "Unknown Position" as the values.
                - DO NOT use generic placeholders like "the company" or "the position".
                
                Job Description:
                {job_description}
            """}
        ]
        
        # Use the prompt_function
        result = self.prompt_function(
            messages=messages, 
            request_id=request_id,
            model=model,
            response_format={"type": "json_object"}
        )
        
        # The prompt_function already handles JSON parsing and error handling
        if "error" in result:
            logger.error(f"[Request {request_id}] Error analyzing job description: {result['error']}")
        else:
            logger.info(f"[Request {request_id}] Job description analysis completed successfully")
            
        # Ensure request_id is included in the response
        if isinstance(result, dict) and "request_id" not in result:
            result["request_id"] = request_id
            
        return result
    
    def identify_relevant_skills(self, resume_data: Dict[str, Any], job_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify skills in the resume that are relevant to the job.
        
        Args:
            resume_data: The resume data.
            job_analysis: The job analysis data.
            
        Returns:
            A dictionary containing the relevant skills.
        """
        request_id = str(uuid.uuid4())
        logger.info(f"[Request {request_id}] Identifying relevant skills")
        
        # Extract skills from resume
        resume_skills = []
        if "skills" in resume_data and isinstance(resume_data["skills"], list):
            for skill in resume_data["skills"]:
                if isinstance(skill, list) and len(skill) >= 2:
                    skill_name = skill[1]
                    resume_skills.append(skill_name)
                elif isinstance(skill, dict) and "skill_name" in skill:
                    skill_name = skill["skill_name"]
                    resume_skills.append(skill_name)
        
        # Extract required skills from job analysis
        required_skills = []
        if "required_skills" in job_analysis and isinstance(job_analysis["required_skills"], list):
            required_skills = job_analysis["required_skills"]
        
        # Extract preferred skills from job analysis
        preferred_skills = []
        if "preferred_skills" in job_analysis and isinstance(job_analysis["preferred_skills"], list):
            preferred_skills = job_analysis["preferred_skills"]
        
        # Combine required and preferred skills
        job_skills = required_skills + preferred_skills
        
        # Create a prompt to identify relevant skills
        messages = [
            {"role": "system", "content": "You are a professional resume analyzer. Identify skills that are relevant to a job."},
            {"role": "user", "content": f"""
                Analyze these skills from a resume and identify which ones are relevant to the job requirements.
                
                Resume Skills:
                {json.dumps(resume_skills, indent=2)}
                
                Job Skills:
                {json.dumps(job_skills, indent=2)}
                
                Return a JSON object with the following structure:
                {{
                    "matching_skills": ["skill1", "skill2", ...],
                    "missing_skills": ["skill1", "skill2", ...],
                    "recommendations": "Recommendations for improving skills match"
                }}
            """}
        ]
        
        # Use the prompt_function
        skill_relevance = self.prompt_function(
            messages=messages,
            request_id=request_id,
            response_format={"type": "json_object"}
        )
        
        # Add request_id to the result
        if isinstance(skill_relevance, dict) and "request_id" not in skill_relevance:
            skill_relevance["request_id"] = request_id
        
        return skill_relevance
    
    def generate_cover_letter(self, resume_data: Dict[str, Any], job_description: str, model: Optional[str] = None, user_prompt: Optional[str] = None) -> str:
        """
        Generate a cover letter based on the resume and job description.
        
        Args:
            resume_data: The resume data.
            job_description: The job description text.
            model: Optional model override for this specific call.
            user_prompt: Optional user instructions for customizing the cover letter.
            
        Returns:
            The generated cover letter text.
        """
        request_id = str(uuid.uuid4())
        logger.info(f"[Request {request_id}] Generating cover letter")
        
          # 1. Analyse the JD
        job_analysis = self.analyze_job_description(job_description, model)
        if "error" in job_analysis:
            logger.error(f"[{request_id}] JD analysis error: {job_analysis['error']}")
            return {"error": f"Error analysing JD: {job_analysis['error']}"}

        # 2. Work out résumé ↔ JD skill intersection 
        skill_filter = self.identify_relevant_skills(resume_data, job_analysis)
        matching_skills = skill_filter.get("matching_skills", [])
        missing_skills  = skill_filter.get("missing_skills", [])

        # Extract personal information
        name = ""
        email = ""
        phone = ""
        if "personal_info" in resume_data:
            personal_info = resume_data["personal_info"]
            if isinstance(personal_info, dict):
                name = personal_info.get("name", "")
                email = personal_info.get("email", "")
                phone = personal_info.get("phone", "")
            elif isinstance(personal_info, list) and len(personal_info) >= 3:
                name = personal_info[0]
                email = personal_info[1]
                phone = personal_info[2]
        
        # Extract company name and job position from job analysis
        company_name = "Unknown Company"
        job_position = "Unknown Position"
        
        # Try to extract company and position from job analysis if available
        if isinstance(job_analysis, dict):
            company_name = job_analysis.get("company_name", "Unknown Company")
            job_position = job_analysis.get("job_position", "Unknown Position")
            
            # If the values are still default or empty, try to extract from the job description
            if company_name in ["Unknown Company", "the company", ""] and job_description:
                # Look for company name in the job description
                company_matches = re.findall(r'at\s+([A-Z][A-Za-z0-9\s&]+)[\.,]', job_description)
                company_matches += re.findall(r'([A-Z][A-Za-z0-9\s&]+)\s+is\s+(?:looking|hiring|seeking)', job_description)
                if company_matches:
                    company_name = company_matches[0].strip()
            
            if job_position in ["Unknown Position", "the position", ""] and job_description:
                # Look for job position in the job description
                position_matches = re.findall(r'((?:Senior|Junior|Lead|Principal|Staff)?\s*[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*\s+(?:Engineer|Developer|Programmer|Analyst|Manager|Director|Specialist))', job_description)
                if position_matches:
                    job_position = position_matches[0].strip()
        
        # Create a prompt for generating a cover letter
        system_content = ("You are a professional cover-letter writer. The letter must be 100 % truthful—never introduce achievements or skills not present in the résumé.")

        
        user_content = f"""
                Generate a professional cover letter for the following:
                
                Applicant: {name}
                Email: {email}
                Phone: {phone}
                
                Job Position: {job_position}
                Company: {company_name}
                
                Job Description:
                {job_description}

                Résumé–JD matching skills (may cite freely):
                {json.dumps(matching_skills, indent=2)}

                JD skills missing from résumé (may acknowledge as growth areas, **do not claim mastery**):
                {json.dumps(missing_skills, indent=2)}
                
                Resume Data:
                {json.dumps(resume_data, indent=2)}               
                                
                The cover letter should:
                1. Have a compelling introduction that mentions the specific position
                2. Highlight **only** the “matching skills” above, phrasing them so they echo JD wording.
                3. If crucial JD skills are in “missing_skills”, you may mention eagerness to develop them, but never state or imply current mastery.
                4. Explain why the applicant is a good fit for the role
                5. Include a strong closing paragraph
                6. Be concise (300-400 words)
                
                IMPORTANT: 
                - DO NOT invent qualifications, tools or degrees absent from the résumé.
                - DO NOT include any placeholders like [Your Email], [Company Address], etc.
                - DO NOT include header information (name, address, date, etc.) - this will be added automatically
                - DO NOT include recipient information (company name, address, etc.) - this will be added automatically"""
                
        # Add user's custom instructions if provided
        if user_prompt and user_prompt.strip():
            logger.info(f"[Request {request_id}] Including user prompt in cover letter generation: {user_prompt}")
            user_content += f"""
                
                IMPORTANT - User's custom instructions: 
                {user_prompt}
                
                Please incorporate these instructions when crafting the cover letter."""
                
        # Add final instructions to user content
        user_content += """
                - DO NOT include a greeting line (Dear Hiring Manager, etc.) - this will be added automatically
                - DO NOT include a signature - this will be added automatically
                - ONLY return the body content of the cover letter, starting with the first paragraph
                
                Return ONLY the body content of the cover letter.
        """
        
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]
        
        # Use the prompt_function
        cover_letter_result = self.prompt_function(
            messages=messages,
            request_id=request_id,
            max_tokens=1000
        )
        
        # Extract the cover letter text
        if "error" in cover_letter_result:
            logger.error(f"[Request {request_id}] Error generating cover letter: {cover_letter_result['error']}")
            return f"Error generating cover letter: {cover_letter_result['error']}"
        
        # Extract the content from the result
        cover_letter = cover_letter_result.get("result", "")
        
        # Post-process the cover letter
        cover_letter = self.post_process_cover_letter(cover_letter, request_id)
        
        # Create a structured response with company name and job position
        # Use the values we already extracted earlier in the method
        response = {
            "body_content": cover_letter,
            "company_name": company_name,
            "job_position": job_position,
            "letter_title": f"Application for {job_position} Position" if job_position not in ["Unknown Position", "the position"] else "Job Application",
            "recipient_greeting": f"Dear Hiring Manager at {company_name}," if company_name not in ["Unknown Company", "the company"] else "Dear Hiring Manager,",
            "request_id": request_id
        }
        
        logger.info(f"[Request {request_id}] Cover letter generated successfully")
        return response
    
    def post_process_cover_letter(self, cover_letter: str, request_id: str) -> str:
        """
        Fix common issues in generated cover letters and remove redundant placeholders.
        
        Args:
            cover_letter: The generated cover letter text
            request_id: Request ID for logging
            
        Returns:
            Processed cover letter text
        """
        logger.info(f"[Request {request_id}] Post-processing cover letter")
        
        # Remove markdown formatting if present
        cover_letter = re.sub(r'```.*?\n', '', cover_letter)
        cover_letter = re.sub(r'```', '', cover_letter)
        
        # Remove any greeting lines that might have been included
        greeting_patterns = [
            r'^Dear Hiring Manager,?\s*\n',
            r'^Dear Hiring Team,?\s*\n',
            r'^Dear Recruiter,?\s*\n',
            r'^Dear Sir/Madam,?\s*\n',
            r'^Dear [^,\n]+,?\s*\n',  # Matches any greeting with a name
            r'^To Whom It May Concern:?\s*\n',
        ]
        
        for pattern in greeting_patterns:
            cover_letter = re.sub(pattern, '', cover_letter, flags=re.IGNORECASE | re.MULTILINE)
        
        # Remove any header information that might have been included
        header_patterns = [
            r'^.*?\n.*?\n.*?\n.*?\n.*?\n\n',  # Typical 5-line header with blank line after
            r'^[A-Za-z]+ [A-Za-z]+\n.*?\n.*?\n',  # Name and address pattern
            r'^\d{1,2}/\d{1,2}/\d{2,4}\n',  # Date at the beginning
            r'^[A-Za-z]+ \d{1,2}, \d{4}\n',  # Date format 
        ]
        
        # Only apply header removal if it looks like there's a header
        first_lines = cover_letter.split('\n')[:6]
        if any('address' in line.lower() for line in first_lines) or \
           any('email' in line.lower() for line in first_lines) or \
           any('phone' in line.lower() for line in first_lines) or \
           any(re.match(r'^[A-Za-z]+ \d{1,2}, \d{4}$', line) for line in first_lines):
            for pattern in header_patterns:
                cover_letter = re.sub(pattern, '', cover_letter, flags=re.IGNORECASE | re.MULTILINE)
        
        # Remove redundant placeholders - more comprehensive list
        placeholder_patterns = [
            r'\[Your Name\].*?\n',
            r'\[Your Address\].*?\n',
            r'\[City, State, Zip Code\].*?\n',
            r'\[Your Email\].*?\n',
            r'\[Your Email Address\].*?\n',
            r'\[Email\].*?\n',
            r'\[Your Phone\].*?\n',
            r'\[Your Phone Number\].*?\n',
            r'\[Phone\].*?\n',
            r'\[Your LinkedIn\].*?\n',
            r'\[Your LinkedIn Profile\].*?\n',
            r'\[Your LinkedIn Profile URL\].*?\n',
            r'\[LinkedIn\].*?\n',
            r'\[Date\].*?\n',
            r'\[Today\'s Date\].*?\n',
            r'\[Current Date\].*?\n',
            r'\[Recipient Name\].*?\n',
            r'\[Recipient Title\].*?\n',
            r'\[Hiring Manager\].*?\n',
            r'\[Hiring Manager Name\].*?\n',
            r'\[Company Name\].*?\n',
            r'\[Company\].*?\n',
            r'\[Company Address\].*?\n',
            r'\[Company Address - if known, otherwise omit\].*?\n',
            r'\[Company Address - if known\].*?\n',
            r'\[Address\].*?\n',
            r'\[City, State ZIP\].*?\n',
            r'\[City, State\].*?\n',
            r'Hiring Team\n',
            r'Hiring Manager\n'
            
        ]
        
        for pattern in placeholder_patterns:
            cover_letter = re.sub(pattern, '', cover_letter, flags=re.IGNORECASE)
        
        # Remove any closing/signature that might have been included
        closing_patterns = [
            r'\nSincerely,\s*\n.*?$',
            r'\nBest regards,\s*\n.*?$',
            r'\nRegards,\s*\n.*?$',
            r'\nThank you,\s*\n.*?$',
            r'\nYours sincerely,\s*\n.*?$',
            r'\nYours truly,\s*\n.*?$',
            r'\nRespectfully,\s*\n.*?$',
        ]
        
        for pattern in closing_patterns:
            cover_letter = re.sub(pattern, '', cover_letter, flags=re.IGNORECASE)
        
        # Fix multiple newlines
        cover_letter = re.sub(r'\n{3,}', '\n\n', cover_letter)
        
        # Fix spacing after periods
        cover_letter = re.sub(r'\.(?! |\n)', '. ', cover_letter)
        
        # Fix spacing after commas
        cover_letter = re.sub(r',(?! |\n)', ', ', cover_letter)
        
        # Trim whitespace at beginning and end
        cover_letter = cover_letter.strip()
        
        logger.info(f"[Request {request_id}] Cover letter post-processing completed")
        return cover_letter
    
    def validate_and_correct_cover_letter(self, cover_letter: str, resume_data: Dict[str, Any], job_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and correct a cover letter.
        
        Args:
            cover_letter: The cover letter text.
            resume_data: The resume data.
            job_analysis: The job analysis data.
            
        Returns:
            A dictionary containing the corrected cover letter and validation notes.
        """
        request_id = str(uuid.uuid4())
        logger.info(f"[Request {request_id}] Validating and correcting cover letter")
        
        # Create a prompt for validating and correcting the cover letter
        messages = [
            {"role": "system", "content": "You are a professional editor. Review and improve cover letters."},
            {"role": "user", "content": f"""
                Review and improve this cover letter. Check for:
                1. Grammar and spelling errors
                2. Professional tone and language
                3. Relevance to the job requirements
                4. Appropriate length and structure
                
                Cover Letter:
                {cover_letter}
                
                Job Analysis:
                {json.dumps(job_analysis, indent=2)}
                
                Return a JSON object with the following structure:
                {{
                    "corrected_cover_letter": "The corrected cover letter text",
                    "improvements_made": ["Improvement 1", "Improvement 2", ...],
                    "overall_assessment": "Brief assessment of the cover letter quality"
                }}
            """}
        ]
        
        # Use the prompt_function
        validation_result = self.prompt_function(
            messages=messages,
            request_id=request_id,
            response_format={"type": "json_object"}
        )
        
        # Add request_id to the result
        if isinstance(validation_result, dict) and "request_id" not in validation_result:
            validation_result["request_id"] = request_id
        
        return validation_result
    
    def tailor_resume(
        self,
        resume_data: Dict,
        job_description: str,
        model: Optional[str] = None,
    ) -> Dict:
        """
        Tailor a résumé to a job description, then copy-edit it.
        Returns the final JSON résumé or {"error": …}.
        """
        request_id = str(uuid.uuid4())
        logger.info(f"[Request {request_id}] Tailoring résumé")

        # 1. Analyse the JD
        job_analysis = self.analyze_job_description(job_description, model)
        if "error" in job_analysis:
            logger.error(f"[Request {request_id}] JD analysis failed: {job_analysis['error']}")
            return {"error": f"Error analysing JD: {job_analysis['error']}",
                    "request_id": request_id}

        # 2. Tailor pass
        tailor_messages = [
            {
                "role": "system",
                "content": (
                    "You are a professional résumé writer. Keep the résumé 100 % factual, and do **not delete** any section or entry."
                ),
            },
            {
                "role": "user",
                "content": f"""
    Tailor this résumé to better match the job description.  Focus on:
    1. Highlighting relevant skills and experience
    2. Introducing exact JD keywords **only when the résumé already evidences the
    same or a clearly synonymous skill/technique**  
    – e.g. JD says “deep learning”; résumé shows an LSTM project ⇒ “deep-learning (LSTM)” is OK  
    – if no supporting evidence exists, do NOT add the keyword
    3. **Re-order** or re-phrase content for relevance, **but keep every original  entry.**
    4. Refining the summary/objective to underscore existing, verifiable strengths
    that align with the role; **never invent new achievements, titles, or skills**

    Résumé JSON:
    {json.dumps(resume_data, indent=2)}

    Job description:
    {job_description}

    Job analysis (for convenience):
    {json.dumps(job_analysis, indent=2)}

    Return ONLY the tailored résumé as JSON (same schema as input).
    """,
            },
        ]

        first_pass = self.prompt_function(
            messages=tailor_messages,
            request_id=request_id,
            model=model,
            response_format={"type": "json_object"},
            max_tokens=10000
        )

        if "error" in first_pass:
            logger.error(f"[Request {request_id}] Tailoring error: {first_pass['error']}")
            return {"error": f"Error tailoring résumé: {first_pass['error']}",
                    "request_id": request_id}

        # 3. Copy-edit pass
        tailored_json_str = json.dumps(first_pass, ensure_ascii=False, indent=2)

        proof_messages = [
            {
                "role": "system",
                "content": (
                    "You are a meticulous copy-editor. Fix spelling, grammar, punctuation, "
                    "and style only; do NOT alter factual content or field names."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Return the same JSON with language corrections only:\n\n"
                    f"{tailored_json_str}"
                ),
            },
        ]

        proof_pass = self.prompt_function(
            messages=proof_messages,
            request_id=request_id,
            model=model,
            response_format={"type": "json_object"},
            max_tokens=10000
        )

        if "error" in proof_pass:
            logger.error(f"[Request {request_id}] Proof-read error: {proof_pass['error']}")
            return {"error": f"Error during proof-reading: {proof_pass['error']}",
                    "request_id": request_id}

        # 4. Success
        if "request_id" not in proof_pass:
            proof_pass["request_id"] = request_id

        logger.info(f"[Request {request_id}] Résumé tailored and proof-read successfully")
        return proof_pass

    
    def get_improvement_suggestions(self, resume_data: Dict, job_description: str, model: Optional[str] = None) -> str:
        """
        Get suggestions for improving a resume based on a job description.
        
        Args:
            resume_data: The resume data as a dictionary.
            job_description: The job description to compare the resume against.
            model: Optional model override for this specific call.
            
        Returns:
            A string containing improvement suggestions or an error message.
        """
        # Generate a unique request ID for this request
        request_id = str(uuid.uuid4())
        logger.info(f"[Request {request_id}] Getting resume improvement suggestions")
        
        try:
            # Create a prompt for getting improvement suggestions
            messages = [
                {"role": "system", "content": "You are a professional resume coach. Provide specific, actionable suggestions to improve resumes."},
                {"role": "user", "content": f"""
                    Review this resume against the job description and provide specific improvement suggestions. Focus on:
                    1. Content gaps compared to job requirements
                    2. Skills that should be highlighted or added
                    3. Experience that should be emphasized or reframed
                    4. Overall resume structure and formatting
                    5. ATS optimization suggestions
                    
                    Resume Data:
                    {json.dumps(resume_data, indent=2)}
                    
                    Job Description:
                    {job_description}
                    
                    Provide detailed, actionable suggestions organized by category.
                """}
            ]
            
            # Use the prompt_function
            result = self.prompt_function(
                messages=messages,
                request_id=request_id,
                model=model,
                max_tokens=1000
            )
            
            # Check for errors
            if "error" in result:
                logger.error(f"[Request {request_id}] Error getting improvement suggestions: {result['error']}")
                return f"Error getting improvement suggestions: {result['error']}"
            
            # Extract the suggestions
            suggestions = result.get("result", "")
            
            logger.info(f"[Request {request_id}] Resume improvement suggestions generated successfully")
            return suggestions
            
        except Exception as e:
            error_msg = f"Unexpected error getting improvement suggestions: {str(e)}"
            logger.error(f"[Request {request_id}] {error_msg}")
            return error_msg