"""
Improved LinkedIn Profile Analyzer
Better prompt handling, input cleaning, few-shot examples, output check.
"""

import json
import logging
import google.generativeai as genai
from config import GEMINI_API_KEY

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfileAnalyzer:
    """Better LinkedIn Profile Analyzer using Gemini API"""

    def __init__(self, temperature=0.5):
        if not GEMINI_API_KEY:
            raise ValueError("Gemini API key is required. Please set GEMINI_API_KEY in your .env file.")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('models/gemini-1.5-flash')
        self.temperature = temperature
        logger.info("\n\n✅ Gemini client initialized with temperature = %s\n", self.temperature)

    def analyze(self, profile_data, mode="bio"):
        """
        mode: one of ["bio", "summary", "analysis"]
        """
        if not isinstance(profile_data, dict):
            raise ValueError("profile_data must be a dict")

        # Clean up the input before sending to prompt
        clean_data = self._sanitize_data(profile_data)
        prompt = self._create_prompt(clean_data, mode)

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"temperature": self.temperature}
            )
            text = response.text.strip() if hasattr(response, "text") else str(response)

            # Basic quality check
            if len(text.split()) < 30:
                logger.warning("⚠️ Output too short — likely incomplete.")
                text += "\n\n(Note: Output was very short, please verify and regenerate.)"

            result = {
                "result": text,
                "mode": mode,
                "profile_name": clean_data.get("name", "Unknown"),
                "model": "models/gemini-1.5-flash",
            }
            logger.info("✅ %s generated successfully for %s", mode.capitalize(), clean_data.get("name", "Unknown"))
            return result

        except Exception as e:
            logger.error(f"Error generating {mode}: {str(e)}")
            return {
                "result": f"Error: {str(e)}",
                "mode": mode,
                "profile_name": clean_data.get("name", "Unknown"),
                "error": True
            }

    def _sanitize_data(self, profile_data):
        """Remove useless or placeholder values"""
        name = profile_data.get("name") or "Unknown"
        headline = profile_data.get("headline") or ""
        about = profile_data.get("about") or ""

        # Remove default filler
        if "not found" in about.lower():
            about = ""

        # Experience
        exp_list = [
            exp for exp in profile_data.get("experience", [])
            if isinstance(exp, dict) and exp.get("title") and exp.get("company")
        ]

        # Skills
        skills_list = [
            s for s in profile_data.get("skills", [])
            if isinstance(s, str) and "not found" not in s.lower()
        ]

        education_list = [
            edu for edu in profile_data.get("education", [])
            if isinstance(edu, str) and "not found" not in edu.lower()
        ]

        return {
            "name": name,
            "headline": headline,
            "about": about,
            "experience": exp_list,
            "skills": skills_list,
            "education": education_list
        }

    def _create_prompt(self, profile_data, mode):
        """Craft a clearer, example-backed prompt"""
        name = profile_data["name"]
        headline = profile_data["headline"] or "No headline available"
        about = profile_data["about"] or ""
        exp_items = profile_data["experience"]
        skills_items = profile_data["skills"]

        exp_text = "\n".join([
            f"- {exp.get('title', 'Unknown')} at {exp.get('company', 'Unknown')}"
            for exp in exp_items[:5]
        ]) or "No work experience listed"

        skills_text = ", ".join(skills_items[:10]) or "No skills listed"

        edu_items = profile_data["education"]
        education_text = ", ".join(edu_items[:5]) if edu_items else "No education listed"

        if mode == "bio":
            prompt = f"""
You are a professional LinkedIn bio writer.
Write a clear, compelling **LinkedIn bio** in **first person**.
Use short paragraphs. Confident, friendly tone. Conclude with what they’re seeking next.
Approx 150-200 words.

**Profile**
Name: {name}
Headline: {headline}
About: {about}
Experience:{exp_text}
Skills: {skills_text}
Education: {education_text}

**Example Bio:**
"Hi, I'm John Doe — a passionate software engineer with 6 years of experience in full-stack development.
I thrive on turning complex problems into simple, elegant solutions that drive business impact.
Throughout my career, I've built scalable apps, mentored junior devs, and led cloud migrations.
When I'm not coding, you'll find me exploring new tech trends or collaborating on open-source projects.
I'm now looking to join a forward-thinking team where I can grow and contribute to impactful products."

Now write the new bio below:
"""
        elif mode == "summary":
            prompt = f"""
You are a professional LinkedIn profile summarizer.
Write a short **networking summary** for {name} in **third person**.
Be neutral, factual, and recruiter-friendly.

**Format:**
- 2-3 sentence overview.
- Line break.
- 3-5 bullet points (each starts with '- ').
- 1 short outreach talking point.

**Profile**
Name: {name}
Headline: {headline}
About: {about}
Experience: {exp_text}
Skills: {skills_text}
Education: {education_text}
"""
        elif mode == "analysis":
            prompt = f"""
You are a career advisor.
Analyze this LinkedIn profile. Provide:

1. A 2-3 sentence objective overview.
2. Line break.
3. 3-5 bullet points (strengths, gaps, opportunities).
4. 1-2 lines of actionable advice.

**Profile**
Name: {name}
Headline: {headline}
About: {about}
Experience: {exp_text}
Skills: {skills_text}
Education: {education_text}
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

def analyze_profile(profile_data, mode="bio", temperature=0.5):
    analyzer = ProfileAnalyzer(temperature=temperature)
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

    result = analyze_profile(sample, mode="bio")
    print("\nGenerated Output:\n", result["result"])
