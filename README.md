# Duke Duber 🌿🚗  
**Sustainable Ride Sharing for the Duke Community**  

[Visit the site](http://alex-main.colab.duke.edu:8000/)

### **About**  
Duke Duber is a ride-sharing web app built with the **Django** framework, allowing users to **request, share, or offer rides** while contributing to a greener campus. Our goal is to reduce **CO₂ emissions**, ease **traffic congestion**, and support **reforestation efforts** in Duke Forest.  
![alt text](<home-page.png>)
### **To Do List**

- **Real-time location**  
  - **Calculate the carbon emission reduced by the ride**  
    - When creating a new Ride, in addition to calling the Google API to estimate travel time (ETA), also retrieve the distance from the starting point to the destination, ensuring that the original time estimation feature remains unaffected.  
    - One way to implement this:  
      - Create or modify a function (for example, `get_estimated_info`) that uses the Google Distance Matrix API to retrieve both duration and distance information in a single call.  
      - Modify the `get_eta` API endpoint so that when it returns JSON data, in addition to `estimated_time`, it also includes an `estimated_distance` field.  
    - The front-end JS can optionally display the distance information, but if this new feature is not used, the existing process can still successfully retrieve the estimated time.

- **Token system**  
  - The goal is to introduce a new token called “Chlorophyll,” with the following distribution rules:  
    - The driver, the ride initiator (the creator of the ride), and all passengers who join the ride (`rider` in `RideShare`) each receive an amount of “Chlorophyll” = distance * coefficient.
  - The balance of this “Chlorophyll” token should be displayed in the user’s drop-down menu in the navigation bar:  
    - Display location: under “Edit Profile” and “Change Password,” above “Logout.”  
    - Requirement: New features and interface elements should not alter the existing page design and functionality.  
  - To implement this requirement, the following changes are needed:  
    - **Extend user data**: You can extend the user model (for example, by linking a `Profile` model to the `User` via a `OneToOneField`), adding a field (such as `token_balance` or `leaf_tokens`) to record the balance of “Chlorophyll.”

- **Reward system**  
  - Add redeemable items to the page:  
    - Succulent (Duke Garden)  
    - Tree seed (Duke Forest)  
    - Vegetables and fruits (Duke Farm)

- **The Ride-share System**



### **Key Features**  
- **Driver & Rider Roles**: Users can register as **drivers** to offer rides or as **riders** to request/share a ride.  
- **Sustainability Rewards**: Earn **Green Coins (Chlorophyll)** for using the service and help plant trees in Duke Forest.  
- **Community Impact**: Reduce campus traffic, promote ride-sharing, and contribute to wildlife preservation.  
- **Django-Powered Web App**: A robust and scalable system using the Django web framework.  

### **Why Duke Duber?**  
- 🌱 **Lower Carbon Footprint**: Every shared ride reduces CO₂ emissions.  
- 🚘 **Less Traffic Congestion**: Fewer cars on the road mean a smoother commute.  
- 🌳 **Support Duke Forest**: Earn **Green Coins** and contribute to reforestation efforts.  

