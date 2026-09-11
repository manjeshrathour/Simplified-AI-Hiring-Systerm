# inspect_faiss.py

import faiss
import pickle
import numpy as np

# --- Configuration ---
# These paths MUST match the paths in your `vector_store.py` or settings
FAISS_INDEX_PATH = "./data/faiss_index"
METADATA_PATH = "./data/faiss_index_metadata.pkl"

def inspect_vector_database():
    """
    Loads the FAISS index and its metadata to print out what's inside.
    """
    print("--- Inspecting FAISS Vector Database ---\n")
    
    try:
        # 1. Load the FAISS index
        index = faiss.read_index(FAISS_INDEX_PATH)
        print(f"✅ Successfully loaded FAISS index from: {FAISS_INDEX_PATH}")
        print(f"   - Total vectors in index: {index.ntotal}")
        print(f"   - Vector dimension: {index.d}\n")

        # 2. Load the metadata
        with open(METADATA_PATH, "rb") as f:
            metadata = pickle.load(f)
        print(f"✅ Successfully loaded metadata from: {METADATA_PATH}")
        print(f"   - Total metadata entries: {len(metadata)}\n")

        # 3. Print out the contents
        print("--- Stored Documents ---")
        if not metadata:
            print("No metadata found.")
            return

        for i, doc_id in enumerate(metadata):
            # The FAISS index stores vectors by their numerical order (0, 1, 2, ...)
            # The metadata file maps this numerical index `i` to your custom doc_id
            
            # You can reconstruct the vector if you want to see it, though it's just numbers
            # vector = index.reconstruct(i)
            
            print(f"  Index {i}:")
            print(f"    - Document ID: {doc_id}")
            # print(f"    - Vector (first 5 dims): {vector[:5]}...") # Uncomment to see the vector data
        
        print("\n--- Inspection Complete ---")

    except FileNotFoundError as e:
        print(f"❌ Error: Could not find a required file. Make sure paths are correct.")
        print(f"   - Missing file: {e.filename}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    inspect_vector_database()