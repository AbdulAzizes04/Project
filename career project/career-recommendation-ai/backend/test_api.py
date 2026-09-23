import sys, os
sys.path.insert(0, 'backend')
sys.path.insert(0, 'ml')

from fastapi.testclient import TestClient
from app.main import app

def run_tests():
    with TestClient(app) as client:
        # Health check
        r = client.get('/health')
        assert r.status_code == 200 and r.json()['status'] == 'healthy', f'Health failed: {r.text}'
        print('PASS: GET /health')

        # Register student (idempotent)
        r = client.post('/api/auth/register', json={'name': 'Test User', 'email': 'testuser@test.com', 'password': 'Test@1234', 'role': 'STUDENT'})
        assert r.status_code in (201, 409), f'Register failed: {r.text}'
        print(f'PASS: POST /api/auth/register (status {r.status_code})')

        # Admin login
        r = client.post('/api/auth/login', json={'email': 'admin@careerai.edu', 'password': 'Admin@123'})
        assert r.status_code == 200, f'Admin login failed: {r.text}'
        admin_token = r.json()['access_token']
        print('PASS: POST /api/auth/login (admin)')

        # Student login
        r = client.post('/api/auth/login', json={'email': 'student@careerai.edu', 'password': 'Student@123'})
        assert r.status_code == 200, f'Student login failed: {r.text}'
        student_token = r.json()['access_token']
        print('PASS: POST /api/auth/login (student)')

        headers = {'Authorization': f'Bearer {student_token}'}
        admin_headers = {'Authorization': f'Bearer {admin_token}'}

        # GET /me
        r = client.get('/api/auth/me', headers=headers)
        assert r.status_code == 200
        print(f'PASS: GET /api/auth/me (role: {r.json()["role"]})')

        # Student profile
        r = client.get('/api/student/profile', headers=headers)
        assert r.status_code == 200
        print('PASS: GET /api/student/profile (profile completion included)')

        # Skills catalog
        r = client.get('/api/skills')
        assert r.status_code == 200
        print(f'PASS: GET /api/skills ({len(r.json())} skills in catalog)')

        # Careers list
        r = client.get('/api/careers')
        assert r.status_code == 200
        print(f'PASS: GET /api/careers ({len(r.json())} career roles)')

        # Student skills
        r = client.get('/api/student/skills', headers=headers)
        assert r.status_code == 200
        print(f'PASS: GET /api/student/skills ({len(r.json())} skills)')

        # Certifications
        r = client.get('/api/student/certifications', headers=headers)
        assert r.status_code == 200
        print(f'PASS: GET /api/student/certifications ({len(r.json())} certs)')

        # Projects
        r = client.get('/api/student/projects', headers=headers)
        assert r.status_code == 200
        print(f'PASS: GET /api/student/projects ({len(r.json())} projects)')

        # Generate recommendations
        r = client.post('/api/recommendations/generate', json={'regenerate': False}, headers=headers)
        assert r.status_code == 200, f'Recommendation generation failed: {r.text}'
        print(f'PASS: POST /api/recommendations/generate -> {r.json().get("message")}')

        # Get recommendations
        r = client.get('/api/recommendations', headers=headers)
        assert r.status_code == 200
        recs = r.json().get('data', [])
        print(f'PASS: GET /api/recommendations ({len(recs)} recommendations)')
        if recs:
            top = recs[0]
            print(f'       Top: {top["career_name"]} - {top["compatibility_score"]}% compatibility')

        # Admin analytics
        r = client.get('/api/admin/analytics', headers=admin_headers)
        assert r.status_code == 200
        summary = r.json()['summary']
        print(f'PASS: GET /api/admin/analytics (students={summary["total_students"]}, skills={summary["total_skills"]})')

        # Model performance
        r = client.get('/api/admin/model-performance', headers=admin_headers)
        assert r.status_code == 200
        m = r.json().get('metrics', {})
        print(f'PASS: GET /api/admin/model-performance (model={m.get("model_name")}, f1={m.get("f1_macro")})')

    print()
    print('=' * 60)
    print('ALL BACKEND API SMOKE TESTS PASSED SUCCESSFULLY!')
    print('=' * 60)

run_tests()
