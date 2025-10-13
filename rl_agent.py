import torch
from torch.utils.data import DataLoader, Dataset
from torch.optim import Adam
from transformers import T5Tokenizer, T5ForConditionalGeneration

class FeedbackDataset(Dataset):
    """Custom PyTorch Dataset to handle feedback data for training."""
    def __init__(self, feedback_data, tokenizer, max_length=512):
        # We only train on examples where the user provided a correct answer.
        self.feedback_data = [item for item in feedback_data if item.get('reward', 0) > 0]
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.feedback_data)

    def __getitem__(self, idx):
        entry = self.feedback_data[idx]
        prompt = entry['prompt']
        correct_response = entry['correct_response']
        
        input_encoding = self.tokenizer(
            prompt, max_length=self.max_length, padding='max_length',
            truncation=True, return_tensors='pt'
        )
        target_encoding = self.tokenizer(
            correct_response, max_length=self.max_length, padding='max_length',
            truncation=True, return_tensors='pt'
        )
        
        return {
            'input_ids': input_encoding['input_ids'].squeeze(),
            'attention_mask': input_encoding['attention_mask'].squeeze(),
            'labels': target_encoding['input_ids'].squeeze()
        }

class RLAgent:
    """Manages the T5 model, including text generation and fine-tuning."""
    def __init__(self, model, tokenizer, lr=5e-5):
        self.model = model
        self.tokenizer = tokenizer
        self.lr = lr
        self.feedback_data = []
        self.optimizer = Adam(self.model.parameters(), lr=self.lr)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        print(f"RL Agent initialized on device: {self.device}")

    def generate_response(self, prompt, max_new_tokens=50):
        """Generates a hint using the T5 model."""
        self.model.eval()
        inputs = self.tokenizer(prompt, return_tensors='pt', max_length=512, truncation=True)
        input_ids = inputs['input_ids'].to(self.device)
        
        max_length = len(input_ids[0]) + max_new_tokens
        with torch.no_grad():
            generated_outputs = self.model.generate(
                input_ids=input_ids,
                max_length=min(max_length, 1024),
                num_return_sequences=1,
                temperature=0.6,
                top_k=40,
                repetition_penalty=1.2,
                pad_token_id=self.tokenizer.eos_token_id,
                do_sample=True
            )

        decoded_output = self.tokenizer.decode(generated_outputs[0], skip_special_tokens=True)
        return decoded_output.strip()

    def store_feedback(self, prompt, generated, correct, reward):
        """Stores feedback in memory."""
        self.feedback_data.append({
            'prompt': prompt, 'generated_response': generated,
            'correct_response': correct, 'reward': reward
        })
        print(f"Stored feedback (Reward: {reward}). Total feedback items: {len(self.feedback_data)}")

    def train(self):
        """Fine-tunes the model on all collected positive feedback."""
        positive_feedback_dataset = FeedbackDataset(self.feedback_data, self.tokenizer)
        if not positive_feedback_dataset:
            print("Training skipped: No positive feedback available.")
            return

        dataloader = DataLoader(positive_feedback_dataset, batch_size=4, shuffle=True)
        self.model.train()
        total_loss = 0
        
        print(f"Starting training on {len(positive_feedback_dataset)} positive examples...")
        for batch in dataloader:
            self.optimizer.zero_grad()
            outputs = self.model(
                input_ids=batch['input_ids'].to(self.device),
                attention_mask=batch['attention_mask'].to(self.device),
                labels=batch['labels'].to(self.device)
            )
            loss = outputs.loss
            loss.backward()
            self.optimizer.step()
            total_loss += loss.item()

        print(f"Model fine-tuned. Average Loss: {total_loss / len(dataloader):.4f}")

