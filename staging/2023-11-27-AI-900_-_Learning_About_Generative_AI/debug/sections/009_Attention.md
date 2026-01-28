### 🎤 [00:20:06 – 00:26:41] Attention  
**Timestamp**: 00:20:06 – 00:26:41

**Key Concepts**  
- Multi-headed attention, self-attention, and masked self-attention are core mechanisms in transformer models.  
- Self-attention allows the model to weigh the importance of different words in the input sequence relative to each other.  
- Masked self-attention restricts attention to the current and previous words only, preventing "looking ahead" in sequence generation.  
- Attention is computed using query, key, and value vectors for each word/token.  
- The attention score is derived from the dot product of query and key vectors, scaled and multiplied by the value vector.  
- The output of attention is fed into a feed-forward neural network, which forms the bulk of the model’s computation.  
- The entire attention and feed-forward process is repeated multiple times (stacked layers) to build complex representations.  
- Encoder-decoder architectures exist, but many models (e.g., GPT) use only the decoder with masked multi-head attention.  
- Encoder-only models (e.g., BERT) are also common and serve different purposes.  
- The attention mechanism enables the model to maintain context over long sequences, preventing it from forgetting critical information.  

**Definitions**  
- **Self-Attention**: A mechanism where each word/token in a sequence attends to other words/tokens in the same sequence to understand context and relationships.  
- **Masked Self-Attention**: A variant of self-attention used in decoder-only models where each token can only attend to itself and previous tokens, not future ones.  
- **Query, Key, Value Vectors**: For each token, the model computes these vectors to measure relationships; the query vector is compared against key vectors of other tokens to determine attention weights, which are then applied to the value vectors.  
- **Context Vector**: The resulting vector representation after applying attention and feed-forward layers, encapsulating the contextual meaning of the input sequence.  

**Key Facts**  
- Attention scores are calculated using the dot product of query and key vectors, followed by multiplication with value vectors.  
- The process of attention plus feed-forward network is repeated multiple times (number of layers varies by model).  
- GPT models use only the decoder part with masked multi-head attention, feeding outputs back as inputs for next token prediction.  
- Encoder-decoder models can produce language-neutral representations useful for tasks like translation, but decoder-only models are simpler and faster to train.  
- Maintaining context (e.g., remembering negations like "don't") is critical to avoid misinterpretation.  
- Large transformer models are computationally expensive both in training and inference, motivating research into smaller, task-specific models.  

**Examples**  
- Sentence example illustrating masked self-attention:  
  *"John was using a computer until it crashed."*  
  - When processing the word "it," the model attends strongly to "computer" (likely cause of crash), not "John."  
  - When processing "crashed," it relates strongly to "computer," whereas "using" relates more to "John."  
- Practical example emphasizing importance of context:  
  *"Don't give John green things to eat."*  
  - Forgetting "don't" changes the meaning drastically, highlighting why attention must preserve earlier context.  

**Key Takeaways 🎯**  
- Self-attention mechanisms enable transformers to understand and maintain relationships between words across long sequences.  
- Masked self-attention is essential for autoregressive models like GPT to predict the next word without peeking ahead.  
- Query, key, and value vectors form the mathematical basis for computing attention scores.  
- The repeated stacking of attention and feed-forward layers builds deep contextual understanding.  
- Encoder-decoder models are useful for tasks like translation, but many large language models use only the decoder for efficiency.  
- Preserving context (especially negations and dependencies) is crucial for accurate language understanding and generation.  
- Transformer models are powerful but computationally intensive, leading to ongoing efforts to develop smaller, more efficient variants.