from flask import Flask, render_template, request
import requests

app = Flask(__name__)
last_message = ''

@app.route('/', methods=['GET', 'POST'])
def index():
    global last_message
    cookies_str = ""

    if request.method == 'POST':
        # Vérifiez si la clé 'action' est présente dans request.form
        action = request.form.get('action')
        
        if action == "submit_message":
            last_message = request.form['message']
        elif action == "get_cookies":
            req = requests.get("https://www.google.com/")
            cookies = req.cookies._cookies
            cookies_str = str(cookies)
    
    return render_template('index.html', message=last_message, cookies=cookies_str)

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
    return prefix_google + "Hello World"

@app.route("/logger")
def logger():
    global last_message
    print("Last Message: " + last_message)  
    return f"Last Message: {last_message}"  

if __name__ == '__main__':
    app.run(debug=True)