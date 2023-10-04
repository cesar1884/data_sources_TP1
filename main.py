from flask import Flask, render_template, request
import requests

app = Flask(__name__)
last_message = ''

@app.route('/')
def hello_world():
    prefix_google = """
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-GKPDQR0FNY"></script>
    <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-GKPDQR0FNY');
    </script>
    """
    return prefix_google + """
    <div>
        <a href="/logger">Go to Logger</a>
        <a href="/google-request">Google Request</a>
    </div>
    Hello World"""

@app.route('/logger', methods=['GET', 'POST'])
def logger():
    global last_message
    
    if request.method == 'POST':
        last_message = request.form['log_message']
        app.logger.warning(f"Log message from Python: {last_message}")

    return """
    <div>
        <a href="/">Home</a>
        <a href="/google-request">Google Request</a>
    </div>
    <form method="POST">
        Log Message: <input type="text" name="log_message">
        <input type="submit" value="Log">
    </form>
    """ + f"<p>Last logged message: {last_message}</p>"

@app.route('/google-request', methods=['GET'])
def google_request():
    return """
    <div>
        <a href="/">Home</a>
        <a href="/logger">Logger</a>
    </div>
    <form method="GET" action="/perform-google-request">
        <input type="submit" value="Make Google Request">
    </form>
    """

@app.route('/perform-google-request', methods=['GET'])
def perform_google_request():
    req = requests.get("https://analytics.google.com/analytics/web/#/p407461953/reports/intelligenthome")
    return str(req.cookies.get_dict())

if __name__ == '__main__':
    app.run(debug=True)
