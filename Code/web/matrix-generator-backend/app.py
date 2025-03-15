from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pandas as pd

app = Flask(__name__)
CORS(app)


@app.route('/generate-matrix', methods=['POST'])
def generate_matrix():
    data = request.json
    columns = data['columns']
    dataframe = pd.DataFrame(data['dataframe'])

    matrix = []
    for column in columns:
        if column['distribution'] == 'random':
            matrix.append(np.random.rand(len(dataframe)))
        elif column['distribution'] == 'normal':
            matrix.append(np.random.normal(size=len(dataframe)))
        elif column['distribution'] == 'uniform':
            matrix.append(np.random.uniform(size=len(dataframe)))

    matrix = np.array(matrix).T
    return jsonify({'matrix': matrix.tolist()})


if __name__ == '__main__':
    app.run(debug=True)
