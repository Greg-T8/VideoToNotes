### 🎤 [00:47:08 – 00:52:04] Face  
**Timestamp**: 00:47:08 – 00:52:04

**Key Concepts**  
- Face service in computer vision focuses on detecting and analyzing human faces in images.  
- Includes face detection, liveness check, identification, and verification.  
- Detection includes facial landmarks and attributes like head pose, mask presence, glasses, blur, exposure, and occlusion.  
- Emotional state, gender, and emotions detection are no longer supported due to concerns about abuse.  
- Supports multiple image formats and size constraints.  
- Custom vision training can be done using Image Analysis v4.0 transformer-based model or older convolutional neural network (CNN) model.  
- Transformer models require fewer images but take longer to train and cost more.  

**Definitions**  
- **Face Detection**: The process of finding faces in an image and analyzing features such as facial landmarks (eyes, nose, ears, lips), head pose, and presence of masks or glasses.  
- **Liveness Check**: A verification step to ensure the face is from a live person and not a 3D print or photo.  
- **Identification**: Matching a detected face against a database of known faces to find a match.  
- **Verification**: Confirming that a detected face matches a specific identity from the database.  
- **Transformer Model**: A newer neural network architecture used in Image Analysis v4.0 that requires fewer training images but longer training time compared to CNN.  
- **Convolutional Neural Network (CNN)**: An older neural network architecture used in the traditional Custom Vision service that requires more images for training.  

**Key Facts**  
- Face detection works on JPEG, PNG, first frame of GIF, bitmap formats.  
- Maximum image size: 6 megabytes.  
- Detectable face size range: minimum 36x36 pixels up to 4096x4096 pixels.  
- Emotional state, gender, and emotion detection are deprecated due to potential abuse.  
- Older Custom Vision CNN model requires ~15 images per category for training.  
- Transformer-based Image Analysis v4.0 can work with as few as 2-5 images per category, though 50-60 images are recommended for best quality.  
- Accuracy example: with 3 training images, CNN model achieved ~56% accuracy, transformer model ~75%.  
- Transformer models provide higher accuracy with less data but take longer and cost more to train.  

**Examples**  
- Creating a database of people’s faces to perform identification and verification.  
- Detecting if a person is wearing a mask or glasses.  
- Checking if a face image is blurred or occluded.  

**Key Takeaways 🎯**  
- Face services are powerful but require onboarding and form submission to access.  
- Liveness checks help prevent spoofing attacks using photos or 3D prints.  
- Privacy and ethical concerns have led to removal of emotional and gender detection features.  
- Image size and face size constraints must be respected for successful detection.  
- Transformer-based models represent the future of custom vision training with better accuracy and less data, but at the cost of longer training times and higher expense.  
- For best results in custom vision, use diverse, high-quality images from multiple angles and conditions.  
- Understanding the trade-offs between CNN and transformer models is important when designing face recognition solutions.  

---