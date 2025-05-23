from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
import json
from .models import CodeSnippet, AIAssistance
import uuid
import os
import logging
from django.utils import timezone
import re

# Set up logging
logger = logging.getLogger(__name__)

# Initialize variables but don't create clients at import time
API_KEY = os.environ.get('OPENAI_API_KEY', None)
BASE_URL = os.environ.get('OPENAI_BASE_URL', "https://api.openai.com/v1")

# Global variable to store the most recently used API key
current_api_key = API_KEY

def get_openai_client(api_key=None):
    """
    Creates and returns an OpenAI client with the provided API key.
    Falls back to the most recently used API key if none is provided.
    
    Args:
        api_key (str, optional): The API key to use for the client. 
                                 If None, uses the most recently stored key.
    
    Returns:
        OpenAI: Configured OpenAI client or None if no valid API key is available
    """
    global current_api_key
    
    try:
        # Import OpenAI here to avoid import errors at module level
        from openai import OpenAI
        
        # If an API key is provided, store it for future use
        if api_key:
            # Store the API key for future calls
            current_api_key = api_key
            logger.debug(f"Using custom API key: {api_key[:5]}...{api_key[-5:] if len(api_key) > 10 else ''}")
            
            # Create a new client with the provided API key
            return OpenAI(
                api_key=api_key,
                base_url=BASE_URL
            )
        
        # If no API key is provided, use the most recently stored one
        if current_api_key:
            logger.debug("Using previously stored API key")
            return OpenAI(
                api_key=current_api_key,
                base_url=BASE_URL
            )
        else:
            logger.warning("No API key available for OpenAI client")
            return None
    except ImportError:
        logger.error("Failed to import OpenAI library")
        return None
    except Exception as e:
        logger.error(f"Error creating OpenAI client: {str(e)}")
        return None

def chat_with_gpt(prompt, chat_history, api_key=None):
    """
    Chats with GPT model using the provided prompt and chat history.
    
    Args:
        prompt (str): The user's prompt
        chat_history (list): List of previous chat messages
        api_key (str, optional): API key to use for this request
    
    Returns:
        str: The model's response
    """
    # Default response in case API is not available
    default_response = "I'm currently unable to process your request as the AI service is not available in this environment. Please try again later or contact support."
    
    messages = [
        {
            "role": "system",
            "content": ("You are a specialized code assistant. Your job is to help users troubleshoot and fix code errors, "
                        "generate new code based on requirements, and suggest improvements to increase efficiency. "
                        "Provide clear, step-by-step guidance and sample code where applicable. "
                        "You are also a specialized code assistant for Python, JavaScript, and C++, Java. "
                        "Your primary goal is to assist users in writing and debugging code in shortest and summarized response possible.")
        }
    ] + chat_history + [
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    try:
        # Check if we're running on Render or another cloud environment
        # where OpenAI API calls might fail or not be configured
        is_cloud_environment = os.environ.get('RENDER', False) or 'DYNO' in os.environ
        
        if is_cloud_environment and not api_key and not current_api_key:
            logger.warning("Running in cloud environment without API key, returning default response")
            return default_response
            
        # Get a client with the appropriate API key
        client = get_openai_client(api_key)
        
        if not client:
            logger.error("Failed to get OpenAI client, returning default response")
            return default_response
        
        # Determine model based on API key type
        model = "gpt-3.5-turbo"  # Default to a more widely available model
        
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=800,
            stream=False,
        )
        return completion.choices[0].message.content
    except Exception as e:
        error_message = str(e)
        logger.error(f"API Error: {error_message}")
        
        if "401" in error_message or "unauthorized" in error_message.lower() or "authentication" in error_message.lower():
            return "Error: Authentication failed. Your API key appears to be invalid or expired."
        
        # Return a generic error message for any other exception
        return default_response
        elif "rate limit" in error_message.lower() or "429" in error_message:
            return "Error: Rate limit exceeded. Please try again later."
        else:
            return f"Error: {error_message}"

# Create your views here.
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login_page')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def dashboard(request):
    user_snippets = CodeSnippet.objects.filter(owner=request.user).order_by('-created_at')
    context = {
        'snippets': user_snippets,
        'user': request.user
    }
    return render(request, 'deshboard.html', context)

