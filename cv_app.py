import streamlit as stui
import pandas as pd
import plotly.express as px
from resume_parser import extract_text
from similarity_checker import analyze_compatibility

stui.set_page_config(
    page_title="Smart Resume Screener",
    page_icon="📄",
    layout="wide"
)


stui.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
    }
    .skill-match {
        background-color: #d4edda;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem;
    }
    .skill-missing {
        background-color: #f8d7da;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    stui.markdown('<h1 class="main-header">🤖 AI-Powered Resume Analyzer</h1>', unsafe_allow_html=True)
    stui.markdown("### Upload resume and job description to get compatibility analysis")

    col1, col2 =stui.columns([1,1])

    with col1:
        stui.header("Job Description")
        job_discrip=stui.text_area(
            "Paste the Job Description Below",
            height=200,
            placeholder="Example: We’re looking for an AI Developer skilled in Python, NLP, and Machine Learning...",
            help="Copy and paste the complete job description here."
        )

    with col2:
        stui.header("📂 Upload Your Resume")
        uploaded_file=stui.file_uploader(
        "Upload Your Resume Here",
        type=['pdf','docx'],
        help="Supported formats: PDF, DOCX. Maximum file size: 10MB"
        )

        if uploaded_file:
            file_details={
                "File Name":uploaded_file.name,
                "File size": f"{uploaded_file.size / 1024:.2f} KB",
                "File type": uploaded_file.type
            }
            stui.success("✅ Resume uploaded successfully!")
            stui.write(file_details)

    if stui.button("🚀 Analyze My Resume", type="primary", use_container_width=True):
        if not job_discrip:
            stui.error("⚠️ Please enter the job description before analyzing.")
            return
        
        if not uploaded_file:
            stui.error("⚠️ Please upload your resume file.")
            return
        
        with stui.spinner("⏳ Analyzing your resume and generating the compatibility report..."):
            resume_text=extract_text(uploaded_file)

            if "Error" in resume_text:
                stui.error(f"{resume_text}")
                return
            
            cv_result=analyze_compatibility(job_discrip,resume_text)

            display_results(cv_result)



def display_results(result):
    stui.markdown("---")
    stui.markdown("## 📊 Analysis Results")
    
    # Score cards
    col1, col2, col3, col4 = stui.columns(4)
    
    with col1:
        stui.markdown('<div class="score-card">', unsafe_allow_html=True)
        stui.metric("Overall Score", f"{result['total_score']:.1f}%")
        stui.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        stui.metric("Content Similarity", f"{result['similarity_score']:.1f}%")
    
    with col3:
        stui.metric("Skills Match", f"{result['skills_match_score']:.1f}%")
    
    with col4:
        stui.metric("Resume Length", f"{result['resume_length']} chars")
    
    
    stui.progress(int(result['total_score']))
    
    col1, col2 = stui.columns(2)
    
    with col1:
        stui.subheader("✅ Job Requirements")
        if result['job_skills']:
            for skill in result['job_skills']:
                stui.markdown(f'<div class="skill-match">✓ {skill.title()}</div>', unsafe_allow_html=True)
        else:
            stui.info("No specific skills detected in job description")
        
        stui.subheader("✅ Skills Found in Resume")
        if result['matched_skills']:
            for skill in result['matched_skills']:
                stui.markdown(f'<div class="skill-match">✓ {skill.title()}</div>', unsafe_allow_html=True)
        else:
            stui.info("No matching skills found")
    
    with col2:
        stui.subheader("📋 Resume Skills")
        if result['resume_skills']:
            for skill in result['resume_skills'][:10]:  # Show first 10
                stui.write(f"• {skill.title()}")
            if len(result['resume_skills']) > 10:
                stui.info(f"+ {len(result['resume_skills']) - 10} more skills")
        else:
            stui.info("No skills detected in resume")
        
        stui.subheader("❌ Missing Skills")
        if result['missing_skills']:
            for skill in result['missing_skills']:
                stui.markdown(f'<div class="skill-missing">✗ {skill.title()}</div>', unsafe_allow_html=True)
        else:
            stui.success("🎉 All required skills found!")
    
    with stui.expander("📈 Detailed Analysis"):
        col1, col2 = stui.columns(2)
        
        with col1:
            stui.write("**Skills Distribution**")
            skills_data = {
                'Category': ['Matched', 'Missing', 'Extra'],
                'Count': [
                    len(result['matched_skills']),
                    len(result['missing_skills']),
                    len(result['resume_skills']) - len(result['matched_skills'])
                ]
            }
            df = pd.DataFrame(skills_data)
            fig = px.pie(df, values='Count', names='Category', title='Skills Distribution')
            stui.plotly_chart(fig)
        
        with col2:
            stui.write("**Score Breakdown**")
            score_data = {
                'Component': ['Content Similarity', 'Skills Match'],
                'Score': [result['similarity_score'], result['skills_match_score']]
            }
            df_scores = pd.DataFrame(score_data)
            fig_bar = px.bar(df_scores, x='Component', y='Score', title='Score Components')
            stui.plotly_chart(fig_bar)
    
    report_text = f"""
    RESUME COMPATIBILITY REPORT
    ===========================
    
    Overall Score: {result['total_score']:.1f}%
    Content Similarity: {result['similarity_score']:.1f}%
    Skills Match: {result['skills_match_score']:.1f}%
    
    JOB REQUIREMENTS:
    {', '.join(result['job_skills'])}
    
    MATCHED SKILLS:
    {', '.join(result['matched_skills'])}
    
    MISSING SKILLS:
    {', '.join(result['missing_skills'])}
    
    RESUME SKILLS:
    {', '.join(result['resume_skills'])}
    """
    
    stui.download_button(
        label="📥 Download Detailed Report",
        data=report_text,
        file_name="resume_analysis_report.txt",
        mime="text/plain"
    )

if __name__=="__main__":
    main()