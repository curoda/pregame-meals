import streamlit as st
import openai

# --- Configure your OpenAI API key from Streamlit secrets ---
openai.api_key = st.secrets["OPENAI_API_KEY"]

def get_recommendations(activity: str, time_until_activity: float):
    """
    Query the OpenAI gpt-4o-mini model to get:
      - 15 foods to eat (list)
      - 15 foods to avoid (list)
      - 2-3 sentence explanation
    
    Returns a dict with "foods_to_eat", "foods_to_avoid", and "explanation".
    """
    
    # Build a user prompt for the model
    # Prompt instructs the model to return JSON so we can parse easily.
    # You can also do direct text parsing, but JSON helps ensure we can handle the output systematically.
    prompt = (
        "You are a nutrition advisor. "
        "Given the following activity and time until that activity, provide guidance on what to consume. "
        "Specifically, output a JSON with exactly three keys: 'foods_to_eat', 'foods_to_avoid', and 'explanation'. "
        "Each of 'foods_to_eat' and 'foods_to_avoid' should be a list of 15 items. "
        "The 'explanation' key should contain 2-3 complete sentences describing why these choices are good or not. "
        "Here are the details:\n\n"
        f"Activity: {activity}\n"
        f"Time until activity: {time_until_activity} hours\n\n"
        "Remember to only return valid JSON, no additional commentary."
    )
    
    # Call the OpenAI chat completions endpoint
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "developer",
                "content": "You are a helpful nutrition assistant that provides meal guidance."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7
    )
    
    # The model response
    model_reply = response.choices[0].message.content.strip()
    
    # Safely parse the JSON from the response
    # We expect the response to be a JSON with "foods_to_eat", "foods_to_avoid", "explanation"
    import json
    
    try:
        data = json.loads(model_reply)
    except json.JSONDecodeError:
        # If there's an error, fallback to a minimal structure
        data = {
            "foods_to_eat": [],
            "foods_to_avoid": [],
            "explanation": "Sorry, I couldn't parse the output properly."
        }
    
    return data

def main():
    st.title("Pre-Activity Nutrition Guide")
    st.write("Select your activity and how long until you do it, and I'll recommend what to eat and avoid.")
    
    # Activity selection
    # Provide a set of suggestions but allow free text
    activities = ["basketball", "weightlifting", "pilates", "running", "swimming", "yoga"]
    activity = st.selectbox("Choose an activity (or type to add your own)", options=activities, index=0)
    
    # Time selection: slider from 0 to 3 in 0.25 increments (15 minutes)
    time_until = st.slider("Hours until activity", 0.0, 3.0, 1.0, 0.25)
    
    if st.button("Get Recommendations"):
        with st.spinner("Getting your recommendations..."):
            results = get_recommendations(activity, time_until)
        
        foods_to_eat = results.get("foods_to_eat", [])
        foods_to_avoid = results.get("foods_to_avoid", [])
        explanation = results.get("explanation", "")
        
        # Display the results
        st.subheader("Foods to Eat")
        if foods_to_eat:
            # Show first 5
            for i, food in enumerate(foods_to_eat[:5], start=1):
                st.write(f"- {food}")
            
            # Show more link
            if len(foods_to_eat) > 5:
                with st.expander("Show more foods to eat"):
                    for food in foods_to_eat[5:]:
                        st.write(f"- {food}")
        else:
            st.write("No foods to eat found.")
        
        st.subheader("Foods to Avoid")
        if foods_to_avoid:
            # Show first 5
            for i, food in enumerate(foods_to_avoid[:5], start=1):
                st.write(f"- {food}")
            
            # Show more link
            if len(foods_to_avoid) > 5:
                with st.expander("Show more foods to avoid"):
                    for food in foods_to_avoid[5:]:
                        st.write(f"- {food}")
        else:
            st.write("No foods to avoid found.")
        
        st.subheader("Explanation")
        st.write(explanation)

if __name__ == "__main__":
    main()
