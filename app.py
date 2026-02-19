# Updated app.py

from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import pandas as pd

app = Flask(__name__)

# Routes for existing tabs

@app.route('/graph')
def graph():
    return render_template('graph.html')  # New graph tab route

# Function to create Run Worm graph
def create_run_worm_graph(data):
    plt.figure()
    plt.plot(data['overs'], data['scores'])
    plt.title('Cumulative Run Tracking for Run Worm')
    plt.xlabel('Overs')
    plt.ylabel('Runs')
    plt.savefig('static/run_worm_graph.png')

# Function to create Manhattan graph
def create_manhattan_graph(data):
    plt.figure()
    plt.hist(data['runs'], bins=20)
    plt.title('Run Distribution for Manhattan')
    plt.xlabel('Runs')
    plt.ylabel('Frequency')
    plt.savefig('static/manhattan_graph.png')

# Function to create Run Rate graph
def create_run_rate_graph(data):
    plt.figure()
    plt.plot(data['overs'], data['run_rate'])
    plt.title('Run Rate Over Overs')
    plt.xlabel('Overs')
    plt.ylabel('Run Rate')
    plt.savefig('static/run_rate_graph.png')

if __name__ == '__main__':
    app.run(debug=True)