import json
import streamlit as st
from openai import OpenAI

# Instantiate your OpenAI client with the key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_recommendations(activity: str, time_until_activity: float):
    """
    Query the gpt-4o or gpt-4o-mini model to get:
      - best_foods (15 items)
      - ok_foods (15 items)
      - foods_to_avoid (15 items)
      - do_eat (plain text)
      - avoid (plain text)

    Each list should be geared toward convenience or fast-food items
    that a 17-year-old can realistically find.
    """

    prompt = (
        "You are a sports performance expert advising a 17-year-old who can only shop at convenience stores "
        "or fast-food places (e.g., 7-Eleven, McDonald’s, Chipotle). They have an upcoming activity: "
        f"{activity}, in {time_until_activity} hours. "
        "\n\n"
        "Return only valid JSON with exactly five keys: 'best_foods', 'ok_foods', 'foods_to_avoid', 'do_eat', and 'avoid'. "
        "No extra commentary or disclaimers, and do not add additional keys. "
        "\n\n"
        "1) 'best_foods': Provide exactly 15 meal/snack items that are ideal for performance. "
        "Each item should be a short string including approximate carb/fat/protein percentages in parentheses, "
        "e.g. \"Grilled Chicken Bowl (Carbs: 45, Fats: 20, Protein: 35)\". "
        "\n\n"
        "2) 'ok_foods': Provide exactly 15 items that are acceptable but not ideal. Same format (name + macronutrient parentheses). "
        "\n\n"
        "3) 'foods_to_avoid': Provide exactly 15 items to avoid. Also use the same short string format. "
        "\n\n"
        "4) 'do_eat': A short plain-text explanation of the recommended macronutrient ratios or nutrients that are beneficial. "
        "\n\n"
        "5) 'avoid': A short plain-text explanation of which foods or drinks to avoid. "
        "\n\n"
        "Again, output only valid JSON with those five keys—best_foods, ok_foods, foods_to_avoid, do_eat, avoid—and nothing else."
    )

    # Build the list of messages for the chat model
    messages = [
        {
            "role": "developer",
            "content": "You are a helpful sports nutrition assistant. Output valid JSON only."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    # Call your desired model; adjust model name as needed
    completion = client.chat.completions.create(
        model="gpt-4o-mini",  # or "gpt-4o"
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
            "best_foods": [],
            "ok_foods": [],
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

        best_foods = results.get("best_foods", [])
        ok_foods = results.get("ok_foods", [])
        foods_to_avoid = results.get("foods_to_avoid", [])
        do_eat = results.get("do_eat", "")
        avoid = results.get("avoid", "")

        # --- Show the DO EAT / AVOID text at the top (in plain text) ---
        st.subheader("Recommended Macronutrient Ratios (DO EAT)")
        st.write(do_eat)

        st.subheader("General Avoidance Guidance")
        st.write(avoid)

        # --- Best Foods to Eat ---
        st.subheader("Best Foods to Eat")
        if best_foods:
            # Show first 5
            for food in best_foods[:5]:
                st.write(f"- {food}")

            # Show more link
            if len(best_foods) > 5:
                with st.expander("Show more best foods"):
                    for food in best_foods[5:]:
                        st.write(f"- {food}")
        else:
            st.write("No best foods found.")

        # --- OK Foods to Eat ---
        st.subheader("OK Foods to Eat")
        if ok_foods:
            # Show first 5
            for food in ok_foods[:5]:
                st.write(f"- {food}")

            # Show more link
            if len(ok_foods) > 5:
                with st.expander("Show more OK foods"):
                    for food in ok_foods[5:]:
                        st.write(f"- {food}")
        else:
            st.write("No OK foods found.")

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
