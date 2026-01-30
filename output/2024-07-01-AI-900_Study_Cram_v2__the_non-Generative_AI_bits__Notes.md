# AI-900 Study Cram v2 (the non-Generative AI bits) - Exam Notes

**Video:** [https://www.youtube.com/watch?v=bTkUTkXrqOQ](https://www.youtube.com/watch?v=bTkUTkXrqOQ)  
**Published:** 2024-07-01  
**Duration:** 1:16:59  

*Generated on 2026-01-30 08:47*

---

## Table of Contents

- [Introduction](#introduction)
- [Preparation materials](#preparation-materials)
- [What is AI](#what-is-ai)
- [Machine learning](#machine-learning)
- [Training process](#training-process)
- [Training data types](#training-data-types)
- [Azure Machine Learning Studio](#azure-machine-learning-studio)
- [Deep learning](#deep-learning)
- [Type summary](#type-summary)
- [Provided solutions](#provided-solutions)
- [Endpoints and keys](#endpoints-and-keys)
- [Responsible AI](#responsible-ai)
- [Computer vision](#computer-vision)
- [Vision services](#vision-services)
- [Face](#face)
- [Natural Language](#natural-language)
- [Speech](#speech)
- [Translation](#translation)
- [Document intelligence](#document-intelligence)
- [Knowledge mining](#knowledge-mining)
- [Review](#review)
- [Exam tips](#exam-tips)
- [Close](#close)

## Introduction

**Timestamp**: 00:00:00 – 00:00:44

**Key Concepts**

- Updating study materials with the latest information
- Differentiation between generative AI content and general Azure AI content
- Importance of using official Microsoft Learn resources for exam preparation

**Definitions**

- **Generative AI**: Not covered in this section; referenced as a separate study cram topic.

**Key Facts**

- The generative AI portion is covered in a separate study cram.
- Microsoft Learn page provides updated information on exam preparation.
- Microsoft Azure AI Fundamentals course is recommended for study.
- The Learn page includes skills measured, preparation tips, and practice assessments.

**Examples**

- None mentioned

**Key Takeaways 🎯**

- Use this study cram for general Azure AI information excluding generative AI.
- Watch the separate generative AI study cram for a complete understanding.
- Start exam preparation with the Microsoft Learn page for the most current and comprehensive resources.
- Utilize practice assessments and sandbox environments on Microsoft Learn to familiarize yourself with the exam format and reduce anxiety.

---

## Preparation materials

**Timestamp**: 00:00:44 – 00:02:28

**Key Concepts**

- Start exam preparation with the Microsoft Learn page for updated and official information.
- Microsoft Learn provides details on exam updates, skills measured, preparation guidance, and practice opportunities.
- The Azure AI Fundamentals course on Microsoft Learn is highly recommended and regularly updated.
- Practice assessments and sandbox environments help familiarize with exam format and reduce anxiety.
- The exam is 45 minutes long, fundamental level, no coding or deployment required.
- Skills measured are clearly broken down into key areas with specific skills to understand.
- Use the skills measured list as a checklist to assess your readiness before the exam.
- Study crams serve as quick refreshers just before taking the exam.

**Definitions**

- **Sandbox**: A practice environment that simulates the exam interface, allowing candidates to experience the exam layout and question types beforehand.

**Key Facts**

- Exam duration: 45 minutes.
- Exam level: Fundamental (basic understanding, no coding/deployment).
- Microsoft Learn provides official, up-to-date learning paths and practice assessments.
- Skills measured are detailed and broken down into main areas and specific skills.

**Examples**

- Practice assessments on Microsoft Learn.
- Sandbox environment to explore exam interface and question types.

**Key Takeaways 🎯**

- Begin preparation with Microsoft Learn’s Azure AI Fundamentals course.
- Use the sandbox to familiarize yourself with the exam environment to reduce exam-day anxiety.
- Review the skills measured document thoroughly and check off areas of confidence.
- Study crams are best used as a final quick review before the exam.
- The exam focuses on understanding which AI technologies to use rather than coding or deploying solutions.

---

## What is AI

**Timestamp**: 00:02:28 – 00:04:38

**Key Concepts**

- Intelligence involves various human capabilities such as seeing, describing, reading text, speaking, hearing, translating, decision-making, and predicting.
- Artificial Intelligence (AI) is about computers imitating some aspects of human intelligence and behavior.
- AI is fundamentally software that mimics human capabilities.
- Writing explicit code for every possible scenario (e.g., number recognition) is impractical.
- Machine learning is a subset of AI where computers train themselves using past data to make future predictions.

**Definitions**

- **Artificial Intelligence (AI)**: The ability of a computer to imitate human capabilities and behaviors.
- **Machine Learning**: A subset of AI focused on training computers with data so they can learn patterns and make predictions without explicit programming for every scenario.

**Key Facts**

- Human intelligence includes capabilities such as image recognition, captioning, text reading, speech, transcription, translation, decision-making, and prediction.
- Explicitly coding all logic for tasks like number recognition is complex and inefficient.
- Machine learning uses training data to build models for prediction.

**Examples**

- Humans can look at a picture and identify objects or provide detailed captions.
- Humans can read text from images and convert speech to text.
- Humans can translate languages (though limited in the example given).
- Number recognition as an example where writing all logic manually is difficult.

**Key Takeaways 🎯**

- AI aims to replicate human intelligence in computers through software.
- Instead of hardcoding every rule, AI systems can learn from data.
- Machine learning enables computers to train on historical data and predict future outcomes.
- Understanding AI starts with recognizing it as imitation of human cognitive functions.

---

## Machine learning

**Timestamp**: 00:04:38 – 00:05:22

**Key Concepts**

- Machine learning is a subset of artificial intelligence.
- Instead of manually coding every bit of logic, the computer trains itself using past data.
- The trained model can then make future predictions based on learned patterns.
- Training data is essential for machine learning, serving as the foundation for the model to learn.

**Definitions**

- **Machine learning**: A branch of artificial intelligence where a computer uses past data (training data) to train a model that can make predictions or decisions without being explicitly programmed for every scenario.

**Key Facts**

- Machine learning relies on having a set of training data.
- Training data consists of many examples with associated correct answers.
- Features are the individual pieces of data or attributes used to describe each example in the training data.

**Examples**

- Number recognition: Instead of coding every possible variation of the number "1," the computer learns from many examples of the number "1" to recognize it.
- Pictures of numbers (e.g., #1, #2, #3, #4) used as training data.
- Other examples mentioned include pictures of oranges or historical temperature data from engines.

**Key Takeaways 🎯**

- Machine learning automates the process of learning from data rather than relying on explicit programming.
- The quality and quantity of training data are crucial for effective machine learning.
- Features represent the data attributes that the model uses to learn patterns.
- Machine learning enables computers to generalize from past examples to new, unseen data.

---

## Training process

**Timestamp**: 00:05:22 – 00:09:33

**Key Concepts**

- Machine learning uses training data to build models that can make future predictions.
- Training data consists of features (input data) and labels (correct answers).
- Algorithms find relationships between features and labels to generalize predictions.
- Different algorithms suit different types of data and problems.
- The output of training is a model that can predict labels for new data.
- The training process is iterative, involving training and testing phases.
- Testing data is used to evaluate model accuracy before deployment.
- Model parameters may be tweaked based on testing results to improve performance.
- There are different types of training; supervised learning involves labeled data.

**Definitions**

- **Machine Learning**: A subset of artificial intelligence where computers train themselves using past data to make future predictions.
- **Features**: The input data values or attributes used to train the model (e.g., pictures, measurements).
- **Label**: The correct answer or outcome associated with each set of features in the training data.
- **Model**: The trained algorithm output that can predict labels for new input data.
- **Supervised Learning**: A type of machine learning where the training data includes both features and their correct labels.

**Key Facts**

- Training data must be labeled to enable supervised learning.
- Common algorithms include decision trees, linear regression, and support vector machines.
- Decision trees split data based on feature values until reaching leaf nodes representing outcomes.
- Linear regression fits a straight line through data points to predict continuous values.
- Support vector machines find the optimal boundary that separates clusters of data.
- The training process involves using training data to build the model and testing data to validate it.
- Model refinement involves tweaking parameters until the model performs satisfactorily.

**Examples**

- Pictures of numbers (#1, #2, #3, #4) labeled correctly.
- Historical temperature data of engines with corresponding labels.
- House price prediction using square footage as a feature (linear regression).
- Clustering data separated by a line with maximum gap (support vector machines).

**Key Takeaways 🎯**

- Machine learning relies heavily on quality labeled training data.
- Choosing the right algorithm depends on the data type and problem.
- The training process is iterative: train, test, evaluate, and refine.
- The final trained model can predict labels for new, unseen data.
- Supervised learning requires labeled data, which is crucial for model accuracy.
- Testing data is essential to avoid overfitting and ensure real-world applicability.

---

## Training data types

**Timestamp**: 00:09:33 – 00:13:40

**Key Concepts**

- Different types of training data used in machine learning.
- Supervised learning involves labeled data.
- Types of supervised learning include regression, binary classification, and multiclass classification.
- Unsupervised learning involves unlabeled data and focuses on clustering or grouping based on similarities.
- Azure Machine Learning Studio supports creating datasets, labeling data, training models, testing performance, and deploying models.
- Models can be deployed in various environments including cloud containers and on-premises.

**Definitions**

- **Supervised Learning**: A type of machine learning where the training data includes the correct labels for each data point.
- **Regression**: A supervised learning task where the output is numeric, e.g., predicting house prices.
- **Classification**: A supervised learning task where the output is a category or class.
  - **Binary Classification**: Classification with two mutually exclusive classes (e.g., will a viewer like a video or not).
  - **Multiclass Classification**: Classification with multiple possible classes (e.g., video genres like horror, fiction, learning).
- **Unsupervised Learning**: A type of machine learning where the data has no labels, and the goal is to find patterns or clusters within the data.

**Key Facts**

- Supervised learning requires labeled data.
- Binary classification answers yes/no or is/is-not type questions.
- Multiclass classification handles multiple categories.
- Unsupervised learning looks for natural groupings in data without labels.
- Azure Machine Learning Studio URL: ml.azure.com
- Azure ML Studio allows importing data (e.g., from BLOB storage), labeling, training, testing, and deploying models.
- Models can be deployed in containers on-premises or in Azure services like Kubernetes or container instances.

**Examples**

- Regression example: Predicting house prices.
- Binary classification example: Predicting if a viewer will like a video or not.
- Multiclass classification example: Categorizing videos into genres such as horror, fiction, or learning.

**Key Takeaways 🎯**

- Understanding the type of training data (supervised vs unsupervised) is crucial for selecting the right machine learning approach.
- Supervised learning requires labeled datasets and can be split into regression and classification tasks.
- Unsupervised learning is useful when labels are not available and focuses on discovering inherent data structures.
- Azure Machine Learning Studio is a comprehensive tool for managing datasets, training models, and deploying them in flexible environments.
- Custom training is not always necessary due to availability of pre-built models, but Azure ML Studio is valuable when customization is needed.

---

## Azure Machine Learning Studio

**Timestamp**: 00:13:40 – 00:14:37

**Key Concepts**

- Azure Machine Learning Studio enables deployment of trained models to various environments, including containers.
- Models can be hosted not only in the cloud but also on-premises or in container services like Azure Kubernetes Service (AKS) or Azure Container Instances (ACI).
- Azure Machine Learning Studio is a cloud service designed to facilitate custom model training.
- While many pre-built models exist, Azure Machine Learning Studio is used when custom training is required.

**Definitions**

- **Azure Machine Learning Studio**: An Azure cloud service that helps users perform custom training of machine learning models and deploy them flexibly across different environments.

**Key Facts**

- Models trained in Azure Machine Learning Studio can be deployed to containers.
- Deployment options include on-premises containers, Azure Kubernetes Service, and Azure Container Instances.
- Azure Machine Learning Studio supports a variety of customized training scenarios.

**Examples**

- Deploying a trained model to a container running on-premises.
- Using Azure Kubernetes Service or Azure Container Instances to host the model.

**Key Takeaways 🎯**

- Azure Machine Learning Studio is a powerful tool for custom training and flexible deployment of machine learning models.
- It supports multiple deployment targets beyond just cloud hosting.
- Users do not always need custom training due to availability of pre-built models, but Azure Machine Learning Studio is essential when customization is necessary.

---

## Deep learning

**Timestamp**: 00:14:37 – 00:22:32

**Key Concepts**

- Deep learning is a subset of machine learning designed to handle complex relationships that basic algorithms cannot express.
- Deep learning models use neural networks composed of multiple layers of neurons.
- Each neuron applies an activation function to decide whether to pass a value forward.
- Neural networks have an input layer, multiple hidden layers, and an output layer.
- Connections between neurons have associated weights and biases that adjust the signal.
- Training involves adjusting these weights and biases to model complex data patterns.
- Large language models (LLMs) like GPT are powered by very deep neural networks with tens of hidden layers.
- The softmax function is commonly used at the output to convert raw values into a probability distribution.
- Training large models requires massive computational resources (e.g., thousands of GPUs over months).
- For most users, retraining large models is impractical; instead, techniques like prompt engineering and retrieval-augmented generation (RAG) are used.
- Smaller neural networks can be trained effectively with less data for specific tasks.

**Definitions**

- **Deep learning**: A subset of machine learning using neural networks with multiple layers to model complex data relationships.
- **Neural network**: A computational model made up of layers of interconnected neurons, where each neuron processes input and passes output to the next layer.
- **Neuron (Activation function)**: A unit in a neural network that applies a function to its input and decides whether to activate (pass a value) or output zero.
- **Activation functions**: Functions that determine neuron output; examples include ReLU (Rectified Linear Unit), sigmoid, and Gaussian Error Linear Unit.
- **Weights**: Parameters on connections between neurons that scale input values.
- **Bias**: A parameter added to a neuron's input to shift the activation threshold.
- **Softmax**: A function that converts a vector of values into a probability distribution summing to one.
- **Prompt engineering**: The practice of designing inputs to large pre-trained models to influence their behavior without retraining.
- **Retrieval-Augmented Generation (RAG)**: A technique to enhance model responses by retrieving relevant information during generation.

**Key Facts**

- Neural networks consist of multiple layers: input, hidden, and output layers.
- Each neuron connects to every neuron in the next layer.
- Activation functions require inputs to reach certain thresholds before activating.
- Large models can have trillions of parameters (weights and biases).
- Training large language models can take months using tens of thousands of powerful GPUs.
- Softmax is commonly used at the output layer to produce probabilities for predictions.
- Deep learning models can predict next tokens in text, classify data, detect abnormalities, and more.
- Retraining large models is generally not practical for most users.

**Examples**

- Large language models like GPT use deep neural networks with tens of hidden layers.
- Use cases include predicting the next most probable token in text generation.
- Applications such as recognizing if someone is wearing a mask or predicting equipment failure by detecting abnormalities.
- Smaller neural networks can be trained for specific tasks with less data and better results than traditional approaches.

**Key Takeaways 🎯**

- Deep learning enables modeling of highly complex data relationships beyond basic machine learning algorithms.
- Neural networks rely on layers of neurons with weighted connections and activation functions to process data.
- Training deep learning models is computationally intensive and resource-heavy.
- Large pre-trained models are typically used as-is, with behavior modified via prompt engineering rather than retraining.
- Smaller, task-specific neural networks remain practical and powerful for many applications.
- Understanding activation functions, weights, biases, and the softmax output is critical to grasping how deep learning works.

---

## Type summary

**Timestamp**: 00:22:32 – 00:23:07

**Key Concepts**

- Different types of machine learning and AI approaches
- Progression from traditional AI to machine learning to deep learning
- Use of labeled data in machine learning for prediction and classification
- Neural networks as the foundation of deep learning

**Definitions**

- **Artificial Intelligence (AI)**: Systems where behavior or decision-making can be explicitly programmed or written by humans (e.g., early chess computers).
- **Machine Learning (ML)**: Algorithms that learn from labeled data to predict, label, or classify new data.
- **Deep Learning**: Advanced machine learning using neural networks capable of handling complex tasks.

**Key Facts**

- Early AI systems like chess computers were rule-based rather than data-driven.
- Machine learning relies on labeled datasets to train models.
- Deep learning leverages neural networks for improved performance.
- There are many pre-trained solutions available for specific tasks.

**Examples**

- Early chess computers as an example of AI.
- Using labeled data in machine learning for classification.
- Neural networks powering deep learning models.

**Key Takeaways 🎯**

- AI, machine learning, and deep learning represent a spectrum of approaches with increasing complexity and capability.
- Labeled data is crucial for machine learning models to function effectively.
- Deep learning uses neural networks to solve more complex problems than traditional ML.
- Pre-trained models can be leveraged for specific purposes without needing to train from scratch.

---

## Provided solutions

**Timestamp**: 00:23:07 – 00:30:47

**Key Concepts**

- Provided AI solutions are pre-trained models designed for specific tasks.
- Vision capabilities include OCR, image tagging, object detection, face detection, and liveliness detection.
- Natural language capabilities include chatbots, text summarization, question answering, speech-to-text, text-to-speech, and translation.
- Document intelligence can extract structured data from forms, invoices, and large text documents.
- Knowledge mining extracts and indexes information from structured, semi-structured, and unstructured data, making it searchable and enrichable.
- Custom AI solutions can be built by combining or extending these models.
- Azure AI services offer a wide range of single-purpose and multi-service AI resources.
- Single service resources often have free tiers for experimentation.
- Multi-service resources provide access to many AI capabilities under one endpoint but lack free tiers and granular cost tracking.
- Azure OpenAI and Azure AI Search are specialized services with different availability and pricing models.
- AI service endpoints are RESTful HTTP interfaces that return JSON responses.

**Definitions**

- **Optical Character Recognition (OCR)**: Technology to read and extract text from images.
- **Document Intelligence**: AI capability to understand and extract key fields and data from documents like forms and invoices.
- **Knowledge Mining**: Process of extracting, indexing, and enriching information from various data types to make it searchable and usable by other applications.
- **Single Service Resource**: An Azure AI resource dedicated to one specific AI capability (e.g., computer vision, speech).
- **Multi-Service Resource**: An Azure AI resource that provides access to multiple AI capabilities through a single endpoint.
- **Endpoint**: A RESTful URL address where AI services are accessed by applications, communicating via HTTP and exchanging JSON data.

**Key Facts**

- Many Azure AI single service resources have free tiers allowing a certain number of free calls for learning and experimentation.
- Azure OpenAI service does not have a free tier.
- Azure AI Search has a limited free tier but lacks some advanced features like semantic re-ranking.
- Single service resources have their own keys, endpoints, and role-based access control.
- Multi-service resources do not have free tiers and use a shared endpoint, making cost attribution less granular.
- Applications interact with AI services through REST endpoints using HTTP requests and JSON responses.

**Examples**

- Vision capabilities: reading text from images (OCR), tagging images, detecting objects and faces, checking if a face is live.
- Natural language: chatbots, summarizing text, question answering, speech-to-text, text-to-speech, translation.
- Document intelligence: extracting addresses, phone numbers, invoice items from forms.
- Knowledge mining: extracting text from images or audio via other AI services to index and search content.

**Key Takeaways 🎯**

- Provided AI solutions enable developers to leverage powerful pre-trained models for specific tasks without building from scratch.
- Azure offers a broad ecosystem of AI services, both single-purpose and multi-service, catering to different development and cost management needs.
- Free tiers on single service resources are ideal for learning and experimentation.
- Understanding the distinction between single service, multi-service, and specialized services (OpenAI, AI Search) is important for planning development and cost.
- AI service endpoints are accessed via REST APIs, making integration straightforward for applications.
- Combining multiple AI services can enable complex, custom AI solutions tailored to specific scenarios.

---

## Endpoints and keys

**Timestamp**: 00:30:47 – 00:33:32

**Key Concepts**

- AI services expose endpoints which are URLs that applications connect to.
- Endpoints are REST-based, using HTTP and typically returning JSON responses.
- SDKs (Software Development Kits) often provide language-friendly ways to interact with these REST endpoints.
- Authentication to endpoints is done via keys or integrated identity solutions.
- Keys must be securely stored, often in Azure Key Vault, to avoid exposure.
- Azure Entra ID integrated authentication allows role-based access control without storing keys.
- Managed identities in Azure provide automatic identities for resources to access services securely.
- Role assignments grant permissions to identities to consume AI services.

**Definitions**

- **Endpoint**: A URL address exposed by an AI service that an application connects to for sending requests and receiving responses.
- **REST endpoint**: An endpoint that uses HTTP protocol for communication, typically exchanging JSON data.
- **SDK (Software Development Kit)**: A set of libraries that simplify interacting with REST endpoints in a programming language.
- **Key**: A secret token used to authenticate and authorize access to an AI service endpoint.
- **Azure Key Vault**: A secure service to store keys and secrets safely, preventing exposure in code or repositories.
- **Entra ID integrated authentication**: Azure’s identity solution that uses role-based access control to grant permissions without needing to store keys.
- **Managed Identity**: An automatically managed identity assigned to Azure resources to authenticate securely with other services.

**Key Facts**

- Each AI service endpoint has an associated URL and one or more keys for authentication.
- Applications can either pass keys directly or use Entra ID integrated authentication if supported.
- Using managed identities avoids the need to store or rotate keys manually.
- Role-based access control (RBAC) is used to assign permissions to identities on the resource.
- Keys should never be stored in source code repositories like Git.

**Examples**

- Viewing a vision AI resource in Azure shows the endpoint URL and two keys.
- An application can fetch keys from Azure Key Vault or use Entra ID integrated authentication with assigned roles to access the endpoint.

**Key Takeaways 🎯**

- Always secure your keys; prefer Azure Key Vault over storing keys in config files or repos.
- Use Entra ID integrated authentication and managed identities where possible to simplify security and avoid key management.
- Understand that endpoints are RESTful URLs that your application communicates with, either directly or via SDKs.
- Role-based access control is critical for securely granting access to AI services without exposing keys.
- Proper authentication and authorization are essential when consuming AI services to maintain security and compliance.

---

## Responsible AI

**Timestamp**: 00:33:32 – 00:39:04

**Key Concepts**

- Responsible AI involves ensuring AI systems are trustworthy, safe, fair, reliable, inclusive, transparent, and accountable.
- Risks arise when AI replaces human decision-making without proper safeguards.
- Bias in training data leads to biased AI models.
- Errors in AI can have serious consequences, especially in critical applications.
- Privacy and security of training data must be maintained.
- Inclusiveness ensures AI works fairly across all demographics.
- Transparency helps users understand AI’s workings, limitations, and purpose.
- Accountability assigns responsibility for AI outcomes to developers, companies, and leadership.

**Definitions**

- **Responsible AI**: The practice of designing, developing, and deploying AI systems that are ethical, fair, safe, reliable, inclusive, transparent, and accountable.
- **Bias**: Systematic error or prejudice in AI outcomes caused by biased training data.
- **Fairness**: Ensuring AI treats all people equitably without discrimination.
- **Reliability and Safety**: The AI system’s ability to perform consistently and safely, especially in high-stakes scenarios.
- **Inclusiveness**: Designing AI to work effectively for all people regardless of race, gender, or other factors.
- **Transparency**: Clarity about how AI works, its limitations, and its intended use.
- **Accountability**: Holding developers and organizations responsible for AI behavior and impacts.

**Key Facts**

- AI systems can be more dependable than humans (no fatigue or breaks) but require trustworthy training.
- Training data bias leads to biased AI outputs ("garbage in, garbage out").
- Errors in AI can cause severe harm (e.g., self-driving car accidents).
- Data used for training must be legally and ethically sourced and privacy protected.
- Six key principles of Responsible AI highlighted: fairness, reliability & safety, privacy & security, inclusiveness, transparency, and accountability.

**Examples**

- Self-driving cars: Errors can cause serious harm, requiring rigorous testing for reliability and safety.
- Facial recognition: Potential for abuse, highlighting the need for accountability and ethical standards.
- AI in surgery or reactor monitoring: High reliability and safety standards needed.

**Key Takeaways 🎯**

- Responsible AI is critical as AI systems increasingly make important decisions impacting human lives.
- Bias in training data must be identified and mitigated through comprehensive testing.
- AI systems must be rigorously tested for reliability and safety before deployment.
- Privacy and security of training data are paramount.
- AI must be inclusive and serve all parts of society fairly.
- Transparency about AI’s function and limitations builds trust.
- Clear accountability structures are necessary to prevent misuse and ensure ethical AI deployment.
- Without responsible AI practices, there is a risk of harmful consequences and loss of public trust.

---

## Computer vision

**Timestamp**: 00:39:04 – 00:41:55

**Key Concepts**

- Computer vision deals with processing and understanding images.
- Images are fundamentally composed of pixels, each having a value.
- Multimodal models support multiple input types/modalities such as images, language, video, and audio.
- Foundational models provide broad capabilities and can be fine-tuned for specific use cases.
- Vision services include image analysis, which can generate captions or identify content in images.

**Definitions**

- **Image**: A collection of pixels, where each pixel has a value (e.g., grayscale values from 0 to 255).
- **Pixel**: The smallest unit of an image, holding a value that represents color or intensity.
- **Multimodal**: Refers to models or systems that can understand and interact with multiple types of data/modalities (e.g., images, text, audio).
- **Foundational model**: A broad, general-purpose AI model that can be adapted or fine-tuned for specific tasks or domains.

**Key Facts**

- Grayscale pixel values typically range from 0 to 255.
- Color images have multiple values per pixel (e.g., RGB channels).
- JPEG images use compression to efficiently store pixel data.
- Examples of multimodal models include GPT-4O and Microsoft’s Florence model.
- Foundational models serve as a base for building more specialized applications.

**Examples**

- An image of a cow under a tree is used as an example for image analysis.
- GPT-4O is highlighted as a multimodal model capable of interacting with different data types.

**Key Takeaways 🎯**

- Understanding that images are pixel-based is fundamental to computer vision.
- Multimodal AI models expand the ability to process and understand diverse data types beyond just images.
- Foundational models provide a versatile starting point for building tailored computer vision solutions.
- Vision services like image analysis can interpret and caption images, though complex scenes may still challenge AI understanding.

---

## Vision services

**Timestamp**: 00:41:55 – 00:47:08

**Key Concepts**

- Vision services focus on analyzing and extracting information from images.
- Image analysis includes captioning, tagging, object detection, background removal, smart cropping, and optical character recognition (OCR).
- Different vision services are suited for different use cases, e.g., image analysis for small text in images vs. document intelligence for large text documents.
- Vision Studio provides a platform to test and customize vision models.
- Face services include detecting faces and performing liveness checks, with onboarding required due to potential for misuse.

**Definitions**

- **Multimodal**: A model or system that works across different input types or modalities (e.g., text, images).
- **Image Analysis**: A vision service that processes images to provide captions, tags, object detection (bounding boxes), background removal, smart cropping, and OCR for small amounts of text.
- **Object Detection**: Identifying objects within an image and providing their locations via bounding boxes.
- **Optical Character Recognition (OCR)**: Extracting text from images; small amounts of text can be handled by image analysis, while large documents require document intelligence.
- **Document Intelligence**: A service designed to process large text documents, returning structured data like pages, lines, and words.
- **Face Service**: Vision service focused on detecting faces, identifying characteristics, and performing liveness checks; requires onboarding due to sensitivity.

**Key Facts**

- Image analysis version 4.0 is the latest at the time of recording, offering advanced features like background removal and smart cropping.
- Object detection returns bounding boxes with coordinates (e.g., cow at 10x20 to 15x25).
- OCR in image analysis is suitable for small text snippets; large text requires document intelligence.
- Vision Studio allows users to create free resources and test features such as product recognition, dense captions, background removal, object detection, text extraction, and face detection.
- Face services require a formal onboarding process to mitigate abuse risks.

**Examples**

- Captioning a poor drawing of a cow under a tree.
- Tagging objects in an image (e.g., "cow" and "tree").
- Object detection providing bounding boxes around a cow and a tree.
- Removing backgrounds and creating smart cropped thumbnails focusing on key objects.
- Extracting text from an identification card image using OCR.
- Detecting faces and performing liveness checks with face services.

**Key Takeaways 🎯**

- Use image analysis for general image understanding tasks including tagging, captioning, object detection, and small-scale OCR.
- For large text extraction from documents, use document intelligence instead of image analysis.
- Vision Studio is a practical tool to experiment with and customize vision models.
- Image analysis 4.0 enhances capabilities with background removal and smart cropping.
- Face detection services are sensitive and require onboarding to ensure responsible use.
- Bounding boxes in object detection provide precise object location data in images.

---

## Face

**Timestamp**: 00:47:08 – 00:52:04

**Key Concepts**

- Face detection and recognition as a vision service.
- Liveness check to prevent spoofing (e.g., 3D print or photo).
- Creation and use of face databases for identification and verification.
- Detection of facial attributes such as head pose, presence of mask or glasses, facial landmarks, blur, exposure, and occlusion.
- Removal of sensitive detections like emotional state and gender to prevent abuse.
- Support for multiple image formats and size constraints.
- Customized vision training using transformer-based neural networks in Image Analysis v4.0.
- Comparison between older convolutional neural network (CNN) based custom vision and newer transformer-based models.
- Transformer models require fewer images but take longer to train and cost more.
- Recommended number of images for best quality is still around 50-60 despite lower minimum requirements.

**Definitions**

- **Face Detection**: The process of finding faces in images and analyzing facial features.
- **Liveness Check**: A verification step to ensure the face is from a live person and not a spoof (e.g., photo or 3D print).
- **Identification**: Matching a detected face against a database to find who it is.
- **Verification**: Confirming if a detected face matches a claimed identity.
- **Facial Landmarks**: Key points on the face such as eyes, nose, ears, and lips used for analysis.
- **Transformer Neural Network**: A newer neural network architecture that processes images differently than CNNs, requiring fewer training images but longer training time.
- **Convolutional Neural Network (CNN)**: An older neural network architecture that uses filters to detect features in images.

**Key Facts**

- Face detection can identify head pose, mask presence, glasses, facial landmarks, blur, exposure, and occlusion.
- Emotional state, gender, and emotions are no longer detected due to potential abuse.
- Supported image formats: JPEG, PNG, first frame of GIF, bitmap.
- Maximum image size: 6 megabytes.
- Detectable face size range: minimum 36x36 pixels, maximum 4096x4096 pixels.
- Older custom vision CNN required ~15 images per category.
- New transformer-based model can work with as few as 2-5 images but recommends 50-60 for best results.
- Accuracy example: With 3 images, CNN model ~56% accuracy vs transformer model ~75%.
- Transformer models take longer to train and incur higher training costs.

**Examples**

- Using face detection to check if a person is wearing a mask or glasses.
- Creating a face database to identify or verify individuals.
- Comparing training accuracy between CNN and transformer models with different numbers of images.

**Key Takeaways 🎯**

- Face services require onboarding and form submission due to sensitivity.
- Liveness checks are important to prevent spoofing attacks.
- Sensitive attributes like emotions and gender are excluded to avoid misuse.
- Transformer-based models in Image Analysis v4.0 represent a significant advancement, needing fewer images but more training time.
- For best model quality, diverse and numerous images (50-60) are still recommended despite lower minimums.
- Be aware of image size and face size constraints for successful detection.
- Training costs and time increase with transformer models, so plan accordingly.

---

## Natural Language

**Timestamp**: 00:52:04 – 00:59:33

**Key Concepts**

- Natural language processing (NLP) involves computers interacting with human language by converting text into tokens.
- Tokens can represent whole words, parts of words, punctuation, emojis, or other language elements.
- Language models (e.g., GPT-3.5, GPT-4) process tokens as inputs and outputs, predicting the most probable next token.
- NLP capabilities include language detection, sentiment analysis, key phrase extraction, entity recognition, summarization, and question-answering.
- Question and Answer (Q&A) systems rely on defined knowledge bases and can be integrated with bot services.
- Azure Bot Service enables development, publishing, and management of bots that interact with Q&A knowledge bases across multiple channels (Teams, web chat, email, custom apps).
- Language Understanding (LUIS) service detects user intent and extracts entities from utterances, supporting automation scenarios.
- Entities can be detected via machine learning or defined patterns like regex (e.g., phone numbers).
- Language Studio offers various NLP features such as summarization, transcription, PII extraction, key phrase and entity extraction.
- Speech capabilities complement NLP by converting text to speech and speech to text, supporting synthesis in multiple voices and transcription.

**Definitions**

- **Token**: A unit of text used by language models, which can be a whole word, part of a word, punctuation, or emoji.
- **Language Model**: A deep neural network that processes tokens to predict the next most probable token in a sequence.
- **Intent**: The purpose or goal behind a user's utterance detected by language understanding services.
- **Entity**: Specific data or objects identified within an utterance, such as "lights" in the command "turn on the lights."
- **LUIS (Language Understanding Intelligent Service)**: An Azure service that detects intent and entities from natural language input.
- **Azure Bot Service**: A platform to build, deploy, and manage conversational bots that interact with knowledge bases and users across multiple channels.

**Key Facts**

- Tokens can number in the tens of thousands in a language model’s vocabulary.
- Example tokenization: "AI-900 study cram" is broken into 8 tokens (e.g., "AI", "900", "study", "-").
- Azure Bot Service supports multiple channels including Microsoft Teams, web chat, email, and custom web apps.
- Language Studio includes features like summarization, post-call transcription, PII extraction, and entity/key phrase extraction.
- LUIS can be used both as an authoring tool and a prediction endpoint.
- Regex patterns can be used to detect entities such as phone numbers.

**Examples**

- Tokenization example: The phrase "AI-900 study cram" is tokenized into 8 tokens by OpenAI’s tokenizer.
- Q&A knowledge base can be created from FAQs or chit-chat sources and consumed via Azure Bot Service.
- Intent/entity example: Utterance "turn on the lights" has intent "turn on" and entity "lights."
- Language Studio extracting key phrases and named entities from text samples.

**Key Takeaways 🎯**

- Natural language processing relies heavily on tokenization to convert text into a format usable by AI models.
- Language models predict the next token based on probability distributions over a large token vocabulary.
- NLP services provide a wide range of capabilities from language detection to summarization and Q&A.
- Integrating Q&A knowledge bases with Azure Bot Service enables multi-channel conversational AI applications.
- LUIS is a powerful tool for intent detection and entity extraction, essential for automation and conversational scenarios.
- Flexible entity detection includes both machine learning and pattern-based approaches like regex.
- Speech services complement NLP by enabling bidirectional conversion between text and speech, enhancing user interaction options.

---

## Speech

**Timestamp**: 00:59:33 – 01:01:13

**Key Concepts**

- Interaction between text and speech in both directions (text-to-speech and speech-to-text)
- Speech synthesis with multiple voice options
- Speech recognition and transcription
- Language recognition within speech input
- Speech translation capabilities (speech-to-text translation and speech-to-speech translation)
- Text translation services supporting custom languages and documents

**Definitions**

- **Speech synthesis**: The process of converting text into spoken voice output.
- **Speech recognition**: The process of converting spoken language into text.
- **Speech translation**: Translating spoken language from one language to another, either as text or synthesized speech.
- **Translation service**: A service that translates text, documents, or custom language phrases between languages.

**Key Facts**

- Supports many different voices for speech synthesis.
- Supports speech translation in about 60 different languages (at time of recording).
- Speech translation can output either translated text or translated speech.
- Translation service works with small amounts of text, documents, and custom language models (industry-specific phrases).

**Examples**

- Translating spoken language from one language and outputting the translated text in another language.
- Translating spoken language and outputting the translated speech in the target language.

**Key Takeaways 🎯**

- Speech capabilities cover both converting text to speech and speech to text.
- Language recognition is integrated into speech processing.
- Speech translation is versatile, supporting both text output and speech output in many languages.
- Translation services extend beyond speech to include text, documents, and customized language models for specific industries.

---

## Translation

**Timestamp**: 01:01:13 – 01:02:31

**Key Concepts**

- Translation service works primarily with text, documents, and custom language models.
- Ability to customize translation with domain- or industry-specific language dictionaries.
- Translation can include filters such as profanity filters or selective translation of terms.
- Some words can be excluded from translation to preserve specific meanings (e.g., brand names like "Azure").
- Translation service supports converting text between languages and can output translated speech from spoken input.

**Definitions**

- **Translation Service**: A service that translates text or documents from one language to another, supporting customization and filtering.
- **Custom Language Dictionary**: A user-defined set of terms and phrases specific to an industry or domain used to improve translation accuracy.
- **Profanity Filter**: A filter applied during translation to remove or censor offensive language.
- **Selective Translation**: The ability to exclude certain words from being translated to maintain their original form or meaning.

**Key Facts**

- Translation service handles small amounts of text and documents.
- Customization allows defining domain-specific language for better translation relevance.
- Filters can be applied to control translation output, including profanity and selective word translation.

**Examples**

- Excluding the word "Azure" from translation to keep it consistent across languages.

**Key Takeaways 🎯**

- Translation services are flexible and can be tailored to specific industry needs through custom dictionaries.
- Filters enhance translation quality by managing sensitive content and preserving key terms.
- Translation can be applied both to text and speech, enabling real-time language conversion.
- Understanding and using customization features can significantly improve translation accuracy and relevance.

---

## Document intelligence

**Timestamp**: 01:02:31 – 01:06:05

**Key Concepts**

- Document intelligence involves analyzing various types of documents to extract structured data.
- It evolved from the former "Forms Recognizer" service to emphasize AI capabilities.
- Uses pre-built and custom AI models to understand and extract semantic information from documents.
- Supports multiple document types including receipts, invoices, identity cards, health insurance cards, tax forms, and general documents.
- Provides outputs in structured formats like JSON, capturing key-value pairs and semantic meaning.
- Custom models can be created easily with minimal examples (as few as 5).
- Document Intelligence Studio offers a no-code interface for building and deploying custom models.
- Works with PDFs and images, not just plain text or OCR.

**Definitions**

- **Document Intelligence**: An AI-powered service that analyzes documents (forms, receipts, invoices, etc.) to extract structured, meaningful data beyond simple text recognition.
- **Pre-built Models**: Ready-to-use AI models designed to handle common document types like receipts and invoices.
- **Custom Models**: User-trained AI models created by providing sample documents to tailor extraction to specific form layouts or data needs.
- **Document Analysis**: The process of converting unstructured or semi-structured documents into structured data by recognizing semantic elements.
- **Document Intelligence Studio**: A no-code tool for creating, training, and deploying custom document intelligence models.

**Key Facts**

- Custom models require as few as 5 sample documents to train.
- Outputs are typically in JSON format with extracted key-value pairs.
- Supports multiple input formats including PDFs and images.
- Pre-built models cover a wide range of document types: invoices, receipts, identity cards, health insurance cards, tax forms, and more.
- The service was renamed from "Forms Recognizer" to "Document Intelligence" to reflect the increased AI focus.

**Examples**

- Extracting structured data from receipts and invoices.
- Recognizing semantic elements such as addresses and phone numbers within documents.
- Creating a custom model by providing sample forms to identify and extract specific parts of the form.
- Using Document Intelligence Studio to build custom models without coding.

**Key Takeaways 🎯**

- Document Intelligence is a powerful AI tool for converting diverse document types into structured, machine-readable data.
- It goes beyond OCR by understanding the meaning and context of the text within documents.
- Pre-built models provide quick solutions for common document types, while custom models allow tailored extraction with minimal training data.
- The no-code Document Intelligence Studio simplifies model creation and deployment.
- Supports a variety of input formats, making it versatile for many business scenarios involving document processing.

---

## Knowledge mining

**Timestamp**: 01:06:05 – 01:09:39

**Key Concepts**

- Knowledge mining is the process of extracting insights and relevant information from large masses of data.
- Azure AI Search (formerly Azure Cognitive Search) is the core service enabling knowledge mining.
- The service supports multiple data sources such as BLOB storage, data lakes, databases, and table storage.
- Skill sets are defined to process and enrich data, including chunking large documents into smaller parts.
- Embedding models convert chunks of data into high-dimensional vector representations to capture semantic meaning.
- Enrichment can include calling vision services to extract text from images within documents.
- Data chunks and their enriched metadata are stored in a knowledge store.
- Azure AI Search creates two types of indexes: traditional exact text indexes and vector indexes for semantic search.
- Hybrid search combines both exact text and vector search results, re-ranking them for better relevance.
- This approach supports natural language queries and improves retrieval of semantically related content.
- Knowledge mining is foundational for advanced AI scenarios like retrieved augmented generation (RAG).

**Definitions**

- **Knowledge mining**: The process of extracting meaningful insights and relevant information from large, unstructured or structured data sets.
- **Azure AI Search**: A dedicated Azure resource for knowledge mining that indexes and searches data using both text and vector-based methods.
- **Skill sets**: Configurable processing steps applied to data to break it down, enrich it, and prepare it for indexing.
- **Chunking**: Breaking large documents into smaller, manageable pieces with some overlap to facilitate processing and semantic understanding.
- **Embedding model**: A model that converts text chunks into high-dimensional vectors representing their semantic meaning.
- **Knowledge store**: A storage layer where processed data chunks and their enriched metadata are saved for querying.
- **Hybrid search**: A search method combining exact phrase matching and vector similarity to improve search relevance.

**Key Facts**

- Azure AI Search is a standalone resource, not part of the multi-service Azure AI accounts.
- Supports a wide variety of data sources including BLOB storage, data lakes, databases, and table storage.
- Chunking involves breaking data into smaller parts with some overlap to maintain context.
- Vector indexes enable semantic search, which is crucial for natural language understanding and AI models like GPT.
- Hybrid search can combine and re-rank results from both traditional text and vector indexes.
- Enables natural language queries that find semantically related content even if the exact words differ.

**Examples**

- Searching for information about "dogs going to the park" can also find documents about "puppies going to public green areas" due to semantic vector search.
- Enrichment can include extracting text from images embedded in PDF documents using vision services.

**Key Takeaways 🎯**

- Knowledge mining leverages Azure AI Search to turn large, complex data into searchable, enriched knowledge.
- The combination of chunking, embedding, and hybrid search enables powerful semantic search capabilities.
- Azure AI Search’s vector indexes allow natural language queries to find relevant information beyond exact keyword matches.
- This technology underpins advanced AI applications like retrieved augmented generation, enhancing generative AI with relevant data retrieval.
- Understanding the architecture—data sources, skill sets, knowledge store, and indexing—is essential for implementing knowledge mining solutions.

---

## Review

**Timestamp**: 01:09:39 – 01:15:26

**Key Concepts**

- Artificial Intelligence (AI) mimics human capabilities such as vision, speech, natural language, document intelligence, and knowledge.
- Machine Learning (ML) is a subset of AI that uses labeled data to train models without explicit programming.
- Types of ML tasks: regression (numeric), classification (binary and multiclass), and unsupervised learning (grouping without labels).
- Deep Learning uses neural networks with neurons, activation functions, weights, and biases to model complex data.
- Azure AI services include single-purpose services (vision, text, translation) and multi-service endpoints.
- Authentication to Azure AI endpoints can be done via keys or Entra ID integrated authentication.
- Responsible AI focuses on fairness, bias mitigation, reliability, safety, privacy, security, inclusivity, transparency, and accountability.
- Vision services include image analysis (captions, tags, object detection, background removal, thumbnails, text extraction) and face detection (face recognition, direction, liveness detection).
- Natural Language services analyze text for language, sentiment, key phrases, entities, summarization, and knowledge base creation.
- Language Understanding identifies intent and entities from utterances.
- Speech services cover text-to-speech synthesis, speech-to-text recognition, and translation (including custom domain training).
- Document Intelligence handles large-scale document analysis with pre-built and custom form models.
- Knowledge Mining (Azure AI Search) supports multiple data sources, enriches data with skills, and creates text and vector indexes for querying.
- Practical advice for exam preparation includes using free SKUs, Microsoft Learn, sandboxes, managing time, and strategic question answering.

**Definitions**

- **Artificial Intelligence (AI)**: Technology that mimics human capabilities such as vision, speech, natural language processing, and knowledge extraction.
- **Machine Learning (ML)**: A subset of AI where models are trained on labeled data to perform tasks without explicit programming.
- **Deep Learning**: A type of ML using neural networks composed of layers of neurons with activation functions, weights, and biases.
- **Activation Function**: A function in a neuron that must reach a threshold before the neuron outputs a signal.
- **Azure AI Services**: Cloud-based AI capabilities offered by Microsoft, including vision, text, translation, and multi-service endpoints.
- **Responsible AI**: Principles ensuring AI systems are fair, unbiased, reliable, safe, private, secure, inclusive, transparent, and accountable.
- **Document Intelligence**: AI service for analyzing large documents and forms, including custom training with few examples.
- **Knowledge Mining (Azure AI Search)**: Service that indexes and enriches data from various sources to enable powerful search and query capabilities.

**Key Facts**

- Machine learning models may require iterative training and testing with labeled data.
- Deep learning networks have input, output, and multiple hidden layers.
- Azure AI single services have free SKUs; multi-service endpoints do not.
- Authentication methods include API keys and Entra ID integrated authentication.
- Document Intelligence can be custom trained with as few as five examples.
- Knowledge Mining supports chunking and enrichment of data for indexing.
- Responsible AI encompasses fairness, bias mitigation, privacy, security, inclusivity, transparency, and accountability.

**Examples**

- Querying a vector-based hybrid search to find documents about dogs going to parks despite varied language input.
- Image analysis features: captions, deep captions, tags, object detection, background removal, smart cropping thumbnails, and text extraction.
- Face detection features: identifying face direction, facial landmarks (ears), person identification, grouping, verification, and liveness detection.
- Natural language processing: detecting language, sentiment analysis, key phrase extraction, entity recognition, summarization, and knowledge base Q&A integration.
- Speech services: text-to-speech synthesis with multiple voices, speech-to-text recognition, and translation including custom domain terms.
- Document Intelligence: analyzing receipts and invoices with pre-built models or custom models trained with minimal examples.
- Knowledge Mining: indexing multiple data sources, chunking data, enriching with skills, and enabling text and vector-based queries.

**Key Takeaways 🎯**

- Understand the broad scope of AI and its subsets: machine learning and deep learning.
- Familiarize yourself with Azure AI service types, their capabilities, and authentication methods.
- Responsible AI principles are critical for trustworthy AI solutions.
- Explore and experiment with free Azure AI SKUs to gain hands-on experience.
- Know the key features and use cases of vision, natural language, speech, document intelligence, and knowledge mining services.
- Prepare for exams by practicing with Microsoft Learn, sandboxes, managing time, and using elimination strategies on questions.
- Remember that multi-service endpoints do not have free SKUs, unlike single-service endpoints.
- Custom training in document intelligence and translation services can be done with minimal examples or domain-specific data.

---

## Exam tips

**Timestamp**: 01:15:26 – 01:16:36

**Key Concepts**

- Familiarize yourself with the exam format and time constraints.
- Use Microsoft Learn and sandbox environments to prepare.
- Manage your exam time effectively; avoid spending too long on any one question.
- Use the process of elimination to narrow down answers.
- Make educated guesses when unsure.
- Review your performance by section if you don’t pass and focus on weak areas.

**Definitions**

- **Sandbox**: A practice environment that simulates the exam experience to help candidates prepare and avoid surprises on exam day.

**Key Facts**

- Pay attention to the number of questions and total time allotted during the exam.
- You can return to questions later if unsure.
- The exam services are designed to be intuitive, not confusing.
- After the exam, results are shown by section to help identify strengths and weaknesses.

**Examples**

- Avoid obviously wrong answers (e.g., “It’s not going to be cheese as an answer”).
- If you don’t pass, use the section results to focus your study for the next attempt.

**Key Takeaways 🎯**

- Prepare thoroughly using Microsoft Learn and sandbox environments.
- Practice time management during the exam.
- Use elimination and educated guessing strategies.
- Don’t be discouraged by failing once; use feedback to improve.
- The exam experience is designed to be straightforward and intuitive.

---

## Close

**Timestamp**: 01:16:36 – unknown

**Key Concepts**

- Approach exam questions with educated guesses when unsure.
- The exam services are designed to be intuitive, not confusing.
- Use exam results to identify weak areas and improve.
- Persistence is important; failing once is not the end.

**Definitions**

- None mentioned.

**Key Facts**

- The exam feedback shows performance by section.
- No question will have an obviously irrelevant answer (e.g., "cheese").
- Retaking the exam after focused study increases chances of success.

**Examples**

- Avoid guessing obviously wrong answers like "cheese."
- After failing, review section scores and focus on weakest areas.

**Key Takeaways 🎯**

- Make educated guesses based on what makes the most sense.
- Don’t be discouraged by failing the first time; use feedback to improve.
- Study targeted areas of weakness before retaking the exam.
- Watch the generative AI study cram video as a next step.
