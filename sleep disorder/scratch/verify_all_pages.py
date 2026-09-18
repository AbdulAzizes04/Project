import os
import sys
import json

# Ensure workspace is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.dirname(BASE_DIR)
sys.path.insert(0, WORKSPACE_DIR)

from app import create_app
from database.models import db, User, Assessment, Prediction

app = create_app()

def test_all_pages():
    print("=== Starting Comprehensive Page & Endpoint Verification ===")
    results = []
    
    with app.test_client() as client:
        # 1. Test Public Pages
        public_endpoints = [
            ("/", "Home Page"),
            ("/about", "About Project Architecture"),
            ("/login", "Login Page"),
            ("/register", "Registration Page"),
            ("/admin/login", "Admin Login Page"),
            ("/api/gemini/status", "Gemini API Status API")
        ]
        
        for url, name in public_endpoints:
            try:
                res = client.get(url, follow_redirects=False)
                status = res.status_code
                status_str = "OK" if status in [200, 302] else f"FAIL ({status})"
                results.append((name, url, status_str, status))
                print(f"[{status_str}] {name} ({url}) -> Status: {status}")
            except Exception as e:
                results.append((name, url, f"EXCEPTION: {e}", 500))
                print(f"[EXCEPTION] {name} ({url}) -> {e}")

        # 2. Test Patient Login
        print("\n--- Testing Patient Login Flow ---")
        login_res = client.post("/login", data={
            "email": "demo@sleepai.org",
            "password": "demo123"
        }, follow_redirects=True)
        print(f"Login response status: {login_res.status_code}")

        # 3. Test Authenticated Patient Pages
        patient_endpoints = [
            ("/dashboard", "Patient Dashboard"),
            ("/assessment", "Assessment Intake Form (GET)"),
            ("/history", "Assessment History"),
            ("/chatbot", "AI Chatbot View"),
            ("/profile", "User Profile")
        ]

        for url, name in patient_endpoints:
            try:
                res = client.get(url, follow_redirects=False)
                status = res.status_code
                status_str = "OK" if status == 200 else f"FAIL ({status})"
                results.append((name, url, status_str, status))
                print(f"[{status_str}] {name} ({url}) -> Status: {status}")
            except Exception as e:
                results.append((name, url, f"EXCEPTION: {e}", 500))
                print(f"[EXCEPTION] {name} ({url}) -> {e}")

        # 4. Test Submitting an Assessment (POST /assessment)
        print("\n--- Testing Assessment Submission (POST /assessment) ---")
        assessment_payload = {
            "Age": 38,
            "Gender": "Male",
            "Occupation": "Software Engineer",
            "Sleep Duration": 5.5,
            "Quality of Sleep": 4,
            "Physical Activity Level": 35,
            "Stress Level": 8,
            "BMI Category": "Overweight",
            "Systolic_BP": 135,
            "Diastolic_BP": 88,
            "Heart Rate": 78,
            "Daily Steps": 4200
        }
        
        post_res = client.post("/assessment", data=assessment_payload, follow_redirects=False)
        print(f"POST /assessment redirect status: {post_res.status_code}, location: {post_res.headers.get('Location')}")
        
        assessment_id = None
        if post_res.status_code == 302:
            redirect_url = post_res.headers.get('Location')
            # Extract id
            assessment_id = int(redirect_url.rstrip("/").split("/")[-1])
            print(f"Assessment created with ID: {assessment_id}")
            
            # Now test result, explanation, recommendations, and PDF download
            ass_endpoints = [
                (f"/result/{assessment_id}", "Assessment Result Page"),
                (f"/explanation/{assessment_id}", "SHAP Explanation Page"),
                (f"/recommendations/{assessment_id}", "Gemini Recommendations Page"),
                (f"/assessment/{assessment_id}/download", "PDF Report Download")
            ]
            
            for url, name in ass_endpoints:
                try:
                    res = client.get(url, follow_redirects=False)
                    status = res.status_code
                    status_str = "OK" if status == 200 else f"FAIL ({status})"
                    results.append((name, url, status_str, status))
                    print(f"[{status_str}] {name} ({url}) -> Status: {status}")
                except Exception as e:
                    results.append((name, url, f"EXCEPTION: {e}", 500))
                    print(f"[EXCEPTION] {name} ({url}) -> {e}")

        # 5. Test Chatbot API POST
        print("\n--- Testing Chatbot API (POST /api/chat) ---")
        try:
            chat_res = client.post("/api/chat", json={"message": "What can I do to sleep better tonight?"})
            print(f"Chat API status: {chat_res.status_code}")
            if chat_res.status_code == 200:
                resp_json = chat_res.get_json()
                print(f"Chatbot response snippet: {resp_json.get('response', '')[:120]}...")
                results.append(("Chatbot API", "/api/chat", "OK", 200))
            else:
                results.append(("Chatbot API", "/api/chat", f"FAIL ({chat_res.status_code})", chat_res.status_code))
        except Exception as e:
            results.append(("Chatbot API", "/api/chat", f"EXCEPTION: {e}", 500))
            print(f"[EXCEPTION] Chatbot API -> {e}")

        # 6. Test Admin Pages
        print("\n--- Testing Admin Workflow ---")
        # Logout patient
        client.get("/logout")
        
        # Login admin
        admin_login = client.post("/admin/login", data={
            "email": "admin@sleepai.org",
            "password": "admin123"
        }, follow_redirects=True)
        print(f"Admin Login response status: {admin_login.status_code}")

        admin_endpoints = [
            ("/admin/dashboard", "Admin Dashboard"),
            ("/admin/users", "Admin User Management"),
            ("/admin/model-performance", "Admin Model Performance")
        ]

        for url, name in admin_endpoints:
            try:
                res = client.get(url, follow_redirects=False)
                status = res.status_code
                status_str = "OK" if status == 200 else f"FAIL ({status})"
                results.append((name, url, status_str, status))
                print(f"[{status_str}] {name} ({url}) -> Status: {status}")
            except Exception as e:
                results.append((name, url, f"EXCEPTION: {e}", 500))
                print(f"[EXCEPTION] {name} ({url}) -> {e}")

    print("\n=== SUMMARY OF ALL VERIFIED PAGES ===")
    all_ok = True
    for name, url, status_str, code in results:
        is_ok = code in [200, 302]
        if not is_ok:
            all_ok = False
        print(f"{'[PASS]' if is_ok else '[FAIL]'} {name:35} | URL: {url:35} | Status: {status_str}")
        
    print(f"\nOverall Result: {'ALL PAGES PASSED PERFECTLY!' if all_ok else 'SOME PAGES FAILED'}")

if __name__ == "__main__":
    test_all_pages()
