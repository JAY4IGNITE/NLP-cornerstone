import argparse
import os
import sys
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def main():
    parser = argparse.ArgumentParser(description="CLI inference for the Student AI Chatbot")
    parser.add_argument('--query', type=str, required=True, help="The query to ask the chatbot")
    parser.add_argument('--model', type=str, default='models/intent/logistic', help="Path to intent model directory")
    parser.add_argument('--threshold', type=float, default=0.6, help="Confidence threshold for intent classification")
    args = parser.parse_args()

    if not os.path.exists(args.model):
        print(f"Model directory '{args.model}' not found. Please train the model first.")
        sys.exit(1)

    print("Loading application state (this may take a moment to load embeddings)...")
    start_time = time.time()
    
    # We set environment variables before importing settings so that the app uses the CLI arguments
    os.environ["INTENT_MODEL_DIR"] = args.model
    os.environ["MIN_FUSED_SCORE"] = str(args.threshold) # Approximation of confidence handling for RAG
    
    from backend.app.core.config import get_settings
    from backend.app.runtime import build_state
    
    settings = get_settings()
    state = build_state(settings)
    
    load_latency = time.time() - start_time
    print(f"[State loaded in {load_latency * 1000:.1f} ms]\n")

    print(f"Query: {args.query}\n")
    
    infer_start = time.time()
    outcome = state.orchestrator.answer(args.query)
    infer_latency = time.time() - infer_start
    
    print(f"Intent: {outcome.intent_label}")
    print(f"Confidence: {outcome.intent_confidence:.2f}\n")
    
    if outcome.status == "abstained":
        print("Status: ABSTAINED")
        print(f"Answer: {outcome.answer}")
    else:
        print("Status: ANSWERED")
        print("Retrieved Evidence:")
        for citation in outcome.citations:
            print(f"- {citation.document_id} ({citation.title}) - {citation.location}")
        
        print(f"\nAnswer:\n{outcome.answer}")
        
    print(f"\n[Inference Latency: {infer_latency * 1000:.1f} ms]")

if __name__ == '__main__':
    main()

