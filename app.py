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
        "Provide guidance on what to consume for the following activity: "
        f"{activity}, with {time_until_activity} hours until that activity. "
        "Output only valid JSON with exactly four keys: 'foods_to_eat', 'foods_to_avoid', 'do_eat', and 'avoid'. "
        "\n\n"
        "1) 'foods_to_eat': a list of 15 meal or snack items that a 17-year-old could realistically find at a "
        "convenience store (e.g., 7-Eleven) or from a fast-food place (e.g., Chipotle). "
        "Each item should be a short string including the food name and approximate macronutrient percentages for carbs, fats, and protein. "
        "For example: 'Grilled Chicken Burrito (Carbs: 45, Fats: 20, Protein: 35)'. "
        "\n\n"
        "2) 'foods_to_avoid': a list of 15 items that a 17-year-old should avoid. Each item should also be a short string "
        "with the name plus approximate carbs/fats/protein. For example: 'Glazed Doughnut (Carbs: 70, Fats: 25, Protein: 5)'. "
        "\n\n"
        "3) 'do_eat': a short plain-text explanation of recommended macronutrient ratios. "
        "\n\n"
        "4) 'avoid': a short plain-text explanation of which types of foods or drinks to avoid. "
        "\n\n"
        "Return only valid JSON with the keys 'foods_to_eat', 'foods_to_avoid', 'do_eat', and 'avoid'. "
        "No disclaimers or extra commentary, and do not add additional keys."
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
