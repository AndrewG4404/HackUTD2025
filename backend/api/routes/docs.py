"""
Documentation and API information endpoints.
"""
from database import client as mongo_client  # noqa: F401
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def api_info():
    """
    API information landing page
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>VendorLens API</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                line-height: 1.6;
            }
            h1 { color: #2563eb; }
            h2 { color: #1e40af; margin-top: 30px; }
            .endpoint { 
                background: #f3f4f6; 
                padding: 10px; 
                margin: 10px 0; 
                border-radius: 5px;
                font-family: monospace;
            }
            .method { 
                font-weight: bold; 
                color: #059669;
            }
            .method.post { color: #dc2626; }
            a { color: #2563eb; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .button {
                display: inline-block;
                background: #2563eb;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                margin: 10px 10px 10px 0;
            }
            .button:hover { background: #1e40af; }
        </style>
    </head>
    <body>
        <h1>🔍 VendorLens API</h1>
        <p><strong>Version:</strong> 1.0.0</p>
        <p>Secure & Intelligent Vendor Onboarding Hub - AI-powered vendor onboarding and assessment platform</p>
        
        <a href="/docs" class="button">📖 Swagger UI</a>
        <a href="/redoc" class="button">📚 ReDoc</a>
        <a href="/openapi.json" class="button">📄 OpenAPI JSON</a>
        <a href="/openapi.yaml" class="button">📋 OpenAPI YAML</a>
        
        <h2>Quick Start</h2>
        <p>This API provides two main workflows:</p>
        <ul>
            <li><strong>Vendor Application</strong> - Single vendor applies for onboarding</li>
            <li><strong>Vendor Assessment & Comparison</strong> - Internal team compares multiple vendors</li>
        </ul>
        
        <h2>Core Endpoints</h2>
        
        <div class="endpoint">
            <span class="method">GET</span> /api/health
            <br><small>Check API health status</small>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> /api/evaluations/apply
            <br><small>Create vendor application evaluation</small>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> /api/evaluations/assess
            <br><small>Create vendor assessment evaluation</small>
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> /api/evaluations/{id}
            <br><small>Get evaluation by ID</small>
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> /api/evaluations
            <br><small>List all evaluations</small>
        </div>
        
        <h2>Workflow Endpoints</h2>
        
        <div class="endpoint">
            <span class="method post">POST</span> /api/workflows/application/{evaluation_id}/run
            <br><small>Run application workflow pipeline</small>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> /api/workflows/assessment/{evaluation_id}/run
            <br><small>Run assessment workflow pipeline</small>
        </div>
        
        <h2>Documentation</h2>
        <ul>
            <li><a href="/docs">Swagger UI</a> - Interactive API documentation</li>
            <li><a href="/redoc">ReDoc</a> - Alternative documentation view</li>
            <li><a href="/openapi.json">OpenAPI JSON</a> - OpenAPI specification in JSON format</li>
            <li><a href="/openapi.yaml">OpenAPI YAML</a> - OpenAPI specification in YAML format</li>
        </ul>
        
        <h2>Technology Stack</h2>
        <ul>
            <li><strong>Backend:</strong> FastAPI, Python</li>
            <li><strong>Database:</strong> MongoDB</li>
            <li><strong>AI:</strong> Nemotron LLM</li>
            <li><strong>Storage:</strong> Local file system</li>
        </ul>
    </body>
    </html>
    """
    return html_content

