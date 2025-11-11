import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_skills_database():
    try:
        with open('skills_database.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    
def get_all_skills():
    database = load_skills_database()
    all_skills = []
    for field, skills in database.items():
        all_skills.extend(skills)
    return list(set(all_skills))




def extract_skills_from_text(text):
    all_skills = get_all_skills()
    detected_skills = []
    text_lower = text.lower()
    
    for skill in all_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            detected_skills.append(skill)
    return detected_skills


def calculate_similarity_score(job_desc, resume_text):
    job_desc_clean = re.sub(r'[^a-zA-Z0-9\s]', ' ', job_desc).lower()
    resume_clean = re.sub(r'[^a-zA-Z0-9\s]', ' ', resume_text).lower()
    
    vectorizer = TfidfVectorizer()
    try:
        vectors = vectorizer.fit_transform([job_desc_clean, resume_clean])
        similarity = cosine_similarity(vectors[0], vectors[1])
        return similarity[0][0] * 100
    except:
        return 0
    


def analyze_compatibility(job_description, resume_text):
    # Skills extract karo
    job_skills = extract_skills_from_text(job_description)
    resume_skills = extract_skills_from_text(resume_text)
    
    # Similarity score calculate karo
    similarity_score = calculate_similarity_score(job_description, resume_text)
    
    # Skills matching
    matched_skills = []
    missing_skills = []
    
    for skill in job_skills:
        if skill in resume_skills:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    skills_match_score = (len(matched_skills) / max(len(job_skills), 1)) * 50
    content_similarity_score = similarity_score * 0.5  # 50% weight
    
    total_score = min(skills_match_score + content_similarity_score, 100)
    
    return {
        'total_score': total_score,
        'similarity_score': similarity_score,
        'skills_match_score': skills_match_score,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'job_skills': job_skills,
        'resume_skills': resume_skills,
        'resume_length': len(resume_text)
    }