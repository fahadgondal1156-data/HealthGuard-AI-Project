from src.healthguard.security import hash_password,verify_password,create_token,decode_token

def test_password_hash_and_token():
    h=hash_password("a-long-test-password")
    assert verify_password("a-long-test-password",h)
    t=create_token("alice","clinician"); p=decode_token(t)
    assert p["sub"]=="alice" and p["role"]=="clinician"
