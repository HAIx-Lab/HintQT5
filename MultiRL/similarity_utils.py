from sentence_transformers import SentenceTransformer, util
import torch

class SimilarityModel:
    """
    A wrapper for a sentence-transformer model to compute semantic similarity
    and map it to a graded reward.
    """
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """Initializes and loads the sentence-transformer model."""
        print(f"Loading sentence-transformer model: {model_name}...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            self.model = SentenceTransformer(model_name, device=self.device)
            print(f"Sentence-transformer model loaded successfully on {self.device}.")
        except Exception as e:
            print(f"Error loading sentence-transformer model: {e}")
            print("Please ensure 'sentence-transformers' and 'torch' are installed.")
            raise

    def _calculate_similarity(self, text1, text2):
        """Calculates the cosine similarity between two text strings."""
        if not text1 or not text2:
            return 0.0
        
        # Encode the texts into vector embeddings
        embedding1 = self.model.encode(text1, convert_to_tensor=True)
        embedding2 = self.model.encode(text2, convert_to_tensor=True)
        
        # Compute cosine-similarity score
        cosine_score = util.pytorch_cos_sim(embedding1, embedding2)
        return cosine_score.item()

    def calculate_reward(self, generated_hint, correct_hint):
        """
        Calculates cosine similarity and maps it to a graded reward scale from 1 to 5,
        as described in the experimental setup.
        """
        similarity = self._calculate_similarity(generated_hint, correct_hint)
        
        # Map the similarity score (from ~0 to 1) to the specified reward scale (1 to 5)
        if similarity >= 0.95:
            reward = 5  # Perfect or near-perfect semantic match
        elif similarity >= 0.8:
            reward = 4  # High similarity
        elif similarity >= 0.6:
            reward = 3  # Moderate similarity
        elif similarity >= 0.4:
            reward = 2  # Low similarity
        else:
            reward = 1  # Irrelevant or incorrect
            
        return reward, similarity
