from flask import Flask, render_template, request, flash, redirect, url_for
import os, logging, sys, argparse
from scraper import scrape_linkedin_profile
from summarizer import analyze_profile
from config import FLASK_ENV, FLASK_DEBUG, HEADLESS
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY",None)

def console_mode():
    print("=" * 60)
    print("LinkedIn Profile Analyzer - Console Mode")
    print("=" * 60)

    if not API_KEY:
        logger.error("API Key not found in environment")
        print("Please set your GEMINI_API_KEY in the .env file or config.py")
        print("Get your API key from: https://aistudio.google.com/app/apikey")
        return
    
    profile_url = input("Enter LinkedIn Profile URL: ").strip()
    if "linkedin.com/in/" not in profile_url:
        logger.error("Invalid Input")
        print("\nInvalid LinkedIn profile URL. Please provide a valid LinkedIn profile URL.\n")
        return
    
    print(f"\n Scraping profile: {profile_url}")

    try:
        profile_data = scrape_linkedin_profile(profile_url, headless=HEADLESS)
        if not profile_data:
            print("\n\n\t\tFailed to scrape profile data\n\n")
            return
        
        print("\n\n\t\t Profile data scraped successfully!\n")
        print(f"Name: {profile_data.get('name', 'Unknown')}")
        print(f"Headline: {profile_data.get('headline', 'Unknown')}\n")
        print(f"About: {profile_data.get('about','Unknown')}\n")
        print(f"Skills: {profile_data.get('skills','Unknown')}\n")
        print(f"Experience: {profile_data.get('experience','Unknown')}\n")
        print(f"Education: {profile_data.get('education','Unknown')}\n")
        print(f"Certifications: {profile_data.get('certifications','Unknown')}\n")

        # Show available analysis modes
        print("\n Available Analysis Modes:")
        print("1. About Profile - Know About this Person")
        print("2. Approach Person - How to Approach this person")
        print("3. Compatibility Score - Check Compatibility Score with your profile")

        while True:
            choice = input("\nSelect analysis mode (1-3) or 'all' for all modes: ").strip().lower()
            
            if choice == '1':
                mode = 'about_profile'
                break
            elif choice == '2':
                mode = 'approach_person'
                break
            elif choice == '3':
                mode = 'compatibility_score'
                break
            elif choice == 'all':
                mode = 'all'
                break
            else:
                print("Invalid choice. Please select 1, 2, 3, or 'all'")
        
        if mode == 'all':
            user_data = None
            print("\n Generating all analysis types...")
            modes = ['about_profile', 'approach_person', 'compatibility_score']
            
            for analysis_mode in modes:
                if analysis_mode == 'compatibility_score':
                    user_url= input("Enter Your Profile URL to check score: ").strip()
                    if "linkedin.com/in/" not in user_url:
                        logger.error("Invalid Input")
                        print("\nInvalid LinkedIn profile URL. Please provide a valid LinkedIn profile URL.\n")
                        return
                    
                    print(f"\n Scraping profile: {user_url}")

                    try:
                        user_data = scrape_linkedin_profile(user_url, headless=HEADLESS)
                        if not user_data:
                            print("\n\n\t\tFailed to scrape profile data\n\n")
                            return
                    except Exception as e:
                        print("Failed at scraping given profile")

                print(f"\n Generating {analysis_mode}...")
                if user_data:
                    result = analyze_profile(profile_data, analysis_mode,user_data=user_data)
                else:
                    result = analyze_profile(profile_data,analysis_mode)
                
                if not result or result.get('error'):
                    print(f"\nFailed to generate {analysis_mode}")
                    continue
                
                print(f"\n{'=' * 60}")
                print(f"{analysis_mode.upper()}")
                print("=" * 60)
                print(result['result'])
                print("=" * 60)
        else:
            print(f"\n Generating {mode}...")
            if mode == 'compatibility_score':
                user_url= input("Enter Your Profile URL to check score: ").strip()
                if "linkedin.com/in/" not in user_url:
                    logger.error("Invalid Input")
                    print("\nInvalid LinkedIn profile URL. Please provide a valid LinkedIn profile URL.\n")
                    return
                
                print(f"\n Scraping profile: {user_url}")

                try:
                    user_data = scrape_linkedin_profile(user_url, headless=HEADLESS)
                    if not user_data:
                        print("\n\n\t\tFailed to scrape profile data\n\n")
                        return
                    result = analyze_profile(profile_data, mode, user_data=user_data)
                except Exception as e:
                    print("Failed at scraping given profile")
            else:
                result = analyze_profile(profile_data, mode)
            
            if not result or result.get('error'):
                print(f"\n Failed to generate {mode}")
                return
            
            print(f"\n{'=' * 60}")
            print(f"{mode.upper()}")
            print("=" * 60)
            print(result['result'])
            print("=" * 60)

    except KeyboardInterrupt:
        print("\n\n Process interrupted by user")
    except Exception as e:
        print(f"\n An error occurred: {str(e)}")
        logger.error(f"Error in console mode: {str(e)}")
        
    
