output = [
    {
        "question": "What is the average engagement rate for the account aldi nord in 2023?",
        "table_name": "instagram_account_kpi"
    },
    {
        "question": "What types of posts does aldi nord publish, and how does the engagement vary by post type in 2023?",
        "table_name": "instagram_userfeed"
    },
    {
        "question": "What has been the follower growth trend for aldi nord throughout 2023?",
        "table_name": "instagram_follower_development"
    },
    {
        "question": "How often has aldi nord been tagged by influencers in posts, and what is the average engagement rate for these influencer tags in 2023?",
        "table_name": "instagram_influencer_tags"
    },
    {
        "question": "What are the demographic characteristics of aldi nord's Instagram audience in 2023?",
        "table_name": "instagram_audience_demographics"
    }
]

# Extract questions
data_queries = [item["question"] for item in output]

# Print questions in list format
print("\n- " + "\n- ".join(data_queries))
