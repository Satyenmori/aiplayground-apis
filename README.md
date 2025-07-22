# Creating a new Environment

    python -m venv venv

    Activate the environment : 
    source venv/Scripts/activate

    deactivate the environment : 
    deactivate

# Install dependencies

    pip install -r requirements.txt

# Running the Code 
    python run.py












 # Endpoints

    POST /generate-code
    POST /generate-image
    POST /generate-post
    POST /text-completion


 # Ideal Request 
    
        {
        "platforms": {
            "openai": ["gpt-4", "gpt-3.5-turbo"]
        },
        "input": "Write a post about benefits of meditation.",
        "options": {
            "tone": "professional",
            "length": "short"
        },
        "history": []
        }

    
 # Response Format
 
    {
    "response": {
        "openai": [
        {"model": "gpt-4.1", "output": "...."},
        {"model": "gpt-4.0", "output": "...."}
        ],
        "gemini": [
        {"model": "gemini-pro", "output": "...."},
        {"model": "gemini-1.5", "output": "...."}
        ],
        "anthropic": [
        {"model": "claude-3-opus", "output": "...."},
        {"model": "claude-3-sonnet", "output": "...."}
        ]
    }
    }
        

  # Concepts
  
  Using 'oncurrent.futures.ThreadPoolExecutor' to make simultaneous API calls      