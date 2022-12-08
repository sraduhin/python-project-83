from flask import Flask

app = Flask(__name__)

@app.route('/')
def main():
    return 'project 83'

if __name__ == '__main__':
    app.run()