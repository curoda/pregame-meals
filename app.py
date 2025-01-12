import streamlit as st
from openai import OpenAI

# Create the OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def prompt_model(messages):
    """
    Helper function to send a list of messages to the chat.completions API
    and return the model's response text.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # or "gpt-4o" as needed
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()


# -----------------------
# STEP 1: Get Macro Info
# -----------------------
def step_one_get_macros(activity, time_until):
    """
    1) Ask the model to recommend a macronutrient ratio (carbs, protein, fats)
       for a 17-year-old's pre-activity meal/snack, given the activity and time.
    2) Return only a short explanation in plain text (no disclaimers).
    """
    user_content = f"""
    You are a sports nutrition expert. 
    The athlete is 17, has only convenience stores or fast-food places available 
    (7-Eleven, McDonald’s, Chipotle), 
    and the upcoming activity is {activity} in {time_until} hours.

    What macronutrient ratio (carbs/protein/fats) do you recommend, and why?
    Return a short explanation in plain text, no disclaimers.
    """

    messages = [
        {"role": "developer", "content": "You are a concise, helpful nutrition coach."},
        {"role": "user", "content": user_content}
    ]
    return prompt_model(messages)


# --------------------------------------------------
# STEP 2A & 2B: Generate & Filter "Best" Foods
# --------------------------------------------------
def generate_best_candidates(macro_summary):
    """
    Prompt the model to create 20 candidate 'Best' items
    (bullet list, each with approximate macros).
    """
    user_content = f"""
    We have the following recommended macronutrient ratio: 
    {macro_summary}

    Step: Create a bullet list of 20 potential 'Best' food/drink items 
    for a 17-year-old (convenience stores / fast-food).
    - Each item should include approximate carbs/fats/protein percentages 
      in parentheses, e.g. (Carbs: 50, Fats: 20, Protein: 30).
    - No disclaimers.
    - Return only the bulleted list, 20 items total.
    """

    messages = [
        {"role": "developer", "content": "Generate 20 bullet-list items."},
        {"role": "user", "content": user_content}
    ]
    return prompt_model(messages)


def filter_best_candidates(macro_summary, candidate_text):
    """
    Prompt the model to:
    - Qualitatively check how each of the 20 items aligns with the macro ratio in macro_summary.
    - Keep only the 10 best matches.
    - Return them as a bulleted list of 10 items.
    """
    user_content = f"""
    We have these 20 'Best' candidate items (with approximate macros):
    {candidate_text}

    Our recommended macronutrient ratio is:
    {macro_summary}

    Now:
    1) Evaluate each item qualitatively for how closely it matches the recommended macros.
    2) Select the 10 closest matches (the best of the best).
    3) Return them as a bullet list of 10 items, no extra commentary.
    """

    messages = [
        {"role": "developer", "content": "Filter to 10 items that best match macros."},
        {"role": "user", "content": user_content}
    ]
    return prompt_model(messages)


# --------------------------------------------------
# STEP 3A & 3B: Generate & Filter "OK" Foods
# --------------------------------------------------
def generate_ok_candidates(macro_summary):
    """
    Prompt the model to create 20 candidate 'OK' items (bullet list).
    """
    user_content = f"""
    We have the following recommended macronutrient ratio:
    {macro_summary}

    Step: Create a bullet list of 20 'OK' food/drink items 
    for a 17-year-old (convenience stores / fast-food).
    - These items should be acceptable, but not as ideal as the 'Best' items.
    - Include approximate carbs/fats/protein percentages in parentheses.
    - Return only the bulleted list, 20 items total, no disclaimers.
    """

    messages = [
        {"role": "developer", "content": "Generate 20 'OK' bullet-list items."},
        {"role": "user", "content": user_content}
    ]
    return prompt_model(messages)


def filter_ok_candidates(macro_summary, candidate_text, best_list_text):
    """
    Prompt the model to:
    - Check that these items are not as good as the 'Best' items, but still somewhat healthy.
    - Keep the 10 healthiest among them.
    - Return as a bullet list of 10 items.
    """
    user_content = f"""
    We have these 20 'OK' candidate items:
    {candidate_text}

    Our recommended macronutrient ratio is:
    {macro_summary}

    The 'Best' list is:
    {best_list_text}

    Now:
    1) Evaluate each 'OK' item. Confirm it's not as ideal as the 'Best' list items.
    2) Choose the 10 healthiest from this 'OK' pool.
    3) Return them as a bullet list of 10 items, no extra commentary.
    """

    messages = [
        {"role": "developer", "content": "Filter to 10 items that are healthy but not as good as 'Best'."},
        {"role": "user", "content": user_content}
    ]
    return prompt_model(messages)


# --------------------------------------------------
# STEP 4A & 4B: Generate & Filter "Avoid" Foods
# --------------------------------------------------
def generate_avoid_candidates(macro_summary):
    """
    Prompt the model to create 20 candidate 'Avoid' items (bullet list).
    """
    user_content = f"""
    We have the following recommended macronutrient ratio:
    {macro_summary}

    Step: Create a bullet list of 20 'Avoid' food/drink items 
    for a 17-year-old with access to convenience stores or fast-food places.
    - These are not ideal for the upcoming activity.
    - Must include approximate carbs/fats/protein in parentheses.
    - Focus on items that are very commonly chosen by a 17-year-old 
      but conflict with the recommended macros.
    - Return only the bulleted list, 20 items total, no disclaimers.
    """

    messages = [
        {"role": "developer", "content": "Generate 20 'Avoid' bullet-list items."},
        {"role": "user", "content": user_content}
    ]
    return prompt_model(messages)


def filter_avoid_candidates(macro_summary, candidate_text):
    """
    Prompt the model to:
    - Confirm these items are very common for a 17-year-old, 
      but are not ideal given the recommended macros.
    - Select 10 that are the most likely to be chosen (yet poor choices).
    - Return them as a bullet list of 10 items, no extra commentary.
    """
    user_content = f"""
    We have these 20 'Avoid' candidate items:
    {candidate_text}

    Our recommended macronutrient ratio is:
    {macro_summary}

    Now:
    1) Evaluate each item as a poor choice for this scenario.
    2) Which 10 are most likely to be chosen by a 17-year-old 
       but still conflict with the recommended macros?
    3) Return them as a bullet list of 10 items, no extra commentary.
    """

    messages = [
        {"role": "developer", "content": "Select 10 'Avoid' items that are most tempting yet poor."},
        {"role": "user", "content": user_content}
    ]
    return prompt_model(messages)


# -----------------------
# Streamlit App
# -----------------------
def main():
    st.title("Pre-Activity Meal Recommendations")

    # Let user pick activity/time
    activities = ["basketball", "weightlifting", "pilates", "running", "swimming", "yoga"]
    activity = st.selectbox("Choose an activity", options=activities)
    time_until = st.slider("Hours until activity", 0.0, 3.0, 1.0, 0.25)

    if st.button("Get Recommendations"):
        with st.spinner("Determining ideal macro ratio..."):
            macro_explanation = step_one_get_macros(activity, time_until)
        
        # -----------------
        # BEST FOODS
        # -----------------
        with st.spinner("Generating 20 candidate 'Best' items..."):
            best_candidates_20 = generate_best_candidates(macro_explanation)
        with st.spinner("Filtering to 10 'Best' items..."):
            best_list_10 = filter_best_candidates(macro_explanation, best_candidates_20)

        # -----------------
        # OK FOODS
        # -----------------
        with st.spinner("Generating 20 candidate 'OK' items..."):
            ok_candidates_20 = generate_ok_candidates(macro_explanation)
        with st.spinner("Filtering to 10 'OK' items..."):
            ok_list_10 = filter_ok_candidates(macro_explanation, ok_candidates_20, best_list_10)

        # -----------------
        # AVOID FOODS
        # -----------------
        with st.spinner("Generating 20 candidate 'Avoid' items..."):
            avoid_candidates_20 = generate_avoid_candidates(macro_explanation)
        with st.spinner("Filtering to 10 'Avoid' items..."):
            avoid_list_10 = filter_avoid_candidates(macro_explanation, avoid_candidates_20)

        st.subheader("Recommended Macronutrient Ratio")
        st.write(macro_explanation)

        st.subheader("Best Foods (10)")
        st.markdown(best_list_10)

        st.subheader("OK Foods (10)")
        st.markdown(ok_list_10)

        st.subheader("Foods to Avoid (10)")
        st.markdown(avoid_list_10)

if __name__ == "__main__":
    main()
