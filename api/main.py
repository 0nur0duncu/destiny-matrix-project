from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv, find_dotenv
import logging
from datetime import datetime
import httpx
from starlette.middleware.base import BaseHTTPMiddleware

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging to write to today's log file
today = datetime.now().strftime('%Y-%m-%d')
log_file = f'logs/{today}.log'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        # Remove console handler to avoid terminal output
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv(find_dotenv())

app = FastAPI(title="Destiny Matrix Analyzer", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "https://api.robark.com.tr",
        "https://destiny.robark.com.tr",
        "http://localhost:9115",
        "https://robark.com.tr/"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Origin", "Content-Type", "Accept", "Authorization"],
)

# Authentication Middleware
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            logger.info(f"Authentication request for {request.url.path}")
            
            # Authorization header'ından bearer token'ı al
            auth_header = request.headers.get("authorization")
            
            if not auth_header or not auth_header.startswith('Bearer '):
                logger.warning("Missing or invalid authorization header")
                return Response(
                    content=json.dumps({"error": "Please send Bearer token in Authorization header."}),
                    status_code=401,
                    media_type="application/json"
                )

            token = auth_header[7:]  # "Bearer " kısmını çıkar

            # External API'ye istek at
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    'https://numina.polo-plus.com/api/user',
                    headers={
                        'Authorization': f'Bearer {token}',
                        'Content-Type': 'application/json'
                    }
                )

                user_data = response.json()

                # API yanıtını kontrol et - JavaScript kodundaki gibi string "true" kontrolü
                if response.status_code != 200 or user_data.get("status") != "true":
                    logger.warning(f"Authentication failed: status_code={response.status_code}, status={user_data.get('status')}")
                    return Response(
                        content=json.dumps({"error": "Expired or invalid bearer token."}),
                        status_code=401,
                        media_type="application/json"
                    )

                # Kullanıcı bilgilerini request state'ine ekle
                request.state.user = user_data.get("user")
                logger.info(f"User authenticated successfully: {user_data.get('user', {}).get('email', 'unknown')}")
                
        except Exception as error:
            logger.error(f'Auth Middleware Error: {error}', exc_info=True)
            return Response(
                content=json.dumps({"error": "An error occurred during authentication."}),
                status_code=500,
                media_type="application/json"
            )

        response = await call_next(request)
        return response

# Service and Order Middleware
class ServiceOrderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            logger.info(f"Service order middleware for {request.url.path}")
            
            # Authorization header'ından bearer token'ı al
            auth_header = request.headers.get("authorization")
            
            if not auth_header or not auth_header.startswith('Bearer '):
                logger.warning("Missing authorization header in service middleware")
                return Response(
                    content=json.dumps({"error": "Please send Bearer token in Authorization header."}),
                    status_code=401,
                    media_type="application/json"
                )

            token = auth_header[7:]  # "Bearer " kısmını çıkar

            async with httpx.AsyncClient() as client:
                # 1. Adım: Servis listesini al
                logger.info("Fetching service details")
                services_response = await client.get(
                    'https://numina.polo-plus.com/api/service/details',
                    headers={
                        'Authorization': f'Bearer {token}',
                        'Content-Type': 'application/json'
                    }
                )

                services_data = services_response.json()

                if services_response.status_code != 200 or not services_data.get("status"):
                    logger.error(f"Failed to retrieve service list: status_code={services_response.status_code}")
                    return Response(
                        content=json.dumps({"error": "Service list could not be retrieved."}),
                        status_code=500,
                        media_type="application/json"
                    )

                # "<service_name>" servisini bul
                coffee_service = None
                for service in services_data.get("services", []):
                    if service.get("name") == "<service_name>":
                        coffee_service = service
                        break
                
                if not coffee_service:
                    logger.error("<service_name> service not found in service list")
                    return Response(
                        content=json.dumps({"error": "<service_name> service not found."}),
                        status_code=404,
                        media_type="application/json"
                    )

                logger.info(f"Found <service_name> service with ID: {coffee_service.get('id')}")

                # 2. Adım: Sipariş oluştur
                logger.info("Creating order for <service_name> service")
                order_response = await client.post(
                    'https://numina.polo-plus.com/api/order/create',
                    headers={
                        'Authorization': f'Bearer {token}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        "service_id": coffee_service.get("id")
                    }
                )

                order_data = order_response.json()

                # Bakiye kontrolü
                if order_response.status_code == 403:
                    logger.warning("Order creation failed: insufficient balance")
                    return Response(
                        content=json.dumps({"error": "Insufficient balance. Please top up your account."}),
                        status_code=403,
                        media_type="application/json"
                    )

                # JavaScript kodundaki gibi kontrol
                if order_response.status_code != 200:
                    logger.error(f"Order creation failed: status_code={order_response.status_code}")
                    return Response(
                        content=json.dumps({"error": "Order could not be created."}),
                        status_code=500,
                        media_type="application/json"
                    )

                # Sipariş bilgilerini request state'ine ekle
                request.state.order = order_data.get("order")
                request.state.service_details = order_data.get("service_details")
                request.state.conversation = order_data.get("conversation")
                
                logger.info(f"Order created successfully: {order_data.get('order', {}).get('id', 'unknown')}")
                
        except Exception as error:
            logger.error(f'Service Order Middleware Error: {error}', exc_info=True)
            return Response(
                content=json.dumps({"error": "An error occurred during service verification."}),
                status_code=500,
                media_type="application/json"
            )

        response = await call_next(request)
        return response

