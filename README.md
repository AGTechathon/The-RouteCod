# 🌍 TripCraft – Your Very Own Smart Travel Planner 🚀

**Team Name:** The RouteCoders  
**Hackathon Theme:** Open Innovation  
**Domain:** Software Development  
**Problem Statement:** AI-Powered Smart Travel Planner: Automating Personalized Itineraries for Seamless Exploration

---

## 📌 Overview

Planning a trip can be exciting yet overwhelming—especially with endless options, unexpected hurdles, and last-minute changes. **TripCraft** transforms this complexity into simplicity with the power of AI, real-time data, and collaborative features.

🎯 **Goal:**  
To create a personalized, adaptive, and collaborative travel planning web application that helps users plan trips effortlessly with:

- AI-generated itineraries 🧠
- Real-time adjustments 🔁
- Collaborative trip building 🤝
- Chatbot travel assistant 🤖

---

## 🧠 Key Features

- ✈️ **Smart & Adaptive Itinerary Planning**  
- 📍 **Location-Based Suggestions**  
- 💬 **Interactive Chatbot Assistant** 
- 📸 **Nearby Places, Stays, Activities with Ratings**  
- 🤝 **Collaborative Trip Management**  
---

## 🧰 Tech Stack

| Technology | Role |
|-----------|------|
| **React.js** | Frontend UI |
| **Spring Boot (Java)** | Backend API & Authentication |
| **Python Flask** | AI-based itinerary & recommendation engine |
| **MongoDB** | NoSQL Database |
| **Open Route Service** | Geolocation & route optimization |
| **Cloudinary** | Image Storage |
| **SMTP Mail API** | Invite collaborators via email |

---

## 📊 Technology Usage Distribution

![Tech Stack Pie Chart](https://quickchart.io/chart?c={type:'pie',data:{labels:['Python','Java','React'],datasets:[{data:[40,35,25]}]},options:{plugins:{legend:{position:'right'}}}})

---

## 🤖 Chatbot Feature

- Helps users with:
  - Trip suggestions
  - FAQs and travel guidelines
- Enhances accessibility and interaction on the platform

---

## 🚀 Project Setup Guide

> You can run all 3 modules locally for full functionality.

### 1️⃣ Frontend – React App

```bash
cd frontend
npm install
npm run dev 
```

2️⃣ Backend – Spring Boot (Java)
```bash
cd backend
mvn clean install
mvn spring-boot:run
```

3️⃣ AI Engine – Python Flask Microservice
```bash
python save.py
python app.py
```