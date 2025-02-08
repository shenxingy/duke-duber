# Duke Duber 🌿🚗  
**Sustainable Ride Sharing for the Duke Community**  

### **About**  
Duke Duber is a ride-sharing web app built with the **Django** framework, allowing users to **request, share, or offer rides** while contributing to a greener campus. Our goal is to reduce **CO₂ emissions**, ease **traffic congestion**, and support **reforestation efforts** in Duke Forest.  

### **To do list**
- Real time location: 
- Calculate the carbon emission that is reduced by the ride:
  在创建新的 Ride 时，除了调用 Google API 预估行程时间（ETA）外，还能额外获取起点到终点的距离，同时保证原有的预估时间功能不受影响。
一种实现方式是：
新建或修改一个函数（例如 get_estimated_info），利用 Google Distance Matrix API 一次性获取时长与距离信息。
修改 get_eta 的 API 接口，在返回 JSON 数据时，除了返回“estimated_time”，再加上一个“estimated_distance”的字段。
前端 JS 部分也可以选择性地显示距离信息，但若没有使用这项新功能，原有流程依然能正常获得时长。
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

### **Key Features**  
- **Driver & Rider Roles**: Users can register as **drivers** to offer rides or as **riders** to request/share a ride.  
- **Sustainability Rewards**: Earn **Green Coins (Chlorophyll)** for using the service and help plant trees in Duke Forest.  
- **Community Impact**: Reduce campus traffic, promote ride-sharing, and contribute to wildlife preservation.  
- **Django-Powered Web App**: A robust and scalable system using the Django web framework.  

### **Why Duke Duber?**  
- 🌱 **Lower Carbon Footprint**: Every shared ride reduces CO₂ emissions.  
- 🚘 **Less Traffic Congestion**: Fewer cars on the road mean a smoother commute.  
- 🌳 **Support Duke Forest**: Earn **Green Coins** and contribute to reforestation efforts.  

