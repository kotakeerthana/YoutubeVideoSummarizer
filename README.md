#  YouTube Video Summarizer with Gemini Pro

An AI-powered web app that summarizes YouTube videos into digestible insights - powered by Google's Gemini 1.5 Pro.

This project was designed to mimic the feel of a handwritten notebook while giving users the power of LLMs, right in the browser.

---

# Features

-  Extracts transcript from YouTube videos
-  Summarizes video using Gemini 1.5 Pro:
  - TL;DR
  - Bullet Points
  - Detailed Summary
  - Key Takeaways
  - Translations (Hindi, Spanish, French, Telugu, German)
  - Keyword Extraction
  - Related Article Suggestions with links
-  Ask questions directly to Gemini about the video
-  Download your summary as:
  - TXT
  - PDF (Unicode-safe)
  - Word (.docx)


---


# Tech Stack

- Streamlit
- Google Generative AI SDK (`gemini-pro`)
- YouTube Transcript API
- FPDF (PDF generation)
- Python 3.10

---

##   Run Locally

```bash
git clone https://github.com/kotakeerthana/YoutubeVideoSummarizer.git
cd YoutubeVideoSummarizer
pip install -r requirements.txt
streamlit run app.py
