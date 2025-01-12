import json
import streamlit as st
from openai import OpenAI

# Instantiate your OpenAI client with the key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_recommendations(activity: str, time_until_activity: float):
    """
    Query the gpt-4o-mini model to get:
      - foods_to_eat (15 items)
      - foods_to_avoid (15 items)
      - do_eat (plain text)
      - avoid (plain text)

    Each list should be suitable for a 17-year-old's realistic options.
    """

    prompt = (
        "You are a sports performance expert. "
        "Given the following activity and time until that activity, provide guidance on what to consume. "
        "Output a JSON with exactly four keys: 'foods_to_eat', 'foods_to_avoid', 'do_eat', and 'avoid'. "
        "1) 'foods_to_eat': a list of 15 sensible snacks, drinks, or supplements that a 17-year-old would want to eat and could easily find. Next to each item list to macronutrient contents."
        "2) 'foods_to_avoid': a list of 15 foods or drinks that a 17-year-old should avoid. Next to each item list to macronutrient contents."
        "3) 'do_eat': a short text with recommended macronutrient ratios/percentages (plain text). "
        "4) 'avoid': a short text description of foods to avoid (plain text). "
        "Be sure each list has exactly 15 items. Return only valid JSON, no extra commentary.\n\n"
        f"Activity: {activity}\n"
        f"Time until activity: {time_until_activity} hours\n\n"
        "Again, provide only valid JSON with those four keys, and do not add extra keys, disclaimers, or text."
    )

    # Build the list of messages for the chat model
    messages = [
        {
            "role": "developer",
            "content": "You are a helpful expert in sports performance that provides meal guidance."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7
    )

    # Extract the model's reply content
    model_reply_content = completion.choices[0].message.content.strip()

    # Attempt to parse the JSON response
    try:
        data = json.loads(model_reply_content)
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        data = {
            "foods_to_eat": [],
            "foods_to_avoid": [],
            "do_eat": "Error parsing JSON from the model.",
            "avoid": "Error parsing JSON from the model.",
        }

    return data

def main():
    st.title("Pre-Activity Nutrition Guide")
    st.write("Select your activity and how long until you do it, and I'll recommend what to eat and avoid.")

    # Activity selection: dropdown with free-text input
    activities = ["basketball", "weightlifting", "pilates", "running", "swimming", "yoga"]
    activity = st.selectbox("Choose an activity (or type to add your own)", options=activities, index=0)

    # Time selection: slider from 0 to 3 in 0.25 increments (15 minutes)
    time_until = st.slider("Hours until activity", 0.0, 3.0, 1.0, 0.25)

    if st.button("Get Recommendations"):
        with st.spinner("Getting your recommendations..."):
            results = get_recommendations(activity, time_until)

        foods_to_eat = results.get("foods_to_eat", [])
        foods_to_avoid = results.get("foods_to_avoid", [])
        do_eat = results.get("do_eat", "")
        avoid = results.get("avoid", "")

        # --- Show the DO EAT / AVOID text at the top (in plain text) ---
        st.subheader("DO EAT")
        st.write(do_eat)

        st.subheader("AVOID")
        st.write(avoid)

        # --- Foods to Eat ---
        st.subheader("Foods to Eat")
        if foods_to_eat:
            for food in foods_to_eat[:5]:
                st.write(f"- {food}")

            # Show more link
            if len(foods_to_eat) > 5:
                with st.expander("Show more foods to eat"):
                    for food in foods_to_eat[5:]:
                        st.write(f"- {food}")
        else:
            st.write("No foods to eat found.")

        # --- Foods to Avoid ---
        st.subheader("Foods to Avoid")
        if foods_to_avoid:
            for food in foods_to_avoid[:5]:
                st.write(f"- {food}")

            # Show more link
            if len(foods_to_avoid) > 5:
                with st.expander("Show more foods to avoid"):
                    for food in foods_to_avoid[5:]:
                        st.write(f"- {food}")
        else:
            st.write("No foods to avoid found.")

if __name__ == "__main__":
    main()
