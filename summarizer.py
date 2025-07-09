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
        if summary_type == "professional":
            tone_instruction = "Write a professional, business-focused summary that highlights key achievements and expertise."
        elif summary_type == "executive":
            tone_instruction = "Write an executive-level summary that emphasizes leadership, strategic thinking, and business impact."
        elif summary_type == "casual":
            tone_instruction = "Write a friendly, conversational summary that captures the person's personality and career journey."
        else:
            tone_instruction = "Write a professional summary that highlights key achievements and expertise."
        prompt = f"""
{tone_instruction}

Based on the following LinkedIn profile information, create a compelling 2-3 sentence professional summary:

Name: {name}
Headline: {headline}
About: {about}

Work Experience:
{exp_text}

Skills: {skills_text}

Please create a summary that:
1. Captures their professional identity and expertise
2. Highlights their key strengths and experience
3. Is engaging and professional in tone
4. Is suitable for networking, introductions, or professional contexts

Summary:
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