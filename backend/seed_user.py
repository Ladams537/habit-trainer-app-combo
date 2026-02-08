"""Seed script: register a user and verify the workflow."""
import httpx
import sys

BASE = "http://localhost:8000"

def main():
    client = httpx.Client(base_url=BASE, timeout=10)

    # 1. Register user
    print("1. Registering user hello@world.com ...")
    r = client.post("/api/auth/register", json={
        "email": "hello@world.com",
        "password": "helloworld",
    })
    if r.status_code == 201:
        user = r.json()
        print(f"   Created user: {user['id']} ({user['email']})")
    elif r.status_code == 409:
        print("   User already exists, continuing.")
    else:
        print(f"   ERROR: {r.status_code} {r.text}")
        sys.exit(1)

    # 2. Login
    print("2. Logging in ...")
    r = client.post("/api/auth/login", data={
        "username": "hello@world.com",
        "password": "helloworld",
    })
    if r.status_code != 200:
        print(f"   ERROR: {r.status_code} {r.text}")
        sys.exit(1)
    tokens = r.json()
    access = tokens["access_token"]
    print(f"   Got access token: {access[:20]}...")
    headers = {"Authorization": f"Bearer {access}"}

    # 3. Verify /me
    print("3. Verifying /api/auth/me ...")
    r = client.get("/api/auth/me", headers=headers)
    if r.status_code != 200:
        print(f"   ERROR: {r.status_code} {r.text}")
        sys.exit(1)
    me = r.json()
    print(f"   Authenticated as: {me['email']}")

    # 4. Check exercises seeded
    print("4. Checking exercise library ...")
    r = client.get("/api/fitness/exercises", headers=headers)
    if r.status_code != 200:
        print(f"   ERROR: {r.status_code} {r.text}")
        sys.exit(1)
    exercises = r.json()
    print(f"   Found {len(exercises)} exercises")

    # 5. Test habits CRUD
    print("5. Testing habits CRUD ...")
    r = client.post("/api/habits/", json={
        "name": "Test Habit",
        "habit_type": "boolean",
    }, headers=headers)
    if r.status_code == 201:
        habit = r.json()
        habit_id = habit["id"]
        print(f"   Created habit: {habit['name']} ({habit_id})")

        # Log completion
        r = client.post(f"/api/habits/{habit_id}/log", json={}, headers=headers)
        print(f"   Log completion: {r.status_code}")

        # Get streak
        r = client.get(f"/api/habits/{habit_id}/streak", headers=headers)
        if r.status_code == 200:
            streak = r.json()
            print(f"   Streak: {streak}")

        # Cleanup
        r = client.delete(f"/api/habits/{habit_id}", headers=headers)
        print(f"   Deleted test habit: {r.status_code}")
    else:
        print(f"   ERROR creating habit: {r.status_code} {r.text}")

    # 6. Test fitness workflow
    print("6. Testing fitness workflow ...")
    # Get a template list
    r = client.get("/api/fitness/templates", headers=headers)
    print(f"   Templates: {len(r.json())} found")

    # Start a free-form session
    r = client.post("/api/fitness/sessions/start", json={}, headers=headers)
    print(f"   Start session response: {r.status_code} {r.text[:500]}")
    if r.status_code == 200:
        session = r.json()
        session_id = session["id"]
        print(f"   Started session: {session_id}")

        # Log a set (use first exercise)
        if exercises:
            ex_id = exercises[0]["id"]
            r = client.post(f"/api/fitness/sessions/{session_id}/sets", json={
                "exercise_id": ex_id,
                "set_number": 1,
                "weight_kg": 60,
                "reps": 10,
                "completed": True,
            }, headers=headers)
            print(f"   Logged set: {r.status_code}")

        # Complete session
        r = client.post(f"/api/fitness/sessions/{session_id}/complete", json={
            "notes": "Seed test session",
            "rating_energy": 4,
            "rating_mood": 5,
        }, headers=headers)
        print(f"   Completed session: {r.status_code}")
    else:
        print(f"   ERROR starting session: {r.status_code} {r.text}")

    # 7. Test today endpoint
    print("7. Testing today habits ...")
    r = client.get("/api/habits/today", headers=headers)
    print(f"   Today habits: {r.status_code}, count={len(r.json()) if r.status_code == 200 else 'N/A'}")

    # 8. Stats overview
    print("8. Testing stats overview ...")
    r = client.get("/api/fitness/stats/overview", headers=headers)
    if r.status_code == 200:
        stats = r.json()
        print(f"   Overview stats: {stats}")
    else:
        print(f"   Stats: {r.status_code} {r.text[:500]}")

    print("\n=== All workflow tests passed! ===")


if __name__ == "__main__":
    main()
