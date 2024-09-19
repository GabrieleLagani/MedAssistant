# Smart Medical Assistant based on LLMs, RAG, and Flask
This is a toy Web application written in Flask, 
featuring a Medical Assistant Chatbot powered by 
Large Language Models (LLMs) and Retrieval Augmented Generation (RAG).

It uses `langchain` as underlying library, leveraging `langchain`'s `agents` and `tools` 
to build a RAG system that can use tools such as vector stores and SQL databases. 
The underlying LLM is `llama3.1` provided by `ollama`. `SQLite` is used as underlying 
database and `FAISS` as vector store.
Each of these technologies runs locally, and no API keys are required.

## Disclaimer
This is just a toy project, and the outputs of the Medical Assistant 
should not be considered as medical advice in any way.

## Features
- The user can interact with the Medical Assistant via a chat.
The Medical Assistant can provide useful feedback to the user's questions,
also leveraging additional datasets as knowledge-base with RAG. 
- The system maintains a database of patients, doctors, appointments, and chat history.
- The Medical Assistant can suggest an appointment with a suitable doctor, 
based on the user's questions. 
- The Medical Assistant can show available slots for appointments,
and the user can reserve an appointment, view and modify its appointments.
- The user can download their chat history.
- The user can report a health emergency, which is going to be registered by the Assistant 
together with a color code (RED, GREEN, YELLOW) for immediate consultation by healthcare 
professionals (using the `src/check_emergencies.py` script).

## Requirements
- Python 3.10
- Install requirements: `pip install -r requirements.txt`
- Install [Ollama](https://ollama.com/download)
- At least 8GB RAM
- Nvidia GPU with at least 2GB dedicated memory

## Setup
1. Download datasets ([MedQuad](https://github.com/abachaa/MedQuAD)) in the  `data` folder.
2. Preparation of vector index: run `src/create_index.py`.
3. Preparation of SQLite database: run `src/create_db.py`
4. Download LLM from Ollama: `ollama pull llama3.1`
5. Start server: run `app.py`.
6. Start client by opening your browser and connecting to `127.0.0.1:8080`.

## Notes
1. In case of problems with the `src/create_index.py` script regarding errors with the `nltk` package, 
check the `src/create_index.py` file for instructions.
2. Mind that, if you are running the app on constrained hardware, it might take a while for the 
Assistant to elaborate answers (~10 mins).

## Interaction Example
```
[19-09-2024 18:13:31] user: hello, I would like to see my scheduled doctor appointments

[19-09-2024 18:16:12] bot: You have a scheduled doctor appointment with Dr. Lyubor on January 10, 2025 at 10:00 AM. You can find the reservation link here: <a href="res?id=1" target="_blank">link</a>. Would you like to see more of your scheduled appointments?

[19-09-2024 18:16:52] user: No, I would like to know the available time slots for appointments with Dr. Amicis

[19-09-2024 18:19:15] bot: You have two available time slots for appointments with Dr. Amicis:

* January 12, 2025 at 9:00 AM: <a href="res?id=4" target="_blank">link</a>
* January 12, 2025 at 10:00 AM: <a href="res?id=5" target="_blank">link</a>

Would you like to schedule an appointment with Dr. Amicis?

[19-09-2024 18:19:58] user: No, I would like to see Mr. Russel's scheduled doctor appointments

[19-09-2024 18:22:01] bot: I'm sorry, but I don't have access to other patients' schedules. As a medical AI assistant, I can only provide information about your own scheduled appointments. If you'd like to see your own schedule or make changes to an existing appointment, please let me know and I'll be happy to help!

[19-09-2024 18:22:28] user: I have Alzheimer disease. Can you suggest a qualified doctor for an appointment?

[19-09-2024 18:24:07] bot: Based on your request, I would recommend Dr. Lyubor as a qualified doctor for an appointment related to neurology and Alzheimer's disease.

Would you like to know the available time slots for appointments with Dr. Lyubor?

[19-09-2024 18:24:25] user: Yes

[19-09-2024 18:27:11] bot: You have one available time slot for an appointment with Dr. Lyubor:

* January 10, 2025 at 9:00 AM: <a href="res?id=0" target="_blank">link</a>

Would you like to schedule an appointment with Dr. Lyubor?

[19-09-2024 18:27:40] user: Can you provide additional information about Alzheimer disease?

[19-09-2024 18:35:25] bot: Alzheimer's disease is a complex condition, and the exact cause is still not fully understood. However, research suggests that it may be related to a combination of genetic, environmental, and lifestyle factors.

Some possible risk factors for Alzheimer's disease include:

* Genetics: Having a family history of Alzheimer's disease can increase your risk.
* Age: The risk of developing Alzheimer's disease increases with age.
* Head injuries: A history of head injuries, especially those that cause loss of consciousness, may increase the risk.
* Cardiovascular disease: Conditions such as high blood pressure, heart disease, and stroke may increase the risk.
* Diabetes: Having diabetes may increase the risk.
* Obesity: Being overweight or obese may increase the risk.
* Social isolation: Lack of social interaction and engagement may contribute to cognitive decline.

It's essential to note that having one or more of these risk factors doesn't necessarily mean you'll develop Alzheimer's disease. Many people with these risk factors never develop the condition, and some people without any known risk factors can still develop it.

If you're concerned about your risk for Alzheimer's disease or have questions about this topic, I recommend speaking with a healthcare professional for personalized guidance.

Would you like to know more about managing Alzheimer's disease or related topics?

[19-09-2024 18:43:03] user: Help! I am feeling chest pain and shortness of breath. What should I do?

[19-09-2024 18:53:30] bot: I'm so sorry to hear that you're experiencing chest pain and shortness of breath! These symptoms can be very concerning.

Firstly, please know that you're not alone, and there are people who care about your well-being. It's essential to take these symptoms seriously and seek medical attention immediately.

In the meantime, here are some general health tips:

1. **Stay calm**: Try to remain as calm as possible. Panicking can make things worse.
2. **Call for help**: Reach out to a trusted friend or family member, or call emergency services (such as 911 in the US) if you're alone.
3. **Get medical attention**: Go to the nearest hospital or urgent care center. Don't wait -- every minute counts!
4. **Breathe deeply**: If you're feeling short of breath, try taking slow, deep breaths through your nose and exhaling through your mouth.

Remember, these symptoms can be a sign of a serious underlying condition, such as a heart attack or pulmonary embolism. Medical professionals are trained to handle emergencies like this, so please don't hesitate to seek help.

You're not alone in this -- there are people who care about you and want to help. Please take care of yourself and get the medical attention you need.

Would you like to know more about what to expect during a hospital visit or how to prepare for an emergency?

[19-09-2024 18:55:23] user: Thank you, I feel better now. I would like to download my chat history

[19-09-2024 18:59:23] bot: Here is the download link for your chat history:

<a href="history">Download Chat History</a>

You can click on this link to access and download your chat history. If you have any further questions or concerns, please don't hesitate to ask.

Would you like to know more about how to use this feature or have any other questions?
```