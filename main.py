from flask import Flask, request, jsonify
import pandas as pd
import openai
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS to allow requests from frontend

# Load datasets
description_df = pd.read_csv('description.csv')
diets_df = pd.read_csv('diets.csv')
medications_df = pd.read_csv('medications.csv')
precautions_df = pd.read_csv('precautions_df.csv')
workout_df = pd.read_csv('workout_df.csv')
symptoms_df = pd.read_csv('symtoms_df.csv')

# Replace underscores with spaces in symptom columns
symptoms_df['Symptom_1'] = symptoms_df['Symptom_1'].str.replace('_', ' ')
symptoms_df['Symptom_2'] = symptoms_df['Symptom_2'].str.replace('_', ' ')
symptoms_df['Symptom_3'] = symptoms_df['Symptom_3'].str.replace('_', ' ')
symptoms_df['Symptom_4'] = symptoms_df['Symptom_4'].str.replace('_', ' ')

# Rename the 'disease' column in workout_df to 'Disease' for consistency
workout_df.rename(columns={'disease': 'Disease'}, inplace=True)

# Merge datasets
merged_df = symptoms_df.merge(description_df, on='Disease', how='left')
merged_df = merged_df.merge(diets_df, on='Disease', how='left')
merged_df = merged_df.merge(medications_df, on='Disease', how='left')
merged_df = merged_df.merge(precautions_df, on='Disease', how='left')
merged_df = merged_df.merge(workout_df[['Disease', 'workout']], on='Disease', how='left')

# OpenAI API key setup
openai.api_key = 'your-openai-api-key'

# Function to query OpenAI LLM
def query_llm(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=500,
        temperature=0.7
    )
    return response.choices[0].text.strip()

# Function to get recommendations based on symptoms
def get_recommendations_from_data(symptom_input):
    symptoms = [sym.strip().lower() for sym in symptom_input.split(",")]
    
    relevant_diseases = merged_df[
        merged_df.apply(lambda row: any(symptom in [str(row['Symptom_1']).strip().lower(),
                                                    str(row['Symptom_2']).strip().lower(),
                                                    str(row['Symptom_3']).strip().lower(),
                                                    str(row['Symptom_4']).strip().lower()]
                        for symptom in symptoms), axis=1)
    ]
    
    if relevant_diseases.empty:
        return "No matching diseases found for the given symptoms."
    
    result = relevant_diseases.iloc[0]
    output = {
        "Disease": result['Disease'],
        "Description": result['Description'],
        "Diet": result['Diet'],
        "Medication": result['Medication'],
        "Precautions": [result['Precaution_1'], result['Precaution_2'], result['Precaution_3'], result['Precaution_4']],
        "Workout": result['workout'],
        "Symptoms": [result['Symptom_1'], result['Symptom_2'], result['Symptom_3'], result['Symptom_4']]
    }
    return output

# Function to generate recommendations using LLM
def generate_llm_recommendation(symptom_input):
    structured_data = get_recommendations_from_data(symptom_input)
    
    if isinstance(structured_data, str):
        prompt = f"Based on the symptoms: {symptom_input}, what could be the potential disease, its description, diet, medication, precautions, and workout?"
        llm_response = query_llm(prompt)
        return {"LLM Response": llm_response}
    else:
        return structured_data

# Route to handle POST request for symptom recommendations
@app.route('/get_recommendation', methods=['POST'])
def get_recommendation():
    symptoms = request.json['symptoms']
    recommendations = generate_llm_recommendation(symptoms)
    return jsonify(recommendations)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)