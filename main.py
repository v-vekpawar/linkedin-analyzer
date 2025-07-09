"""
LinkedIn Profile Summarizer - Main Application
Orchestrates the scraping and summarization process
"""

import os
import sys
import logging
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from scraper import scrape_linkedin_profile
from summarizer import ProfileSummarizer, summarize_profile
from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG, GEMINI_API_KEY

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_console_mode():
    """Run the application in console mode"""
    print("=" * 60)
    print("LinkedIn Profile Summarizer - Console Mode")
    print("=" * 60)
    
    # Check if Gemini API key is available
    if not GEMINI_API_KEY:
        print("❌ Error: Gemini API key not found!")
        print("Please set your GEMINI_API_KEY in the .env file or config.py")
        print("Get your API key from: https://aistudio.google.com/app/apikey")
        return
    
    print("✅ Gemini API key found")
    
    # Get LinkedIn profile URL
    profile_url = input("\nEnter LinkedIn profile URL: ").strip()
    
    if not profile_url:
        print("❌ No profile URL provided")
        return
    
    if "linkedin.com/in/" not in profile_url:
        print("\n❌ Invalid LinkedIn profile URL. Please provide a valid LinkedIn profile URL.\n")
        return
    
    print(f"\n🔍 Scraping profile: {profile_url}")
    print("\nNote: You will need to log in to LinkedIn manually when the browser opens.\n")
    
    # Scrape the profile
    try:
        profile_data = scrape_linkedin_profile(profile_url, headless=False)
        
        if not profile_data:
            print("\n\n\t\t❌ Failed to scrape profile data\n\n")
            return
        
        print("\n\n\t\t✅ Profile data scraped successfully!\n")
        print(f"Name: {profile_data.get('name', 'Unknown')}")
        print(f"Headline: {profile_data.get('headline', 'Unknown')}")
        
        # Generate summary
        print("\n\n\t\t🤖 Generating professional summary...")
        summary_result = summarize_profile(profile_data, "professional")
        
        if not summary_result or summary_result.get('error'):
            print("\n\n\t\t❌ Failed to generate summary\n\n")
            return
        
        print("\n" + "=" * 60)
        print("PROFESSIONAL SUMMARY")
        print("=" * 60)
        print(summary_result['summary'])
        print("=" * 60)
        
        # Ask if user wants to generate other types of summaries
        generate_more = input("\nWould you like to generate executive and casual summaries? (y/n): ").lower().strip()
        
        if generate_more == 'y':
            summarizer = ProfileSummarizer()
            all_summaries = summarizer.generate_multiple_summaries(profile_data)
            
            for summary_type, result in all_summaries.items():
                if not result.get('error'):
                    print(f"\n{summary_type.upper()} SUMMARY:")
                    print("-" * 40)
                    print(result['summary'])
                    print("-" * 40)
        
        # Ask if user wants to save the summary
        save_summary = input("\nWould you like to save the summary to a file? (y/n): ").lower().strip()
        
        if save_summary == 'y':
            summarizer = ProfileSummarizer()
            filename = summarizer.save_summary_to_file(summary_result)
            if filename:
                print(f"✅ Summary saved to: {filename}")
        
        print("\n\n\t\t🎉 Process completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        logger.error(f"Error in console mode: {str(e)}")


def create_flask_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    
    @app.route('/')
    def index():
        """Main page"""
        return render_template('index.html')
    
    @app.route('/summarize', methods=['POST'])
    def summarize():
        """Handle profile summarization request"""
        try:
            profile_url = request.form.get('profile_url', '').strip()
            summary_type = request.form.get('summary_type', 'professional')
            
            use_sample = 'use_sample' in request.form
            
            if not use_sample:
                if not profile_url:
                    flash('Please provide a LinkedIn profile URL', 'error')
                    return redirect(url_for('index'))
                if "linkedin.com/in/" not in profile_url:
                    flash('Please provide a valid LinkedIn profile URL', 'error')
                    return redirect(url_for('index'))
            
            if not GEMINI_API_KEY:
                flash('Gemini API key not configured. Please check your configuration.', 'error')
                return redirect(url_for('index'))
            
            # Check if user wants to use sample data (for testing without scraping)
            if use_sample:
                # Use sample data for testing
                profile_data = {
                    'name': 'John Doe',
                    'headline': 'Senior Software Engineer at Tech Company',
                    'about': 'Passionate software engineer with 5+ years of experience in full-stack development, specializing in Python, JavaScript, and cloud technologies.',
                    'experience': [
                        {'title': 'Senior Software Engineer', 'company': 'Tech Corp'},
                        {'title': 'Software Engineer', 'company': 'Startup Inc'},
                        {'title': 'Junior Developer', 'company': 'Web Solutions'}
                    ],
                    'skills': ['Python', 'JavaScript', 'React', 'Node.js', 'AWS', 'Docker', 'Git', 'SQL', 'MongoDB', 'REST APIs'],
                    'url': profile_url
                }
                flash('Using sample data for demonstration', 'info')
            else:
                # Scrape the actual profile - use headless=False for web mode so users can see the browser
                flash('Starting profile scraping. A browser window will open for LinkedIn login...', 'info')
                profile_data = scrape_linkedin_profile(profile_url, headless=False)
                
                if not profile_data:
                    flash('Failed to scrape profile data. Please check the URL and try again.', 'error')
                    return redirect(url_for('index'))
            
            # Generate summary
            summary_result = summarize_profile(profile_data, summary_type)
            
            if not summary_result or summary_result.get('error'):
                flash('Failed to generate summary. Please check your Gemini API key.', 'error')
                return redirect(url_for('index'))
            
            return render_template('result.html', 
                                profile_data=profile_data, 
                                summary_result=summary_result)
            
        except Exception as e:
            logger.error(f"Error in Flask route: {str(e)}")
            flash(f'An error occurred: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    @app.route('/api/summarize', methods=['POST'])
    def api_summarize():
        """API endpoint for profile summarization"""
        try:
            data = request.get_json()
            profile_url = data.get('profile_url', '').strip()
            summary_type = data.get('summary_type', 'professional')
            
            if not profile_url:
                return jsonify({'error': 'Profile URL is required'}), 400
            
            if not GEMINI_API_KEY:
                return jsonify({'error': 'Gemini API key not configured'}), 500
            
            # Scrape profile
            profile_data = scrape_linkedin_profile(profile_url, headless=False)
            
            if not profile_data:
                return jsonify({'error': 'Failed to scrape profile data'}), 400
            
            # Generate summary
            summary_result = summarize_profile(profile_data, summary_type)
            
            if not summary_result or summary_result.get('error'):
                return jsonify({'error': 'Failed to generate summary'}), 500
            
            return jsonify({
                'success': True,
                'profile_data': profile_data,
                'summary': summary_result
            })
            
        except Exception as e:
            logger.error(f"Error in API route: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    return app


def run_flask_mode():
    """Run the application in Flask web mode"""
    print("=" * 60)
    print("LinkedIn Profile Summarizer - Web Mode")
    print("=" * 60)
    
    if not GEMINI_API_KEY:
        print("❌ Error: Gemini API key not found!")
        print("Please set your GEMINI_API_KEY in the .env file or config.py")
        return
    
    print("✅ Gemini API key found")
    print(f"🌐 Starting web server at http://{FLASK_HOST}:{FLASK_PORT}")
    print("Press Ctrl+C to stop the server")
    
    app = create_flask_app()
    
    try:
        app.run(
            host=FLASK_HOST,
            port=FLASK_PORT,
            debug=FLASK_DEBUG
        )
    except KeyboardInterrupt:
        print("\n\n⚠️ Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {str(e)}")


def main():
    """Main entry point"""
    print("LinkedIn Profile Summarizer")
    print("Choose your mode:")
    print("1. Console Mode (Interactive)")
    print("2. Web Mode (Flask)")
    
    try:
        choice = input("Enter your choice (1 or 2): ").strip()
        
        if choice == "1":
            run_console_mode()
        elif choice == "2":
            run_flask_mode()
        else:
            print("Invalid choice. Please run the script again and choose 1 or 2.")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Application interrupted by user")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        logger.error(f"Error in main: {str(e)}")


if __name__ == "__main__":
    main() 