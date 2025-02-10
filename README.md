# Cocktail Advisor Chat

Cocktail Advisor Chat is a FastAPI-based chat application that leverages a LangChain agent to answer questions about cocktails. The system integrates a vector database (FAISS) to maintain personalized conversation history for each user. The chat frontend is built using Bootstrap for a modern, responsive design and includes smooth animations and loading spinners.

## Features

- **LLM Integration**: Utilizes OpenAI's GPT-4 (via LangChain) to provide expert answers on cocktails.
- **Personalized History**: Each user has an individual FAISS vector store that maintains the conversation history.
- **Retrieval-Augmented Generation (RAG)**: The agent retrieves relevant past messages from the user’s history to provide context-aware answers.
- **Custom Prompts**: All system and tool prompts are stored in a JSON file (`data/prompts.json`) for easy configuration.
- **Modular Architecture**: The project is structured into modules—`AgentFabric` for agent logic and `app` (with `routes`) for the server—making the code easy to maintain and extend.
- **Responsive UI**: The chat interface uses Bootstrap and custom CSS/JavaScript for a clean, mobile-friendly design with smooth animations and a loading spinner.

## Project Structure

project/ ├── AgentFabric/ │ ├── init.py │ ├── agent.py # Agent logic including LLM integration and FAISS history handling │ ├── factory.py # Factory for creating the agent instance │ └── tools.py # Additional tools (e.g., Anthropic LLM tool for message enhancement) ├── app/ │ ├── init.py │ ├── config.py # Application configuration and environment variable loading │ ├── main.py # Application entry point (startup, mounting static files, etc.) │ └── routes/ │ ├── init.py │ └── chat.py # Chat-related endpoints (GET/POST) ├── data/ │ ├── prompts.json # JSON file containing all system prompts and tool descriptions │ └── cocktails.csv # CSV data file with cocktail information ├── static/ │ ├── css/ │ │ └── style.css # Custom CSS (integrated with Bootstrap) │ └── js/ │ └── script.js # Custom JavaScript for chat interactions and animations ├── templates/ │ └── index.html # HTML template for the chat interface ├── .env # Environment variables file (API keys, etc.) ├── requirements.txt # Python package dependencies └── README.md # This file

bash
Copy

## Installation and Running Locally

### Prerequisites

- Python 3.8 or higher
- Git

### Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/cocktail-advisor-chat.git
   cd cocktail-advisor-chat
Create and Activate a Virtual Environment

On macOS/Linux:

bash
Copy
python3 -m venv venv
source venv/bin/activate
On Windows:

bash
Copy
python -m venv venv
venv\Scripts\activate
Install Dependencies

bash
Copy
pip install -r requirements.txt
Configure Environment Variables

Create a .env file in the project root with the following (replace with your keys):

env
Copy
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
Run the Application

bash
Copy
uvicorn app.main:app --reload
Open the Application

Open your browser and navigate to http://localhost:8000.

Results and Thought Process
The goal of this project was to build a robust, modular chat application capable of answering cocktail-related questions using advanced language models. Key considerations included:

Modular Design: We separated agent logic (in the AgentFabric directory) from the server and routes (in the app directory). This separation makes the project easier to understand, test, and extend.
Personalized History Management: Each user receives an individual FAISS vector store to store and retrieve conversation history. This history is used to build context for new queries, ensuring more relevant and accurate responses.
Customizable Prompts: By storing system and tool prompts in a JSON file (data/prompts.json), the application can be easily reconfigured to adjust the agent's behavior without modifying the code.
Enhanced User Interface: The frontend leverages Bootstrap for responsiveness and a modern look. Custom animations and a loading spinner provide a smooth user experience without expanding the chat container.
Integration of External Tools: An Anthropic tool is included for post-processing and enhancing message readability, ensuring that responses are clear and well-formatted.
This project demonstrates a complete end-to-end solution—from user input to LLM-based response generation, with context-aware personalization—packaged in an easy-to-deploy web application.

License
This project is licensed under the MIT License.

Contact
For any questions or feedback, please contact [your_email@example.com] or visit my GitHub profile.