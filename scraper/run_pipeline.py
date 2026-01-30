"""
Complete Scraping and Indexing Pipeline

Runs the entire pipeline:
1. Scrape Hermes products
2. Download images to S3
3. Push to Coveo
"""

import sys
import subprocess
from datetime import datetime


def run_script(script_name, description):
    """Run a Python script and handle errors"""
    print("\n" + "="*70)
    print(f"STEP: {description}")
    print("="*70)
    print(f"Running: {script_name}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            capture_output=False,
            text=True
        )
        
        print("\n" + "="*70)
        print(f"✅ {description} - COMPLETED")
        print("="*70)
        return True
        
    except subprocess.CalledProcessError as e:
        print("\n" + "="*70)
        print(f"❌ {description} - FAILED")
        print("="*70)
        print(f"Error: {e}")
        return False
    except Exception as e:
        print("\n" + "="*70)
        print(f"❌ {description} - ERROR")
        print("="*70)
        print(f"Error: {e}")
        return False


def main():
    """Run complete pipeline"""
    print("\n" + "="*70)
    print("HERMES SCRAPING AND INDEXING PIPELINE")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    steps = [
        ('hermes_scraper.py', 'Scrape Hermes Products'),
        ('metadata_enricher.py', 'Enrich Product Metadata'),
        ('image_downloader.py', 'Download Images to S3'),
        ('coveo_indexer.py', 'Push to Coveo'),
    ]
    
    results = {}
    
    for script, description in steps:
        success = run_script(script, description)
        results[description] = success
        
        if not success:
            print(f"\n⚠️  Pipeline stopped at: {description}")
            print("Please fix the errors and run again.")
            break
    
    # Print final summary
    print("\n" + "="*70)
    print("PIPELINE SUMMARY")
    print("="*70)
    
    for step, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status}: {step}")
    
    print("="*70)
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    if all(results.values()):
        print("\n🎉 All steps completed successfully!")
        print("\nNext steps:")
        print("  1. Wait 1-2 minutes for Coveo to index")
        print("  2. Run embedding generator:")
        print("     cd ../backend/embedding_generator")
        print("     python generate_embeddings.py")
        print("  3. Test the search UI")
    else:
        print("\n⚠️  Some steps failed. Please check the errors above.")


if __name__ == '__main__':
    main()
