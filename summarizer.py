"""
LinkedIn Profile Summarizer
Uses Google Gemini API to generate professional summaries from scraped profile data
"""

import json
import logging
import google.generativeai as genai
from config import GEMINI_API_KEY

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfileSummarizer:
    """LinkedIn Profile Summarizer using Gemini API"""
    
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("Gemini API key is required. Please set GEMINI_API_KEY in your .env file.")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('models/gemini-1.5-flash')
        logger.info("\n\n\t\tGemini client initialized successfully\n\n")

    def generate_summary(self, profile_data, summary_type="professional"):
        try:
            if not isinstance(profile_data, dict):
                raise ValueError("profile_data must be a dict")
            prompt = self._create_prompt(profile_data, summary_type)
            response = self.model.generate_content(prompt)
            summary = response.text.strip() if hasattr(response, 'text') else str(response)
            result = {
                'summary': summary,
                'type': summary_type,
                'profile_name': profile_data.get('name', 'Unknown'),
                'model': 'models/gemini-1.5-flash',
            }
            logger.info(f"Summary generated successfully for {profile_data.get('name', 'Unknown')}")
            return result
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return {
                'summary': f"Error generating summary: {str(e)}",
                'type': summary_type,
                'profile_name': profile_data.get('name', 'Unknown') if isinstance(profile_data, dict) else 'Unknown',
                'error': True
            }

    def _create_prompt(self, profile_data, summary_type):
        name = profile_data.get('name', 'Unknown')
        headline = profile_data.get('headline', 'No headline available')
        about = profile_data.get('about', 'No about section available')
        experience = profile_data.get('experience', [])
        if isinstance(experience, list) and experience:
            exp_text = "\n".join([
                f"• {exp.get('title', 'Unknown')} at {exp.get('company', 'Unknown Company')}"
                for exp in experience[:3] if isinstance(exp, dict)
            ])
        else:
            exp_text = "No work experience listed"
        skills = profile_data.get('skills', [])
        if isinstance(skills, list) and skills:
            skills_text = ", ".join(skills[:10])
        else:
            skills_text = "No skills listed"

        # Better tone instructions
        if summary_type == "professional":
            tone_instruction = (
                "Write a clear, compelling LinkedIn summary in third person, "
                "naturally using the candidate’s name. Highlight their top skills, "
                "relevant years of experience, industry background, and major achievements "
                "with measurable results if possible. Use a confident, professional tone "
                "that appeals to recruiters and hiring managers. Conclude with a short "
                "line about what they are looking for next. Keep it concise, around 150–200 words."
            )
        elif summary_type == "executive":
            tone_instruction = (
                "Write a polished, executive-level summary in third person, using the candidate’s name. "
                "Emphasize leadership experience, strategic vision, and measurable business impact, "
                "such as driving revenue growth, expanding markets, or leading large teams. "
                "Use a formal, authoritative tone suitable for senior leadership bios and investor audiences. "
                "End with a forward-looking statement about the executive’s goals or vision for the future. "
                "Keep it concise, under 200 words."
            )
        elif summary_type == "casual":
            tone_instruction = (
                "Write a warm, conversational LinkedIn summary in first person. "
                "Show the candidate’s personality and career journey, using friendly and authentic language. "
                "Include what they enjoy about their work, unique interests or values, and any personal touches "
                "that make them relatable. Keep it informal but still professional, as if introducing themselves "
                "to a new connection over coffee. End with a friendly invitation to connect or reach out. "
                "Keep it under 200 words."
            )
        else:
            tone_instruction = (
                "Write a clear, professional LinkedIn summary in third person that highlights "
                "key achievements, experience, and skills. Use a confident, recruiter-friendly tone "
                "and conclude with what the candidate is looking for next. Keep it under 200 words."
            )

        # Improved prompt with clearer instructions
        prompt = f"""
    {tone_instruction}

    Use the following LinkedIn profile information to craft the summary:

    Name: {name}
    Headline: {headline}
    About: {about}

    Work Experience:
    {exp_text}

    Skills: {skills_text}

    Please write a summary that:
    1. Clearly presents the candidate’s professional identity and career highlights.
    2. Emphasizes their unique strengths, skills, and accomplishments.
    3. Matches the specified tone and perspective above (third person or first person).
    4. Ends with a short line about their goals or an invitation to connect (if appropriate).
    5. Is clear, engaging, and suitable for LinkedIn or professional networking.
    """
        return prompt.strip()


    def generate_multiple_summaries(self, profile_data):
        summary_types = ["professional", "executive", "casual"]
        summaries = {}
        for summary_type in summary_types:
            try:
                summary_result = self.generate_summary(profile_data, summary_type)
                summaries[summary_type] = summary_result
            except Exception as e:
                logger.error(f"Error generating {summary_type} summary: {str(e)}")
                summaries[summary_type] = {
                    'summary': f"Error generating {summary_type} summary",
                    'error': True
                }
        return summaries

    def save_summary_to_file(self, summary_data, filename=None):
        try:
            if not filename:
                profile_name = summary_data.get('profile_name', 'unknown').replace(' ', '_').lower()
                filename = f"summary_{profile_name}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Summary saved to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error saving summary to file: {str(e)}")
            return None

def summarize_profile(profile_data, summary_type="professional"):
    try:
        summarizer = ProfileSummarizer()
        return summarizer.generate_summary(profile_data, summary_type)
    except Exception as e:
        logger.error(f"Error in summarization process: {str(e)}")
        return None

if __name__ == "__main__":
    sample_profile = {
        'name': 'John Doe',
        'headline': 'Software Engineer at Tech Company',
        'about': 'Passionate software engineer with 5 years of experience in web development.',
        'experience': [
            {'title': 'Senior Software Engineer', 'company': 'Tech Corp'},
            {'title': 'Software Engineer', 'company': 'Startup Inc'}
        ],
        'skills': ['Python', 'JavaScript', 'React', 'Node.js']
    }
    result = summarize_profile(sample_profile)
    if result:
        print("Generated Summary:")
        print(result['summary'])
    else:
        print("Failed to generate summary")