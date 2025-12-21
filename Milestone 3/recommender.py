def generate_recommendations(study_hours, sleep_hours, social_media, exercise, attention):
    recommendations = []

    # 1. Study Hours Logic
    if study_hours < 4:
        recommendations.append(
            "📚 **Increase Study Time:** Your study hours are low. Try to reach at least 4-5 hours for better retention.")
    elif study_hours > 10:
        recommendations.append(
            "⚠️ **Avoid Burnout:** You are studying very long hours. Make sure to take breaks to maintain focus.")

    # 2. Sleep Logic
    if sleep_hours < 6:
        recommendations.append(
            "😴 **Sleep More:** You are sleeping less than 6 hours. Lack of sleep drastically reduces memory retention.")

    # 3. Social Media Logic
    if social_media > 3:
        recommendations.append(
            "📵 **Limit Distractions:** High social media usage (3+ hours) is linked to lower attention spans. Try using an app blocker.")

    # 4. Exercise Logic
    if exercise < 0.5:
        recommendations.append(
            "🏃 **Get Moving:** Even 30 minutes of walking can boost blood flow to the brain and improve focus.")

    # 5. Attention Logic
    if attention < 6:
        recommendations.append(
            "🧘 **Improve Focus:** Your reported attention level is low. Try the 'Pomodoro Technique' (25 min work, 5 min break).")

    # If they are perfect
    if len(recommendations) == 0:
        recommendations.append("🌟 **Great Job!** Your habits are balanced. Keep it up!")

    return recommendations


# --- TEST THE RECOMMENDER ---
print("--- TESTING ADVICE FOR A 'LAZY' STUDENT ---")
advice = generate_recommendations(study_hours=2, sleep_hours=5, social_media=5, exercise=0, attention=4)

for tip in advice:
    print(tip)