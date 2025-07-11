"""
LinkedIn Profile Analyzer - Main Application
Orchestrates the scraping and analysis process
"""

import os
import sys
import logging
import argparse
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from scraper import scrape_linkedin_profile
from summarizer import ProfileAnalyzer, analyze_profile
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
    print("LinkedIn Profile Analyzer - Console Mode")
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
        print(f"Headline: {profile_data.get('headline', 'Unknown')}\n")
        print(f"About: {profile_data.get('about','Unknown')}\n")
        print(f"Skills: {profile_data.get('skills','Unknown')}\n")
        print(f"Experience: {profile_data.get('experience','Unknown')}\n")
        
        # Show available analysis modes
        print("\n📊 Available Analysis Modes:")
        print("1. Bio - Generate a professional LinkedIn bio")
        print("2. Tell me about this Profile - Create a networking summary for recruiters")
        print("3. Analysis - Comprehensive profile analysis with strengths/gaps")
        
        # Get user choice
        while True:
            choice = input("\nSelect analysis mode (1-3) or 'all' for all modes: ").strip().lower()
            
            if choice == '1':
                mode = 'bio'
                break
            elif choice == '2':
                mode = 'summary'
                break
            elif choice == '3':
                mode = 'analysis'
                break
            elif choice == 'all':
                mode = 'all'
                break
            else:
                print("❌ Invalid choice. Please select 1, 2, 3, or 'all'")
        
        # Generate analysis
        if mode == 'all':
            print("\n🤖 Generating all analysis types...")
            modes = ['bio', 'summary', 'analysis']
            
            for analysis_mode in modes:
                print(f"\n🔄 Generating {analysis_mode}...")
                result = analyze_profile(profile_data, analysis_mode)
                
                if not result or result.get('error'):
                    print(f"\n❌ Failed to generate {analysis_mode}")
                    continue
                
                print(f"\n{'=' * 60}")
                print(f"{analysis_mode.upper()}")
                print("=" * 60)
                print(result['result'])
                print("=" * 60)
        else:
            mode_names = {'bio': 'Bio', 'summary': 'Summary', 'analysis': 'Analysis'}
            print(f"\n🤖 Generating {mode_names[mode]}...")
            
            result = analyze_profile(profile_data, mode)
            
            if not result or result.get('error'):
                print(f"\n❌ Failed to generate {mode}")
                return
            
            print(f"\n{'=' * 60}")
            print(f"{mode_names[mode].upper()}")
            print("=" * 60)
            print(result['result'])
            print("=" * 60)
        
        # Ask if user wants to save the result
        save_result = input("\nWould you like to save the result to a file? (y/n): ").lower().strip()
        
        if save_result == 'y':
            try:
                analyzer = ProfileAnalyzer()
                if mode == 'all':
                    # Save all results
                    for analysis_mode in modes:
                        result = analyze_profile(profile_data, analysis_mode)
                        if result and not result.get('error'):
                            filename = analyzer.save_result(result)
                            if filename:
                                print(f"✅ {analysis_mode.capitalize()} saved to: {filename}")
                else:
                    filename = analyzer.save_result(result)
                    if filename:
                        print(f"✅ Result saved to: {filename}")
            except Exception as e:
                print(f"❌ Error saving file: {str(e)}")
        
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
    
    @app.route('/analyze', methods=['POST'])
    def analyze():
        """Handle profile analysis request"""
        try:
            profile_url = request.form.get('profile_url', '').strip()
            analysis_mode = request.form.get('analysis_mode', 'bio')
            
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
                    'about': 'Passionate software engineer with 5+ years of experience in full-stack development, specializing in Python, JavaScript, and cloud technologies. I love building scalable applications and mentoring junior developers.',
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
                profile_data = scrape_linkedin_profile(profile_url, headless=False)
                
                if not profile_data:
                    flash('Failed to scrape profile data. Please check the URL and try again.', 'error')
                    return redirect(url_for('index'))
            
            # Generate analysis
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
    
    @app.route('/api/analyze', methods=['POST'])
    def api_analyze():
        """API endpoint for profile analysis"""
        try:
            data = request.get_json()
            profile_url = data.get('profile_url', '').strip()
            analysis_mode = data.get('analysis_mode', 'bio')
            
            if not profile_url:
                return jsonify({'error': 'Profile URL is required'}), 400
            
            if not GEMINI_API_KEY:
                return jsonify({'error': 'Gemini API key not configured'}), 500
            
            # Scrape profile
            profile_data = scrape_linkedin_profile(profile_url, headless=False)
            
            if not profile_data:
                return jsonify({'error': 'Failed to scrape profile data'}), 400
            
            # Generate analysis
            analysis_result = analyze_profile(profile_data, analysis_mode)
            
            if not analysis_result or analysis_result.get('error'):
                return jsonify({'error': 'Failed to generate analysis'}), 500
            
            return jsonify({
                'success': True,
                'profile_data': profile_data,
                'analysis': analysis_result
            })
            
        except Exception as e:
            logger.error(f"Error in API route: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    return app


def run_flask_mode():
    """Run the application in Flask web mode"""
    print("=" * 60)
    print("LinkedIn Profile Analyzer - Web Mode")
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
    parser = argparse.ArgumentParser(description="LinkedIn Profile Analyzer")
    parser.add_argument("--mode", choices=["console", "web"], default="web",
                        help="Run in console or web mode")
    args = parser.parse_args()

    if args.mode == "console":
        run_console_mode()
    else:
        run_flask_mode()


if __name__ == "__main__":
    main()