# Destiny Matrix Analyzer API

## Setup Instructions

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variable for Gemini API key:
```bash
# Windows
set GEMINI_API_KEY=your_api_key_here

# Linux/Mac
export GEMINI_API_KEY=your_api_key_here
```

3. Run the API server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### POST /analyze-matrix
Analyze destiny matrix data using AI.

**Request Body:**
```json
{
  "matrix_data": {
    "points": {
      "A": 15,
      "B": 8,
      "C": 22,
      "D": 3,
      "E": 11,
      "F": 7,
      "G": 19,
      "H": 14
    },
    "purposes": {
      "spiritual": 12,
      "social": 9,
      "material": 16
    },
    "chartHeart": {
      "chakra1": 5,
      "chakra2": 13,
      "chakra3": 21,
      "chakra4": 4,
      "chakra5": 18,
      "chakra6": 10,
      "chakra7": 2
    }
  },
  "analysis_type": "personal"
}
```

**Response:**
```json
{
  "analysis": "Bu kader matrisi analizi sonucunda, kişinin güçlü liderlik özelliklerine sahip olduğu görülmektedir. A noktasındaki 15 değeri, doğal bir öğretmen ve rehber olma potansiyelini göstermektedir...",
  "success": true
}
```

**Analysis Types:**
- `"personal"` - Personal destiny matrix analysis
- `"compatibility"` - Compatibility analysis between two people

### Compatibility Analysis Example

**Request Body:**
```json
{
  "matrix_data": {
    "compatibility": {
      "person1": {
        "points": {"A": 15, "B": 8, "C": 22},
        "purposes": {"spiritual": 12, "social": 9}
      },
      "person2": {
        "points": {"A": 7, "B": 14, "C": 21},
        "purposes": {"spiritual": 8, "social": 15}
      },
      "compatibility_score": 0.78,
      "shared_energies": [8, 15, 22]
    }
  },
  "analysis_type": "compatibility"
}
```

**Response:**
```json
{
  "analysis": "Bu uyumluluk analizi sonucunda, iki kişi arasında %78 uyumluluk görülmektedir. Ortak enerji noktaları güçlü bir bağ oluşturmaktadır...",
  "success": true
}
```

### GET /health
Health check endpoint to verify API status.

**Response:**
```json
{
  "status": "healthy",
  "message": "Destiny Matrix Analyzer is running"
}
```

## Error Responses

**400 Bad Request:**
```json
{
  "detail": "Invalid matrix data format"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Analysis failed: GEMINI_API_KEY environment variable is not set"
}
```

## Usage

The frontend will automatically call the API when the "Analyze Matrix with AI" button is clicked. You can also test the API manually using tools like curl or Postman:

```bash
curl -X POST "http://localhost:8000/analyze-matrix" \
  -H "Content-Type: application/json" \
  -d '{
    "matrix_data": {
      "points": {"A": 15, "B": 8, "C": 22},
      "purposes": {"spiritual": 12, "social": 9}
    },
    "analysis_type": "personal"
  }'
```
