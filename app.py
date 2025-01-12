import json
import streamlit as st
from openai import OpenAI

# Set up the OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def prompt_model(messages):
    """
    Helper function to send a list of messages to the model 
    and return the model's text response.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # or "gpt-4o", adjust as needed
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def step_one_get_macros(activity, time_until):
    """
    Step 1: Derive recommended macronutrient ratio given:
      - The specific activity
      - The time until that activity
    Returns a short paragraph of text describing the ideal ratios 
    and why they make sense for this scenario.
    """
    user_msg = f"""
    You are a sports nutrition expert. 
    The athlete is 17 years old, with only convenience stores 
    (e.g., 7-Eleven) or fast-food places (e.g., McDonald’s, Chipotle) available.
    The upcoming activity is {activity}, starting in {time_until} hours.
    Based on this scenario, 
    1) What macronutrient ratio (carbs/protein/fats) do you recommend 
       for a pre-activity meal/snack?
    2) Why is that ratio beneficial?
    Return only a short paragraph of plain text.
    No extra commentary or disclaimers.
    """

    messages = [
        {"role": "developer", "content": "You are a concise, helpful nutrition coach."},
        {"role": "user", "content": user_msg}
    ]
    return prompt_model(messages)

def step_two_generate_candidates():
    """
    Step 2: Generate a broad set of ~30 food/drink items 
    that might be found at convenience stores or fast-food chains.
    Return them as plain text (one item per line or comma separated).
    """
    user_msg = """
    Generate a list of 30 foods or drinks that might be found at 7-Eleven, 
    McDonald’s, Chipotle, or similar fast-food/convenience places. 
    No need for macronutrient data yet. 
    Just provide item names or short descriptions (plain text).
    """
    messages = [
        {"role": "developer", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_msg}
    ]
    return prompt_model(messages)

def step_three_categorize_items(candidate_list, macro_text):
    """
    Step 3: For each candidate item:
       - Estimate approximate carbs/fats/protein percentages 
         given the macro guidance from 'macro_text'.
       - Categorize each item as 'Best', 'OK', or 'Avoid' 
         for a pre-activity meal/snack.
    Return a structured text (or JSON) with each item, macros, and category.
    """
    user_msg = f"""
    We have these items: {candidate_list}.
    The recommended macronutrient ratio (from step one) is:
    {macro_text}.

    For each item, do the following:
     1) Estimate approximate carbs/fats/protein percentages 
        (just a best guess).
     2) Label each item as 'Best', 'OK', or 'Avoid' for this pre-activity scenario.

    Return the result in a structured format (you can use a bullet list or JSON),
    but keep it concise—no extra disclaimers.
    """
    messages = [
        {"role": "developer", "content": "Categorize items with approximate macros."},
        {"role": "user", "content": user_msg}
    ]
    return prompt_model(messages)

def step_four_final_json(categorized_info):
    """
    Step 4: Produce valid JSON with these keys:
      - 'best_foods' (15 items)
      - 'ok_foods' (15 items)
      - 'foods_to_avoid' (15 items)
      - 'do_eat' (short text about the recommended macro approach)
      - 'avoid' (short text about what to avoid)

    The user might not want disclaimers, so strictly return only JSON with those five keys.
    """
    user_msg = f"""
    Based on the categorized items below:

    {categorized_info}

    Create valid JSON with exactly five keys:
      - best_foods (array of 15 items)
      - ok_foods (array of 15 items)
      - foods_to_avoid (array of 15 items)
      - do_eat (short text)
      - avoid (short text)

    If you have fewer than 15 items in a category, fill with "N/A" 
    or similar placeholders, but make sure each array has exactly 15 strings.

    No extra commentary, disclaimers, or text outside the JSON. 
    Only the five keys listed above.
    """
    messages = [
        {"role": "developer", "content": "Produce the final JSON with 5 keys."},
        {"role": "user", "content": user_msg}
    ]
    return prompt_model(messages)

def main():
    st.title("Pre-Activity Nutrition Guide (Multi-step Approach)")

    # Step 0: User input
    activities = ["basketball", "weightlifting", "pilates", "running", "swimming", "yoga"]
    activity = st.selectbox("Choose an activity", options=activities)
    time_until = st.slider("Hours until activity", 0.0, 3.0, 1.0, 0.25)

    if st.button("Get Multi-step Recommendations"):
        # Step 1: Derive macros from the specific activity & time
        st.subheader("Step 1: Derived Macronutrient Ratios")
        macro_explanation = step_one_get_macros(activity, time_until)
        st.write(macro_explanation)

        # Step 2: Generate ~30 candidate items
        st.subheader("Step 2: Candidate Food/Drink Items")
        candidate_items_text = step_two_generate_candidates()
        st.write(candidate_items_text)

        # Convert the returned text into a list (very rough parse)
        # For reliability, you might want to do more robust parsing or have the model return JSON.
        items_list = []
        for line in candidate_items_text.split("\n"):
            cleaned = line.strip("-*•").strip()
            if cleaned:
                items_list.append(cleaned)

        # Step 3: Categorize each item with approximate macros & best/ok/avoid
        st.subheader("Step 3: Categorized Items")
        cat_info = step_three_categorize_items(items_list, macro_explanation)
        st.write(cat_info)

        # Step 4: Final JSON with best_foods, ok_foods, foods_to_avoid, do_eat, avoid
        st.subheader("Step 4: Final JSON Output")
        final_output = step_four_final_json(cat_info)
        st.write(final_output)

        # Attempt to parse the final output as JSON
        try:
            data = json.loads(final_output)
            st.success("Successfully parsed the final JSON!")
            # Optionally, display the JSON in a nicer format:
            with st.expander("See Final Structured Output"):
                st.json(data)
        except json.JSONDecodeError:
            st.error("Could not parse the final output as JSON. Check the logs/response.")

if __name__ == "__main__":
    main()
