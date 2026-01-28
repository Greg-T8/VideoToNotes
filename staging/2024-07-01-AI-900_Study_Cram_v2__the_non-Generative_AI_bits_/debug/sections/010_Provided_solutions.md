### 🎤 [00:23:07 – 00:30:47] Provided solutions  
**Timestamp**: 00:23:07 – 00:30:47

**Key Concepts**  
- Provided AI solutions are pre-trained models designed for specific tasks.  
- Vision capabilities include OCR, image tagging, object detection, face detection, and live face verification.  
- Natural language capabilities include chatbots, summarization, question answering, speech-to-text, text-to-speech, and translation.  
- Document intelligence can extract structured data from forms, invoices, and large text documents.  
- Knowledge mining extracts and indexes information from structured, semi-structured, and unstructured data to make it searchable and enrichable.  
- Custom AI solutions can be built by combining or extending these pre-trained models.  
- Azure AI services offer a wide range of single-purpose and multi-service AI resources.  
- Single service resources often have free tiers for experimentation.  
- Multi-service resources combine many AI capabilities under one endpoint but lack free tiers and granular cost tracking.  
- Azure OpenAI and AI Search are special service types with different availability and pricing models.  
- AI services expose REST endpoints for applications to interact with, typically using HTTP and JSON.

**Definitions**  
- **Optical Character Recognition (OCR)**: Technology to read and extract text from images.  
- **Document Intelligence**: AI capability to understand and extract data from documents such as forms and invoices.  
- **Knowledge Mining**: Process of extracting, indexing, and enriching information from various data types to make it searchable and usable by other applications.  
- **Single Service Resource**: An Azure AI resource dedicated to one specific AI capability (e.g., computer vision, face API).  
- **Multi-Service Resource**: An Azure AI resource that provides access to multiple AI capabilities through a single endpoint, excluding OpenAI and AI Search.  
- **Endpoint**: A RESTful URL where an AI service is accessed by applications, communicating via HTTP and exchanging JSON data.

**Key Facts**  
- Many Azure AI single service resources have free tiers allowing a certain number of free calls for learning and experimentation.  
- Azure OpenAI service does not have a free tier.  
- AI Search has a limited free tier but lacks some advanced features like semantic re-ranking.  
- Single service resources provide granular cost tracking and role-based access control per resource.  
- Multi-service resources do not offer free tiers and have a shared endpoint, making cost attribution less granular.  
- Applications interact with AI services via REST endpoints using HTTP requests and JSON responses.

**Examples**  
- Vision capabilities: reading text from images (OCR), tagging images, detecting objects and faces, verifying if a face is live.  
- Natural language: chatbots, summarizing text, question answering, speech-to-text, text-to-speech, translation.  
- Document intelligence: extracting addresses, phone numbers, invoice items from forms.  
- Knowledge mining: extracting text from images or audio via vision or speech services to index and make searchable.

**Key Takeaways 🎯**  
- Provided AI solutions cover a broad range of specialized tasks, enabling rapid development without training models from scratch.  
- Azure AI offers flexible resource types: single service for focused use with free tiers, multi-service for convenience but without free tiers or detailed cost tracking.  
- Understanding the distinction between single service, multi-service, and OpenAI resources is important for cost management and capability planning.  
- REST endpoints are the standard interface for integrating AI services into applications, facilitating easy HTTP-based communication.  
- Experimenting with free tiers of single service resources is recommended for hands-on learning and prototyping.