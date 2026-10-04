import pandas as pd
import uuid
import random
import os
import json

def generate_synthetic_data(num_samples_per_intent=1000):
    templates = {
        "admissions_applications": {
            "queries": [
                "What is the deadline for {program} applications?",
                "How do I apply for the {program} program?",
                "What are the admission requirements for {program}?",
                "Can you tell me the application fee for {program}?",
                "When will I hear back about my {program} admission?",
                "Is there an entrance exam for {program}?"
            ],
            "programs": ["B.Tech", "M.Tech", "Ph.D", "MBA", "undergrad", "grad"]
        },
        "financial_aid_scholarships": {
            "queries": [
                "How do I apply for {aid_type}?",
                "What are the criteria for the {aid_type}?",
                "Is {aid_type} available for international students?",
                "When is the deadline to submit the {aid_type} application?",
                "Who do I contact regarding my {aid_type} status?"
            ],
            "programs": ["financial aid", "merit scholarship", "student loan", "tuition waiver", "need-based grant"]
        },
        "campus_life_housing": {
            "queries": [
                "How do I apply for {housing}?",
                "What are the fees for {housing}?",
                "Are freshmen required to live in {housing}?",
                "Can you tell me about the {facility} facilities?",
                "What are the timings for the {facility}?"
            ],
            "programs": ["on-campus housing", "hostel", "dorms", "married student housing"],
            "facilities": ["dining hall", "gym", "recreation center", "library", "student union"]
        },
        "placements_career_services": {
            "queries": [
                "When does the {event} start?",
                "How do I register for {event}?",
                "Which companies come for {event}?",
                "Can the career center help me with my {doc}?",
                "Where is the {doc} review session held?"
            ],
            "programs": ["campus placements", "internship drive", "career fair", "on-campus recruiting"],
            "docs": ["resume", "cover letter", "portfolio", "interview prep"]
        }
    }

    responses = {
        "admissions_applications": "Admissions information including deadlines, requirements, and fees can be found on the university admissions portal.",
        "financial_aid_scholarships": "Financial aid and scholarship details, eligibility criteria, and deadlines are available at the Financial Aid Office website.",
        "campus_life_housing": "Details regarding housing applications, fees, and campus facilities (like dining and gym) are managed by the Office of Student Life.",
        "placements_career_services": "Career services, placement drives, and resume reviews are coordinated through the University Career Center."
    }

    new_data = []
    
    for intent, config in templates.items():
        for _ in range(num_samples_per_intent):
            template = random.choice(config["queries"])
            # Replace placeholders
            if "{program}" in template:
                query = template.replace("{program}", random.choice(config["programs"]))
            elif "{aid_type}" in template:
                query = template.replace("{aid_type}", random.choice(config["programs"]))
            elif "{housing}" in template:
                query = template.replace("{housing}", random.choice(config["programs"]))
            elif "{facility}" in template:
                query = template.replace("{facility}", random.choice(config.get("facilities", [])))
            elif "{event}" in template:
                query = template.replace("{event}", random.choice(config["programs"]))
            elif "{doc}" in template:
                query = template.replace("{doc}", random.choice(config.get("docs", [])))
            else:
                query = template
                
            row = {
                "id": "synthetic_" + str(uuid.uuid4())[:8],
                "query": query,
                "intent": intent,
                "response": responses[intent],
                "document_id": "doc_synthetic_" + intent,
                "document_version": "v1.0",
                "evidence": "Synthetic generation for dataset augmentation",
                "entities": "{}",
                "answerable": True,
                "difficulty": "easy",
                "split": "train",
                "source_authority": "generated",
                "provenance": "Synthetic rules-based generation"
            }
            new_data.append(row)
            
    return pd.DataFrame(new_data)


def main():
    print("Loading existing datasets...")
    df_18k_path = "data/real_world_university_queries.csv"
    df_50k_path = "CampusFAQ-50K-v1.0/data/campusfaq_50k_v1.0.csv"
    
    df1 = pd.read_csv(df_18k_path) if os.path.exists(df_18k_path) else pd.DataFrame()
    df2 = pd.read_csv(df_50k_path) if os.path.exists(df_50k_path) else pd.DataFrame()
    
    df_merged = pd.concat([df1, df2], ignore_index=True)
    print(f"Total rows before cleaning: {len(df_merged)}")
    
    # 1. Clean data: Drop exact duplicate queries (case insensitive)
    df_merged['query_lower'] = df_merged['query'].str.lower().str.strip()
    df_merged = df_merged.drop_duplicates(subset=['query_lower'])
    
    # 2. Clean data: Remove very short queries (less than 3 words) unless it's a greeting/thanks
    def is_valid(row):
        words = str(row['query']).split()
        if len(words) < 3 and row['intent'] not in ['greeting', 'thanks']:
            return False
        return True
        
    df_merged = df_merged[df_merged.apply(is_valid, axis=1)]
    df_merged = df_merged.drop(columns=['query_lower'])
    
    print(f"Total rows after cleaning: {len(df_merged)}")
    
    # 3. Augment data
    print("Generating synthetic data for missing topics...")
    df_synthetic = generate_synthetic_data(num_samples_per_intent=2000)
    
    df_final = pd.concat([df_merged, df_synthetic], ignore_index=True)
    # Shuffle dataset
    df_final = df_final.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"Total rows in FINAL augmented dataset: {len(df_final)}")
    
    # Save the cleaned and augmented dataset
    out_path = "data/university_faq_cleaned_augmented.csv"
    df_final.to_csv(out_path, index=False)
    print(f"Successfully saved new dataset to {out_path}")

if __name__ == '__main__':
    main()
