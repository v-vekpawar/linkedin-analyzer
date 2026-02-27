import os
import logging
from google import genai
from dotenv import load_dotenv
from datetime import datetime
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger(__name__)
load_dotenv()

class ProfileAnalyzer:

    def __init__(self, temperature=0.4):
        if not os.getenv("GEMINI_API_KEY"):
            raise ValueError("Gemini API key is required. Please set GEMINI_API_KEY in your .env file.")
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = 'gemini-2.5-flash'
        self.temperature = temperature
        logger.info("\n\nProfessional Gemini client initialized\n")

    def analyze(self, profile_data, mode="about_profile", **kwargs):
        if not isinstance(profile_data, dict):
            raise ValueError("profile_data must be a dict")
        
        gen_config = self._get_generation_config(mode)

        prompt = self._create_professional_prompt(profile_data, mode, **kwargs)

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "temperature": gen_config["temperature"],
                    "top_p": gen_config["top_p"],
                    "top_k": gen_config["top_k"],
                    # "max_output_tokens": gen_config["max_output_tokens"]
                }
            )
            try:
                if hasattr(response, 'candidates') and response.candidates:
                    text = response.candidates[0].content.parts[0].text.strip()
                elif hasattr(response, 'text'):
                    text = response.text.strip()
                else:
                    text = str(response)
            except (AttributeError, IndexError) as e:
                logger.exception(f"Error extracting text: {e}")
                text = str(response)
            text = self._clean_output(text)

            result = {
                "result": text,
                "mode": mode,
                "profile_name": profile_data.get("name", "Unknown"),
                "model": self.model,
                "temperature": gen_config["temperature"],
                "generated_at": datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p")
            }
            
            logger.info("%s generated successfully for %s", mode.capitalize(), profile_data.get("name", "Unknown"))
            return result
        
        except Exception as e:
            logger.exception(f"Error generating {mode}: {e}")
            return {
                "result": f"Error generating analysis: {str(e)}",
                "mode": mode,
                "profile_name": profile_data.get("name", "Unknown"),
                "error": True
            }
    
    def _get_generation_config(self, mode):
        """Optimized generation settings for professional output"""
        config_map = {
            "about_profile": {
                "temperature": 0.3,
                "top_p": 0.8,
                "top_k": 35,
                # "max_output_tokens": 800,
            },
            "approach_person": {
                "temperature": 0.6,
                "top_p": 0.9,
                "top_k": 50,
                # "max_output_tokens": 1500,
            },
            "compatibility_score": {
                "temperature": 0.35,
                "top_p": 0.8,
                "top_k": 40,
                # "max_output_tokens": 600,
            }
        }
        return config_map.get(mode, {
            "temperature": 0.45,
            "top_p": 0.85,
            "top_k": 37,
            # "max_output_tokens": 1000
        })
    
    def _create_professional_prompt(self, profile_data, mode, **kwargs):
        
        match mode:
            case "about_profile": 
                return self._about_prompt(profile_data)
            case "approach_person": 
                return self._approach_prompt(profile_data)
            case "compatibility_score": 
                user_data = kwargs.get('user_data')
                return self._compatibility_prompt(user_data, profile_data)
        
    def _about_prompt(self,profile_data):
        
        return f"""You are an expert career analyst and professional communicator.

Task: Generate a 30-second intelligence brief from a LinkedIn profile. The goal is to allow someone to quickly understand the person's professional background without reading the full profile.

Profile Information: 
Name: {profile_data["name"]}
Headline: {profile_data["headline"]}
About: {profile_data["about"]}
Experience: {profile_data["experience"]}
Skills: {profile_data["skills"]}
Education: {profile_data["education"]}
Certifications: {profile_data["certifications"]}

Output Requirements:
- Keep it concise (~150 words max) for a 30-second read.
- Present as a numbered list with these sections:
    1. Who they are (summary of professional identity)
    2. What they specialize in (core skills and expertise)
    3. Seniority level (junior, mid, senior, executive)
    4. Key strengths (top 3–5)
    5. Career trajectory (brief progression highlights)
    6. Potential talking points (notable certifications, projects, achievements)
- Write in a professional, approachable tone suitable for networking or quick briefings.
- If any field is missing or empty, skip that section gracefully.

Example Output:
1. Who they are: Senior product manager with 10+ years in SaaS and fintech.
2. What they specialize in: Product strategy, Agile roadmapping, team leadership.
3. Seniority level: Senior
4. Key strengths: Strategic thinking, cross-functional leadership, product execution.
5. Career trajectory: Progressed from product manager to senior product manager at TechCorp; MBA from Harvard.
6. Potential talking points: PMP and CSPO certified; led launch of flagship SaaS product.

Now generate a 30-second intelligence brief using the Profile Information provided.
"""

    def _approach_prompt(self,profile_data):
        return f"""You are an expert professional networking strategist and LinkedIn outreach coach.

Task: Using the LinkedIn profile of a target person, generate a set of personalized outreach angles and LinkedIn messages that are highly relevant and non-generic. The goal is to help someone connect effectively, leveraging shared background, skills, and interests.

Profile Information:
Name: {profile_data["name"]}
Headline: {profile_data["headline"]}
About: {profile_data["about"]}
Experience: {profile_data["experience"]}
Skills: {profile_data["skills"]}
Education: {profile_data["education"]}
Certifications: {profile_data["certifications"]}

Output Requirements:

Step 1: Suggested Outreach Angles
- Generate 3–5 personalized outreach angles using the following types (use only relevant angles if some don’t apply):
    1. Shared background angle
    2. Career compliment angle
    3. Industry insight angle
    4. Value-driven pitch angle
    5. Curiosity angle
- For each angle, provide a 1–2 sentence explanation of why it works.

Step 2: Personalized LinkedIn Messages
- For each outreach angle, generate a LinkedIn message in 60–120 words.
- Include the following message types (generate only messages appropriate for the profile and angle):
    1. Casual connect – friendly tone, references shared background or interest
    2. Value-first connect – explains value you can provide
    3. Recruiting outreach – professional tone, highlights opportunity
    4. Sales outreach – contextualized pitch, references shared interest
    5. Mentorship ask – respectful, personalized reasoning
    6. Collaboration proposal – concise, actionable, solution-oriented

Tone & Style:
- Professional, approachable, and contextually relevant.
- Do not copy long sentences from the profile; synthesize and summarize.
- Each message should feel personal, natural, and tailored to the recipient.

Example Output:

Step 1: Suggested Outreach Angles
1. Shared background angle: You both studied at the same university, making an easy personal connection.
2. Career compliment angle: Their recent promotion shows strong leadership in SaaS, a point to highlight.
3. Industry insight angle: They work in renewable energy trends that align with your expertise.
4. Value-driven pitch angle: Offer insights from your overlapping skills in marketing automation.
5. Curiosity angle: Ask an engaging question about their recent project.

Step 2: Personalized Messages
1. Casual connect: [60–120 words, friendly tone, references shared background]
2. Value-first connect: [60–120 words, explains value you can offer]
3. Recruiting outreach: [60–120 words, professional tone, highlights opportunity]
4. Sales outreach: [60–120 words, contextualized pitch with shared interest]
5. Mentorship ask: [60–120 words, respectful, personalized reasoning]
6. Collaboration proposal: [60–120 words, concise and actionable]

Now generate the outreach angles and messages using the Profile Information provided.
"""            

    def _compatibility_prompt(self,user_data, profile_data):
        return f"""You are an expert professional networking analyst.

Task: Compare two LinkedIn profiles and generate a compatibility score (0–100%) that estimates how well User 1 and User 2 align for professional networking, collaboration, or outreach. Based on the analysis, provide a recommendation on whether User 1 should connect with User 2.

Inputs:
User 1 Profile:
Name: {user_data["name"]}
Headline: {user_data["headline"]}
About: {user_data["about"]}
Experience: {user_data["experience"]}
Skills: {user_data["skills"]}
Education: {user_data["education"]}
Certifications: {user_data["certifications"]}

User 2 Profile:
Name: {profile_data["name"]}
Headline: {profile_data["headline"]}
About: {profile_data["about"]}
Experience: {profile_data["experience"]}
Skills: {profile_data["skills"]}
Education: {profile_data["education"]}
Certifications: {profile_data["certifications"]}

Evaluation Dimensions:
- Industry overlap
- Skill overlap
- Career stage alignment
- Education similarity
- Geographic proximity (if available)
- Complementary skills
- Network proximity (if available)

Output Requirements:
1. **Compatibility Score:** A percentage (0–100%) indicating overall alignment.
2. **Explanation:** 3–5 concise bullet points summarizing why the score was assigned. Include examples like shared skills, similar industries, overlapping career stages, education, or network connections.
3. **Recommendation:** Clearly state whether User 1 should connect with User 2. Base the decision on the compatibility score, alignment of skills, industry relevance, and networking potential.

Tone & Style:
- Professional, objective, and concise.
- Focus on actionable insights rather than repeating profile details.

Example Output:

Compatibility: 78%

Why:
- 3 shared skills: Python, SQL, Machine Learning
- Similar industry experience in SaaS
- Career stage alignment: both senior-level professionals
- Both attended top-tier universities
- 2nd-degree connection on LinkedIn

Recommendation: Yes, User 1 should connect with User 2, as the high compatibility and shared skills indicate a strong potential for meaningful professional engagement.

Now generate the compatibility score, reasoning, and recommendation for User 1 and User 2 using the profile data provided.

"""
    def _clean_output(self, text):
        preamble_patterns = [
            r'^Here\'s a [^.!?]*[.!?]\s*',
            r'^Here is a [^.!?]*[.!?]\s*',
            r'^I\'ll write [^.!?]*[.!?]\s*',
            r'^I\'ll create [^.!?]*[.!?]\s*',
            r'^Let me write [^.!?]*[.!?]\s*',
            r'^I\'ll provide [^.!?]*[.!?]\s*',
            r'^Here\'s the [^.!?]*[.!?]\s*',
            r'^I can help [^.!?]*[.!?]\s*',
            r'^Sure, here\'s [^.!?]*[.!?]\s*',
        ]
        
        for pattern in preamble_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remove markdown bold formatting
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      
        
        # Normalize whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Remove closing fluff if it's at the very end
        end_phrases = [
            "Let me know if", "Feel free to", "I hope this helps",
            "This should work", "Does this look good"
        ]
        
        for phrase in end_phrases:
            if phrase.lower() in text.lower():
                idx = text.lower().find(phrase.lower())
                # Only remove if it's in the last 20% of the text
                if idx > len(text) * 0.8: 
                    text = text[:idx].strip()
                    break
    
        return text.strip()
    
def analyze_profile(profile_data, mode="about_profile", temperature=None, **kwargs):
    """Main analysis function"""
    analyzer = ProfileAnalyzer(temperature=temperature or 0.4)
    return analyzer.analyze(profile_data, mode, **kwargs)
