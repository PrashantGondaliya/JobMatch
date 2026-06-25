import re


KNOWN_SKILLS = {
    "Python": ["python", "python3"],
    "FastAPI": ["fastapi", "fast api"],
    "Django": ["django"],
    "Flask": ["flask"],
    "SQL": ["sql", "postgresql", "postgres", "mysql", "sqlite"],
    "PostgreSQL": ["postgresql", "postgres"],
    "Docker": ["docker", "container", "containers", "containerization"],
    "Git": ["git", "github", "version control"],
    "REST APIs": ["rest api", "rest apis", "api", "apis"],
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure"],
    "GCP": ["gcp", "google cloud"],
    "JavaScript": ["javascript", "js"],
    "TypeScript": ["typescript", "ts"],
    "React": ["react", "react.js", "reactjs"],
    "Node.js": ["node.js", "nodejs", "node"],
    "Machine Learning": ["machine learning", "ml"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Excel": ["excel", "spreadsheet", "spreadsheets"],
    "Data Analysis": ["data analysis", "analytics", "data analytics"],
    "Kubernetes": ["kubernetes", "k8s"],
    "CI/CD": ["ci/cd", "continuous integration", "continuous deployment"],
}


def normalize_text(text: str) -> str:
    return text.lower()


def contains_skill_keyword(text: str, keyword: str) -> bool:
    pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
    return re.search(pattern, text) is not None


def extract_required_skills_from_text(text: str) -> list[str]:
    normalized_text = normalize_text(text)

    detected_skills = []

    for skill_name, keywords in KNOWN_SKILLS.items():
        for keyword in keywords:
            if contains_skill_keyword(normalized_text, keyword):
                detected_skills.append(skill_name)
                break

    return detected_skills