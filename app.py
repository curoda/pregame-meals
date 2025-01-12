import json
import streamlit as st
from openai import OpenAI

# Instantiate your OpenAI client with the key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Inject a little CSS to condense bullet spacing
st.markdown(
    """
    <style>
    /* Reduce spacing for list items */
    ul, li {
        margin-bottom: 0.2rem !important;
        padding: 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def get_recommendations(activity: str, time_until_activity: float):
    """
    Query the gpt-4o-mini model to get:
      - foods_to_eat (15 items)
      - foods_to_avoid (15 items)
      - do_eat (text for DO EAT in green bold)
      - avoid (text for AVOID in red bold)
    
    The lists should be suitable snacks/drinks/supplements for a 17 year old.
    """

    prompt = (
        "You are a nutrition advisor. "
        "Given the following activity and time until that activity, provide guidance on what to consume. "
        "Output a JSON with exactly four keys: 'foods_to_eat', 'foods_to_avoid', 'do_eat', and 'avoid'. "
        "1) 'foods_to_eat': a list of 15 sensible snacks, drinks, or supplements that a 17-year-old could realistically find. "
        "2) 'foods_to_avoid': a list of 15 foods or drinks that a 17-year-old should avoid. "
        "3) 'do_eat': a short text with recommended macronutrient ratios/percentages, prefixed with '**DO EAT**' in bold green text. "
        "4) 'avoid': a short text description of foods to avoid (like 'heavy, greasy, or sugary'), prefixed with '**AVOID**' in bold red text. "
        "Be sure each list has exactly 15 items. Return only valid JSON, no extra commentary.\n\n"
        f"Activity: {activity}\n"
        f"Time until activity: {time_until_activity} hours\n\n"
        "Remember to return only valid JSON."
    )

    # Build the list of messages for the chat model
    messages = [
        {
            "role": "developer",
            "content": "You are a helpful nutrition assistant that provides meal guidance."
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

    try:
        data = json.loads(model_reply_content)
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        data = {
            "foods_to_eat": [],
            "foods_to_avoid": [],
            "do_eat": "**DO EAT** in green text: (Error parsing output)",
            "avoid": "**AVOID** in red text: (Error parsing output)",
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

        # --- Show the DO EAT / AVOID text at the top ---
        # DO EAT (bold, green text). We assume the model returns the string with HTML or Markdown inside it.
        st.markdown(do_eat, unsafe_allow_html=True)
        st.markdown(avoid, unsafe_allow_html=True)

        # --- Foods to Eat ---
        st.subheader("Foods to Eat")
        if foods_to_eat:
            # Show first 5
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
        st.subheade
