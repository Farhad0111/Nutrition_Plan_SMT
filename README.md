# Meal Plan API

A FastAPI-based REST API that generates personalized meal plans using OpenAI's GPT model. The API takes into account user profiles including gender, age, weight goals, and dietary preferences to create customized daily meal plans.

## Features

- Personalized meal plan generation
- Custom dietary preferences support
- Detailed meal portions and quantities
- Fast response times with OpenAI integration

## Tech Stack

- Python 3.11+
- FastAPI - Modern web framework
- Pydantic - Data validation
- OpenAI API - AI-powered meal plan generation
- pytest - Testing framework

## Project Structure

```
├── app/
│   ├── api/
│   │   └── routes.py          # API endpoints
│   ├── core/
│   │   └── config.py          # Configuration settings
│   ├── models/
│   │   └── shemas.py          # Data models
│   └── services/
│       └── openAI_services.py # OpenAI integration
├── main.py                    # Application entry point
├── requirements.txt           # Project dependencies
└── pytest.ini                # Test configuration
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-folder>
```

2. Create a virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\Activate
```

3. Install dependencies:
```powershell
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your OpenAI API key:
```
API_KEY="your-openai-api-key"
```

## Usage

1. Start the server:
```powershell
uvicorn main:app --reload
```

2. The API will be available at `http://localhost:8000`

3. Access the interactive API documentation at `http://localhost:8000/docs`

### Example Request

```json
POST /meal-plan

{
  "gender": "male",
  "age": 30,
  "height": 175,
  "weight": 80.5,
  "desiredWeight": 75.0,
  "weeklyWeightLossGoal": 0.5,
  "trainingDay": 3,
  "workoutLocation": "gym",
  "dietType": "balanced",
  "reachingGoals": "weight_loss",
  "accomplish": "healthy lifestyle"
}
```

## API Endpoints

### POST /meal-plan
Generates a personalized meal plan based on user profile and preferences.

#### Request Body Parameters:
- `gender` (string): User's gender
- `age` (integer): User's age
- `height` (integer): Height in centimeters
- `weight` (float): Current weight in kilograms
- `desiredWeight` (float): Target weight in kilograms
- `weeklyWeightLossGoal` (float): Weekly weight loss target in kilograms
- `trainingDay` (integer): Number of training days per week
- `workoutLocation` (string): Preferred workout location
- `dietType` (string): Preferred diet type
- `reachingGoals` (string): Primary fitness goal
- `accomplish` (string, optional): Additional goals

## Development

### Running Tests
```powershell
pytest
```

### Code Style
The project follows PEP 8 guidelines for Python code styling.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
