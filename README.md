# Privacy-Focused Voice Assistant: NeptuneX

NeptuneX is an innovative voice assistant architecture designed to provide personalized ad experiences while prioritizing user privacy. This project demonstrates how voice assistants can operate in an economically sustainable manner without compromising on user data protection.

## Research Paper

This repository includes a research paper titled "NeptuneX: A Privacy-Focused Voice Assistant Architecture" authored by Vikraman Senthil Kumar and Madhumitha Santhanakrishnan. The paper is under review for publication in ACM and details the methodologies, technologies, and ethical considerations behind NeptuneX.

## Installation

To get started with NeptuneX, ensure you have Docker installed on your system. The project comes packaged with a Dockerfile for easy setup and a `requirements.txt` file for managing Python dependencies.

### Steps

1. Clone the repository:
   ```
   git clone https://github.com/Vikramansen/NeptuneX.git
   ```
2. Navigate to the project directory:
   ```
   cd NeptuneX
   ```
3. Build the Docker image:
   ```
   docker build -t neptunex .
   ```
4. Run the Docker container:
   `docker run -p 8501:8501 neptunex`
   After running the container, NeptuneX will be accessible at `http://localhost:8501` on your browser.

## Usage

NeptuneX integrates a voice assistant capable of understanding and responding to user queries in a privacy-preserving manner. All data processing and ad personalization logic are encapsulated within `Similator.py`.

- **Voice Assistant Interaction**: Use the provided interface to interact with the voice assistant.
- **Personalized Ads**: Experience personalized ad suggestions based on anonymized user data.
- **Privacy Settings**: Adjust your privacy settings and ad preferences via the user interface.

## Data

All user interaction data and preferences are stored in the `data` folder. This includes CSV files that are dynamically updated based on user interactions and settings.

## Contribution

Contributions to NeptuneX are welcome. Whether you're interested in enhancing the voice recognition capabilities, improving the privacy features, or expanding the ad personalization algorithms, your input is valuable.

## Acknowledgments

We are particularly thankful to Prof. Alexander Gamero- Garrido for his pivotal role in shaping the direction of this project. His course inspired us to explore and develop poli- cies aimed at enhancing digital privacy, guiding our efforts towards meaningful outcomes. Additionally, we wish to ex- press our appreciation to our friends and colleagues who generously participated in our feedback survey, providing insights that were crucial for refining our project. Their en- gagement and support have been invaluable to our research.
