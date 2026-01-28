### 🎤 [00:19:00 – 00:20:06] Positional encoding  
**Timestamp**: 00:19:00 – 00:20:06

**Key Concepts**  
- Word order and position in a sentence are crucial for meaning.  
- Positional encoding is added to word vectors to incorporate information about word positions.  
- Positional encoding uses sine and cosine waves of different frequencies.  
- This encoding is merged into the vector representing each word.  
- Positional encoding enables the model to distinguish between sentences with the same words but different word orders.

**Definitions**  
- **Positional encoding**: A method of adding information about the position of words in a sequence to their vector representations, typically using sine and cosine functions at varying frequencies.

**Key Facts**  
- The model uses cosine and sine waves with different frequencies to encode position.  
- Positional encoding is combined with semantic vectors to form the final input representation for the model.

**Examples**  
- The sentences "John eats burger" vs. "Burger eats John" illustrate how word order changes meaning, highlighting the need for positional encoding.

**Key Takeaways 🎯**  
- Simply having semantic vectors is not enough; the model must know the order of words to understand meaning correctly.  
- Positional encoding cleverly integrates position information into vectors using trigonometric functions.  
- This technique is foundational for enabling attention mechanisms to process sequences effectively.