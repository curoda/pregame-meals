import streamlit as st
from openai import OpenAI

# Create the OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def prompt_model(messages):
    """
    A helper function to make a chat.completions request 
    and return the model's text response.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # or "gpt-4o"
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()


def step_one_get_macros(activity, time_until):
    """
    Step 1: Derive recommended macronutrient ratio 
    based on the specific activity and time.
    """
    user_content = f"""
    You are a sports nutrition expert. 
    The athlete is 17 years old, with only convenience stores 
    or fast-food places available (e.g., 7-Eleven, McDonald’s, Chipotle).
    The upcoming activity is {activity}, starting in {time_until} hours.
    
    1) What macronutrient ratio (carbs/protein/fats) do you recommend 
       for the pre-activity meal/snack, and why?
    2) Keep your answer brief and in plain text.
    3) Do not include disclaimers or extra commentary.
    """

    messages = [
        {"role": "developer", "content": "You are a concise, helpful nutrition coach."},
        {"role": "user", "content": user_content}
    ]
    return prompt_model(messages)


def step_two_get_best_foods(macro_summary):
    """
    Step 2: Return a bulleted list of 'Best' food choices 
    that match the macro_summary from Step 1.
    Each item should have approximate carbs/fats/protein percentages.
    """
    user_content = f"""
    You previously stated the recommended macronutrient ratio is:
    {macro_summary}

    Now:
    - Return a bulleted list of around 10 'Best' food choices (not more than 10 items).
    - Each item must be realistic for a 17-year-old at a convenience store 
      or fast-food chain (e.g., 7-Eleven, McDonald’s, Chipotle).
    - Each item must include approximate carbs, fats, and protein percentages 
      in parentheses, e.g. (Carbs: 50, Fats: 20, Protein: 30).
    - No extra commentary or disclaimers.
    - Keep it very concise.
    """

    messages = [
        {"role": "developer", "content": "Return only a concise bulleted list."},
        {"role": "user", "content": user_content}
    ]
    return prompt_model(messages)


def step_three_get_ok_foods(macro_summary):
    """
    Step 3: Return a bulleted list of 'OK' food choices 
    with approximate macros, still referencing the macro_summary.
    """
    user_content = f"""
    Given the recommended macronutrient ratio: 
    {macro_summary}

    - Now return a bulleted list of around 10 'OK' food choices. 
    - These are acceptable, but not ideal. 
    - Each item must have approximate carbs/fats/protein in parentheses.
    - No extra commentary or disclaimers.
    """

    messages = [
        {"role": "developer", "content": "Return only a concise bulleted list."},
        {"role": "user", "content": user_content}
    ]
    return prompt_model(messages)


def step_four_get_avoid_foods(macro_summary):
    """
    Step 4: Return a bulleted list of 'Avoid' food choices 
    with approximate macros, referencing the macro_summary again.
    """
    user_content = f"""
    Based on the recommended macronutrient ratio:
    {macro_summary}

    - Return a bulleted list of around 10 foods/drinks to 'Avoid'. 
    - Still list approximate carbs/fats/protein in parentheses.
    - No extra commentary or disclaimers.
    """

    messages = [
        {"role": "developer", "content": "Return only a concise bulleted list."},
        {"role": "user", "content": user_content}
    ]
    return prompt_model(messages)


def main():
    st.title("Multi-Step Prompting Demo")

    # Step 0: Collect user inputs
    activities = ["basketball", "weightlifting", "pilates", "running", "swimming", "yoga"]
    activity = st.selectbox("Choose an activity", options=activities)
    time_until = st.slider("Hours until activity", 0.0, 3.0, 1.0, 0.25)

    if st.button("Run Multi-Step Prompts"):
        with st.spinner("Getting recommended macros..."):
            # Step 1: Get recommended macros & explanation
            macro_explanation = step_one_get_macros(activity, time_until)
            st.subheader("Step 1: Recommended Macronutrient Ratio")
            st.write(macro_explanation)

        with st.spinner("Getting best foods..."):
            # Step 2: Best foods
            best_foods = step_two_get_best_foods(macro_explanation)
            st.subheader("Step 2: Best Foods (Bulleted List)")
            st.markdown(best_foods)

        with st.spinner("Getting OK foods..."):
            # Step 3: OK foods
            ok_foods = step_three_get_ok_foods(macro_explanation)
            st.subheader("Step 3: OK Foods (Bulleted List)")
            st.markdown(ok_foods)

        with st.spinner("Getting foods to avoid..."):
            # Step 4: Avoid foods
            avoid_foods = step_four_get_avoid_foods(macro_explanation)
            st.subheader("Step 4: Foods to Avoid (Bulleted List)")
            st.markdown(avoid_foods)

if __name__ == "__main__":
    main()
