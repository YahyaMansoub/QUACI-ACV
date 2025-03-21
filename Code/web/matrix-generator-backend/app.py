from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pandas as pd
import os

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


@app.route('/upload-dataframe', methods=['POST'])
def upload_dataframe():
    try:
        # Get the data frame from the request
        data = request.json
        dataframe = pd.DataFrame(data['dataframe'])

        # Generate a unique filename
        filename = os.path.join(UPLOAD_FOLDER, 'dataframe.csv')

        # Save the data frame to a CSV file
        dataframe.to_csv(filename, index=False)

        return jsonify({'message': 'Data frame saved successfully!', 'filename': filename}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
