# Duke Duber

### **To do list**
- Real time location
- Calculate the carbon emission that is reduced by the ride
- token system:
目标是新增一种代币“叶绿素”，分发规则如下：
• 每笔 ride 完成后，司机获得的叶绿素数量 = 里程数 × 2
• 拼单发起者（ride 的创建者）以及所有参与拼单的乘客（RideShare 中的 rider）各自获得的叶绿素数量 = 里程数
同时，这个“叶绿素”余额需要在网站导航栏中用户的下拉菜单中显示，具体位置要求是在“Edit Profile”和“Change Password”下面、“Logout”上面。
要求是新增的功能和界面元素不改变现有的页面设计和功能。
为了实现这一需求，可以考虑以下几点改动：
用户数据扩展
• 为了记录每个用户的叶绿素余额，可以扩展用户模型（例如通过 OneToOneField 将一个 Profile 模型与 User 关联）并添加一个字段，比如 token_balance 或 leaf_tokens。
- reward system: Add succulent (duke garden) tree seed (duke forest) and vegtables and fruits (duke farm) figure on the page.
- Carmax API

### **Repository Description**  
`duke-duber` is a Django-based ride-sharing web application designed to promote sustainable and efficient transportation within the Duke University community. Users can register as **drivers** to accept ride requests or as **riders** to request or share rides. By facilitating shared travel, `duke-duber` helps reduce CO₂ emissions, ease campus traffic congestion, and contribute to Duke’s environmental initiatives.  

As users participate in the system, they earn **Green Coins (Chlorophyll)**, which can be used to support tree-planting efforts in the **Duke Forest**, a crucial habitat for wildlife. This initiative aligns with ongoing forest management efforts, as some aging trees are being removed to maintain ecological balance.

---

## **README Introduction**  

# Duke Duber 🌿🚗  
**Sustainable Ride Sharing for the Duke Community**  

### **About**  
Duke Duber is a ride-sharing web app built with the **Django** framework, allowing users to **request, share, or offer rides** while contributing to a greener campus. Our goal is to reduce **CO₂ emissions**, ease **traffic congestion**, and support **reforestation efforts** in Duke Forest.  

### **Key Features**  
- **Driver & Rider Roles**: Users can register as **drivers** to offer rides or as **riders** to request/share a ride.  
- **Sustainability Rewards**: Earn **Green Coins (Chlorophyll)** for using the service and help plant trees in Duke Forest.  
- **Community Impact**: Reduce campus traffic, promote ride-sharing, and contribute to wildlife preservation.  
- **Django-Powered Web App**: A robust and scalable system using the Django web framework.  

### **Why Duke Duber?**  
- 🌱 **Lower Carbon Footprint**: Every shared ride reduces CO₂ emissions.  
- 🚘 **Less Traffic Congestion**: Fewer cars on the road mean a smoother commute.  
- 🌳 **Support Duke Forest**: Earn **Green Coins** and contribute to reforestation efforts.  

