"""
LinkedIn Profile Analyzer
Uses Gemini API to generate a bio, networking summary, or analysis from scraped profile data.
"""

import json
import logging
import google.generativeai as genai
from config import GEMINI_API_KEY

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfileAnalyzer:
    """LinkedIn Profile Analyzer using Gemini API"""

    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("Gemini API key is required. Please set GEMINI_API_KEY in your .env file.")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('models/gemini-1.5-flash')
        logger.info("\n\n\t✅ Gemini client initialized\n\n")

    def analyze(self, profile_data, mode="bio"):
        """
        mode: one of ["bio", "summary", "analysis"]
        """
        if not isinstance(profile_data, dict):
            raise ValueError("profile_data must be a dict")

        try:
            prompt = self._create_prompt(profile_data, mode)
            response = self.model.generate_content(prompt)
            text = response.text.strip() if hasattr(response, "text") else str(response)

            result = {
                "result": text,
                "mode": mode,
                "profile_name": profile_data.get("name", "Unknown"),
                "model": "models/gemini-1.5-flash",
            }
            logger.info(f"✅ {mode.capitalize()} generated successfully for {profile_data.get('name', 'Unknown')}")
            return result

        except Exception as e:
            logger.error(f"Error generating {mode}: {str(e)}")
            return {
                "result": f"Error: {str(e)}",
                "mode": mode,
                "profile_name": profile_data.get("name", "Unknown"),
                "error": True
            }

    def _create_prompt(self, profile_data, mode):
        name = profile_data.get("name", "Unknown")
        headline = profile_data.get("headline", "No headline available")
        about = profile_data.get("about", "No about section available")

        exp_list = profile_data.get("experience", [])
        # Only use items that are dicts
        exp_items = [exp for exp in exp_list if isinstance(exp, dict)]
        if exp_items:
            exp_text = "\n".join([
                f"- {exp.get('title', 'Unknown')} at {exp.get('company', 'Unknown Company')}"
                for exp in exp_items[:5]
            ])
        else:
            exp_text = "No work experience listed"

        skills_list = profile_data.get("skills", [])
        # Only use items that are strings and not 'Skills not found'
        skills_items = [s for s in skills_list if isinstance(s, str) and s != "Skills not found"]
        skills_text = ", ".join(skills_items[:10]) if skills_items else "No skills listed"

        if mode == "bio":
            prompt = f"""
You are a professional LinkedIn bio writer.
Write a clear, compelling **LinkedIn bio** in **first person**.
Use short paragraphs (2-4 sentences each).
Include the person's top skills, years of experience, industry background, and major achievements.
Use a confident, friendly tone that appeals to recruiters and connections.
Conclude with a sentence about what they are looking for next in their career.
Add line breaks for readability.
Keep it around 150-200 words.

Profile:
Name: {name}
Headline: {headline}
About: {about}
Experience:
{exp_text}
Skills: {skills_text}
"""
        elif mode == "summary":
            prompt = f"""
You are a professional LinkedIn profile summarizer.
Write a short **networking summary** for {name} in **third person**.
Be neutral, factual, and suitable for a recruiter or hiring manager.

**Format:**
1. Start with a 2-3 sentence overview paragraph.
2. Then add a line break.
3. Then write **3-5 bullet points**, each starting with '- ' on its own line.
4. Then add 1 short outreach talking point on a new line.

Profile:
Name: {name}
Headline: {headline}
About: {about}
Experience:
{exp_text}
Skills: {skills_text}
"""
        elif mode == "analysis":
            prompt = f"""
You are an expert career advisor.
Analyze this LinkedIn profile and provide:

1. A short 2-3 sentence overview in **third person**.
2. Then add a line break.
3. Then list **3-5 bullet points** with strengths, gaps, or opportunities for improvement — each bullet starts with ' - ' on its own line.
4. Then add 1-2 lines of clear advice for next career steps.

Profile:
Name: {name}
Headline: {headline}
About: {about}
Experience:
{exp_text}
Skills: {skills_text}
"""
        else:
            raise ValueError(f"Invalid mode: {mode}. Must be one of ['bio', 'summary', 'analysis'].")

        return prompt.strip()


    def save_result(self, result_data, filename=None):
        try:
            if not filename:
                safe_name = result_data.get("profile_name", "unknown").replace(" ", "_").lower()
                filename = f"profile_{safe_name}_{result_data.get('mode', 'output')}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Result saved to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error saving result: {str(e)}")
            return None

def analyze_profile(profile_data, mode="bio"):
    analyzer = ProfileAnalyzer()
    return analyzer.analyze(profile_data, mode)

if __name__ == "__main__":
    sample = {
        "name": "Jane Doe",
        "headline": "Senior AI Researcher at BigTech",
        "about": "Innovator in large language models with a decade of experience.",
        "experience": [
            {"title": "Senior AI Researcher", "company": "BigTech"},
            {"title": "Machine Learning Engineer", "company": "Startup Inc."}
        ],
        "skills": ["Python", "Deep Learning", "NLP", "TensorFlow", "Research"]
    }

    result = analyze_profile(sample, mode="summary")
    print("\nGenerated Output:\n", result["result"])