def create_flask_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["FLASK_ENV"] = FLASK_ENV

    @app.route('/')
    def index():
        return render_template("index.html")
    
    @app.route('/analyze', methods=['POST'])
    def analyze():
        try:
            profile_url = request.form.get('profile_url', '').strip()
            analysis_mode = request.form.get('analysis_mode', 'about_profile')
            user_url = request.form.get('user_url', '').strip()
            use_sample = 'use_sample' in request.form

            # Validate profile URL
            if not use_sample:
                if not profile_url:
                    flash('Please provide a LinkedIn profile URL', 'error')
                    return redirect(url_for('index'))
                if "linkedin.com/in/" not in profile_url:
                    flash('Please provide a valid LinkedIn profile URL', 'error')
                    return redirect(url_for('index'))
            
            # Validate user URL for compatibility_score mode
            if analysis_mode == "compatibility_score":
                if not use_sample and not user_url:
                    flash('Please provide your LinkedIn profile URL for compatibility score analysis', 'error')
                    return redirect(url_for('index'))
                if not use_sample and "linkedin.com/in/" not in user_url:
                    flash('Please provide a valid LinkedIn profile URL for your profile', 'error')
                    return redirect(url_for('index'))
            
            if use_sample:
                # Use sample data for testing
                profile_data = {
                    'name': 'John Doe',
                    'headline': 'Senior Software Engineer at Tech Company',
                    'about': 'Passionate software engineer with 5+ years of experience in full-stack development, specializing in Python, JavaScript, and cloud technologies. I love building scalable applications and mentoring junior developers.',
                    'experience': [
                        {'title': 'Senior Software Engineer', 'company': 'Tech Corp'},
                        {'title': 'Software Engineer', 'company': 'Startup Inc'},
                        {'title': 'Junior Developer', 'company': 'Web Solutions'}
                    ],
                    'skills': ['Python', 'JavaScript', 'React', 'Node.js', 'AWS', 'Docker', 'Git', 'SQL', 'MongoDB', 'REST APIs'],
                    'education': ['Bachelor of Science in Computer Science', 'Master of Science in Artificial Intelligence'],
                    'certifications': [{'certificate':'Some Course Certifications', 'link':'some_url', 'issuer':'issued by some company', 'date':'some date'}],
                    'url': profile_url
                }
                # For compatibility_score with sample data, use sample user data too
                if analysis_mode == "compatibility_score":
                    user_data = {
                        'name': 'Jane Smith',
                        'headline': 'Product Manager at Innovation Co',
                        'about': 'Product-focused professional with 8+ years building SaaS products. Passionate about user experience and data-driven decisions.',
                        'experience': [
                            {'title': 'Senior Product Manager', 'company': 'Innovation Co'},
                            {'title': 'Product Manager', 'company': 'Tech Ventures'},
                            {'title': 'Business Analyst', 'company': 'Analytics Firm'}
                        ],
                        'skills': ['Product Strategy', 'Agile', 'Data Analysis', 'Python', 'SQL', 'Jira', 'Figma'],
                        'education': ['MBA in Business Administration', 'Bachelor of Science in Economics'],
                        'certifications': [{'certificate': 'Certified Scrum Product Owner', 'link': 'some_url', 'issuer': 'Scrum Alliance', 'date': 'some date'}],
                        'url': 'https://www.linkedin.com/in/sample-pm'
                    }
                flash('Using sample data for demonstration', 'info')
            else:
                # Scrape the actual profile
                profile_data = scrape_linkedin_profile(profile_url, headless=HEADLESS)
                
                if not profile_data:
                    flash('Failed to scrape profile data. Please check the URL and try again.', 'error')
                    return redirect(url_for('index'))
                
                # For compatibility_score, also scrape user profile
                if analysis_mode == "compatibility_score":
                    user_data = scrape_linkedin_profile(user_url, headless=HEADLESS)
                    if not user_data:
                        flash('Failed to scrape your profile data. Please check the URL and try again.', 'error')
                        return redirect(url_for('index'))

            # Generate analysis based on mode
            if analysis_mode == "compatibility_score":
                analysis_result = analyze_profile(profile_data, analysis_mode, user_data=user_data)
            else:
                analysis_result = analyze_profile(profile_data, analysis_mode)

            if not analysis_result or analysis_result.get('error'):
                flash('Failed to generate analysis. Please check your Gemini API key.', 'error')
                return redirect(url_for('index'))
            
            return render_template('result.html', 
                profile_data=profile_data, 
                analysis_result=analysis_result)
            
        except Exception as e:
            logger.error(f"Error in Flask route: {str(e)}")
            flash(f'An error occurred: {str(e)}', 'error')
            return redirect(url_for('index'))
            
    return app

def web_mode():
    print("=" * 60)
    print("LinkedIn Profile Analyzer - Web Mode")
    print("=" * 60)

    if not API_KEY:
        logger.error("Error: Gemini API key not found!")
        print("Please set your API_KEY in the .env file")
        return
    
    app = create_flask_app()

    try:
        app.run(
            debug=FLASK_DEBUG
        )
    except KeyboardInterrupt:
        print("\n\n Server stopped by user")
    except Exception as e:
        print(f"\n Error starting server: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="LinkedIn Profile Analyzer")
    parser.add_argument("--mode", choices=["console", "web"], default="web",
                        help="Run in console or web mode")
    args = parser.parse_args()

    if args.mode == "console":
        console_mode()
    else:
        web_mode()


if __name__ == "__main__":
    main()