# Middleware'leri ekle
app.add_middleware(AuthMiddleware)
app.add_middleware(ServiceOrderMiddleware)

class MatrixAnalysisRequest(BaseModel):
    matrix_data: Dict[str, Any]
    analysis_type: str = "personal"

class MatrixAnalysisResponse(BaseModel):
    analysis: str
    success: bool

def initialize_gemini_client():
    """Initialize Gemini client with API key from environment"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    return genai.Client(api_key=api_key)

def create_analysis_prompt(matrix_data: Dict[str, Any], analysis_type: str) -> str:
    """Create analysis prompt based on matrix data and analysis type"""
    
    if analysis_type == "personal":
        return f"""
        Kişisel Kader Matrisini Analiz Et:
        
        Temel Noktalar: {json.dumps(matrix_data.get('points', {}), indent=2)}
        Amaçlar: {json.dumps(matrix_data.get('purposes', {}), indent=2)}
        Çakra Analizi: {json.dumps(matrix_data.get('chartHeart', {}), indent=2)}
        
        Lütfen bu kader matrisini analiz ederek kişinin:
        1. Temel kişilik özellikleri
        2. Güçlü ve zayıf yönleri
        3. Yaşam amacı ve hedefleri
        4. Ruhsal gelişim potansiyeli
        5. Kariyер ve ilişki önerileri
        
        hakkında detaylı ve anlayışlı bir analiz yap. Türkçe olarak yanıtla.
        """
    
    elif analysis_type == "compatibility":
        return f"""
        Uyumluluk Matrisini Analiz Et:
        
        Uyumluluk Verileri: {json.dumps(matrix_data.get('compatibility', {}), indent=2)}
        
        Lütfen bu uyumluluk matrisini analiz ederek:
        1. Genel uyumluluk seviyesi
        2. Güçlü uyumluluk alanları
        3. Potansiyel zorluklar
        4. İlişki önerileri
        5. Birlikte büyüme potansiyeli
        
        hakkında detaylı bir analiz yap. Türkçe olarak yanıtla.
        """
    
    return "Genel kader matrisi analizi yapın."

async def analyze_with_gemini(matrix_data: Dict[str, Any], analysis_type: str) -> str:
    """Analyze matrix data using Gemini AI"""
    model = "gemini-2.5-flash"
    
    try:
        client = initialize_gemini_client()
        
        prompt = create_analysis_prompt(matrix_data, analysis_type)
        
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                ],
            ),
        ]
        
        response = client.models.generate_content(
            model=model,
            contents=contents
        )
        
        return response.text
        
    except Exception as e:
        print(f"Error in Gemini analysis: {str(e)}")
        return "Üzgünüm, analizinizi şu anda gerçekleştiremiyorum. Lütfen daha sonra tekrar deneyin."

@app.post("/analyze-matrix", response_model=MatrixAnalysisResponse)
async def analyze_matrix(request: MatrixAnalysisRequest):
    """Analyze destiny matrix using AI"""
    try:
        analysis = await analyze_with_gemini(request.matrix_data, request.analysis_type)
        
        return MatrixAnalysisResponse(
            analysis=analysis,
            success=True
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Destiny Matrix Analyzer is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
