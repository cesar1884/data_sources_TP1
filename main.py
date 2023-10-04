from flask import Flask, render_template, request, redirect, url_for, session
from flask_oauthlib.client import OAuth
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'random_secret_key'

oauth = OAuth(app)
import code_1

google = oauth.remote_app(
    'google',
    consumer_key=code_1.client,
    consumer_secret=code_1.code_client,
    request_token_params={
        'scope': 'https://www.googleapis.com/auth/analytics.readonly'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

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
        <a href="/login">Login with Google</a>
    </div>
    Hello World"""

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.pop('google_token')
    return redirect(url_for('index'))

@app.route('/login/authorized')
def authorized():
    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Accès refusé: raison=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )

    session['google_token'] = (response['access_token'], '')
    user_info = google.get('userinfo')
    return redirect(url_for('google_request'))

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

@app.route('/google-request', methods=['GET', 'POST'])
def google_request():
    cookies_str = ""

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == "google_request":
            req = requests.get("https://www.google.com/")
            cookies_str = str(req.cookies._cookies)

        elif action == "ganalytics_request":
            req2 = requests.get("https://analytics.google.com/analytics/web/#/p407461953/reports/intelligenthome")
            cookies_str = str(req2.cookies._cookies)
    
    return """
    <div>
        <a href="/">Home</a>
        <a href="/logger">Logger</a>
    </div>
    <form method="POST">
        <input type="submit" name="action" value="google_request" placeholder="Make Google Request">
        <input type="submit" name="action" value="ganalytics_request" placeholder="Make GAnalytics Request">
    </form>
    """ + f"<p>{cookies_str}</p>"

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

if __name__ == '__main__':
    app.run(debug=True)