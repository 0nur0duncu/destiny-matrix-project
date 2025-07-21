# Destiny Matrix

Destiny Matrix project is a programming project that involved the creation of two calculators designed to calculate Destiny Matrix. The project used technologies such as CSS, HTML, JavaScript, and now includes a FastAPI service for AI-powered matrix interpretation using Google's Gemini API.

# Technologies Used

- CSS
- HTML
- JavaScript
- Python (FastAPI)
- Google Gemini API

# Features

Destiny Matrix project includes two calculators that allow users to input their birthdate and calculate Destiny Matrix. The first calculator uses numerology to create a personalized numerology chart for users, while the second calculator uses astrology to determine the user's horoscope.

**New Feature**: AI-powered matrix interpretation service that provides detailed analysis of the calculated matrix using Google's Gemini API.

# How to Use

## Frontend Calculators
To use the Destiny Matrix project, simply open the project in your web browser and navigate to the calculators. From there, input your birthdate and the calculators will automatically calculate your Destiny Matrix.

## API Service
To use the AI interpretation service:

1. Install dependencies:
```bash
cd api
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

3. Run the service:
```bash
python run.py
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

## API Endpoints

- `POST /interpret` - Interpret destiny matrix table
- `GET /health` - Health check
- `GET /` - API information

### Example API Request

```json
POST /interpret
{
  "matrix_data": {
    "chakras": [
      {
        "name": "Root Chakra",
        "physics": 5,
        "energy": 8,
        "emotions": 3
      }
    ],
    "result_physics": 15,
    "result_energy": 22,
    "result_emotions": 18
  },
  "user_name": "John Doe",
  "birth_date": "1990-05-15"
}
```

[PERSONAL CALCULATION](https://destinymatrix.netlify.app/) |
[YOUR COMPATIBILITY](https://compatibilitymatrix.netlify.app/) 

# Contributors

- [Elena Koroleva](https://github.com/berriestime)
- [Evgeniia Shirshikova](https://github.com/EvgeniiaShirshikova)
- [Alesia](https://github.com/Alesia-15)
- [Anastasia Goncharova](https://github.com/goncharovastacy)
- [Aelita](https://github.com/aelita-dzhafarova)
- [Irina](https://github.com/BarhatovaIrina)

# License

Destiny Matrix project is licensed under the MIT license. Please see the `LICENSE` file for more information.
