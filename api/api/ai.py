import random
import torch
from transformers import DistilBertForSequenceClassification, DistilBertTokenizer
import joblib  # Import joblib for loading label_encoder
import os
import json

def process(question, fallback_threshold=0.75, fallback_response="I'm sorry, I didn't understand your inquiry."):
   model_path = os.path.join(os.path.dirname(__file__), 'distilbert')
   # Load the fine-tuned model
   model = DistilBertForSequenceClassification.from_pretrained(model_path)

   # Load the corresponding tokenizer
   tokenizer = DistilBertTokenizer.from_pretrained(model_path)

   # Set device (CPU or GPU)
   device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
   model.to(device)
   # Load the label encoder
   label_encoder_file = model_path + '\\label_encoder.joblib'
   label_encoder = joblib.load(label_encoder_file)

    # Tokenize the input question
   encoded_question = tokenizer(question, truncation=True, padding=True, return_tensors='pt')
   encoded_question = {key: tensor.to(device) for key, tensor in encoded_question.items()}

    # Perform inference
   with torch.no_grad():
      output = model(**encoded_question)
      logits = output.logits
      predicted_label_idx = logits.argmax().item()

   # Decode the predicted label
   predicted_label = label_encoder.inverse_transform([predicted_label_idx])[0]

   probs = torch.max(output.logits, 1)
   prob = probs.values[0]  # Using .values to access the tensor content

   if prob.item() > fallback_threshold:
      with open(model_path + '/dataset.json', encoding="utf-8") as dataset:
         data = json.load(dataset)
      # Check if the predicted label is in the list of intents
      if predicted_label in [intent['tag'] for intent in data['intents']]:
         # Find the intent corresponding to the predicted label
         intent = next((intent for intent in data['intents'] if intent['tag'] == predicted_label), None)

         # Retrieve and return a random response
         if intent and 'responses' in intent:
            responses = intent['responses']
            random_response = random.choice(responses)
            return predicted_label, random_response

   # If the predicted label is not in the list of intents or the confidence is below the threshold, return the fallback response
   return "fallback", fallback_response