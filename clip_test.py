import torch 
import open_clip 
from PIL import Image 
import numpy as np 

# Load model (this downloads automatically first time) 
model, _, preprocess = open_clip.create_model_and_transforms( 
    'ViT-B-32',  # lightweight and good 
    pretrained='laion2b_s34b_b79k' 
) 

model.eval() 

# Choose device 
device = "cuda" if torch.cuda.is_available() else "cpu" 
model = model.to(device) 

def get_image_embedding(image_path): 
    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device) 
    
    with torch.no_grad(): 
        embedding = model.encode_image(image) 
        embedding /= embedding.norm(dim=-1, keepdim=True) 

    return embedding.cpu().numpy() 

# Test on two images 
try:
    emb1 = get_image_embedding("image1.jpg") 
    emb2 = get_image_embedding("image2.jpg") 

    # Cosine similarity 
    similarity = np.dot(emb1, emb2.T) 

    print("Similarity Score:", similarity[0][0])
except FileNotFoundError as e:
    print(f"Error: {e}. Please ensure image1.jpg and image2.jpg exist.")
except Exception as e:
    print(f"An error occurred: {e}")
