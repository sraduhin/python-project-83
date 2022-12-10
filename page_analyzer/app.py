from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def main():
    project_name = 'project 83'
    return render_template('index.html', project_name=project_name)

if __name__ == '__main__':
    app.run()