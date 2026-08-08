"""
End-to-end test of the whole API, run in-process via httpx ASGITransport.
Exercises every endpoint AND the race condition (concurrent same-slot booking).
"""
import asyncio
from datetime import datetime, timezone, timedelta

import httpx

from app.main import app
from app.core.database import connect_to_mongo, close_mongo_connection, get_db

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
results = []


def check(name, condition, detail=""):
    tag = PASS if condition else FAIL
    print(f"  [{tag}] {name}" + (f"  ({detail})" if detail and not condition else ""))
    results.append(bool(condition))


async def main():
    # Fresh DB for a clean run
    await connect_to_mongo()
    db = get_db()
    await db.appointments.delete_many({})
    await db.users.delete_many({"$or": [{"role": {"$in": ["patient", "PATIENT"]}}, {"email": {"$in": ["asha@test.com", "bob@test.com", "sneaky@test.com"]}}]})
    await close_mongo_connection()

    transport = httpx.ASGITransport(app=app)
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:

            print("\n== AUTH ==")
            r = await c.post("/auth/signup", json={
                "first_name": "Asha", "last_name": "Rao",
                "email": "asha@test.com", "mobile": "+919876543210",
                "password": "secret123"})
            check("signup patient A -> 201", r.status_code == 201, r.text)
            check("password never returned", "password" not in r.text)
            check("role forced to patient", r.json().get("role") == "patient")

            r = await c.post("/auth/signup", json={
                "first_name": "Asha", "last_name": "Rao",
                "email": "asha@test.com", "mobile": "+919876543210",
                "password": "secret123"})
            check("duplicate email -> 409", r.status_code == 409, r.text)

            r = await c.post("/auth/signup", json={
                "first_name": "Sneaky", "last_name": "User",
                "email": "sneaky@test.com", "mobile": "9876543211",
                "password": "secret123", "role": "doctor"})
            check("signup can't self-assign doctor", r.json().get("role") == "patient")

            r = await c.post("/auth/signup", json={
                "first_name": "Bob", "last_name": "Singh",
                "email": "bob@test.com", "mobile": "9876543212",
                "password": "secret123"})
            check("signup patient B -> 201", r.status_code == 201, r.text)

            # short reason & bad temp rejected at Gate 2
            r = await c.post("/auth/signup", json={
                "first_name": "X", "last_name": "Y",
                "email": "bad-email", "mobile": "123",
                "password": "x"})
            check("bad signup fields -> 422", r.status_code == 422, r.text)

            r = await c.post("/auth/login", json={
                "email": "asha@test.com", "password": "secret123"})
            check("login A -> 200", r.status_code == 200, r.text)
            tok_a = r.json()["access_token"]

            r = await c.post("/auth/login", json={
                "email": "bob@test.com", "password": "secret123"})
            tok_b = r.json()["access_token"]

            r = await c.post("/auth/login", json={
                "email": "asha@test.com", "password": "WRONG"})
            check("wrong password -> 401", r.status_code == 401, r.text)
            msg_wrong_pw = r.json()["detail"]
            r = await c.post("/auth/login", json={
                "email": "nobody@test.com", "password": "whatever"})
            check("unknown email -> 401 same message",
                  r.status_code == 401 and r.json()["detail"] == msg_wrong_pw)

            r = await c.post("/auth/login", json={
                "email": "dr.meera@citycare.clinic", "password": "doctor123"})
            check("doctor login -> 200", r.status_code == 200, r.text)
            tok_doc = r.json()["access_token"]
            check("doctor role in token response", r.json()["role"] == "doctor")

            print("\n== CLINIC (open) ==")
            r = await c.get("/clinic/info")
            check("clinic info -> 200", r.status_code == 200)
            check("exactly 12 slots", len(r.json()["slots"]) == 12,
                  str(len(r.json()["slots"])))

            tomorrow = (datetime.now(timezone.utc).date() + timedelta(days=1)).isoformat()
            r = await c.get(f"/clinic/free-slots?date={tomorrow}")
            check("free slots -> 200", r.status_code == 200)
            check("all 12 free initially", len(r.json()["free_slots"]) == 12)

            r = await c.get("/clinic/free-slots?date=not-a-date")
            check("bad date format -> 422", r.status_code == 422, r.text)
            yesterday = (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()
            r = await c.get(f"/clinic/free-slots?date={yesterday}")
            check("past date -> 400", r.status_code == 400, r.text)
            far = (datetime.now(timezone.utc).date() + timedelta(days=30)).isoformat()
            r = await c.get(f"/clinic/free-slots?date={far}")
            check("beyond window -> 400", r.status_code == 400, r.text)

            print("\n== BOOKING (protected, 4 gates) ==")
            hdr_a = {"Authorization": f"Bearer {tok_a}"}
            hdr_b = {"Authorization": f"Bearer {tok_b}"}
            hdr_doc = {"Authorization": f"Bearer {tok_doc}"}

            r = await c.post("/appointments", json={
                "date": tomorrow, "slot": "10:30",
                "reason": "Persistent fever since morning", "temperature": 101.5,
                "symptoms": ["fever", "headache"]})
            check("Gate 1: no token -> 401", r.status_code == 401, r.text)

            r = await c.post("/appointments", headers=hdr_a, json={
                "date": tomorrow, "slot": "10:30",
                "reason": "flu", "temperature": 101.5, "symptoms": ["fever"]})
            check("Gate 2: one-word reason -> 422", r.status_code == 422, r.text)

            r = await c.post("/appointments", headers=hdr_a, json={
                "date": tomorrow, "slot": "10:30",
                "reason": "High fever since morning", "temperature": 450,
                "symptoms": ["fever"]})
            check("Gate 2: impossible temp -> 422", r.status_code == 422, r.text)

            r = await c.post("/appointments", headers=hdr_a, json={
                "date": tomorrow, "slot": "99:99",
                "reason": "High fever since morning", "symptoms": ["fever"]})
            check("Gate 3: slot not on menu -> 400", r.status_code == 400, r.text)

            r = await c.post("/appointments", headers=hdr_a, json={
                "date": tomorrow, "slot": "10:30",
                "reason": "High fever since this morning", "temperature": 101.5,
                "symptoms": ["fever", "headache"]})
            check("valid booking -> 201", r.status_code == 201, r.text)
            appt_a_id = r.json()["id"]

            r = await c.get(f"/clinic/free-slots?date={tomorrow}")
            check("booked slot vanishes from free list",
                  "10:30" not in r.json()["free_slots"])

            r = await c.post("/appointments", headers=hdr_b, json={
                "date": tomorrow, "slot": "10:30",
                "reason": "Also need this exact slot please", "symptoms": ["cough"]})
            check("Gate 4: second patient same slot -> 409", r.status_code == 409, r.text)

            print("\n== THE RACE (steel door) ==")
            # Fire N concurrent bookings for the SAME fresh slot.
            async def race_book(hdr, tag):
                return await c.post("/appointments", headers=hdr, json={
                    "date": tomorrow, "slot": "11:00",
                    "reason": f"Race test booking {tag} needs slot",
                    "symptoms": ["fever"]})
            # both patients + repeats, all at once
            tasks = [race_book(hdr_a, "a"), race_book(hdr_b, "b"),
                     race_book(hdr_a, "a2"), race_book(hdr_b, "b2")]
            race_results = await asyncio.gather(*tasks)
            codes = sorted(rr.status_code for rr in race_results)
            successes = sum(1 for rr in race_results if rr.status_code == 201)
            conflicts = sum(1 for rr in race_results if rr.status_code == 409)
            check("exactly ONE wins the race", successes == 1,
                  f"successes={successes} codes={codes}")
            check("all others get 409", conflicts == len(tasks) - 1,
                  f"conflicts={conflicts}")

            print("\n== MY APPOINTMENTS (privacy) ==")
            r = await c.get("/appointments/mine", headers=hdr_a)
            a_ids = {x["id"] for x in r.json()}
            check("A sees only A's bookings", appt_a_id in a_ids)
            r_b = await c.get("/appointments/mine", headers=hdr_b)
            b_ids = {x["id"] for x in r_b.json()}
            check("A's booking not in B's list", appt_a_id not in b_ids)

            print("\n== DOCTOR-ONLY (403 vs 401) ==")
            r = await c.get(f"/doctor/schedule?date={tomorrow}")
            check("doctor route no token -> 401", r.status_code == 401)
            r = await c.get(f"/doctor/schedule?date={tomorrow}", headers=hdr_a)
            check("PATIENT token on doctor route -> 403", r.status_code == 403, r.text)
            r = await c.get(f"/doctor/schedule?date={tomorrow}", headers=hdr_doc)
            check("doctor sees schedule -> 200", r.status_code == 200, r.text)
            sched = r.json()["schedule"]
            check("schedule shows patient names",
                  any("patient_name" in item and item["patient_name"] for item in sched))
            r = await c.get("/doctor/stats", headers=hdr_doc)
            check("doctor stats -> 200", r.status_code == 200, r.text)
            check("stats count patients", r.json()["total_registered_patients"] >= 2)

            print("\n== CANCEL (R9) ==")
            r = await c.patch(f"/appointments/{appt_a_id}/cancel", headers=hdr_b)
            check("cancel someone else's -> 403", r.status_code == 403, r.text)
            r = await c.patch(f"/appointments/{appt_a_id}/cancel", headers=hdr_a)
            check("cancel own -> 200", r.status_code == 200, r.text)
            r = await c.get(f"/clinic/free-slots?date={tomorrow}")
            check("cancelled slot reappears as free", "10:30" in r.json()["free_slots"])
            r = await c.patch(f"/appointments/{appt_a_id}/cancel", headers=hdr_a)
            check("double cancel -> 409", r.status_code == 409, r.text)

    print("\n" + "=" * 40)
    total = len(results)
    passed = sum(results)
    print(f"  {passed}/{total} checks passed")
    print("=" * 40)
    return passed == total


if __name__ == "__main__":
    ok = asyncio.run(main())
    raise SystemExit(0 if ok else 1)
