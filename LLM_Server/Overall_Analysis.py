from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
model_name = "o4-mini"

def overall_analyser(transcription_input, audio_metrics):
    print("Entered Overall Analyser")
    llm = ChatOpenAI(model=model_name, api_key=os.getenv("OPENAI_API_KEY"))
    output_parser = StrOutputParser()
    # with open("json/presentation.json", "r") as file:  # Correct path
    #     data = json.load(file)

    # presentation_mode = data.get("presentation_mode", False)
    presentation_mode = "off"
    if presentation_mode == "on":
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", 
                "You are an expert interviewer evaluating a video resume based on a transcription and provided audio metrics. For questions 3–6, provide only a rating (no explanation)."),
            ("user", 
                """
    Transcription: {transcription_input}

    Questions:
    1. Did the Speaker Speak with Confidence? (One line answer)
    2. Did the speaker vary their tone, speed, and volume while delivering the speech/presentation? Here are the details provided about the tone, speed, pace, and volume, {audio_metrics}, I want you 
    to give the answer in a sentence format, (For ex : The Tone and Volume was appropriate. you could have maintained a steady Speed in Delivery. A few Words were pronounced very fast), I want you to give the answer in a proper sentence like the example, and doesn't provide the numerical metrics to user, it should be in sentence, but dont tell like, dont tell your that your tone was neutrl/sad/happy, say that your maintained a good tone, this is an example
    3. Did the speech have a structure of Opening, Body and Conclusion? (3-4 lines descriptive answer)
    4. Was the overall “Objective” of the speech delivered clearly? (3-4 lines descriptive answer)
    5. Was the content of the presentation/speech brief and to the point, or did it include unnecessary details that may have distracted or confused the audience? (3-4 lines descriptive answer)
    6. Was the content of the presentation/speech engaging, and did it capture the audience’s attention? (3-4 lines descriptive answer)
    7. Was the content of the presentation/speech relevant to the objective of the presentation? (3-4 lines descriptive answer)
    8. Was the content of the presentation/speech clear and easy to understand? (3-4 lines descriptive answer)
    9. Did the speaker add relevant examples, anecdotes and data to back their content? (3-4 lines descriptive answer)
    10. Did the speaker demonstrate credibility? Will you trust the speaker?  (3-4 lines descriptive answer)
    11.Did the speaker clearly explain how the speech or topic would benefit you and what you could gain from it? (3-4 lines descriptive answer)
    12. Was the speaker able to evoke an emotional connection with the audience? (3-4 lines descriptive answer)
    13. Overall, were you convinced/ persuaded with the speaker’s view on the topic? (3-4 lines descriptive answer)
    Only provide the answers to these questions—do not include any extra commentary. 
    Start your response with "These are the Answers:" and then list each answer on a new line. Call the user as you.
                """
                )
            ])
    else:
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", 
                "You are an expert interviewer evaluating a video resume based on a transcription and provided audio metrics. For questions 3–6, provide only a rating (no explanation)."),
            ("user", 
                """
    Transcription: {transcription_input}

    Questions:
    1. Did the Speaker Speak with Confidence? (One line answer)
    2. Was the content interesting and as per the guidelines provided? (One line answer)
    3. Who are you and what are your skills, expertise, and personality traits? (Provide only a rating: Needs Improvement, Poor, Satisfactory, or Excellent)
    4. Why are you the best person to fit this role? (Provide only a rating: Excellent, Good, or Poor)
    5. How are you different from others? (Provide only a rating: Excellent, Good, or Poor)
    6. What value do you bring to the role? (Provide only a rating: Excellent, Good, or Poor)
    7. Did the speech have a structure of Opening, Body, and Conclusion? (One line descriptive answer)
    8. Did the speaker vary their tone, speed, and volume while delivering the speech/presentation? Here are the details provided about the tone, speed, pace, and volume, {audio_metrics}, I want you 
    to give the answer in a sentence format, (For ex : The Tone and Volume was appropriate. you could have maintained a steady Speed in Delivery. A few Words were pronounced very fast), I want you to give the answer in a proper sentence like the example, and doesn't provide the numerical metrics to user, it should be in sentence, but dont tell like, dont tell your that your tone was neutrl/sad/happy, say that your maintained a good tone, this is an example
    9. How was the quality of research for the topic? Did the speech demonstrate good depth and proper citations? (3-4 lines descriptive answer)
    10. How convinced were you with the overall speech on the topic? Was it persuasive? Will you consider them for the job/opportunity? (Descriptive answer)
    Only provide the answers to these questions—do not include any extra commentary. 
    Start your response with "These are the Answers:" and then list each answer on a new line.
                """
                )
            ])
        
    chain = prompt_template | llm | output_parser
    response = chain.invoke({"transcription_input": transcription_input, "audio_metrics": audio_metrics})
    return response



# print(overall_analyser("/", audio_metrics))
