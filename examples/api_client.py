"""Example API client for SmartPDF-Science."""
import requests
from pathlib import Path
import time


API_URL = "http://localhost:8000"


def convert_pdf(pdf_path: str, output_format: str = "docx") -> str:
    """Convert PDF using API.
    
    Args:
        pdf_path: Path to PDF file
        output_format: Output format (docx, md, tex, html)
    
    Returns:
        Path to downloaded file
    """
    # Upload and convert
    with open(pdf_path, 'rb') as f:
        files = {'file': f}
        data = {'output_format': output_format}
        
        print(f"Uploading {pdf_path}...")
        response = requests.post(
            f"{API_URL}/convert",
            files=files,
            data=data
        )
        response.raise_for_status()
    
    result = response.json()
    job_id = result['job_id']
    
    print(f"Job ID: {job_id}")
    print(f"Status: {result['status']}")
    print(f"Pages: {result['pages']}")
    print(f"Processing time: {result['processing_time']:.1f}s")
    
    # Download result
    download_url = f"{API_URL}{result['download_url']}"
    print(f"\nDownloading from {download_url}...")
    
    response = requests.get(download_url)
    response.raise_for_status()
    
    # Save to file
    output_path = f"output/api_result.{output_format}"
    Path(output_path).write_bytes(response.content)
    
    print(f"✓ Saved to: {output_path}")
    return output_path


def main():
    print("=" * 50)
    print("SmartPDF-Science API Client Example")
    print("=" * 50)
    print()
    
    # Check API health
    print("Checking API...")
    response = requests.get(f"{API_URL}/health")
    if response.status_code == 200:
        print("✓ API is running\n")
    else:
        print("❌ API not available. Start it with: ./scripts/run_api.sh")
        return
    
    # Convert PDF
    pdf_path = "input_pdfs/sample.pdf"
    
    if not Path(pdf_path).exists():
        print(f"❌ {pdf_path} not found")
        return
    
    try:
        output_path = convert_pdf(pdf_path, output_format="docx")
        print(f"\n✅ Conversion successful!")
        print(f"Output: {output_path}")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()