from sentence_transformers import SentenceTransformer

## Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Example test
text = "A fact table stores business measurments"

#Convert text into an embedding
embedding = model.encode(text)

print("Embedding : " , embedding)
print("Number of dimensions: " , len(embedding))