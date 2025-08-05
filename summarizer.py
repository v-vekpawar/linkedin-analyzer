"""
Enhanced LinkedIn Profile Analyzer with Professional Output Quality
Completely redesigned prompts to avoid poor formatting and unprofessional results.
"""

import json
import logging
import google.generativeai as genai
from config import GEMINI_API_KEY
from datetime import datetime
import re

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfileAnalyzer:
    """Professional LinkedIn Profile Analyzer with high-quality output generation"""

    def __init__(self, temperature=0.4):
        if not GEMINI_API_KEY:
            raise ValueError("Gemini API key is required. Please set GEMINI_API_KEY in your .env file.")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('models/gemini-1.5-flash')
        self.temperature = temperature
        logger.info("\n\n✅ Professional Gemini client initialized\n")

    def analyze(self, profile_data, mode="bio"):
        """
        Generate professional analysis with clean, structured output
        mode: one of ["bio", "summary", "analysis"]
        """
        if not isinstance(profile_data, dict):
            raise ValueError("profile_data must be a dict")

        # Clean and structure the input data
        clean_data = self._sanitize_data(profile_data)
        
        # Get optimal configuration for each mode
        gen_config = self._get_generation_config(mode)
        
        # Create professional prompt
        prompt = self._create_professional_prompt(clean_data, mode)

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=gen_config
            )
            text = response.text.strip() if hasattr(response, "text") else str(response)

            # Clean and format output professionally
            text = self._clean_output(text, mode)

            result = {
                "result": text,
                "mode": mode,
                "profile_name": clean_data.get("name", "Unknown"),
                "model": "models/gemini-1.5-flash",
                "temperature": gen_config["temperature"],
                "generated_at": datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p")
            }
            
            logger.info("✅ %s generated successfully for %s", mode.capitalize(), clean_data.get("name", "Unknown"))
            return result

        except Exception as e:
            logger.error(f"Error generating {mode}: {str(e)}")
            return {
                "result": f"Error generating analysis: {str(e)}",
                "mode": mode,
                "profile_name": clean_data.get("name", "Unknown"),
                "error": True
            }

    def _get_generation_config(self, mode):
        """Optimized generation settings for professional output"""
        config_map = {
            "bio": {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 500,
            },
            "summary": {
                "temperature": 0.4,
                "top_p": 0.8,
                "top_k": 35,
                "max_output_tokens": 400,
            },
            "analysis": {
                "temperature": 0.3,
                "top_p": 0.7,
                "top_k": 30,
                "max_output_tokens": 800,
            }
        }
        return config_map.get(mode, {
            "temperature": 0.4,
            "top_p": 0.8,
            "top_k": 35,
            "max_output_tokens": 500,
        })

    def _sanitize_data(self, profile_data):
        """Clean and structure profile data"""
        name = profile_data.get("name", "").strip() or "Professional"
        headline = profile_data.get("headline", "").strip()
        about = profile_data.get("about", "").strip()

        # Clean HTML entities and formatting
        about = about.replace("&#34;", '"').replace("&amp;", "&")
        about = re.sub(r'[🌟⭐✨🚀💼📈💡🎯]', '', about)  # Remove emojis for cleaner processing
        
        # Process experience
        exp_list = []
        for exp in profile_data.get("experience", []):
            if isinstance(exp, dict):
                title = exp.get("title", "").strip()
                company = exp.get("company", "").strip()
                if title or company:
                    exp_list.append({
                        "title": title,
                        "company": company,
                        "duration": exp.get("duration", "").strip()
                    })

        # Process skills (remove duplicates and clean)
        skills_list = []
        for skill in profile_data.get("skills", []):
            if isinstance(skill, str) and skill.strip():
                clean_skill = skill.strip()
                if clean_skill not in skills_list:
                    skills_list.append(clean_skill)

        # Process education
        education_list = []
        for edu in profile_data.get("education", []):
            if isinstance(edu, str) and edu.strip():
                education_list.append(edu.strip())

        return {
            "name": name,
            "headline": headline,
            "about": about,
            "experience": exp_list,
            "skills": skills_list,
            "education": education_list
        }

    def _create_professional_prompt(self, data, mode):
        """Create high-quality prompts that produce professional results"""
        
        if mode == "bio":
            return self._bio_prompt(data)
        elif mode == "summary":
            return self._summary_prompt(data)
        elif mode == "analysis":
            return self._analysis_prompt(data)

    def _bio_prompt(self, data):
        """Generate compelling personal bio"""
        experience_text = self._format_experience(data["experience"])
        skills_text = ", ".join(data["skills"][:8]) if data["skills"] else "Various professional skills"
        education_text = data["education"][0] if data["education"] else "Educational background"

        return f"""Write a compelling LinkedIn bio for a professional. Create ONLY the bio text - no introductions, no explanations, no formatting instructions.

REQUIREMENTS:
- Write in first person (I, my, me)
- Professional and confident tone
- 120-180 words
- Include value proposition
- End with call-to-action
- No bullet points or excessive formatting

PROFILE INFORMATION:
Name: {data["name"]}
Current Role: {data["headline"]}
Background: {data["about"][:300]}
Experience: {experience_text}
Skills: {skills_text}
Education: {education_text}

EXAMPLE STYLE (adapt for this person):
"I'm Sarah Chen, a digital marketing strategist who helps B2B companies increase their online revenue by 40% through data-driven campaigns. With 6 years of experience at leading agencies, I've managed over $2M in ad spend and launched 50+ successful campaigns.

My expertise spans Google Ads, Facebook advertising, marketing automation, and conversion optimization. I excel at turning complex data into actionable strategies that drive measurable growth.

Currently leading digital initiatives at TechCorp, I'm passionate about helping businesses navigate the evolving digital landscape. I love connecting with fellow marketers and business leaders.

Let's connect if you're looking to scale your digital presence or discuss the latest marketing trends."

Write the bio now:"""

    def _summary_prompt(self, data):
        """Generate professional summary for networking"""
        experience_text = self._format_experience(data["experience"])
        skills_text = ", ".join(data["skills"][:10]) if data["skills"] else "Professional skills"
        
        return f"""Write a professional networking summary about this LinkedIn profile. Write ONLY the summary - no introductions, explanations, or extra text.

REQUIREMENTS:
- Write in third person
- Professional and informative tone
- 100-150 words
- Focus on what they do and their value
- Include why someone should connect with them
- No bullet points

PROFILE INFORMATION:
Name: {data["name"]}
Role: {data["headline"]}
Background: {data["about"][:300]}
Experience: {experience_text}
Skills: {skills_text}

EXAMPLE STYLE (adapt for this person):
"Michael Rodriguez is a software engineer with 5 years of experience building scalable web applications for fintech companies. He specializes in React, Node.js, and cloud architecture, having led development teams at two successful startups.

Michael has a proven track record of delivering complex projects on time and mentoring junior developers. His technical expertise combined with strong communication skills makes him valuable for cross-functional collaboration.

He's currently exploring opportunities in senior engineering roles and is actively involved in the tech community through meetups and open-source contributions. Michael is an excellent connection for professionals in software development, startup ecosystems, and fintech innovation."

Write the summary now:"""

    def _analysis_prompt(self, data):
        """Generate comprehensive profile analysis"""
        experience_text = self._format_experience(data["experience"])
        skills_text = ", ".join(data["skills"][:12]) if data["skills"] else "Skills not listed"
        
        return f"""Provide a professional LinkedIn profile analysis. Write ONLY the analysis content - no introductions or explanations.

FORMAT REQUIREMENTS:
- Use clear section headers
- Professional language
- Specific and actionable feedback
- No excessive bullet points
- Focus on improvement opportunities

PROFILE INFORMATION:
Name: {data["name"]}
Headline: {data["headline"]}
About: {data["about"][:400]}
Experience: {experience_text}
Skills: {skills_text}
Education: {", ".join(data["education"][:2]) if data["education"] else "Not specified"}

ANALYSIS STRUCTURE:

PROFILE OVERVIEW
[2-3 sentences about their current positioning and profile strength]

STRENGTHS
[3-4 specific positive aspects of their profile]

AREAS FOR IMPROVEMENT  
[3-4 specific areas that need enhancement]

RECOMMENDATIONS
[4-5 actionable steps to improve their profile]

Write the analysis now:"""

    def _format_experience(self, experience_list):
        """Format experience for prompt context"""
        if not experience_list:
            return "No experience listed"
        
        formatted = []
        for exp in experience_list[:5]:
            title = exp.get("title", "")
            company = exp.get("company", "")
            if title and company:
                formatted.append(f"{title} at {company}")
            elif title:
                formatted.append(title)
        
        return "; ".join(formatted) if formatted else "Various roles"

    def _clean_output(self, text, mode):
        """Clean and format the output professionally"""
        
        # Remove common AI response prefixes
        prefixes = [
            "Here's a", "Here is a", "I'll write", "I'll create", "Let me write",
            "I'll provide", "Here's the", "I can help", "Sure, here's"
        ]
        
        for prefix in prefixes:
            if text.lower().startswith(prefix.lower()):
                # Find the end of the sentence and remove it
                first_sentence_end = text.find('.') + 1
                if first_sentence_end > 0 and first_sentence_end < 100:
                    text = text[first_sentence_end:].strip()
                break
        
        # Remove markdown formatting that might appear
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Italic
        
        # Clean up spacing and line breaks
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Remove any trailing instructions or notes
        end_phrases = [
            "Let me know if", "Feel free to", "I hope this helps",
            "This should work", "Does this look good"
        ]
        
        for phrase in end_phrases:
            if phrase.lower() in text.lower():
                idx = text.lower().find(phrase.lower())
                if idx > len(text) * 0.8:  # Only if it's near the end
                    text = text[:idx].strip()
                    break
        
        return text.strip()

    def save_result(self, result_data, filename=None):
        """Save results with clean formatting"""
        try:
            if not filename:
                safe_name = result_data.get("profile_name", "unknown").replace(" ", "_").lower()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"linkedin_{result_data.get('mode', 'output')}_{safe_name}_{timestamp}.txt"
                
            # Create clean formatted output
            output_content = f"""LinkedIn Profile Analysis

Profile: {result_data.get('profile_name', 'Unknown')}
Type: {result_data.get('mode', 'unknown').title()}
Generated: {result_data.get('generated_at', 'Unknown time')}

Result:

{result_data.get('result', 'No result available')}

Generated by LinkedIn Profile Analyzer"""
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(output_content)
                
            logger.info(f"✅ Result saved to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error saving result: {str(e)}")
            return None

def analyze_profile(profile_data, mode="bio", temperature=None):
    """Main analysis function"""
    analyzer = ProfileAnalyzer(temperature=temperature or 0.4)
    return analyzer.analyze(profile_data, mode)

if __name__ == "__main__":
    # Test with fictional data
    sample = {
        "name": "Alex Johnson",
        "headline": "Senior Software Engineer | Full Stack Developer | Tech Lead",
        "about": "Experienced software engineer with passion for building scalable applications. Strong background in web development and team leadership.",
        "experience": [
            {"title": "Senior Software Engineer", "company": "TechCorp", "duration": "2022-Present"},
            {"title": "Software Developer", "company": "StartupXYZ", "duration": "2020-2022"}
        ],
        "skills": ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker", "Leadership"],
        "education": ["Computer Science Degree - State University"]
    }

    print("Testing Bio Generation:")
    result = analyze_profile(sample, mode="bio")
    print(result["result"])
    print("\n" + "="*60 + "\n")
    
    print("Testing Summary Generation:")
    result = analyze_profile(sample, mode="summary")
    print(result["result"])
    print("\n" + "="*60 + "\n")
    
    print("Testing Analysis Generation:")
    result = analyze_profile(sample, mode="analysis")
    print(result["result"])