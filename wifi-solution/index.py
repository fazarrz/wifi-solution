from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def loadSymptoms():
    symp = pd.read_csv('data/symptoms.csv', delimiter=';')
    return symp

def loadProblems():
    problems = pd.read_csv('data/problems.csv', delimiter=';', index_col='id')
    return problems

def loadRules():
    rules = pd.read_csv('data/rules.csv', delimiter=';', index_col='id')
    return rules

@app.route('/start', methods=['GET'])
def startApplication():
    symp = loadSymptoms()

    if not symp.empty:
        current_symp = symp.iloc[0].to_dict()
        return jsonify({'symptoms': current_symp['symptoms'], 'current_index': 0, 'responses': {}})
    return jsonify({'error': 'Gejala tidak ditemukan'})

@app.route('/next', methods=['POST'])
def nextSymptom():
    data = request.json
    current_index = data.get('current_index', 0)
    response = data.get('response', '')
    responses = data.get('responses', {})

    symp = loadSymptoms()
    if not symp.empty:
        symptom_code = symp.iloc[current_index]['kode']
        responses[symptom_code] = 1 if response == 'yes' else 0

        current_index += 1

        if current_index < len(symp):
            next_symp = symp.iloc[current_index].to_dict()
            return jsonify({'symptoms': next_symp['symptoms'], 'current_index': current_index, 'responses': responses, 'completed': False})
        else:
            
            rule = loadRules()
            for index, row in rule.iterrows():
                if all(responses.get(symptom, 0) == row[symptom] for symptom in row.index):
                    problems = loadProblems()
                    problem = problems.loc[index]['masalah']
                    solution = problems.loc[index]['solusi']
                    return jsonify({'message': f'Anda mengalami masalah: {problem}', 'solution': f'Solusi: {solution}', 'responses': responses, 'completed': True})

            return jsonify({'message': 'Tidak ditemukan masalah yang sesuai dengan gejala Anda.', 'responses': responses, 'completed': True})

    return jsonify({'error': 'Gejala tidak ditemukan'})

if __name__ == '__main__':
    app.run(port=3000, debug=True)
