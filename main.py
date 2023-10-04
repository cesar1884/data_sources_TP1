from flask import Flask

app = Flask(__name__)
@app.route("/")
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
    print("This is a log message from Python.")
    return "This is a log message from the browser."

if __name__ == '__main__':
    app.run(debug=True)  # The debug=True flag will help in automatically reloading the app on code changes