@login_required
def create_code(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        language = request.POST.get('language')
        code_content = request.POST.get('code_content')
        user_input = request.POST.get('user_input', '')
        requirements = request.POST.get('requirements', '')
        
        # Create new code snippet
        snippet = CodeSnippet(
            title=title,
            description=description,
            language=language,
            code_content=code_content,
            user_input=user_input,
            requirements=requirements,
            owner=request.user
        )
        snippet.save()
        
        return redirect('code_detail', pk=snippet.id)
    
    # For GET requests, render the main.html template with the code editor
    languages = [choice[0] for choice in CodeSnippet._meta.get_field('language').choices]
    context = {
        'languages': languages,
        'user': request.user
    }
    return render(request, 'main.html', context)

@login_required
def code_detail(request, pk):
    snippet = get_object_or_404(CodeSnippet, pk=pk, owner=request.user)
    return render(request, 'code_detail.html', {'snippet': snippet})

def logout_view(request):
    logout(request)
    return redirect('home_page')

@login_required
def delete_code(request, pk):
    snippet = get_object_or_404(CodeSnippet, pk=pk, owner=request.user)
    if request.method == 'POST':
        snippet.delete()
        messages.success(request, f'Code "{snippet.title}" has been deleted successfully.')
    return redirect('dashboard')

def shared_code(request, pk):
    snippet = get_object_or_404(CodeSnippet, pk=pk)
    return render(request, 'shared_code.html', {'snippet': snippet})

@login_required
def chat_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            prompt = data.get('prompt')
            chat_history = data.get('chat_history', [])
            code_id = data.get('code_id')
            
            # Get API key from request headers if available
            api_key = None
            if 'X-OpenAI-API-Key' in request.headers:
                api_key = request.headers.get('X-OpenAI-API-Key')
            elif 'X-Github-Api-Key' in request.headers:
                api_key = request.headers.get('X-Github-Api-Key')
            
            if not prompt:
                return JsonResponse({'error': 'Prompt is required'}, status=400)
            
            # Get code snippet if ID is provided
            code_snippet = None
            if code_id:
                try:
                    code_snippet = CodeSnippet.objects.get(id=code_id)
                except CodeSnippet.DoesNotExist:
                    logger.warning(f"CodeSnippet with ID {code_id} not found")
            
            # Extract actual code content from the prompt for storage
            code_content = ""
            try:
                # Try to extract code from the prompt which typically follows a pattern like:
                # I'm working with the following code:
                # ```python
                # def hello():
                #     print("hello world")
                # ```
                code_match = re.search(r'```(?:\w+)?\n(.*?)\n```', prompt, re.DOTALL)
                if code_match:
                    code_content = code_match.group(1)
            except Exception as e:
                # If extraction fails, don't prevent the API from functioning
                logger.warning(f"Failed to extract code content: {str(e)}")
            
            # If no code snippet exists but user is querying about code, create a temporary one
            if not code_snippet and code_content and request.user.is_authenticated:
                # Try to determine language from the prompt
                language = 'python'  # Default
                language_match = re.search(r'```(\w+)', prompt)
                if language_match:
                    detected_lang = language_match.group(1).lower()
                    if detected_lang in ['python', 'py']:
                        language = 'python'
                    elif detected_lang in ['javascript', 'js']:
                        language = 'javascript'
                    elif detected_lang in ['cpp', 'c++']:
                        language = 'cpp'
                    elif detected_lang in ['java']:
                        language = 'java'
                
                try:
                    code_snippet = CodeSnippet.objects.create(
                        title=f"AI Chat Snippet - {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}",
                        language=language,
                        owner=request.user,
                        code_content=code_content
                    )
                except Exception as e:
                    logger.error(f"Failed to create CodeSnippet: {str(e)}")
            
            # Pass the API key from the headers to the chat_with_gpt function
            response = chat_with_gpt(prompt, chat_history, api_key)
            
            # Create AIAssistance record if possible
            try:
                if request.user.is_authenticated:
                    AIAssistance.objects.create(
                        user=request.user,
                        code=code_snippet,  # This can be None
                        prompt=prompt,
                        response=response
                    )
            except Exception as e:
                logger.error(f"Failed to create AIAssistance record: {str(e)}")
            
            return JsonResponse({
                'response': response
            })
        except Exception as e:
            logger.error(f"Error in chat_api: {str(e)}")
            return JsonResponse({
                'error': 'An error occurred while processing your request',
                'details': str(e) if settings.DEBUG else ''
            }, status=500)
    
    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
