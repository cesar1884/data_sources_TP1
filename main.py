from flask import Flask, render_template, request, redirect, url_for, session
from flask_oauthlib.client import OAuth
import requests
from logging.config import dictConfig
import logging
from pytrends.request import TrendReq
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest
from matplotlib import pyplot as plt
import numpy as np
import base64
from io import BytesIO
import utils

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


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
    
    
@app.route('/get_google_trends', methods=['GET'])
def get_google_trends():
    
    pytrends = TrendReq(hl='en-US', tz=360)  # Create a pytrends instance with your preferred settings
    pytrends.build_payload(kw_list=['neymar', 'messi'], timeframe='2021-01-01 2021-12-31')
    data = pytrends.interest_over_time()
    
    # Generate a line plot to see the trends
    plt.figure(figsize=(10, 4))
    plt.plot(data.index, data['neymar'], label='neymar')
    plt.plot(data.index, data['messi'], label='messi')
    plt.xlabel('Date')
    plt.ylabel('Search Interest')
    plt.title('Google Trends Data')
    plt.legend()

    # Convert the plot to a bytes object and then to base64 for embedding in a web page
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.read()).decode()
    
    return render_template('trends.html', plot_data=plot_data)


@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@app.route('/word_count_experiment', methods=['GET'])
def word_count_experiment():
    """
    Endpoint to perform a word count experiment using two different counting methods and display the results as a boxplot.

    This route loads Shakespeare's text, counts words using dictionary and Counter methods, measures execution times,
    calculates mean and variance, and displays a boxplot of execution times.

    Returns:
        str: HTML page containing the boxplot with execution time distributions.

    Example:
        Access the route '/word_count_experiment' in a web browser.
    """
    # Load Shakespeare's text (you can also download it here if needed)
    with open('shakespeare.txt', 'r') as file:
        shakespeare_text = file.read()

    # Create lists to store execution times and results
    execution_times_dict = []
    execution_times_counter = []

    # Run the experiment 10 times
    for _ in range(100):
        result_dict, execution_time_dict = utils.count_dict(shakespeare_text)
        result_counter, execution_time_counter = utils.count_counter(shakespeare_text)

        execution_times_dict.append((result_dict, execution_time_dict))
        execution_times_counter.append((result_counter, execution_time_counter))

    # Extract execution times from the results
    execution_times_dict = [execution_time for _, execution_time in execution_times_dict]
    execution_times_counter = [execution_time for _, execution_time in execution_times_counter]

    # Calculate the mean and variance for each dataset
    mean_dict = np.mean(execution_times_dict)
    variance_dict = np.var(execution_times_dict)
    mean_counter = np.mean(execution_times_counter)
    variance_counter = np.var(execution_times_counter)

    # Create a boxplot
    data = [execution_times_dict, execution_times_counter]
    labels = ['Using Dictionary\nMean: {:.2f}\nVariance: {:.2f}'.format(mean_dict, variance_dict),
            'Using Counter\nMean: {:.2f}\nVariance: {:.2f}'.format(mean_counter, variance_counter)]

    plt.boxplot(data, labels=labels)
    plt.ylabel('Execution Time (seconds)')
    plt.title('Execution Time Distributions')
    plt.grid(True)

    # Convert the plot to a bytes object and then to base64 for embedding in a web page
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.read()).decode()

    return render_template('word_count_results.html', plot_data=plot_data)

if __name__ == '__main__':
    app.run(debug=True)
    
    