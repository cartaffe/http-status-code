from flask import Flask, request, jsonify
from functools import wraps
import time
import os

# Content Security Policy header
CSP_POLICY = "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; img-src 'self' data:; font-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
app = Flask(__name__)

@app.after_request
def add_csp_header(response):
    response.headers.setdefault("Content-Security-Policy", CSP_POLICY)
    return response

# Bearer token for authentication
VALID_TOKEN = os.environ.get("BEARER_TOKEN", "my-secret-token-12345")

# Rate limiting (simple in-memory counter)
request_counts = {}
RATE_LIMIT = int(os.environ.get("RATE_LIMIT", 5))  # requests per minute

# HTML templates
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Status Code Demo</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        a { color: #007bff; text-decoration: none; margin-right: 15px; }
        a:hover { text-decoration: underline; }
        code { background: #e9ecef; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ title }}</h1>
        <div class="status {{ status_class }}">
            <strong>Status Code:</strong> {{ status_code }}
        </div>
        <p>{{ message }}</p>
        
        <h3>Available Endpoints:</h3>
        <ul>
            <li><a href="/">/</a> - Home (200 OK)</li>
            <li><a href="/success">/success</a> - Success page (200 OK)</li>
            <li><a href="/created">/created</a> - Resource created (201 Created)</li>
            <li><a href="/accepted">/accepted</a> - Request accepted (202 Accepted)</li>
            <li><a href="/no-content">/no-content</a> - No content (204 No Content)</li>
            <li><a href="/redirect-temp">/redirect-temp</a> - Temporary redirect (302 Found)</li>
            <li><a href="/redirect-perm">/redirect-perm</a> - Permanent redirect (301 Moved Permanently)</li>
            <li><a href="/not-modified">/not-modified</a> - Not modified (304 Not Modified)</li>
            <li><a href="/bad-request">/bad-request</a> - Bad request (400 Bad Request)</li>
            <li><a href="/protected">/protected</a> - Protected resource (401 Unauthorized without token)</li>
            <li><a href="/forbidden">/forbidden</a> - Forbidden access (403 Forbidden)</li>
            <li><a href="/notfound">/notfound</a> - Not found (404 Not Found)</li>
            <li><a href="/method-not-allowed">/method-not-allowed</a> - Method not allowed (405)</li>
            <li><a href="/conflict">/conflict</a> - Conflict (409 Conflict)</li>
            <li><a href="/gone">/gone</a> - Resource gone (410 Gone)</li>
            <li><a href="/rate-limited">/rate-limited</a> - Rate limited (429 Too Many Requests)</li>
            <li><a href="/error">/error</a> - Internal error (500 Internal Server Error)</li>
            <li><a href="/not-implemented">/not-implemented</a> - Not implemented (501 Not Implemented)</li>
            <li><a href="/service-unavailable">/service-unavailable</a> - Service unavailable (503)</li>
        </ul>
        
        <h3>Authentication:</h3>
        <p>For <code>/protected</code> endpoint, use Bearer Token:</p>
        <ul>
            <li>Token: <code>my-secret-token-12345</code></li>
        </ul>
        <p>Example: <code>curl -H "Authorization: Bearer my-secret-token-12345" http://localhost:5000/protected</code></p>

        <h3>Received Headers:</h3>
        <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
            <thead>
                <tr style="background-color: #f2f2f2; text-align: left;">
                    <th style="padding: 8px; border: 1px solid #ddd; width: 66.66%;">Header</th>
                    <th style="padding: 8px; border: 1px solid #ddd; width: 33.33%;">Value</th>
                </tr>
            </thead>
            <tbody>
                {% for key, value in request.headers.items() %}
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">{{ key }}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{{ value }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

PAGE_TEMPLATE = app.jinja_env.from_string(HTML_TEMPLATE)


def render_page(title, status_code, status_class, message):
    ctx = dict(title=title, status_code=status_code, status_class=status_class, message=message)
    app.update_template_context(ctx)
    return PAGE_TEMPLATE.render(ctx)


# Bearer Token Auth decorator
def require_bearer_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return render_page(
                title="401 Unauthorized",
                status_code="401",
                status_class="error",
                message="Authentication required. Please provide a Bearer token in the Authorization header."
            ), 401
        
        # Check if it starts with "Bearer "
        if not auth_header.startswith('Bearer '):
            return render_page(
                title="401 Unauthorized",
                status_code="401",
                status_class="error",
                message="Invalid authentication format. Use 'Bearer <token>'."
            ), 401
        
        token = auth_header.split(' ')[1]
        
        if token != VALID_TOKEN:
            return render_page(
                title="401 Unauthorized",
                status_code="401",
                status_class="error",
                message="Invalid token provided."
            ), 401
        
        return f(*args, **kwargs)
    return decorated

# Routes
@app.route('/')
def home():
    return render_page(
        title="HTTP Status Code Demo",
        status_code="200 OK",
        status_class="success",
        message="Welcome! This server demonstrates different HTTP status codes."
    ), 200

@app.route('/success')
def success():
    return render_page(
        title="Success",
        status_code="200 OK",
        status_class="success",
        message="Request was successful!"
    ), 200

@app.route('/protected')
@require_bearer_auth
def protected():
    return render_page(
        title="Protected Resource",
        status_code="200 OK",
        status_class="success",
        message="You successfully accessed the protected resource with valid token!"
    ), 200

@app.route('/created')
def created():
    return render_page(
        title="201 Created",
        status_code="201",
        status_class="success",
        message="Resource has been created successfully."
    ), 201

@app.route('/accepted')
def accepted():
    return render_page(
        title="202 Accepted",
        status_code="202",
        status_class="success",
        message="Request accepted for processing, but not yet completed."
    ), 202

@app.route('/no-content')
def no_content():
    # 204 typically returns no body
    return '', 204

@app.route('/redirect-temp')
def redirect_temp():
    return '', 302, {'Location': '/success'}

@app.route('/redirect-perm')
def redirect_perm():
    return '', 301, {'Location': '/success'}

@app.route('/not-modified')
def not_modified():
    return '', 304

@app.route('/bad-request')
def bad_request():
    return render_page(
        title="400 Bad Request",
        status_code="400",
        status_class="error",
        message="The server cannot process the request due to invalid syntax or missing parameters."
    ), 400

@app.route('/forbidden')
def forbidden():
    return render_page(
        title="403 Forbidden",
        status_code="403",
        status_class="error",
        message="You don't have permission to access this resource."
    ), 403

@app.route('/notfound')
def not_found():
    return render_page(
        title="404 Not Found",
        status_code="404",
        status_class="error",
        message="The requested resource was not found on this server."
    ), 404

@app.route('/error')
def internal_error():
    return render_page(
        title="500 Internal Server Error",
        status_code="500",
        status_class="error",
        message="An internal server error occurred while processing your request."
    ), 500

@app.route('/method-not-allowed', methods=['GET'])
def method_not_allowed():
    return render_page(
        title="405 Method Not Allowed",
        status_code="405",
        status_class="error",
        message="The HTTP method is not allowed for this resource. Try POST instead of GET."
    ), 405, {'Allow': 'POST'}

@app.route('/conflict')
def conflict():
    return render_page(
        title="409 Conflict",
        status_code="409",
        status_class="error",
        message="The request conflicts with the current state of the resource (e.g., duplicate entry)."
    ), 409

@app.route('/gone')
def gone():
    return render_page(
        title="410 Gone",
        status_code="410",
        status_class="error",
        message="The requested resource is no longer available and will not be available again."
    ), 410

@app.route('/rate-limited')
def rate_limited():
    client_ip = request.remote_addr
    current_minute = int(time.time() / 60)
    key = f"{client_ip}:{current_minute}"
    
    request_counts[key] = request_counts.get(key, 0) + 1
    
    if request_counts[key] > RATE_LIMIT:
        return render_page(
            title="429 Too Many Requests",
            status_code="429",
            status_class="error",
            message=f"Rate limit exceeded. Maximum {RATE_LIMIT} requests per minute allowed."
        ), 429, {'Retry-After': '60'}
    
    return render_page(
        title="Rate Limited Endpoint",
        status_code="200 OK",
        status_class="success",
        message=f"Request successful. You have made {request_counts[key]}/{RATE_LIMIT} requests this minute."
    ), 200

@app.route('/not-implemented')
def not_implemented():
    return render_page(
        title="501 Not Implemented",
        status_code="501",
        status_class="error",
        message="The server does not support the functionality required to fulfill the request."
    ), 501

@app.route('/service-unavailable')
def service_unavailable():
    return render_page(
        title="503 Service Unavailable",
        status_code="503",
        status_class="error",
        message="The server is temporarily unable to handle the request (maintenance or overload)."
    ), 503, {'Retry-After': '120'}

# Catch-all for actual 404s
@app.errorhandler(404)
def page_not_found(e):
    return render_page(
        title="404 Not Found",
        status_code="404",
        status_class="error",
        message=f"The page '{request.path}' does not exist."
    ), 404

if __name__ == '__main__':
    print("Starting Flask server...")
    print("Visit: http://localhost:5000")
    print("\nBearer Token: my-secret-token-12345 (default one, you can change it using env variable)")
    print("\nTest with curl:")
    print("  curl http://localhost:5000/success")
    print("  curl -H 'Authorization: Bearer my-secret-token-12345' http://localhost:5000/protected")
    print("  curl http://localhost:5000/forbidden")
    print("  curl http://localhost:5000/created")
    print("  curl http://localhost:5000/rate-limited")
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1", host='0.0.0.0', port=5000)
