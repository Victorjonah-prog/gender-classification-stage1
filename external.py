import httpx
import asyncio


async def fetch_all(name: str):
    async with httpx.AsyncClient(timeout=10.0) as client:
        gender_res, age_res, nation_res = await asyncio.gather(
            client.get(f"https://api.genderize.io", params={"name": name}),
            client.get(f"https://api.agify.io", params={"name": name}),
            client.get(f"https://api.nationalize.io", params={"name": name}),
        )

    gender_data = gender_res.json()
    age_data = age_res.json()
    nation_data = nation_res.json()

    # Validate Genderize
    if gender_data.get("gender") is None or gender_data.get("count") == 0:
        raise ValueError("Genderize returned an invalid response")

    # Validate Agify
    if age_data.get("age") is None:
        raise ValueError("Agify returned an invalid response")

    # Validate Nationalize
    countries = nation_data.get("country", [])
    if not countries:
        raise ValueError("Nationalize returned an invalid response")

    # Pick country with highest probability
    top_country = max(countries, key=lambda c: c["probability"])

    # Age group logic
    age = age_data["age"]
    if age <= 12:
        age_group = "child"
    elif age <= 19:
        age_group = "teenager"
    elif age <= 59:
        age_group = "adult"
    else:
        age_group = "senior"

    return {
        "gender": gender_data["gender"],
        "gender_probability": gender_data["probability"],
        "sample_size": gender_data["count"],
        "age": age,
        "age_group": age_group,
        "country_id": top_country["country_id"],
        "country_probability": top_country["probability"],
    }