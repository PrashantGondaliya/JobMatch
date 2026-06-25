import html
import re

import httpx

from app.schemas.job import JobCreate
from app.services.skill_extraction import extract_required_skills_from_text


GREENHOUSE_BASE_URL = "https://boards-api.greenhouse.io/v1/boards"


class GreenhouseConnectorError(Exception):
    pass


def clean_html_content(raw_content: str | None) -> str:
    if not raw_content:
        return "No description provided."

    unescaped_content = html.unescape(raw_content)

    without_tags = re.sub(r"<[^>]+>", " ", unescaped_content)

    cleaned_content = re.sub(r"\s+", " ", without_tags).strip()

    return cleaned_content or "No description provided."


def get_location_name(job_data: dict) -> str:
    location = job_data.get("location") or {}

    if isinstance(location, dict):
        return location.get("name") or "Not specified"

    return "Not specified"


def infer_remote_type(text: str, location: str) -> str:
    combined_text = f"{text} {location}".lower()

    if "remote" in combined_text:
        return "remote"

    if "hybrid" in combined_text:
        return "hybrid"

    if "on-site" in combined_text or "onsite" in combined_text:
        return "onsite"

    return "not_specified"


def normalize_greenhouse_job(
    job_data: dict,
    company_slug: str,
) -> JobCreate:
    title = job_data.get("title") or "Untitled role"
    company = company_slug.replace("-", " ").title()
    location = get_location_name(job_data)
    description = clean_html_content(job_data.get("content"))
    apply_url = job_data.get("absolute_url") or ""

    combined_text_for_skills = f"{title} {description}"
    required_skills = extract_required_skills_from_text(combined_text_for_skills)

    remote_type = infer_remote_type(
        text=description,
        location=location,
    )

    return JobCreate(
        title=title,
        company=company,
        location=location,
        remote_type=remote_type,
        employment_type="full_time",
        description=description,
        apply_url=apply_url,
        source=f"greenhouse:{company_slug}",
        required_skills=required_skills,
        salary_min=None,
        salary_max=None,
    )


def fetch_greenhouse_jobs(company_slug: str) -> list[JobCreate]:
    url = f"{GREENHOUSE_BASE_URL}/{company_slug}/jobs"

    try:
        response = httpx.get(
            url,
            params={"content": "true"},
            timeout=15.0,
        )

        response.raise_for_status()

    except httpx.HTTPStatusError as error:
        raise GreenhouseConnectorError(
            f"Greenhouse returned status {error.response.status_code} "
            f"for company slug '{company_slug}'."
        ) from error

    except httpx.RequestError as error:
        raise GreenhouseConnectorError(
            f"Could not connect to Greenhouse for company slug '{company_slug}'."
        ) from error

    data = response.json()

    raw_jobs = data.get("jobs", [])

    return [
        normalize_greenhouse_job(
            job_data=job_data,
            company_slug=company_slug,
        )
        for job_data in raw_jobs
    ]