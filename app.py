import streamlit as st

st.set_page_config(page_title="🍓 Fruit Catcher Preview", layout="centered")

st.title("🍓 Fruit Catcher Hand Gesture Game")

st.markdown("""
Use your **index finger** to control the basket and catch the falling fruits!  
Real-time hand tracking is powered by **MediaPipe**, and the game uses **Pygame**.
""")

# Show image preview
st.image("assets/images/fruit.jpg", caption="Game Preview", use_container_width=True)

st.markdown("""
### 🕹️ How to Play:
1. Run `fruit_catcher_hand_gesture.py`.
2. Use your hand in front of the camera.
3. Control the basket and catch fruits to score points.
""")

st.success("Game setup complete. Enjoy catching fruits using your hand!")
